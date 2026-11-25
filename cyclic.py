"""Random cyclic (Z_m-invariant) K-CNFs in which every literal occurs exactly B times.
r variable orbits of size m, b base clauses; clause set = all Z_m-shifts of the base clauses."""
import random, sys, time
from pysat.solvers import Cadical195
def design(K, B, r, b, m, rng):
    slots = [(j, s) for j in range(r) for s in (1, -1) for _ in range(B)]
    assert len(slots) == K * b
    rng.shuffle(slots)
    base = []
    for c in range(b):
        cl = []
        for t, (j, s) in enumerate(slots[c*K:(c+1)*K]):
            cl.append((j, s, 0 if t == 0 else rng.randrange(m)))
        base.append(cl)
    return base
def expand(base, m):
    cls = []
    for t in range(m):
        for cl in base:
            lits = [(j*m + (o + t) % m + 1) * s for (j, s, o) in cl]
            if len(set(abs(x) for x in lits)) < len(lits): return None
            cls.append(lits)
    return cls
if __name__ == "__main__":
    K, B, r, b = map(int, sys.argv[1:5]); ms = list(map(int, sys.argv[5].split(','))); trials = int(sys.argv[6])
    rng = random.Random(int(sys.argv[7]) if len(sys.argv) > 7 else 0)
    for m in ms:
        t0 = time.time(); found = 0; valid = 0
        for _ in range(trials):
            base = design(K, B, r, b, m, rng); cls = expand(base, m)
            if cls is None: continue
            valid += 1
            with Cadical195(bootstrap_with=cls) as s:
                if not s.solve():
                    found += 1
                    if found <= 3: print(f"UNSAT K={K} B={B} m={m} k={r*m} c={len(cls)} base={base}", flush=True)
        print(f"K={K} B={B} r={r} b={b} m={m}: valid {valid}, unsat {found} [{time.time()-t0:.0f}s]", flush=True)
