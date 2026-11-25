from pysat.solvers import Cadical195
cl = [[1,9,-11],[-4,-10,-13],[1,-9,-14],[2,6,14],[-5,-6,15],[2,-3,15],[3,5,-9],[-6,-12,-15],[-1,5,-11],[4,-7,-15],[-2,8,-12],[3,9,11],[-4,-8,10],[7,-8,13],[4,7,-13],[-2,-7,14],[-3,11,-14],[8,10,12],[-10,12,13],[-1,-5,6]]
def models(cls, nv, cap=100000):
    out = []
    with Cadical195(bootstrap_with=cls) as s:
        while s.solve():
            m = s.get_model()[:nv]; out.append(m)
            s.add_clause([-l for l in m])
            if len(out) >= cap: break
    return out
print("minimally unsat?", all(len(models([c for j,c in enumerate(cl) if j!=i],15,1))>0 for i in range(20)))
for i in range(20):
    ms = models([c for j,c in enumerate(cl) if j!=i], 15)
    bb = set(ms[0]); [bb.intersection_update(m) for m in ms]
    print(f"remove C{i+1}: models={len(ms)} backbone size={len(bb)}")
