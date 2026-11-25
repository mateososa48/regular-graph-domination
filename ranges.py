"""Vertex ranges on which Gupta's reduction is guaranteed to succeed.

For a Delta-regular graph on n vertices, a minimum maximal matching M has
|M| >= ceil(Delta*n/(4*Delta-2)) (Gupta, Proposition 2), so at most n - 2*|M| vertices are
unmatched.  Each unmatched vertex gives one clause of width Delta, every literal occurring at
most Delta-1 times.  The reduction succeeds whenever that formula is satisfiable, which is
guaranteed when it has fewer clauses than the smallest unsatisfiable formula of its kind.

  union bound (Gupta):        every such formula with <= 2^Delta - 1 clauses is satisfiable
  tiling argument (this log): every such formula with <= 2^Delta clauses is satisfiable
                              (Delta >= 4: with exactly 2^Delta clauses the falsified subcubes
                              would tile the cube, so every two clauses would clash, but a clause
                              clashes with at most Delta*(Delta-1) < 2^Delta - 1 others)
  Delta = 3: Zhang-Peitl-Szeider's exact value 20 (formulas with <= 19 clauses are satisfiable)
"""
from math import ceil

def max_safe_n(delta, max_sat_clauses, n_limit=2000):
    best = None
    for n in range(delta + 1, n_limit):
        if (delta * n) % 2:          # odd degree needs an even number of vertices
            continue
        m = ceil(delta * n / (4 * delta - 2))
        if n - 2 * m <= max_sat_clauses:
            best = n
        else:
            return best
    return best

for delta, gupta, ours in [(3, 19, 19), (4, 15, 16), (5, 31, 32), (6, 63, 64)]:
    print(f"Delta={delta}: union bound -> n <= {max_safe_n(delta, gupta)};  "
          f"tiling argument -> n <= {max_safe_n(delta, ours)}")
