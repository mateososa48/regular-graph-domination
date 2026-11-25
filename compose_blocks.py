"""Build an all-4-clause formula from copies of an unsatisfiable block H whose short clauses
have total deficiency D = sum(4-|C|) <= 5, using a tree of disjunctive splittings (new
variable x: add x to some open clauses on the left, -x on the right).  Unsatisfiability is
preserved at every step.  Each splitting variable is used at most 3 times per sign, so if H has
every literal <= 3 times, the result is an unsatisfiable (4,3,3)-formula."""
import itertools, sys
from pysat.solvers import Cadical195

def deficiency(H): return sum(4 - len(c) for c in H)

def copy_block(H, offset):
    return [[(abs(l) + offset) * (1 if l > 0 else -1) for l in c] for c in H]

def compose(H, nv):
    """Try 2, 4 and 6 copies (in that order); six copies always suffice when D <= 5 and every
    clause has width >= 2 (checked for every open-slot profile)."""
    D = deficiency(H)
    assert 0 < D <= 5 and all(len(c) >= 2 for c in H), D
    for ncopies in (2, 4, 6):
        clauses = []
        blocks = []
        for i in range(ncopies):
            base = len(clauses)
            clauses += copy_block(H, i * nv)
            blocks.append(list(range(base, base + len(H))))
        nxt = ncopies * nv
        def open_clauses(idx_list):
            return [j for j in idx_list if len(clauses[j]) < 4]
        def split(left, right):
            nonlocal nxt
            nxt += 1; x = nxt
            L = sorted(open_clauses(left), key=lambda j: len(clauses[j]))[:3]
            R = sorted(open_clauses(right), key=lambda j: len(clauses[j]))[:3]
            for j in L: clauses[j].append(x)
            for j in R: clauses[j].append(-x)
            return left + right
        if ncopies == 2:
            split(blocks[0], blocks[1])
        elif ncopies == 4:
            split(split(blocks[0], blocks[1]), split(blocks[2], blocks[3]))
        else:  # ((B1+B2)+B3) + ((B4+B5)+B6)
            split(split(split(blocks[0], blocks[1]), blocks[2]), split(split(blocks[3], blocks[4]), blocks[5]))
        if all(len(c) == 4 for c in clauses):
            return clauses, nxt
    raise RuntimeError("schedule failed")

def stats(F, n):
    occ = {}
    for c in F:
        for l in c: occ[l] = occ.get(l, 0) + 1
    return min(len(c) for c in F), max(len(c) for c in F), max(occ.values())

def is_sat(F):
    with Cadical195(bootstrap_with=F) as s: return s.solve()

if __name__ == "__main__":
    # synthetic test block: complete 4-CNF on 4 vars with clause pairs merged into 3-clauses
    # (unsat, profile five 3-clauses, but literal counts are large; this only tests the mechanics)
    full = [[(i + 1) * (1 if (m >> i) & 1 else -1) for i in range(4)] for m in range(16)]
    H = []
    used = set()
    merges = 0
    for m in range(16):
        if m in used: continue
        if merges < 5 and (m ^ 8) not in used:
            used |= {m, m ^ 8}; H.append(full[m][:3]); merges += 1
        else:
            used.add(m); H.append(full[m])
    print("block: clauses", len(H), "deficiency", deficiency(H), "unsat:", not is_sat(H))
    F, n = compose(H, 4)
    print("composed: clauses", len(F), "vars", n, "(min width, max width, max literal occ) =", stats(F, n), "unsat:", not is_sat(F))
    sel = {}
    for c in F:
        for l in c:
            if abs(l) > 6 * 4: sel[l] = sel.get(l, 0) + 1
    print("splitting-variable literal counts:", sorted(sel.items()))
