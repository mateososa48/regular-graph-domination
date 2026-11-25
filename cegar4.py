"""CEGAR search for a Delta-regular clause-gadget graph G_F with  i(G_F) > k  (target='i')
or gamma(G_F) > k (target='gamma'), where k = #variables = gamma_e(G_F).

Gadget: literal vertices for x_v / not x_v joined by a pair edge, plus one vertex per clause
adjacent to its Delta literals.  Each literal occurs in exactly Delta-1 clauses, so the graph
is Delta-regular, n = 2k + c with c = 2k(Delta-1)/Delta, and gamma_e = k by counting.

Outer loop: SAT-synthesize a formula F that defeats every candidate set found so far;
inner check: SAT-search a (independent) dominating set of size <= k in G_F; if none exists,
G_F is a counterexample.
"""
import sys, time, random, json
from pysat.formula import IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
from domlib import gadget, is_dominating, is_independent
from satdom import dom_le


def lit_name(l):  # literal index 0..2k-1 -> DIMACS literal
    v = l // 2 + 1
    return v if l % 2 == 1 else -v


def run(k, Delta=4, target="i", seed=0, max_iter=100000, time_limit=3000, log_every=50, fix_first=True):
    assert (2 * k * (Delta - 1)) % Delta == 0
    c = 2 * k * (Delta - 1) // Delta
    L = 2 * k  # literal l: variable l//2, positive iff l odd (matches gadget vertex ids)
    pool = IDPool()
    a = [[pool.id(("a", j, l)) for l in range(L)] for j in range(c)]
    S = Solver(name="cadical195")
    def add(cls):
        for cl in cls:
            S.add_clause(cl)
    for j in range(c):
        add(CardEnc.equals(lits=a[j], bound=Delta, vpool=pool, encoding=EncType.seqcounter).clauses)
        for v in range(k):
            S.add_clause([-a[j][2 * v], -a[j][2 * v + 1]])
    for l in range(L):
        add(CardEnc.equals(lits=[a[j][l] for j in range(c)], bound=Delta - 1, vpool=pool,
                           encoding=EncType.seqcounter).clauses)
    if fix_first:  # WLOG clause 0 = {x_1,...,x_Delta} (rename / flip variables)
        for l in range(L):
            S.add_clause([a[0][l]] if (l % 2 == 1 and l // 2 < Delta) else [-a[0][l]])
    # mild clause-order symmetry breaking: clause j's literal pattern >= clause j+1's in lex order
    # (implemented on the first literal block only: if a[j+1][l] for the smallest l then ... ) -- skipped

    rng = random.Random(seed)
    t0 = time.time()
    n_cex = 0
    for it in range(max_iter):
        if time.time() - t0 > time_limit:
            return ("timeout", it, n_cex)
        # random phases to diversify
        if not S.solve():
            return ("no_formula", it, n_cex)
        model = set(x for x in S.get_model() if x > 0)
        clauses = [[lit_name(l) for l in range(L) if a[j][l] in model] for j in range(c)]
        G = gadget(clauses, k)
        D = dom_le(G, k, independent=(target == "i"))
        if D is None:
            return ("FOUND", it, clauses)
        # add constraint: in the next formula, D must fail
        Dset = set(D)
        DL = [w for w in D if w < L]          # literal vertices in D (vertex id == literal index)
        DC = [w - L for w in D if w >= L]     # clause indices in D
        big = []
        # literal vertex w not in D undominated: partner not in D and no clause in DC contains w
        for w in range(L):
            if w in Dset or (w ^ 1) in Dset:
                continue
            if not DC:
                continue  # can't be undominated: pair partner absent but w adjacent to... no clause in D
            u = pool.id(("u", it, "L", w))
            for j in DC:
                S.add_clause([-u, -a[j][w]])
            big.append(u)
        if not DC:
            # with DC empty, an undominated literal w (partner not in D) is always undominated
            pass
        # clause vertex j not in D undominated: contains no literal of DL
        for j in range(c):
            if j in DC:
                continue
            u = pool.id(("u", it, "C", j))
            for l in DL:
                S.add_clause([-u, -a[j][l]])
            big.append(u)
        if target == "i":
            for j in DC:
                for l in DL:
                    big.append(a[j][l])  # D not independent in the new formula
        # literal vertices whose pair has no D-vertex and DC empty are undominated outright:
        if not DC and any(w not in Dset and (w ^ 1) not in Dset for w in range(L)):
            continue  # D was never dominating for any formula; cannot happen for a found D
        S.add_clause(big)
        n_cex += 1
        if it % log_every == 0:
            print(f"  it={it} |D|={len(D)} DC={len(DC)} t={time.time()-t0:.0f}s", flush=True)
    return ("maxiter", max_iter, n_cex)


if __name__ == "__main__":
    k = int(sys.argv[1]); target = sys.argv[2] if len(sys.argv) > 2 else "i"
    Delta = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    tl = float(sys.argv[4]) if len(sys.argv) > 4 else 3000
    res = run(k, Delta=Delta, target=target, time_limit=tl)
    print("RESULT", res[0], res[1])
    if res[0] == "FOUND":
        print(json.dumps(res[2]))
        with open(f"found_D{Delta}_k{k}_{target}.json", "w") as f:
            json.dump({"k": k, "Delta": Delta, "target": target, "clauses": res[2]}, f)
