"""Local 'shrink' moves on a cubic graph: delete two adjacent vertices u,v and reconnect the four
orphaned neighbours by two new edges (3 pairings).  Output graph6 of every simple cubic result."""
import sys, itertools, networkx as nx
def shrink_once(G):
    out = []
    for u, v in G.edges():
        A = [w for w in G[u] if w != v]; B = [w for w in G[v] if w != u]
        if len(set(A + B)) < 4: continue
        H0 = G.copy(); H0.remove_nodes_from([u, v])
        for (p, q), (r, s) in [((A[0], A[1]), (B[0], B[1])), ((A[0], B[0]), (A[1], B[1])), ((A[0], B[1]), (A[1], B[0]))]:
            if H0.has_edge(p, q) or H0.has_edge(r, s): continue
            H = H0.copy(); H.add_edge(p, q); H.add_edge(r, s)
            if all(d == 3 for _, d in H.degree()) and nx.is_connected(H):
                out.append(nx.convert_node_labels_to_integers(H))
    return out
if __name__ == "__main__":
    from domlib import gadget
    cl = [[1,9,-11],[-4,-10,-13],[1,-9,-14],[2,6,14],[-5,-6,15],[2,-3,15],[3,5,-9],[-6,-12,-15],[-1,5,-11],[4,-7,-15],[-2,8,-12],[3,9,11],[-4,-8,10],[7,-8,13],[4,7,-13],[-2,-7,14],[-3,11,-14],[8,10,12],[-10,12,13],[-1,-5,6]]
    G = gadget(cl, 15)
    level = [G]
    for depth in range(int(sys.argv[1])):
        nxt = []
        for H in level: nxt += shrink_once(H)
        # dedupe by canonical form via graph6 of nauty canonical labelling is costly; keep all (small)
        level = nxt
        sys.stderr.write(f"depth {depth+1}: {len(level)} graphs on {level[0].number_of_nodes() if level else '-'} vertices\n")
    for H in level:
        print(nx.to_graph6_bytes(H, header=False).decode().strip())
