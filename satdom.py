"""SAT-based exact decision procedures (CaDiCaL via PySAT).

dom_le(G, K)   : is there a dominating set of size <= K ?  (returns set or None)
idom_le(G, K)  : is there an independent dominating set of size <= K ?
emm_le(G, K)   : is there a maximal matching of size <= K ?
Optionally writes the CNF + DRAT proof so UNSAT answers can be independently checked.
"""
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


def _card_le(lits, K, pool):
    return CardEnc.atmost(lits=lits, bound=K, vpool=pool, encoding=EncType.seqcounter).clauses


def dom_cnf(G, K, independent=False):
    pool = IDPool()
    x = {v: pool.id(("x", v)) for v in G}
    cls = []
    for v in G:
        cls.append([x[v]] + [x[u] for u in G[v]])
    if independent:
        for u, v in G.edges():
            cls.append([-x[u], -x[v]])
    cls += _card_le(list(x.values()), K, pool)
    return cls, x


def dom_le(G, K, independent=False, solver="cadical195", proof_path=None, extra=None):
    cls, x = dom_cnf(G, K, independent)
    if extra:
        cls += extra(x)
    if proof_path:
        CNF(from_clauses=cls).to_file(proof_path + ".cnf")
        with Solver(name=solver, bootstrap_with=cls, with_proof=True) as s:
            ok = s.solve()
            if not ok:
                with open(proof_path + ".drat", "w") as f:
                    f.write("\n".join(s.get_proof()) + "\n")
            model = s.get_model() if ok else None
    else:
        with Solver(name=solver, bootstrap_with=cls) as s:
            ok = s.solve()
            model = s.get_model() if ok else None
    if not ok:
        return None
    ms = set(l for l in model if l > 0)
    return sorted(v for v in G if x[v] in ms)


def emm_le(G, K, solver="cadical195"):
    pool = IDPool()
    E = [tuple(sorted(e)) for e in G.edges()]
    y = {e: pool.id(("y", e)) for e in E}
    inc = {v: [] for v in G}
    for e in E:
        inc[e[0]].append(y[e]); inc[e[1]].append(y[e])
    cls = []
    for v in G:
        cls += CardEnc.atmost(lits=inc[v], bound=1, vpool=pool, encoding=EncType.pairwise).clauses
    for (u, v) in E:
        cls.append(inc[u] + inc[v])
    cls += _card_le(list(y.values()), K, pool)
    with Solver(name=solver, bootstrap_with=cls) as s:
        if not s.solve():
            return None
        ms = set(l for l in s.get_model() if l > 0)
    return [e for e in E if y[e] in ms]


def exact_min(G, decide, lo, hi):
    """Smallest K in [lo, hi] with decide(G, K) not None (decide monotone)."""
    best = decide(G, hi)
    assert best is not None, "upper bound infeasible"
    K = len(best) - 1
    while K >= lo:
        r = decide(G, K)
        if r is None:
            return K + 1, best
        best = r
        K = len(best) - 1
    return lo, best
