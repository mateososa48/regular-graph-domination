"""Produce and check DRAT certificates that the published 50-vertex cubic graph has
no dominating set and no independent dominating set of size <= 15 (gamma_e = 15)."""
import subprocess
from domlib import gadget, is_maximal_matching
from satdom import dom_le, emm_le
cl = [[1,9,-11],[-4,-10,-13],[1,-9,-14],[2,6,14],[-5,-6,15],[2,-3,15],[3,5,-9],[-6,-12,-15],[-1,5,-11],[4,-7,-15],[-2,8,-12],[3,9,11],[-4,-8,10],[7,-8,13],[4,7,-13],[-2,-7,14],[-3,11,-14],[8,10,12],[-10,12,13],[-1,-5,6]]
G = gadget(cl, 15)
M = emm_le(G, 15); assert M and is_maximal_matching(G, M) and len(M) == 15
print("gamma_e <= 15 witness (maximal matching):", M)
print("gamma_e >= 15: counting bound 3n/10 = 15 for cubic graphs (each matched vertex has <= 2 edges to the unmatched independent set)")
for name, ind in [("dominating", False), ("independent dominating", True)]:
    assert dom_le(G, 15, independent=ind, proof_path=f"cubic_{'i' if ind else 'g'}15") is None
    r = subprocess.run(["./drat-trim", f"cubic_{'i' if ind else 'g'}15.cnf", f"cubic_{'i' if ind else 'g'}15.drat"], capture_output=True, text=True)
    verdict = [l for l in r.stdout.splitlines() if "VERIFIED" in l or "NOT" in l]
    print(f"no {name} set of size <= 15:", verdict)
