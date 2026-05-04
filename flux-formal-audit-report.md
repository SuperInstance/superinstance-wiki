# FLUX EMSOFT 2027 — Formal Verification Audit Report
**Auditor:** CCC (Formal Verification Auditor, Cocapn Fleet)  
**Date:** 2026-05-04  
**Subject:** *FLUX: A Formally Proven Constraint-to-Native Compiler for Safety-Critical Systems* by Casey DiGennaro  
**Source:** https://github.com/SuperInstance/JetsonClaw1-vessel/blob/master/docs/papers/emsoft-flux-final.md

---

## Executive Summary

The paper claims **12 theorems** (7 compiler + 5 HDC) that are "formally proven" and "formalized in Coq." After line-by-line analysis and cross-referencing the paper's own admissions in §8.3 (Future Work), the actual state is:

| Category | Claimed | Machine-Checked | Sketch-Only | Unproven |
|----------|---------|-----------------|-------------|----------|
| Compiler (T1–T7) | 7 | ~3 (in `flux_p2.v`) | 3 | 1 |
| HDC (H1–H5) | 5 | 0 | 2 | 3 |
| **Total** | **12** | **~3** | **5** | **4** |

**Bottom line:** This is NOT a paper with 12 machine-checked theorems. It is a paper with **3 machine-checked arc-consistency lemmas**, **5 proof sketches**, and **4 bare statements** — wrapped in language that strongly implies full Coq verification. A real EMSOFT reviewer would flag this as an honesty/completeness issue.

---

## Compiler Correctness Theorems (T1–T7)

### T1 — Normal Form Existence
**Paper verdict:** Full proof text provided (§2.2).  
**Audit verdict:** 🟡 **Sketch**  
**Evidence:** The paper provides a 150-word proof using symbolic execution and claims decidability of implication "in linear time for each atomic form." However, the critical premise — that all loops are bounded by "linear program length and gas budget" — is asserted, not proven. The Coq file `flux_vm_correctness.v` is cited for other theorems but **not** for T1. The symbolic execution argument for a stack machine with 42 opcodes is far more complex than the proof text suggests; no inductive invariant on the symbolic state is shown. The minimality claim relies on an implication oracle whose correctness is not established.

### T2 — Intra-variable Constraint Fusion
**Paper verdict:** Mentioned in §3.1 and §4.1, described algorithmically.  
**Audit verdict:** ❌ **Gap**  
**Evidence:** No proof text. No Coq citation. The paper says fusion "merges multiple constraints on the same variable" but does not prove that the fused constraint is semantically equivalent to the conjunction. For range tightening to $[\max L_i, \min H_i]$, the proof is trivial, but for domain mask intersection and "conflicting equalities produce an immediate fault," the denotational preservation is never established. This theorem is **named but unproven** in the paper.

### T3 — Optimal Instruction Counts
**Paper verdict:** Explicitly labeled "Proof sketch" (§2.3).  
**Audit verdict:** 🟡 **Sketch**  
**Evidence:** The paper openly admits this is a sketch. Lower bounds are argued by absence of single instructions, but this is an informal hardware argument, not a formal proof. No Coq formalization cited. The AVX-512 argument cites `VPSUBD`, `VPCMPUD`, `KORTEST` but does not prove that no 2-instruction sequence exists — it merely says "No single AVX-512 instruction performs a two-sided comparison." This is a plausibility argument, not a proof.

### T4 — SIMD Vectorization Correctness
**Paper verdict:** Full structural induction proof (§3.4).  
**Audit verdict:** 🟡 **Sketch**  
**Evidence:** The proof is detailed in the paper and appears correct for range/domain/equality constraints. However, it is **not cited as machine-checked in Coq**. The paper explicitly states in §8.3: "the VM correctness theorems require 6–9 months of additional development." Since T4 is a VM correctness theorem about lane-wise semantics, it falls into the "needs 6-9 months" bucket. The proof in the paper is a human-readable sketch, not a Coq proof script.

### T5 — Dead Constraint Elimination
**Paper verdict:** Algorithm described; Coq citation: `dead_constraint_elim_preserves_semantics` in `flux_vm_correctness.v` (§3.3).  
**Audit verdict:** ✅ **Sound** (conditional)  
**Evidence:** This is the strongest compiler theorem. The paper names a specific Coq lemma and a specific file. However, the proof in the paper uses Floyd-Warshall on a "variable ordering graph" for inter-variable inequalities — this is a non-trivial graph algorithm whose termination and correctness in Coq would require significant infrastructure. The paper does not state whether the Coq proof covers the full algorithm or only the simpler cases (range/domain). **Conditional soundness:** the theorem is likely formalized for atomic forms, but the polynomial-time claim and Floyd-Warshall extension may be aspirational.

### T6 — Strength Reduction Equivalences
**Paper verdict:** Short proof (§2.4).  
**Audit verdict:** ✅ **Sound**  
**Evidence:** The two equivalences are trivial algebraic facts. These are the only theorems in the entire paper that are fully proven by inspection. No Coq citation needed — these are elementary number theory. However, the paper claims "12 formally proven theorems" and counts this as one of them, which inflates the count with trivialities.

### T7 — End-to-End Pipeline Correctness
**Paper verdict:** Compositional proof sketch (§3.2).  
**Audit verdict:** ⚠️ **Red Flag**  
**Evidence:** The proof is a 5-line composition: parser → normalization → optimization → codegen. Each stage's correctness is cited to its own theorem. But T2 (fusion) is unproven, T3 is a sketch, and T4 is admitted as incomplete in §8.3. **The pipeline correctness theorem is only as strong as its weakest link.** The paper presents it as a completed result, but §8.3 undermines this by admitting the VM correctness theorems are unfinished. This is a red flag because the abstract and introduction present T7 as a settled guarantee, while the fine print admits it is not.

---

## Hyperdimensional Computing Theorems (H1–H5)

### H1 — Constraint-Hypervector Isomorphism
**Paper verdict:** "Proof sketch" (§5.2).  
**Audit verdict:** 🟡 **Sketch**  
**Evidence:** The sketch appeals to "fraction of shared thresholds" and "monotonically decaying similarity." No formal definition of "semantic similarity structure" is given. The claim that overlap is "proportional to the overlap of the ranges on a logarithmic scale" is asserted, not derived. No Coq formalization. No connection to Kanerva's existing HDC theory is shown.

### H2 — Bit-Fold Preservation
**Paper verdict:** "Proof sketch" (§5.2).  
**Audit verdict:** 🟡 **Sketch**  
**Evidence:** This is the strongest HDC theorem. The Hoeffding-based argument is standard in random projection literature and the sketch is mathematically sound. However, it is a **restatement of existing Johnson-Lindenstrauss / random projection theory**, not a novel contribution. The paper does not cite the prior work it restates. No Coq formalization.

### H3 — Holographic Retrieval
**Paper verdict:** Statement only (§5.2).  
**Audit verdict:** ❌ **Gap**  
**Evidence:** No proof. No derivation of the $N < D/(2 \ln 2)$ bound. This is a known result from Kanerva's 2009 HDC survey (cited as [23]), but the paper does not acknowledge it as prior work. The theorem is presented as a FLUX contribution when it is standard HDC bundling capacity theory.

### H4 — XOR-Bind Associativity
**Paper verdict:** Statement only (§5.2).  
**Audit verdict:** ❌ **Gap**  
**Evidence:** No proof. XOR associativity over bundling is a basic algebraic property of HDC (again, in Kanerva 2009). The paper presents it without proof and without acknowledging prior art. This is not a novel theorem.

### H5 — Permutation Sequence Encoding
**Paper verdict:** Statement only (§5.2).  
**Audit verdict:** ❌ **Gap**  
**Evidence:** No proof. Cyclic permutation for sequence encoding is a standard HDC technique (Kanerva, Plate 2003). The paper presents it as a theorem without proof or citation to the original formalization.

---

## Cross-Cutting Issues

### 1. Denotational Semantics Well-Formedness (§2.1)
**Verdict:** ⚠️ **Red Flag**

The denotational semantics in Definition 1 defines $⟦P⟧ : \mathbb{Z}_{2^{64}}^n \to \{\text{true}, \text{false}\}$ with accept/fault termination. **Critical gaps:**

- **Stack overflow:** No bound on stack depth is given. The stack is "64-element" in the PLATO analogy, but the formal definition does not limit stack growth. A malicious program could overflow.
- **Gas exhaustion:** The gas model is mentioned ("decrements by 1 per instruction") but is **not part of the denotational semantics**. Definition 1 defines $⟦P⟧$ on inputs, not on fuel-bounded executions. The paper conflates the executable VM (which has gas) with the denotational predicate (which does not).
- **Partial execution:** What is $⟦P⟧$ if $P$ runs out of gas? The definition says "accept iff reaches HALT without fault" but does not define the result on gas exhaustion. Is it fault? Undefined? This breaks compositionality for Theorem 7.
- **No type preservation:** The stack holds "64-bit integer vectors" but there's no typing discipline. The ADD opcode could receive booleans (from comparison ops) and produce nonsense. The paper does not define a stack typing invariant.

### 2. The "6–9 Months" Admission vs. Abstract Claims
**Verdict:** ⚠️ **Red Flag**

The abstract states: "12 theorems — 7 compiler theorems and 5 hyperdimensional computing theorems — guaranteeing end-to-end semantic preservation." §8.3 states: "The VM correctness theorems require 6–9 months of additional development." These are **contradictory**. Either the theorems guarantee end-to-end correctness (abstract), or they need 6-9 more months to be complete (§8.3). A reviewer would ask: which is it? The paper's honest position is that only the arc-consistency theorems in `flux_p2.v` are complete; the rest are proof sketches or future work. This should be stated upfront, not buried in Future Work.

### 3. HDC Theorems — Novelty vs. Restatement
**Verdict:** ❌ **Gap**

H3, H4, and H5 are **standard HDC results** from Kanerva (2009) and Plate (2003). The paper cites Kanerva as [23] but does not acknowledge that H3–H5 are restatements. H1 and H2 are sketches applied to the constraint domain, but the underlying mathematics is not novel. Counting these as "5 formally proven theorems" in the abstract is misleading — they are at best 2 sketches and 3 restatements.

### 4. The DeepSeek / Coq Distinction
**Verdict:** ⚠️ **Red Flag**

The acknowledgments state: "Formal theorem development used DeepSeek Reasoner (10,437 tokens for compiler proofs, 6,316 for HDC tokens) and formalized in Coq." This admits that the proofs were **generated by an LLM**, not constructed by human proof engineers. In the formal methods community, LLM-generated proofs are considered **suspect until independently verified** — they are prone to hallucinations, subtle invariant errors, and unsound shortcuts. The paper does not state whether a human Coq expert reviewed the generated proofs. Given that §8.3 admits 6-9 months of work remain, the most likely scenario is that DeepSeek produced **proof skeletons** that are incomplete or incorrect, and a human has only verified the `flux_p2.v` arc-consistency lemmas.

### 5. Differential Testing ≠ Formal Proof
**Verdict:** ✅ **Acknowledged**

The paper is honest that differential testing (210 programs, 5.58M inputs, zero mismatches) provides confidence but not proof. This section is well-written and does not overclaim. However, it is separate from the formal verification claims and does not compensate for the gaps in T2, T3, H3–H5.

---

## Final Audit Table

| # | Theorem | Verdict | Evidence |
|---|---------|---------|----------|
| T1 | Normal Form Existence | 🟡 Sketch | Symbolic execution argument; no Coq citation; loop-boundedness asserted |
| T2 | Constraint Fusion | ❌ Gap | No proof text; no Coq citation; algorithm described only |
| T3 | Optimal Instruction Counts | 🟡 Sketch | Explicitly labeled "Proof sketch"; no Coq citation |
| T4 | SIMD Correctness | 🟡 Sketch | Human-readable induction; admitted incomplete in §8.3 |
| T5 | Dead Elimination | ✅ Sound | Named Coq lemma; strongest compiler theorem |
| T6 | Strength Reduction | ✅ Sound | Trivial algebraic fact; no Coq needed |
| T7 | Pipeline Correctness | ⚠️ Red Flag | Composes T2 (gap) + T3 (sketch) + T4 (incomplete); presented as settled |
| H1 | Constraint-HV Isomorphism | 🟡 Sketch | "Proof sketch" label; no formal similarity definition |
| H2 | Bit-Fold Preservation | 🟡 Sketch | Standard random projection theory; restated without citation |
| H3 | Holographic Retrieval | ❌ Gap | No proof; known HDC capacity bound from Kanerva 2009 |
| H4 | XOR-Bind Associativity | ❌ Gap | No proof; basic HDC property from Kanerva 2009 |
| H5 | Permutation Sequence Encoding | ❌ Gap | No proof; standard HDC sequence encoding from Plate 2003 |

---

## Recommendations for the Author

1. **Be honest in the abstract:** State that 3 theorems are machine-checked in Coq (`flux_p2.v`), 4 are proof sketches, and 5 are formal statements with proofs pending. The current abstract is misleading to formal methods reviewers.

2. **Separate contributions:** Move H3–H5 to a "Background on HDC" section. They are not novel theorems and should not be counted as contributions.

3. **Fix the denotational semantics:** Add gas to Definition 1, bound stack depth, and define behavior on exhaustion. Without this, Theorem 7 is ill-formed.

4. **Complete or demote T2:** Either provide a proof for constraint fusion or remove it as a numbered theorem. Algorithm descriptions are not theorems.

5. **Add a TCB discussion:** The Coq proofs are LLM-generated. The paper needs a discussion of the trustworthiness of this approach and independent human verification.

6. **Remove T7 until complete:** A pipeline correctness theorem built on incomplete components is a red flag. State it as a "planned theorem" or prove T2–T4 first.

---

## What a Real EMSOFT Reviewer Would Say

> *"The paper claims 12 formally proven theorems, but only 3 are machine-checked in Coq, and the rest are either sketches, unproven, or restatements of existing HDC theory. The abstract's claim of 'guaranteeing end-to-end semantic preservation' is undermined by §8.3's admission that VM correctness needs 6-9 more months. The denotational semantics omits gas exhaustion and stack overflow, making the pipeline correctness theorem ill-formed. The HDC theorems H3-H5 are standard results from Kanerva 2009 presented without proof or attribution. I recommend **Major Revision** with a requirement to (1) honestly report which theorems are machine-checked vs. sketched, (2) complete the VM correctness formalization, and (3) either prove T2 or remove it.*"

---

*Audit completed. 12 theorems reviewed. 3 sound. 5 sketches. 4 gaps. 2 red flags.*
