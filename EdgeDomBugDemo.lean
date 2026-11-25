import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Domination
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Saturation

/-!
# `edgeDominationNumber` does not require the dominating set to be made of edges of `G`

In `FormalConjecturesForMathlib/Combinatorics/SimpleGraph/Domination.lean`,
`IsEdgeDominating G M` only asks that every edge of `G` lies in `M` or meets an
element of `M`. It never asks `M ⊆ G.edgeSet`. So non-edges can be used.

For `K₃,₃` the true edge domination number is 3 (it equals the minimum size of a
maximal matching, which is 3 here), but the set `{s(a₀, a₁), s(a₂, b₀)}` (whose first
element is not an edge) is accepted, so the library value is at most 2.
-/

open SimpleGraph

namespace EdgeDomBugDemo

abbrev V := Fin 3 ⊕ Fin 3

abbrev K33 : SimpleGraph V := completeBipartiteGraph (Fin 3) (Fin 3)

instance : DecidableRel K33.Adj := fun a b =>
  inferInstanceAs (Decidable (a.isLeft ∧ b.isRight ∨ a.isRight ∧ b.isLeft))

/-- Two "edges": the first one, `s(a₀, a₁)`, is not an edge of `K₃,₃`. -/
def M : Finset (Sym2 V) := {s(Sum.inl 0, Sum.inl 1), s(Sum.inl 2, Sum.inr 0)}

theorem M_card : M.card = 2 := by decide

theorem M_not_subset_edgeSet : ¬ ((M : Set (Sym2 V)) ⊆ K33.edgeSet) := by
  intro h
  have h1 : s(Sum.inl 0, Sum.inl 1) ∈ K33.edgeSet := h (by simp [M])
  simp [K33, completeBipartiteGraph] at h1

/-- Every edge of `K₃,₃` has an endpoint in some element of `M`. -/
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

/-- The (correct) saturation number of `K₃,₃`, i.e. its minimum maximal matching size. -/
theorem saturationNumber_K33 : K33.saturationNumber = 3 := by
  rw [SimpleGraph.saturationNumber_eq_computable]
  native_decide

/-- In the library, edge domination number < saturation number for `K₃,₃`, although for
every graph the two are equal (Yannakakis–Gavril). -/
theorem edgeDominationNumber_lt_saturationNumber :
    K33.edgeDominationNumber < K33.saturationNumber := by
  rw [saturationNumber_K33]
  exact lt_of_le_of_lt edgeDominationNumber_K33_le_two (by norm_num)

end EdgeDomBugDemo
