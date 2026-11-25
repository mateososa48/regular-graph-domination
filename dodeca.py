import networkx as nx, itertools
from pysat.solvers import Cadical195
from domlib import gadget, degrees
from satdom import dom_le
D = nx.dodecahedral_graph()
# antipodal map: vertex at max distance (5) is unique in the dodecahedron
dist = dict(nx.all_pairs_shortest_path_length(D))
anti = {v: [w for w in D if dist[v][w] == 5][0] for v in D}
edges = [tuple(sorted(e)) for e in D.edges()]
pairs, seen = [], set()
for e in edges:
    if e in seen: continue
    f = tuple(sorted((anti[e[0]], anti[e[1]])))
    seen.add(e); seen.add(f); pairs.append((e, f))
print("pairs:", len(pairs))
lit = {}
for j, (e, f) in enumerate(pairs):
    lit[e] = j + 1; lit[f] = -(j + 1)
clauses = [[lit[tuple(sorted((v, w)))] for w in D[v]] for v in D]
with Cadical195(bootstrap_with=clauses) as s:
    print("dodecahedral antipodal formula SAT?", s.solve())
G = gadget(clauses, 15)
print("gadget degrees", degrees(G), "n", G.number_of_nodes())
print("gamma<=15?", dom_le(G, 15) is not None, " i<=15?", dom_le(G, 15, independent=True) is not None)
# compare with published graph
cl = [[1,9,-11],[-4,-10,-13],[1,-9,-14],[2,6,14],[-5,-6,15],[2,-3,15],[3,5,-9],[-6,-12,-15],[-1,5,-11],[4,-7,-15],[-2,8,-12],[3,9,11],[-4,-8,10],[7,-8,13],[4,7,-13],[-2,-7,14],[-3,11,-14],[8,10,12],[-10,12,13],[-1,-5,6]]
print("isomorphic to published gadget?", nx.is_isomorphic(G, gadget(cl, 15)))
# structure of the published formula: clause graph (clauses adjacent if they share a literal)
H = nx.Graph()
for a, b in itertools.combinations(range(20), 2):
    if set(cl[a]) & set(cl[b]): H.add_edge(a, b)
print("published clause-sharing graph: regular deg", degrees(H), "girth?", nx.girth(H) if hasattr(nx,'girth') else '?', "is dodecahedron?", nx.is_isomorphic(H, D))
