"""Exact graph parameters for the domination vs edge-domination problem.

gamma(G)    : domination number
idom(G)     : independent domination number
gamma_e(G)  : edge domination number = minimum size of a maximal matching

All are solved exactly with OR-tools CP-SAT (optimality is proven by the solver).
"""
import itertools
import networkx as nx
from ortools.sat.python import cp_model


def _solve(model, time_limit=600.0, workers=2):
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_workers = workers
    st = s.Solve(model)
    if st != cp_model.OPTIMAL:
        raise RuntimeError(f"solver status {s.StatusName(st)}")
    return s


def gamma(G, upper=None, time_limit=600.0):
    """Exact domination number and a minimum dominating set."""
    m = cp_model.CpModel()
    x = {v: m.NewBoolVar(f"x{v}") for v in G}
    for v in G:
        m.AddBoolOr([x[v]] + [x[u] for u in G[v]])
    m.Minimize(sum(x.values()))
    s = _solve(m, time_limit)
    D = sorted(v for v in G if s.Value(x[v]))
    return len(D), D


def idom(G, time_limit=600.0):
    """Exact independent domination number and a witness set."""
    m = cp_model.CpModel()
    x = {v: m.NewBoolVar(f"x{v}") for v in G}
    for v in G:
        m.AddBoolOr([x[v]] + [x[u] for u in G[v]])
    for u, v in G.edges():
        m.AddBoolOr([x[u].Not(), x[v].Not()])
    m.Minimize(sum(x.values()))
    s = _solve(m, time_limit)
    D = sorted(v for v in G if s.Value(x[v]))
    return len(D), D


def gamma_e(G, time_limit=600.0):
    """Exact minimum maximal matching size and a witness matching."""
    m = cp_model.CpModel()
    E = [tuple(sorted(e)) for e in G.edges()]
    y = {e: m.NewBoolVar(f"y{e}") for e in E}
    inc = {v: [] for v in G}
    for e in E:
        inc[e[0]].append(y[e])
        inc[e[1]].append(y[e])
    for v in G:
        m.Add(sum(inc[v]) <= 1)
    for (u, v) in E:  # maximality: every edge touches a matched vertex
        m.AddBoolOr(inc[u] + inc[v])
    m.Minimize(sum(y.values()))
    s = _solve(m, time_limit)
    M = [e for e in E if s.Value(y[e])]
    return len(M), M


# ---------- independent checkers (no solver) ----------

def is_dominating(G, D):
    D = set(D)
    return all(v in D or any(u in D for u in G[v]) for v in G)


def is_independent(G, D):
    D = set(D)
    return not any(u in D and v in D for u, v in G.edges())


def is_maximal_matching(G, M):
    used = set()
    for u, v in M:
        if not G.has_edge(u, v) or u in used or v in used:
            return False
        used.add(u); used.add(v)
    return all(u in used or v in used for u, v in G.edges())


# ---------- clause gadget graphs ----------

def gadget(clauses, nvars):
    """Literal vertices v_j^- = 2(j-1), v_j^+ = 2(j-1)+1 joined by a pair edge;
    one vertex per clause joined to its literal vertices.  Literals are nonzero
    ints in DIMACS style (j or -j, 1-based)."""
    G = nx.Graph()
    for j in range(1, nvars + 1):
        G.add_edge(2 * (j - 1), 2 * (j - 1) + 1)
    base = 2 * nvars
    for a, C in enumerate(clauses):
        c = base + a
        for lit in C:
            j = abs(lit)
            G.add_edge(c, 2 * (j - 1) + (1 if lit > 0 else 0))
    return G


def degrees(G):
    return sorted(set(d for _, d in G.degree()))
