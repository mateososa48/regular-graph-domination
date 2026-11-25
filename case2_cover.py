"""README item 9, degree 4, case (ii) (computer-assisted step).  Run: python3 case2_cover.py (about 2 minutes).

Case (ii) for degree 4: some variable a of C has blockers of pattern {1,1,0} (two blockers sharing one
literal of C each, one sharing none).  Their free parts give events P, P' (2 literals each) and A (3 literals),
and a is blocked iff P or P' or A happens.  If beta >= 3/5 then
  * Pr[P or P' or A] >= 3/5, which forces P, P', A pairwise inconsistent (any consistent pair overlaps by
    >= 1/32 > 1/40), so U_a = P + P' + A has probability exactly 5/8;
  * every other variable b must satisfy Pr[U_a minus U_b] <= 5/8 - 3/5 = 1/40.
Necessary condition used: Pr[E minus U_b] >= Pr[E] - sum_F Pr[E and F] for each E in {P, P', A}, F over the
events of b.  b has pattern {2,0,0} or {2,0} (main literal + residual 3-sets) or {1,1,0}.
We enumerate all structures of U_a, all ways b can use literals on a's variables (other literals are
independent of U_a), keep those with loss <= 1/40, and test whether three such b fit the literal budget
(every literal at most 3 occurrences in total, counting a's own blockers).
"""
import itertools
from fractions import Fraction as Fr

def canon_structures():
    # literals: (var, sign); P, P' 2-sets, A 3-set over variables 0..6, canonical first-appearance labelling
    seen = set(); out = []
    sizes = [2, 2, 3]
    slots = 7
    def rec(i, lits, nv):
        if i == slots:
            sets = [lits[0:2], lits[2:4], lits[4:7]]
            if any(len({v for v, s in S}) != len(S) for S in sets):
                return
            def incons(X, Y):
                return any((v, 1 - s) in Y for v, s in X)
            if not (incons(sets[0], sets[1]) and incons(sets[0], sets[2]) and incons(sets[1], sets[2])):
                return
            key = (tuple(sorted(sets[0])), tuple(sorted(sets[1])), tuple(sorted(sets[2])))
            key2 = (key[1], key[0], key[2])
            if key in seen or key2 in seen:
                return
            seen.add(key); out.append(sets)
            return
        for v in range(nv + 1):
            for s in (0, 1):
                if v == nv and s == 1 and False:
                    pass
                rec(i + 1, lits + [(v, s)], max(nv, v + 1))
    rec(0, [], 0)
    return out

def main():
    structs = canon_structures()
    print("structures of U_a (P, P', A pairwise inconsistent):", len(structs))
    mu = [Fr(1, 4), Fr(1, 4), Fr(1, 8)]
    worst_feasible = []
    for sets in structs:
        avars = sorted({v for S in sets for v, s in S})
        pool = [(v, s) for v in avars for s in (0, 1)]
        Ls = [set(S) for S in sets]
        def ev_options(k):
            # all choices of literals from pool (distinct variables) of size <= k; rest are "other" literals
            opts = []
            for r in range(0, k + 1):
                for comb in itertools.combinations(pool, r):
                    if len({v for v, s in comb}) == r:
                        opts.append((frozenset(comb), k - r))
            return opts
        def cov(ev):
            lits, other = ev
            c = []
            for L in Ls:
                if any((v, 1 - s) in L for v, s in lits):
                    c.append(Fr(0))
                else:
                    c.append(Fr(1, 2 ** (len(L | set(lits)) + other)))
            return c
        o1, o2, o3 = ev_options(1), ev_options(2), ev_options(3)
        c1 = [cov(e) for e in o1]; c2 = [cov(e) for e in o2]; c3 = [cov(e) for e in o3]
        def usage(evs):
            u = {}
            for lits, other in evs:
                for l in lits:
                    u[l] = u.get(l, 0) + 1
            return u
        def loss(cs):
            tot = Fr(0)
            for i in range(3):
                s = sum(c[i] for c in cs)
                if s < mu[i]:
                    tot += mu[i] - s
            return tot
        good = []
        lim = Fr(1, 40)
        # pattern {2,0,0} (and {2,0} is dominated: dropping a residual only increases the loss)
        for i in range(len(o1)):
            for j in range(len(o3)):
                for k in range(j, len(o3)):
                    if loss([c1[i], c3[j], c3[k]]) <= lim:
                        good.append(usage([o1[i], o3[j], o3[k]]))
        # pattern {1,1,0}
        for i in range(len(o2)):
            for j in range(i, len(o2)):
                for k in range(len(o3)):
                    if loss([c2[i], c2[j], c3[k]]) <= lim:
                        good.append(usage([o2[i], o2[j], o3[k]]))
        # budget: each literal at most 3 occurrences; a's own blockers use its literals once per set
        own = {}
        for S in sets:
            for l in S:
                own[l] = own.get(l, 0) + 1
        cap = {l: 3 - own.get(l, 0) for l in pool}
        # minimal usage vectors
        uniq = {tuple(sorted(u.items())) for u in good}
        feas = False
        ul = [dict(u) for u in uniq]
        for x, y, z in itertools.combinations_with_replacement(range(len(ul)), 3):
            if all(ul[x].get(l, 0) + ul[y].get(l, 0) + ul[z].get(l, 0) <= cap[l] for l in pool):
                feas = True
                worst_feasible.append((sets, ul[x], ul[y], ul[z]))
                break
        print(f"U_a = P{sorted(sets[0])} P'{sorted(sets[1])} A{sorted(sets[2])}: covering patterns for b: "
              f"{len(good)} ({len(uniq)} usage vectors); three fit the budget: {feas}")
    print("case (ii) can reach beta >= 3/5 only if some line above says True:", bool(worst_feasible))

main()
