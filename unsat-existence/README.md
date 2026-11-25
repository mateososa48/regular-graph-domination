# Unsatisfiable-formula side ("false side") of the Baste problem

Branch `research/unsat-existence`, written by the second agent ([fable] in issue #2). It does not touch
`research/degree-ranges` or PR #1.

**Question.** For Δ = 4, 5, 6: is there an unsatisfiable Δ-CNF in which every literal occurs at most Δ − 1
times? One is needed for any counterexample to γ ≤ γₑ among Δ-regular graphs (Gupta's reduction), and if
none exists the inequality holds for that Δ.

Labels: **[hand]** proved by hand, **[machine]** machine-checked, **[unchecked]**.

## Results so far (25 Nov 2026)

1. **The Zhang–Peitl–Szeider 235-clause (4,5)-formula is not of the (4,3,3) kind [hand, from the source].**
   In the TeX source of arXiv:2405.16149 (section "A smaller unsatisfiable (4,5)-formula") the new axiom
   F₆′ is printed as a variable-by-clause sign matrix. Its second row is (−,−,−,−,+): one variable occurs
   negatively in four of the seven clauses. The ⊕-derivation in their Figure also uses four-arrowhead
   splits (p = 4) at F₄, F₆, F₇, F₉ and F₁₂. So the formula has literals with four occurrences.

2. **Tree-like (MU(1)) formulas cannot work for Δ = 5, 6 either [hand].** Same capacity count as README
   Lemma 2 on the other branch: a splitting node with a and b leaves below it supplies at most
   min(a, L) + min(b, L) literal occurrences, L = Δ − 1. The best total is c(m) = Δ·m − (1 + Δ(Δ−1)/2), so
   every MU(1) formula has deficit D ≥ 7, 11, 16 for Δ = 4, 5, 6 (m ≥ Δ − 1 clauses). Agrees with [opus].

3. **What a "core" must look like [hand].** A core is an unsatisfiable CNF with clause widths 2..Δ, literals
   ≤ L, and D = Σ(Δ − |C|) open slots.
   - Cores that share only selector variables can be combined into a full formula only if D ≤ 2L − 1.
     Reason (Hall): each core needs D selector-literal occurrences and a selector variable supplies 2L, so
     if D ≥ 2L every set S of cores sees at least |S| selector variables, the cores can be matched to
     distinct selector variables, and setting each matched variable to satisfy its core's padded clauses
     satisfies the formula. So this is a limit on every selector scheme, not just on trees of joins.
   - For Δ ≥ 5 the bound D ≤ 2L − 1 is not sufficient: a join puts a fresh variable into at most L clauses
     per side and at most once per clause, so a core also needs at least L clauses with open slots.
     Example: for Δ = 5 the empty clause has D = 5 ≤ 7 but only one open clause, and trees built from it
     never get below D = 11.

4. **No small core for Δ = 4 [machine, exhaustive].** `coredfs.c` enumerates all covers of {0,1}^r by clause
   subcubes (smallest-uncovered-point branching, fail-first, twin-variable symmetry, exact capacity bound).
   - No unsatisfiable CNF with widths 2..4, literals ≤ 3 and D ≤ 5 exists on r ≤ 7 variables
     (r = 7: 497,371,526 nodes, 106 s). r = 8 is running.
   - Calibration: the same program finds the known cores (Δ = 3: D = 3 on 3 variables, none with D ≤ 2 on
     ≤ 5 variables; Δ = 4: D = 6 on 5 variables).
   - **No hitting core for Δ = 4 at any size [hand + machine].** A hitting formula (every two clauses
     clash) is an exact partition of the cube. With D ≤ 5 the measure is exactly 1 only for five width
     profiles, each with at most 11 clauses; every pair of clauses must clash, a variable with a positive
     and b negative occurrences gives a·b clashing pairs, and counting shows at most 8 variables can be
     used. `HIT=1 ./coredfs 4 3 5 8` finds none.

5. **Δ = 5 and 6 need much larger cores [hand].** By the measure count Σ 2^(−|C|) ≥ 1, a Δ = 5 core with
   D ≤ 7 has at least 17 clauses and 10 variables, and a Δ = 6 core with D ≤ 9 has at least 33 clauses and
   19 variables. For Δ = 6 the pair count rules out exact partitions with the two cheapest profiles.

## Files

- `coredfs.c` — exhaustive core search. `cc -O3 -o coredfs coredfs.c; ./coredfs K L DMAX r [WMIN] [mode]`,
  `HIT=1` restricts to exact partitions. Example: `./coredfs 4 3 5 7 2 1`.
- `cyc_cegar.py` — complete search for unsatisfiable formulas with a cyclic symmetry (CEGAR with CaDiCaL).
  `python cyc_cegar.py K L v N r` (v variable orbits, r clause orbits, shift group Z_N).
- `core_search.py` — direct SAT encoding of the core search (slow, kept as an independent cross-check).
