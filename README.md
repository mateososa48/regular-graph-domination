# Domination vs. edge domination in regular graphs: research log (24 Nov 2026)

Unrefereed notes from one working session (Claude + Mateo). Everything here is reproducible with
the scripts in this folder.

## The problem

**Baste–Fürst–Henning–Mohr–Rautenbach conjecture** (Discrete Appl. Math. 285 (2020) 343–349,
arXiv:1906.10420). For every Δ-regular graph G with Δ ≥ 1, γ(G) ≤ γₑ(G). Here γ is the domination number
and γₑ is the edge domination number, which equals the size of a smallest maximal matching.

**TxGraffiti's stronger version** (Conjecture 3 in arXiv:2507.17780): i(G) ≤ γₑ(G), where i is the
independent domination number. Since γ ≤ i, a counterexample to Baste is also one to TxGraffiti.

| Degree Δ | Status before this session |
|---|---|
| 1–2 | true (trivial) |
| 3 | **false**: a 50-vertex cubic graph with i = γ = 16 > 15 = γₑ (Zenodo 10.5281/zenodo.21852504 for i; Afrasyab, arXiv:2609.10783 for γ) |
| 4, 5, 6 | **open** (Gupta, arXiv:2608.22498, settles γ ≤ γₑ up to 37 / 70 / 140 vertices; item 7 below extends this to 40 / 76 / 145) |
| ≥ 7 | γ ≤ γₑ true (Gupta, Lovász Local Lemma). TxGraffiti's i ≤ γₑ: not settled |

## What was done and what came out

The open degrees 4, 5 and 6 were **not** resolved. Concretely:

1. **Independent confirmation of the cubic counterexample, with checked certificates.** I rebuilt the
   50-vertex graph from the clause table in arXiv:2609.10783. A maximal matching of size 15 plus the
   counting bound γₑ ≥ 3n/10 give γₑ = 15. CaDiCaL proves there is no dominating set and no independent
   dominating set of size ≤ 15, and drat-trim verifies both DRAT proofs (`s VERIFIED`). An independent
   C branch-and-bound solver agrees. Files: `certify_cubic.py`, `cubic_{g,i}15.{cnf,drat}.xz`.

2. **Exhaustive check of the stronger inequality i ≤ γₑ (which implies γ ≤ γₑ)** over all connected
   regular graphs (generated with nauty `geng`; graph counts match OEIS A002851, A006820, A006821, A006822):

   | Degree | Orders checked | Graphs at the largest order | Counterexamples |
   |---|---|---|---|
   | 3 | n ≤ 20 | 510,489 | 0 |
   | 4 | n ≤ 16 | 8,037,418 | 0 |
   | 5 | n ≤ 14 | 3,459,383 | 0 |
   | 6 | n ≤ 13 | 367,860 | 0 |

   On 1,097 sampled graphs, the C solver's exact γₑ and i match an independent SAT computation.
   For γ these ranges are weaker than Gupta's theorems. For i, no comparable ranges were found published.
   (TxGraffiti's own database covered cubic graphs up to 16 vertices.)

3. **SAT reformulation.** Let M be a minimum maximal matching and U = V − V(M). For each edge of M,
   choose one endpoint; one clause per u ∈ U says "some neighbour of u is chosen". This is a Δ-CNF in which
   every literal occurs at most Δ − 1 times. If it is satisfiable, the chosen endpoints dominate, so
   γ ≤ γₑ (this is Gupta's reduction). Conversely, any Δ-CNF in which every literal occurs exactly Δ − 1 times
   gives a Δ-regular "gadget" graph with γₑ = (number of variables).
   - The cubic counterexample is exactly such a gadget. Its formula is a *minimum-size* unsatisfiable 3-CNF in
     which every literal occurs twice: 20 clauses, matching μ(3,2,2) = 20 of Zhang–Peitl–Szeider (SAT 2024).
   - Unsatisfiability is necessary but **not sufficient**. My annealing search found a different
     unsatisfiable 20-clause formula of this kind (`sa_D3_k15b.out`), and its gadget satisfies i ≤ γₑ.
   - **Consequence for Δ = 4:** Baste's conjecture would follow for 4-regular graphs if every 4-CNF in which
     every literal occurs at most 3 times were satisfiable. I could not find this question
     (the class "(4,3,3)") treated in the literature. Zhang–Peitl–Szeider settle literal-bounded 3-CNF classes
     and variable-bounded (4,s), but not this one.

4. **Evidence that degree 4 behaves differently from degree 3** (heuristic, not proof):
   - Annealing over 4-CNFs with every literal exactly 3 times never got near unsatisfiable. The best runs
     still had ≥ 400 satisfying assignments at 12 variables and ≥ 3,300 at 16. The same code finds
     unsatisfiable degree-3 formulas at 15 variables in about 2 minutes.
   - Random degree-4 gadgets have slack γₑ − i of roughly k/6 to k/5 (k = 16: slack 3). Degree-3 gadgets have
     slack 1–2 at k = 18. Using unmatched vertices in the dominating set helps much more at degree 4.
   - Share of connected graphs that are tight (i = γₑ):

     | Degree | Tight graphs by order |
     |---|---|
     | 3 | n=12: 42/85 · n=14: 18/509 · n=16: 1,470/4,060 · n=18: 1,692/41,301 |
     | 4 | n=12: 25/1,544 · n=13: 142/10,778 · n=14: 229/88,168 · n=15: 144/805,491 |
     | 5 | n=12: 3/7,848 · n=14: 9/3,459,383 |
     | 6 | n=11: 1/266 · n=12: 2/7,849 · n=13: 1/367,860 |

   - Annealing over 4-regular graphs on 28 vertices never reached i = γₑ. It got stuck at γₑ − i = 1.

5. **A definitional bug in google-deepmind/formal-conjectures.** `SimpleGraph.edgeDominationNumber`
   (FormalConjecturesForMathlib/Combinatorics/SimpleGraph/Domination.lean) never requires the set M to
   consist of edges of G. For K₃,₃, M = {s(a₁,a₂), s(a₃,b₁)} is accepted, giving 2 instead of the true value 3.
   The definition is unused so far, and a search of issues and PRs found no report of it.
   Filed as google-deepmind/formal-conjectures#8290 (text in `ISSUE_formal_conjectures.md`). (TxGraffiti Conjecture 3 still being marked "open" there is already
   reported: issue #6737, PR #7661.) `EdgeDomBugDemo.lean` proves `edgeDominationNumber K₃,₃ ≤ 2` against
   the repository itself (commit `9097e2f`, Lean v4.33.1) using only the standard axioms, and compares it
   with the library's own `saturationNumber K₃,₃ = 3` (that step uses `native_decide`).

6. **Degree 4 reduces to a question about small "blocks" (new, with proofs).** Write D(H) = Σ (4 − |C|)
   for a CNF H with clauses of width ≤ 4 (the number of missing literal slots).

   - **Lemma 1 (reduction).** The following are equivalent:
     (a) some 4-CNF in which every literal occurs at most 3 times is unsatisfiable;
     (b) some unsatisfiable CNF with clause widths 3 or 4, every literal at most 3 times, has at most
     three clauses of width 3;
     (c) some unsatisfiable CNF with clause widths 2 to 4, every literal at most 3 times, has D ≤ 5.
     *Proof.* (a)⇒(b): set any variable x true; at most 3 clauses lose ¬x. (b)⇒(c) is trivial.
     (c)⇒(a): take 2, 4 or 6 copies of the block on disjoint variables and join them by disjunctive
     splitting: a fresh variable x is added to at most 3 open clauses on one side and ¬x to at most 3 on the
     other, which preserves unsatisfiability. The six-copy schedule (((H⊕H)⊕H)⊕((H⊕H)⊕H)) fills every
     open slot for every possible slot profile with D ≤ 5 (checked exhaustively; fewer copies suffice for
     some profiles). `compose_blocks.py` builds it and was tested on blocks with five 3-clauses, with a
     2-clause and three 3-clauses, and with two 2-clauses and a 3-clause.
     So **Baste's conjecture for Δ = 4 follows unless an unsatisfiable block with D ≤ 5 exists**, and if one
     exists then (4,3,3)-SAT is NP-complete (Lemma 4 of Zhang–Peitl–Szeider) and Gupta's method cannot
     work for Δ = 4.
   - **Lemma 2 (tree-like formulas cannot work).** Every minimally unsatisfiable formula of deficiency 1
     (m = n + 1 clauses) with widths ≤ 4, literals ≤ 3 and m ≥ 3 has D ≥ 7. *Proof.* Such formulas are exactly
     the disjunctive-splitting trees over the empty clause, each variable living at one node. A node whose
     subtrees have a and b leaves contributes at most min(a,3) + min(b,3) literal occurrences. If g(m) is the
     least possible D over trees with m leaves, then g(1) = 4, g(2) = 6 and
     g(m) = min over a + b = m of [g(a) − min(a,3)] + [g(b) − min(b,3)], so by induction g(m) = 7 for every
     m ≥ 3 (the split 1 + (m − 1) is optimal; also checked by computer up to m = 40). The same count for 3-CNF with literals ≤ 2 gives D ≥ 4,
     which matches Zhang–Peitl–Szeider's finding that the smallest unsatisfiable (3,2,2)-formula lies
     outside this class.
   - **Near miss.** The minimally unsatisfiable formula
     (p∨q∨r∨x)(p∨q∨r∨¬x)(¬p∨¬q∨¬r∨y)(¬p∨¬q∨¬r∨¬y)(¬p∨q)(¬q∨r)(¬r∨p) has every literal at most 3 times and
     D = 6, one more than Lemma 1 allows. For 3-CNF the analogous block (the NAE-cycle on p, q, r) sits exactly
     at its threshold, and four copies of it give the 20-clause (3,2,2)-formula behind the cubic counterexample.
   - **Local lemma heuristic.** For k-CNF with literals ≤ k − 1 (the class Gupta's reduction produces for
     Δ = k), the ratio between 2^-k and the Shearer threshold of the tree of K_{k−1,k−1} blocks is:
     k=3: 1.84 (unsatisfiable formulas exist), **k=4: 1.93**, k=5: 1.64, k=6: 1.24, k=7: 0.88 (below 1, which is
     Gupta's Δ ≥ 7 theorem). By this measure Δ = 4 is the hardest open case, so the heuristic does not favour
     satisfiability (`shearer_block.py`).
   - **A related theorem pointing the other way.** Formulas of the form (e) ∧ (¬e) over the edges e of a
     4-uniform hypergraph with maximum degree ≤ 4 are always satisfiable (Thomassen 1992; Alon–Bregman for
     k ≥ 8). So "not-all-equal" constructions, which give unsatisfiable 3-CNFs via the Fano plane, cannot give
     an unsatisfiable block here.
   - **Searches for a block (none found).**
     - Annealing on the number of satisfying assignments, calibrated on the 3-CNF analogue (it finds those
       blocks at 7 to 14 variables within seconds). For 4-CNF blocks with D = 5 it found none up to
       17 variables, and the best counts grow with size: five 3-clauses: 56, 179, 429, 1,357 models at
       n = 11, 13, 15, 17; a 2-clause and three 3-clauses: 39, 227, 684 at n = 11, 14, 17; two 2-clauses and a
       3-clause: 24, 117 at n = 11, 14. With exactly three 3-clauses: 205 to 1,897 models at n = 12 to 16.
     - Exact counterexample-guided search over blocks with a cyclic symmetry (the short clauses forming one
       orbit), `cegar_sym2.py`: no Z₅-symmetric block with 10 variables and 15 clauses, no Z₄-symmetric block
       with 12 variables and 16 clauses. Larger symmetric cases (up to 30 variables) were still running on the
       Mac when this was written.

7. **Slightly larger verified ranges for degrees 4, 5, 6 (rigorous, elementary).** Gupta's reduction succeeds
   whenever the formula it produces is satisfiable. He guarantees this when the formula has at most 2^Δ − 1
   clauses (union bound). One more clause is free: an unsatisfiable formula with exactly 2^Δ clauses of width Δ
   would need its falsified subcubes to tile the cube exactly, so every two clauses would clash. But with every
   literal occurring at most Δ − 1 times, a clause clashes with at most Δ(Δ − 1) others, and
   Δ(Δ − 1) < 2^Δ − 1 for Δ ≥ 4. For Δ = 6 one more clause is free: restrict a 65-clause formula to the 6
   variables of any clause C. The 64 restricted Kraft sums add up to 65 and are each ≥ 1. The restriction that
   falsifies C contains the empty clause and at least 34 surviving clauses, so it exceeds 1 by ≥ 34/64. Every
   other restriction keeps ≥ 35 clauses that each clash with ≤ 30 others, so it cannot tile and exceeds 1 by
   ≥ 1/64. That totals ≥ 97/64 > 1, a contradiction. With the integer form of Gupta's bound
   |M| ≥ ⌈Δn/(4Δ − 2)⌉ this gives **Δ = 4: all graphs with n ≤ 40 (was 37); Δ = 5: n ≤ 76 (was 70);
   Δ = 6: n ≤ 145 (was 140)** (`ranges.py` reproduces Gupta's 48 / 37 / 70 and computes the new values; for
   Δ = 6 the union bound alone already gives 141 with exact rounding). The same restriction trick does not
   settle 17 clauses for Δ = 4 or 33 for Δ = 5, because there the restricted formulas are small enough that
   tiling cannot be ruled out by counting. A further observation for Δ = 4: in an unsatisfiable formula of this
   kind with 17 clauses, setting a variable x false leaves Kraft sum (17 + p − q)/16, where p and q count the
   positive and negative occurrences of x. If q = p + 1 this is exactly 1, so the restricted formula would have
   to tile its half-cube, which the same clash count rules out (a 3-clause clashes with at most 9 others). Hence
   every variable occurs equally often with each sign. Excluding 17 clauses altogether would extend Δ = 4 to
   n ≤ 41, and each further clause adds about two vertices; I did not manage that (an exact SAT search is too
   weak at this kind of counting).

## Honest assessment

- Nothing here settles Δ ∈ {4,5,6}. The evidence points toward the inequality being **true** for Δ = 4.
  Any counterexample would need an unsatisfiable 4-CNF with literal occurrences ≤ 3 that is also robust to
  "escapes". It is unknown whether such a formula exists at all.
- The most promising routes to a real theorem:
  1. Prove that every 4-CNF with each literal occurring ≤ 3 times is satisfiable. This would settle Δ = 4.
     It may be false.
  2. Find a randomized or discharging argument that uses unmatched vertices as well as matching endpoints.
     The large slack in random gadgets suggests room.
  3. Push Gupta's LLL to Δ = 6 using the structure of literal-bounded formulas (the gap there is only
     about 25%).
- **Lead checked and closed:** Berman, Karpinski and Scott (ECCC TR03-022, 2003) build unsatisfiable
  4-CNFs with every variable occurring at most 6 times, but their gadget has a variable with 5 positive and
  1 negative occurrence, so it is not of the (4,3,3) kind. Knuth's 257-clause unsatisfiable (4,5)-formula
  is tree-like (deficiency 1), so by Lemma 2 it must contain a literal occurring 4 or more times, and no
  rebalancing within that class can help. Zhang–Peitl–Szeider's 235-clause version adds a 7-clause
  non-tree axiom; I did not check its literal counts.
- **Where Δ = 4 now stands:** by Lemma 1 it is enough to decide whether an unsatisfiable block with D ≤ 5
  exists. Lemma 2 and the near miss show that tree-like blocks and the natural NAE-cycle blocks miss by 2 and
  by 1. No block appeared in any search, but the searches only reach about 17 variables, and the 3-CNF
  experience (smallest objects much larger than the counting bound) says small searches prove little.

## Reproduce

```bash
apt-get install nauty; pip install python-sat ortools networkx
gcc -O3 -o regcheck regcheck.c                       # exact gamma_e and i<=gamma_e test (graph6 on stdin)
nauty-geng -cq -d4 -D4 16 | ./regcheck 4             # 8,037,418 graphs, ~17 min
gcc -O3 -o regcheck2 regcheck2.c                     # also prints the (gamma_e - i) histogram
python3 cubic_check2.py                              # cubic counterexample: gamma=i=16>15
python3 certify_cubic.py                             # DRAT certificates, checked with drat-trim
python3 crosscheck.py                                # C solver vs SAT solver on sample_vals.txt
gcc -O3 -o sa_unsat sa_unsat.c -lm; ./sa_unsat 3 2 15 7 1500000 1.0   # annealing for unsat formulas
gcc -O3 -o graphsa3 graphsa3.c -lm; ./graphsa3 4 28 5 2000000 0.5 1 100000   # graph annealing
gcc -O3 -o hsearch3 hsearch3.c -lm; ./hsearch3 15 18 5 3 1 400000 1.0 0 4      # block annealing (n m4 #3-clauses L seed steps T0 #2-clauses width)
./hsearch3 14 16 2 2 1 400000 1.0 0 3                                          # calibration on the 3-CNF analogue (finds a block)
python3 compose_blocks.py                            # Lemma 1 composition, tested on a synthetic block
python3 cegar_sym2.py 5 2 3,4,4 3                    # symmetric exact search: "NO BLOCK" for Z5, 10 variables
python3 shearer_block.py                             # local lemma ratios
python3 ranges.py                                    # vertex ranges where the reduction is guaranteed to work
```

`EdgeDomBugDemo.lean`: copy into a checkout of google-deepmind/formal-conjectures, run
`lake exe cache get`, build the two imported modules, then `lake env lean EdgeDomBugDemo.lean`.

## Sources

- Baste, Fürst, Henning, Mohr, Rautenbach. Domination versus edge domination. DAM 285 (2020); arXiv:1906.10420
- C. Gupta. Domination versus edge domination in regular graphs of degree at least seven. arXiv:2608.22498
- K. Afrasyab. A 50-vertex cubic counterexample to the domination-versus-edge-domination conjecture. arXiv:2609.10783
- "TxGraffiti Conjecture 15/3 resolution", Zenodo, doi:10.5281/zenodo.21852504
- Davila, Brimkov, Pepper. In Reverie Together. arXiv:2507.17780
- Zhang, Peitl, Szeider. Small unsatisfiable k-CNFs with bounded literal occurrence. SAT 2024; arXiv:2405.16149
- google-deepmind/formal-conjectures, issue #6737 and PR #7661
- D. G. Harris. Comparison of two convergence criteria for the variable-assignment lopsided LLL. arXiv:1610.01926
- Gebauer, Szabó, Tardos. The local lemma is asymptotically tight for SAT. J. ACM 63 (2016)
- Davydov, Davydova, Kleine Büning. An efficient algorithm for the minimal unsatisfiability problem for a subclass of CNF. Ann. Math. AI 23 (1998)
- C. Thomassen. The even cycle problem for directed graphs. J. AMS 5 (1992) 217–229
- N. Alon, Z. Bregman. Every 8-uniform 8-regular hypergraph is 2-colorable. Graphs Combin. 4 (1988)
- Berman, Karpinski, Scott. Approximation hardness and satisfiability of bounded occurrence instances of SAT. ECCC TR03-022
