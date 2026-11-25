"""Complete search for UNSATISFIABLE cyclic-symmetric K-CNFs with every literal in at most L clauses.

Variables x[c][i], c in range(v) (classes), i in Z_N.  The formula is the union of r orbits under the shift
i -> i+1 of r base clauses of width K.  A base literal of class c and sign s gives every variable of class c
one more occurrence with sign s, so the literal bound is: per (class, sign) at most L base literals.

CEGAR: an outer SAT instance chooses the base clauses; an inner SAT call tries to satisfy the resulting
formula.  A satisfying assignment alpha is turned into the constraint "some shifted base clause is false
under alpha" and added to the outer instance.  Outer UNSAT = no unsatisfiable formula in this family
(exhaustive).  Inner UNSAT = found one (then re-verified by brute force / second solver).

usage: cyc_cegar.py K L v N r [max_iters] [seed]
"""
import sys, itertools, random, time
from pysat.solvers import Cadical195, Glucose4
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

K, L, v, N, r = map(int, sys.argv[1:6])
MAXIT = int(sys.argv[6]) if len(sys.argv) > 6 else 200000
random.seed(int(sys.argv[7]) if len(sys.argv) > 7 else 1)
pool = IDPool()
opts = [(c, s, sg) for c in range(v) for s in range(N) for sg in (1, -1)]
sel = {(o, p, opt): pool.id(('s', o, p, opt)) for o in range(r) for p in range(K) for opt in opts}
outer = Cadical195()
def add(c): outer.add_clause(c)
for o in range(r):
    for p in range(K):
        lits = [sel[o, p, opt] for opt in opts]
        add(lits)
        for cl in CardEnc.atmost(lits=lits, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses: add(cl)
    # positions strictly increasing in variable index (class, shift): distinct variables, canonical order
    for p in range(K - 1):
        for A in opts:
            for B in opts:
                if (B[0], B[1]) <= (A[0], A[1]): add([-sel[o, p, A], -sel[o, p + 1, B]])
    # rotate so that the first literal has shift 0
    for opt in opts:
        if opt[1] != 0: add([-sel[o, 0, opt]])
# literal bound
for c in range(v):
    for sg in (1, -1):
        lits = [sel[o, p, (c, s, sg)] for o in range(r) for p in range(K) for s in range(N)]
        for cl in CardEnc.atmost(lits=lits, bound=L, vpool=pool, encoding=EncType.seqcounter).clauses: add(cl)
# orbit order symmetry: first-literal class non-decreasing across orbits (weak but valid)
for o in range(r - 1):
    for A in opts:
        for B in opts:
            if A[1] == 0 and B[1] == 0 and B[0] < A[0]: add([-sel[o, 0, A], -sel[o + 1, 0, B]])

var = lambda c, i: c * N + (i % N) + 1
def decode(model):
    ms = set(l for l in model if l > 0)
    base = []
    for o in range(r):
        cl = []
        for p in range(K):
            for opt in opts:
                if sel[o, p, opt] in ms: cl.append(opt)
        base.append(cl)
    return base
def expand(base):
    F = set()
    for cl in base:
        for rho in range(N):
            F.add(tuple(sorted((sg * var(c, s + rho) for (c, s, sg) in cl), key=abs)))
    return sorted(F)
def inner_models(F, want=6):
    out = []
    for t in range(want):
        with Glucose4(bootstrap_with=F) as g:
            # random phases for diversity
            g.set_phases([random.choice((1, -1)) * x for x in range(1, v * N + 1)])
            if not g.solve(): return None
            out.append(g.get_model()[:v * N])
    return out
def add_cex(alpha):
    val = {abs(l): (l > 0) for l in alpha}
    fs = []
    for o in range(r):
        for rho in range(N):
            f = pool.id(); fs.append(f)
            for p in range(K):
                add([-f] + [sel[o, p, (c, s, sg)] for (c, s, sg) in opts if val[var(c, s + rho)] != (sg > 0)])
    add(fs)

t0 = time.time(); it = 0; ncex = 0
while it < MAXIT:
    it += 1
    if not outer.solve():
        print(f"EXHAUSTED: no unsatisfiable cyclic formula for K={K} L={L} v={v} N={N} r={r} "
              f"(n={v*N}, m<={r*N}); iterations={it} counterexamples={ncex} time={time.time()-t0:.0f}s", flush=True)
        sys.exit(0)
    base = decode(outer.get_model()); F = expand(base)
    ms = inner_models([list(c) for c in F])
    if ms is None:
        print(f"FOUND unsatisfiable formula: K={K} L={L} v={v} N={N} r={r} n={v*N} m={len(F)}", flush=True)
        print("base clauses (class, shift, sign):", base, flush=True)
        print("clauses:", F, flush=True)
        from collections import Counter
        cnt = Counter(l for c in F for l in c); print("max literal occurrences:", max(cnt.values()), flush=True)
        with Cadical195(bootstrap_with=[list(c) for c in F]) as c2: print("second solver says satisfiable:", c2.solve(), flush=True)
        sys.exit(0)
    seen = set()
    for a in ms:
        key = tuple(a)
        if key in seen: continue
        seen.add(key); add_cex(a); ncex += 1
    if it % 200 == 0: print(f"# it={it} cex={ncex} t={time.time()-t0:.0f}s", flush=True)
print("STOPPED at max iterations", it, flush=True)
