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
  Delta = 4, 17 clauses: also always satisfiable (low-degree polynomial argument, README item 8):
                              h = N - 1, where N(x) counts the clauses falsified at x, is a polynomial
                              of degree <= 4 with sum 2^(n-4); a nonzero degree-4 polynomial is nonzero
                              on >= 2^(n-4) points of the cube, so h is 0/1-valued; then
                              sum N(N-1) = 2^(n-3), but every clause has >= 4 non-clashing partners,
                              which forces sum N(N-1) >= 17*4*2^(n-8) > 2^(n-3).
  Delta = 6, 65 clauses: also always satisfiable.  Restrict F to the 6 variables of any clause C.
                              The 64 restrictions have Kraft sums adding up to 65, each >= 1.  The one
                              falsifying C contains the empty clause plus >= 64 - 30 surviving clauses,
                              so it exceeds 1 by >= 34/64.  Every other restriction keeps >= 65 - 30 = 35
                              clauses, each clashing with <= 30 others, so it cannot tile and exceeds 1
                              by >= 1/64.  Total excess >= 97/64 > 1, a contradiction.
  one-flip count (README item 9, supersedes the three lines above for Delta = 4, 5, 6):
                              at least (2 - m/2^Delta) 2^n assignments falsify exactly one clause C, each
                              lies in the set B_C where every flip of a variable of C is blocked, and
                              |B_C| <= b 2^(n-Delta) with b = 5/8, 17/32, 7/16.  So m >= 2^(Delta+1)/(1+b):
                              every such formula with <= 19 / 41 / 89 clauses is satisfiable.
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

for delta, gupta, ours in [(3, 19, 19), (4, 15, 19), (5, 31, 41), (6, 63, 89)]:
    print(f"Delta={delta}: union bound -> n <= {max_safe_n(delta, gupta)};  "
          f"this log -> n <= {max_safe_n(delta, ours)}")
