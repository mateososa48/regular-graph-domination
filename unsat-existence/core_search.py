"""Exact search for small 'cores' (blocks) for the Baste problem.

A core for clause width K and literal bound L is an UNSATISFIABLE CNF on r variables with t clauses,
every clause of width between WMIN and K, every literal in at most L clauses, and total deficit
D = sum_C (K - |C|) <= DMAX.  (A formula with D = 0 would be an unsatisfiable (K,L,L)-formula.)

Encoding: P[i][j] / N[i][j] = clause i contains x_j / not x_j.  For every assignment a, some clause is
falsified.  Symmetry breaking: rows (clauses) and columns (variables) in lexicographic order, and each
variable has at least as many positive as negative occurrences.  Solved with kissat (or cadical).

usage: core_search.py K L DMAX r t [WMIN=2] [solver=kissat] [timeout_s=3600]
prints SAT + the formula, or UNSAT (= no such core, exhaustive), or UNKNOWN on timeout.
"""
import sys, itertools, subprocess, tempfile, os, time
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

def build(K, L, DMAX, r, t, WMIN=2):
    pool = IDPool(); cls = []
    P = [[pool.id(('P', i, j)) for j in range(r)] for i in range(t)]
    N = [[pool.id(('N', i, j)) for j in range(r)] for i in range(t)]
    def card_atmost(lits, k):
        if k >= len(lits): return
        if k < 0: cls.append([]); return
        enc = CardEnc.atmost(lits=lits, bound=k, vpool=pool, encoding=EncType.seqcounter); cls.extend(enc.clauses)
    def card_atleast(lits, k):
        if k <= 0: return
        if k > len(lits): cls.append([]); return
        enc = CardEnc.atleast(lits=lits, bound=k, vpool=pool, encoding=EncType.seqcounter); cls.extend(enc.clauses)
    for i in range(t):
        for j in range(r): cls.append([-P[i][j], -N[i][j]])
        occ = [P[i][j] for j in range(r)] + [N[i][j] for j in range(r)]
        card_atmost(occ, K); card_atleast(occ, WMIN)
    for j in range(r):
        card_atmost([P[i][j] for i in range(t)], L)
        card_atmost([N[i][j] for i in range(t)], L)
    # deficit: O[i][d] true iff width_i <= K-1-d, i.e. clause i has at least d+1 open slots (d = 0..K-WMIN-1)
    openv = []
    for i in range(t):
        occ = [P[i][j] for j in range(r)] + [N[i][j] for j in range(r)]
        for d in range(K - WMIN):
            o = pool.id(('O', i, d)); openv.append(o)
            # not o -> width >= K-d   (at least K-d literals)
            enc = CardEnc.atleast(lits=occ, bound=K - d, vpool=pool, encoding=EncType.seqcounter)
            for c in enc.clauses: cls.append(c + [o])
    card_atmost(openv, DMAX)
    # coverage
    for a in range(1 << r):
        row = []
        for i in range(t):
            f = pool.id(('F', i, a)); row.append(f)
            for j in range(r):
                if (a >> j) & 1: cls.append([-f, -P[i][j]])   # x_j true -> clause must not contain x_j
                else:            cls.append([-f, -N[i][j]])
        cls.append(row)
    # every variable used, with #pos >= #neg  (sign symmetry): encode pos>=neg via pairwise counter is heavy;
    # use the weaker valid rule: the variable occurs positively somewhere.
    for j in range(r): cls.append([P[i][j] for i in range(t)])
    # lex order helpers
    def lex_leq(A, B):
        # vectors of literals; enforce A <=lex B (A before B), where True > False
        n = len(A); e = [pool.id() for _ in range(n + 1)]   # e[k]: prefixes of length k equal
        cls.append([e[0]])
        for k in range(n):
            cls.append([-e[k], -A[k], B[k]])                 # equal so far and A[k]=1 -> B[k]=1
            cls.append([-e[k + 1], e[k]])
            cls.append([-e[k + 1], -A[k], B[k]]); cls.append([-e[k + 1], A[k], -B[k]])
            cls.append([-e[k], A[k], B[k], e[k + 1]]); cls.append([-e[k], -A[k], -B[k], e[k + 1]])
    rowvec = lambda i: [v for j in range(r) for v in (P[i][j], N[i][j])]
    colvec = lambda j: [v for i in range(t) for v in (P[i][j], N[i][j])]
    for i in range(t - 1): lex_leq(rowvec(i + 1), rowvec(i))     # rows non-increasing
    for j in range(r - 1): lex_leq(colvec(j + 1), colvec(j))     # columns non-increasing
    return pool, cls, P, N

def solve(K, L, DMAX, r, t, WMIN=2, solver='kissat', timeout=3600):
    pool, cls, P, N = build(K, L, DMAX, r, t, WMIN)
    nv = pool.top
    fd, path = tempfile.mkstemp(suffix='.cnf'); os.close(fd)
    with open(path, 'w') as f:
        f.write(f"p cnf {nv} {len(cls)}\n")
        for c in cls: f.write(' '.join(map(str, c)) + ' 0\n')
    t0 = time.time()
    try:
        cmd = [solver, '-q', path] if solver == 'kissat' else [solver, '-q', path]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout
    except subprocess.TimeoutExpired:
        os.unlink(path); return 'UNKNOWN', None, time.time() - t0
    os.unlink(path)
    if 's UNSATISFIABLE' in out: return 'UNSAT', None, time.time() - t0
    if 's SATISFIABLE' not in out: return 'UNKNOWN', None, time.time() - t0
    model = set()
    for line in out.splitlines():
        if line.startswith('v '):
            for tok in line.split()[1:]:
                v = int(tok)
                if v > 0: model.add(v)
    F = []
    for i in range(t):
        c = [j + 1 for j in range(r) if P[i][j] in model] + [-(j + 1) for j in range(r) if N[i][j] in model]
        F.append(sorted(c, key=abs))
    return 'SAT', F, time.time() - t0

def check(F, K, L, r):
    """independent brute-force check that F is an unsatisfiable formula within the bounds"""
    from collections import Counter
    cnt = Counter(l for c in F for l in c)
    assert all(v <= L for v in cnt.values()), 'literal bound'
    assert all(len(set(map(abs, c))) == len(c) <= K for c in F), 'width'
    for a in range(1 << r):
        val = lambda l: ((a >> (abs(l) - 1)) & 1) == (l > 0)
        if all(any(val(l) for l in c) for c in F): return False
    return True

if __name__ == '__main__':
    K, L, DMAX, r, t = map(int, sys.argv[1:6])
    WMIN = int(sys.argv[6]) if len(sys.argv) > 6 else 2
    solver = sys.argv[7] if len(sys.argv) > 7 else 'kissat'
    timeout = int(sys.argv[8]) if len(sys.argv) > 8 else 3600
    st, F, dt = solve(K, L, DMAX, r, t, WMIN, solver, timeout)
    print(f"K={K} L={L} DMAX={DMAX} r={r} t={t} WMIN={WMIN}: {st} ({dt:.1f}s)", flush=True)
    if F:
        print("  formula:", F, " D =", sum(K - len(c) for c in F), " verified unsat:", check(F, K, L, r), flush=True)
