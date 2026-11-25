"""Do 'clause trees' exist?  Full binary tree, every leaf at depth >= K (clause size),
and for every internal node v and each child subtree, the number of leaves at distance
1..K below v inside that child subtree is <= B (literal occurrence bound).
Leaf clause = negated labels of its last K ancestor edges -> UNSAT K-CNF in which every
literal occurs <= B times.  Profile of a subtree = (#leaves at relative depth 0..K-1)."""
import sys, itertools
def search(K, B, max_rounds=200):
    leaf = (1,) + (0,)*(K-1)
    prof = {leaf: None}
    for r in range(max_rounds):
        new = {}
        ok = [p for p in prof if sum(p) <= B]          # usable as a child of any node
        for a, b in itertools.combinations_with_replacement(ok, 2):
            q = (0,) + tuple(a[j] + b[j] for j in range(K-1))
            if q not in prof and q not in new:
                new[q] = (a, b)
        if not new:
            break
        prof.update(new)
        if (0,)*K in prof:
            return True, r, prof
    return ((0,)*K in prof), r, prof
for K,B in [(3,1),(3,2),(4,2),(4,3),(5,3),(5,4),(6,4),(6,5),(7,6)]:
    ok, r, prof = search(K,B)
    print(f"clause size {K}, literal bound {B}: tree exists={ok} (rounds {r}, profiles {len(prof)})")
