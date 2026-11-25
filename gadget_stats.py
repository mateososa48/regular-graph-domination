import random, sys, time, collections
from domlib import gadget
from satdom import dom_le
from pysat.solvers import Cadical195
def random_balanced(k, K, B, rng):
    c = 2*k*B//K
    while True:
        stubs = [ (v+1) * s for v in range(k) for s in (1,-1) for _ in range(B)]
        rng.shuffle(stubs)
        cls = [stubs[i*K:(i+1)*K] for i in range(c)]
        # repair repeated variables by random swaps
        for _ in range(20000):
            bad = [(i,t) for i,C in enumerate(cls) for t in range(K) if sum(abs(x)==abs(C[t]) for x in C) > 1]
            if not bad: return cls
            i,t = rng.choice(bad); j = rng.randrange(c); u = rng.randrange(K)
            cls[i][t], cls[j][u] = cls[j][u], cls[i][t]
def min_size(G, K, indep):
    # smallest s <= K with a (independent) dominating set of size s, scanning down from K
    best = None; s = K
    while s >= 1:
        r = dom_le(G, s, independent=indep)
        if r is None: break
        best = len(r); s = best - 1
    return best
rng = random.Random(1)
K, B = int(sys.argv[1]), int(sys.argv[2]); trials = int(sys.argv[3])
for k in map(int, sys.argv[4:]):
    gi = collections.Counter(); gg = collections.Counter(); unsat = 0; t = time.time()
    for _ in range(trials):
        cls = random_balanced(k, K, B, rng)
        with Cadical195(bootstrap_with=cls) as s:
            if not s.solve(): unsat += 1
        G = gadget(cls, k)
        i = min_size(G, k, True); g = min_size(G, k, False)
        gi[k - i if i is not None else -1] += 1; gg[k - g if g is not None else -1] += 1
    print(f"Delta={K} k={k} n={G.number_of_nodes()}: unsat formulas {unsat}/{trials}; (k - i) dist {dict(sorted(gi.items()))}; (k - gamma) dist {dict(sorted(gg.items()))} [{time.time()-t:.0f}s]", flush=True)
