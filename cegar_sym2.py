"""CEGAR search for an unsatisfiable "block": a CNF whose clauses have prescribed widths
(mostly 4, a few short ones), with every literal occurring at most LB times, and which is
invariant under a cyclic group Z_r acting on the variables in r-cycles.

Variables are (o, i): orbit o in [0, t), phase i in Z_r.  A clause orbit is given by a
representative; the formula is the union of all r shifts of all representatives.

Loop: a structure solver proposes representatives that falsify every assignment found so
far (with all its shifts); a checker solver looks for a model of the proposed formula.
Stops when the checker finds the formula unsatisfiable (success) or the structure
solver runs out of candidates (no such symmetric block exists, for these parameters).

usage: cegar_sym.py r t widths(comma list) [LB=3] [seed] [maxiter]
"""
import sys, time, random, itertools
from pysat.solvers import Cadical195
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

def main():
    r = int(sys.argv[1]); t = int(sys.argv[2])
    widths = [int(x) for x in sys.argv[3].split(',')]
    LB = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    maxiter = int(sys.argv[6]) if len(sys.argv) > 6 else 10**9
    global KMOD
    KMOD = int(sys.argv[7]) if len(sys.argv) > 7 else 8
    random.seed(seed)
    J = len(widths); n = r * t
    pool = IDPool()
    IN = lambda j, o, i: pool.id(('in', j, o, i))
    POS = lambda j, o, i: pool.id(('pos', j, o, i))
    LP = lambda j, o, i: pool.id(('lp', j, o, i))
    LN = lambda j, o, i: pool.id(('ln', j, o, i))
    S = Cadical195()
    def add(cl): S.add_clause(cl)
    for j in range(J):
        for o in range(t):
            for i in range(r):
                a, p, lp, ln = IN(j, o, i), POS(j, o, i), LP(j, o, i), LN(j, o, i)
                add([-lp, a]); add([-lp, p]); add([lp, -a, -p])
                add([-ln, a]); add([-ln, -p]); add([ln, -a, p])
        # width exactly widths[j]
        lits = [IN(j, o, i) for o in range(t) for i in range(r)]
        for cl in CardEnc.equals(lits=lits, bound=widths[j], vpool=pool, encoding=EncType.seqcounter).clauses: add(cl)
        # a clause must not contain two shifts of the same variable that collide after shifting:
        # within one representative, variables (o,i) are distinct automatically; but the full
        # orbit is fine.  normalisation: some literal of rep j sits at phase 0
        add([IN(j, o, 0) for o in range(t)])
    # literal bounds: positive occurrences of any variable of orbit o = sum_j sum_i LP(j,o,i)
    for o in range(t):
        for F in (LP, LN):
            lits = [F(j, o, i) for j in range(J) for i in range(r)]
            for cl in CardEnc.atmost(lits=lits, bound=LB, vpool=pool, encoding=EncType.seqcounter).clauses: add(cl)
    # symmetry breaking (valid): orbit 0 is used; orbits used in order (orbit o used => orbit o-1 used)
    used = [pool.id(('used', o)) for o in range(t)]
    for o in range(t):
        occ = [IN(j, o, i) for j in range(J) for i in range(r)]
        add([-used[o]] + occ)
        for v in occ: add([used[o], -v])
    for o in range(1, t): add([-used[o], used[o - 1]])
    # (optional) every orbit used: a block with an unused orbit is a block with smaller t
    for o in range(t): add([used[o]])
    # normalisation (orbit relabelling, per-orbit phase shift, per-orbit sign flip are symmetries):
    add([IN(0, 0, 0)]); add([POS(0, 0, 0)])

    var = lambda o, i: o * r + (i % r) + 1
    def build(model):
        ms = set(l for l in model if l > 0)
        reps = []
        for j in range(J):
            rep = []
            for o in range(t):
                for i in range(r):
                    if IN(j, o, i) in ms:
                        rep.append((o, i, POS(j, o, i) in ms))
            reps.append(rep)
        F = []
        for rep in reps:
            for s in range(r):
                F.append([var(o, i + s) * (1 if pos else -1) for (o, i, pos) in rep])
        return reps, F
    def block_assignment(alpha):
        # alpha: dict var -> bool. add: some clause (j, shift s) is falsified by alpha
        ors = []
        for j in range(J):
            for s in range(r):
                f = pool.id(('f', len(seen), j, s))
                ors.append(f)
                for o in range(t):
                    for i in range(r):
                        val = alpha[var(o, i + s)]
                        # literal (o,i,pos) false under alpha  <=>  pos != val
                        add([-f, -IN(j, o, i), (-POS(j, o, i) if val else POS(j, o, i))])
        add(ors)
    seen = []
    t0 = time.time(); it = 0
    while it < maxiter:
        it += 1
        if not S.solve():
            print(f"NO BLOCK: structure space exhausted after {it} iterations ({time.time()-t0:.1f}s)  r={r} t={t} widths={widths} LB={LB}", flush=True)
            return
        reps, F = build(S.get_model())
        with Cadical195(bootstrap_with=F) as C:
            if not C.solve():
                print(f"UNSAT BLOCK FOUND after {it} iterations: r={r} t={t} widths={widths} LB={LB}", flush=True)
                print("reps:", reps, flush=True)
                print("formula:", F, flush=True)
                return
            models = []
            for _k in range(KMOD):
                m = C.get_model()
                models.append(m)
                C.add_clause([-l for l in m if abs(l) <= n])
                if not C.solve(): break
        for m in models:
            alpha = {abs(l): l > 0 for l in m}
            for v in range(1, n + 1): alpha.setdefault(v, False)
            seen.append(alpha)
            block_assignment(alpha)
        if it % 20 == 0:
            print(f"iter {it}  {time.time()-t0:.0f}s  vars={pool.top}", flush=True)
    print("maxiter reached", flush=True)

if __name__ == "__main__":
    main()
