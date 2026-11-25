import time, networkx as nx
from domlib import gadget, degrees, is_dominating, is_independent, is_maximal_matching
from satdom import dom_le, emm_le
cl = [[1,9,-11],[-4,-10,-13],[1,-9,-14],[2,6,14],[-5,-6,15],[2,-3,15],[3,5,-9],[-6,-12,-15],
      [-1,5,-11],[4,-7,-15],[-2,8,-12],[3,9,11],[-4,-8,10],[7,-8,13],[4,7,-13],[-2,-7,14],
      [-3,11,-14],[8,10,12],[-10,12,13],[-1,-5,6]]
G = gadget(cl, 15)
n=G.number_of_nodes(); D=3
print("counting lower bound for gamma_e:", D*n/(4*D-2))
M = emm_le(G, 15); print("maximal matching of size 15:", M is not None and is_maximal_matching(G, M))
for K, ind in [(16,False),(15,False),(16,True),(15,True)]:
    t=time.time(); r = dom_le(G, K, independent=ind)
    ok = r is not None and is_dominating(G,r) and (not ind or is_independent(G,r))
    print(("i" if ind else "gamma"), "<=", K, ":", "YES" if r else "NO", ok if r else "", f"{time.time()-t:.1f}s", flush=True)
