"""Adversarial search over local configurations around a clause C of width D
(literals l_0..l_{D-1}), maximising beta = Pr[every variable of C is blocked | C false].

A blocker for index i contains ~l_i, j literals of C other than l_i, and D-1-j free literals.
Constraints: <= D-1 blockers per index; each l_k used by blockers at most D-2 times;
each free literal used at most D-1 times; blockers of one index distinct.
usage: beta_anneal_general.py D V seed steps restarts
"""
import itertools, random, sys
import numpy as np

D, V, seed, steps, R = (int(a) for a in sys.argv[1:6])
rng = random.Random(seed)
Z = np.array(list(itertools.product([0, 1], repeat=V)), dtype=np.int8)

def fm(free):
    m = np.ones(len(Z), dtype=bool)
    for v, s in free:
        m &= (Z[:, v] == s)
    return m

def beta(cfg):
    tot = np.ones(len(Z), dtype=bool)
    for i in range(D):
        u = np.zeros(len(Z), dtype=bool)
        for K, free in cfg[i]:
            u |= fm(free)
        tot &= u
    return tot.mean()

def feasible(cfg):
    use = [0] * D; occ = {}
    for i in range(D):
        if len(cfg[i]) > D - 1:
            return False
        keys = set()
        for K, free in cfg[i]:
            key = (K, tuple(sorted(free)))
            if key in keys or i in K or len(K) + len(free) != D - 1:
                return False
            keys.add(key)
            for k in K:
                use[k] += 1
            if len({v for v, s in free}) != len(free):
                return False
            for l in free:
                occ[l] = occ.get(l, 0) + 1
    return all(u <= D - 2 for u in use) and all(o <= D - 1 for o in occ.values())

def rblk(i):
    j = rng.randint(0, D - 1)
    K = tuple(sorted(rng.sample([k for k in range(D) if k != i], j)))
    return (K, tuple((v, rng.randint(0, 1)) for v in rng.sample(range(V), D - 1 - j)))

def mutate(cfg):
    new = [list(b) for b in cfg]
    i = rng.randrange(D); r = rng.random()
    if r < 0.12 and new[i]:
        new[i].pop(rng.randrange(len(new[i])))
    elif r < 0.3 and len(new[i]) < D - 1:
        new[i].append(rblk(i))
    elif new[i]:
        t = rng.randrange(len(new[i])); K, free = new[i][t]
        if rng.random() < 0.4 or not free:
            new[i][t] = rblk(i)
        else:
            free = list(free); p = rng.randrange(len(free)); used = {v for v, s in free}
            v = rng.choice([w for w in range(V) if w not in used] + [free[p][0]])
            free[p] = (v, rng.randint(0, 1)); new[i][t] = (K, tuple(free))
    return new

gbest = 0.0
for rs in range(R):
    cfg = [[] for _ in range(D)]; cur = beta(cfg); best = cur
    for s in range(steps):
        T = 0.05 * (1 - s / steps) + 1e-4
        new = mutate(cfg)
        if not feasible(new):
            continue
        b = beta(new)
        if b >= cur or rng.random() < np.exp((b - cur) / T):
            cfg, cur = new, b
            best = max(best, cur)
    gbest = max(gbest, best)
    print(f"D={D} restart {rs}: best {best:.5f}  overall {gbest:.5f}", flush=True)
