**Title:** `edgeDominationNumber` does not require the dominating set to consist of edges of `G`

**Body:**

In `FormalConjecturesForMathlib/Combinatorics/SimpleGraph/Domination.lean`:

```lean
def IsEdgeDominating (G : SimpleGraph α) (M : Set (Sym2 α)) : Prop :=
  ∀ ⦃e⦄, e ∈ G.edgeSet → e ∈ M ∨ ∃ e' ∈ M, edgesAdjacent e e'
...
noncomputable def edgeDominationNumber (G : SimpleGraph α) : ℕ :=
  sInf {n | ∃ M : Finset (Sym2 α), G.IsNEdgeDominatingSet n M}
```

Nothing forces `M ⊆ G.edgeSet`, unlike `IsEdgeCover` a few lines above, which requires it. So the infimum ranges
over arbitrary unordered pairs, including non-edges and diagonals `s(v, v)`. The result is not the edge domination
number. It is roughly the least number of vertex pairs whose union meets every edge, about ⌈τ(G)/2⌉.

**Example.** Take `K₃,₃` with parts `{a₁,a₂,a₃}` and `{b₁,b₂,b₃}`. Then `M = {s(a₁,a₂), s(a₃,b₁)}` satisfies
`IsEdgeDominating`, because every edge `aᵢbⱼ` meets `a₁`, `a₂` or `a₃`. So `edgeDominationNumber K₃,₃ ≤ 2`.
The edge domination number of `K₃,₃` is 3: a matching of size 2 leaves one vertex free on each side, and those
two vertices are adjacent.

**Checked in Lean.** The file below compiles against this repository at commit `9097e2f` (Lean v4.33.1).
`edgeDominationNumber_K33_le_two` uses only `propext`, `Classical.choice` and `Quot.sound`. The comparison with
the library's own `saturationNumber K₃,₃ = 3` uses `native_decide`.

```lean
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Domination
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Saturation

open SimpleGraph

namespace EdgeDomBugDemo

abbrev V := Fin 3 ⊕ Fin 3
abbrev K33 : SimpleGraph V := completeBipartiteGraph (Fin 3) (Fin 3)

instance : DecidableRel K33.Adj := fun a b =>
  inferInstanceAs (Decidable (a.isLeft ∧ b.isRight ∨ a.isRight ∧ b.isLeft))

def M : Finset (Sym2 V) := {s(Sum.inl 0, Sum.inl 1), s(Sum.inl 2, Sum.inr 0)}

theorem M_card : M.card = 2 := by decide

theorem M_not_subset_edgeSet : ¬ ((M : Set (Sym2 V)) ⊆ K33.edgeSet) := by
  intro h
  have h1 : s(Sum.inl 0, Sum.inl 1) ∈ K33.edgeSet := h (by simp [M])
  simp [K33, completeBipartiteGraph] at h1

theorem key : ∀ a b : V, K33.Adj a b → ∃ e' ∈ M, a ∈ e' ∨ b ∈ e' := by
  decide

theorem M_isEdgeDominating : K33.IsEdgeDominating (M : Set (Sym2 V)) := by
  intro e he
  right
  induction e using Sym2.ind with
  | h a b =>
    obtain ⟨e', he', hab⟩ := key a b ((SimpleGraph.mem_edgeSet K33).1 he)
    refine ⟨e', Finset.mem_coe.mpr he', ?_⟩
    unfold SimpleGraph.edgesAdjacent
    rcases hab with ha | hb
    · exact ⟨a, Sym2.mem_mk_left a b, ha⟩
    · exact ⟨b, Sym2.mem_mk_right a b, hb⟩

theorem edgeDominationNumber_K33_le_two : K33.edgeDominationNumber ≤ 2 := by
  unfold SimpleGraph.edgeDominationNumber
  exact Nat.sInf_le ⟨M, ⟨M_isEdgeDominating, M_card⟩⟩

theorem saturationNumber_K33 : K33.saturationNumber = 3 := by
  rw [SimpleGraph.saturationNumber_eq_computable]
  native_decide

theorem edgeDominationNumber_lt_saturationNumber :
    K33.edgeDominationNumber < K33.saturationNumber := by
  rw [saturationNumber_K33]
  exact lt_of_le_of_lt edgeDominationNumber_K33_le_two (by norm_num)

end EdgeDomBugDemo
```

The definition has no users yet. It is, however, the natural one to use when formalizing the
Baste–Fürst–Henning–Mohr–Rautenbach conjecture γ(G) ≤ γₑ(G) for regular graphs (DAM 285 (2020);
arXiv:1906.10420), and that statement would then silently change meaning.

**Suggested fix:**

```lean
def IsEdgeDominating (G : SimpleGraph α) (M : Set (Sym2 α)) : Prop :=
  M ⊆ G.edgeSet ∧ ∀ ⦃e⦄, e ∈ G.edgeSet → e ∈ M ∨ ∃ e' ∈ M, edgesAdjacent e e'
```

A sanity lemma such as `edgeDominationNumber (completeBipartiteGraph (Fin 3) (Fin 3)) = 3` would also help, or a
bridge lemma `edgeDominationNumber G = saturationNumber G` (Yannakakis–Gavril).

**Possible follow-up:** add the Baste et al. conjecture, which does not appear to be in the repository yet. Its
current status:
- false for Δ = 3: a 50-vertex cubic graph, arXiv:2609.10783, building on doi:10.5281/zenodo.21852504
- true for Δ ≥ 7: arXiv:2608.22498
- open for Δ ∈ {4, 5, 6}
