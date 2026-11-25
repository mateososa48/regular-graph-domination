"""Maximise beta over configurations where every index has free-set sizes {1,3,3} or {2,2,3}
(the only case in which beta can exceed 1/2), each free literal used at most 3 times."""
import itertools, random, sys
import numpy as np
V = int(sys.argv[1]); seed = int(sys.argv[2]); steps = int(sys.argv[3]); R = int(sys.argv[4])
rng = random.Random(seed)
Z = np.array(list(itertools.product([0, 1], repeat=V)), dtype=np.int8)
TYPES = [(1, 3, 3), (2, 2, 3)]

def fm(free):
    m = np.ones(len(Z), dtype=bool)
    for v, s in free:
        m &= (Z[:, v] == s)
    return m

def beta(cfg):
    tot = np.ones(len(Z), dtype=bool)
    for blks in cfg:
        u = np.zeros(len(Z), dtype=bool)
        for f in blks:
            u |= fm(f)
        tot &= u
    return tot.mean()

def ok(cfg):
    occ = {}
    for blks in cfg:
        if len({tuple(sorted(f)) for f in blks}) < len(blks):
            pass  # same free set in one index is allowed (different C-literals)
        for f in blks:
            if len({v for v, s in f}) != len(f):
                return False
            for l in f:
                occ[l] = occ.get(l, 0) + 1
    return all(o <= 3 for o in occ.values())

def rand_set(k):
    return tuple((v, rng.randint(0, 1)) for v in rng.sample(range(V), k))

def init():
    while True:
        cfg = []
        for i in range(4):
            t = rng.choice(TYPES)
            cfg.append([rand_set(k) for k in t])
        if ok(cfg):
            return cfg

def mutate(cfg):
    new = [list(b) for b in cfg]
    i = rng.randrange(4)
    r = rng.random()
    if r < 0.05:
        t = rng.choice(TYPES)
        new[i] = [rand_set(k) for k in t]
    else:
        t = rng.randrange(3)
        f = list(new[i][t])
        p = rng.randrange(len(f))
        used = {v for v, s in f}
        v = rng.choice([w for w in range(V) if w not in used] + [f[p][0]])
        f[p] = (v, rng.randint(0, 1))
        new[i][t] = tuple(f)
    return new

gbest = 0
for rs in range(R):
    cfg = init(); cur = beta(cfg); best, bc = cur, cfg
    for s in range(steps):
        T = 0.04 * (1 - s / steps) + 1e-4
        new = mutate(cfg)
        if not ok(new):
            continue
        b = beta(new)
        if b >= cur or rng.random() < np.exp((b - cur) / T):
            cfg, cur = new, b
            if cur > best:
                best, bc = cur, cfg
    if best > gbest:
        gbest = best
        print(f"restart {rs}: beta = {best:.6f} ({round(best*2**V)}/{2**V})", flush=True)
        for blks in bc:
            print("   ", blks, flush=True)
print("best", gbest)
