import networkx as nx
from satdom import dom_le, emm_le
bad = 0; tot = 0
for line in open('sample_vals.txt'):
    _, ge, iv, g6 = line.split(); ge, iv = int(ge), int(iv)
    G = nx.from_graph6_bytes(g6.encode())
    # SAT: ge is a maximal matching size achievable and ge-1 is not; same for i
    ok = emm_le(G, ge) is not None and emm_le(G, ge - 1) is None and \
         dom_le(G, iv, independent=True) is not None and dom_le(G, iv - 1, independent=True) is None
    tot += 1; bad += (not ok)
print(f"cross-checked {tot} graphs (C branch-and-bound vs CaDiCaL SAT): mismatches = {bad}")
