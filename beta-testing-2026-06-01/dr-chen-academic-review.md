# Academic Review: Cathedral-Probe and Associated Crates

**Reviewer:** Dr. Wei Chen, Associate Professor of Applied Mathematics  
**Institution:** Research university (spectral graph theory, algebraic topology)  
**Date:** 2026-06-01  
**Crates Reviewed:** cathedral-probe v0.1.0, crackle-runtime v0.1.0, conservation-checker v0.1.0, negative-space-testing (unversioned), forbidden-zones (unversioned)

---

## Who I Am

I am an associate professor working in spectral graph theory and algebraic topology. My research concerns Laplacian spectra of families of graphs arising from cell complexes, Cheeger-type inequalities on simplicial complexes, and the relationship between Betti numbers and spectral gaps. I grade papers for a living. I found these crates on crates.io while looking for Rust implementations of Laplacian eigenvalue computation.

I am reviewing these crates as I would a submitted paper — checking mathematical correctness, proper attribution, and whether I would trust these implementations in my own work.

---

## 1. Cathedral-Probe — Spectral Graph Theory

### 1.1 Laplacian Construction

The Laplacian is constructed in `build_laplacian()` as follows:

```rust
lap[i][i] += w;    // diagonal: degree
lap[j][j] += w;    // diagonal: degree
lap[i][j] -= w;    // off-diagonal: -weight
lap[j][i] -= w;    // off-diagonal: -weight
```

**Assessment: Correct.** This is the standard combinatorial (unnormalized) graph Laplacian L = D − A, where D is the degree matrix and A is the weighted adjacency matrix. The construction handles multi-edges implicitly (multiple calls to `connect()` with the same endpoints accumulate weight), which is a reasonable design choice.

**Edge case note:** Zero-weight edges are added to the Laplacian as 0 − 0 = 0, effectively no-ops. This is silently correct but potentially confusing. Negative weights are not guarded against — they would produce a non-positive-semidefinite Laplacian, breaking every downstream computation.

### 1.2 Eigenvalue Computation (QR Iteration)

The `spectrum()` method uses explicit QR iteration with Wilkinson shift:

```rust
for _ in 0..200 {
    let shift = mat[nn-1][nn-1];
    // shift, QR decompose, reform
}
```

**Assessment: Problematic but functional for small graphs.**

Issues:

1. **O(n³) per iteration, O(n³) storage.** The Laplacian is stored as a dense `Vec<Vec<f64>>` matrix. QR decomposition is Gram-Schmidt (also O(n³)). For n > ~100 this will be slow and memory-hungry. No sparse matrix support.

2. **Fixed iteration count (200).** There is no convergence check — the algorithm runs 200 iterations regardless. For a well-conditioned matrix this is overkill; for an ill-conditioned one it may be insufficient.

3. **Wilkinson shift is applied from the bottom-right corner only.** Standard implicit QR uses the trailing 2×2 block for the Wilkinson shift. This implementation takes `mat[nn-1][nn-1]` as the shift — this is a Rayleigh quotient shift, not a proper Wilkinson shift. The distinction matters for convergence rate.

4. **No deflation.** When a subdiagonal element converges to zero, the algorithm should deflate the matrix. This implementation merely zeros out subdiagonal entries below 1e-12 but continues operating on the full matrix. Wasteful but not incorrect.

5. **Gram-Schmidt orthogonalization.** The QR decomposition uses classical Gram-Schmidt, which is numerically unstable. Modified Gram-Schmidt or Householder reflections would be more appropriate. For small matrices this is acceptable; for larger ones, eigenvalue accuracy will degrade.

6. **No tridiagonalization.** Since the Laplacian is symmetric, it should first be reduced to tridiagonal form (O(n³), one-time cost), after which QR iteration on the tridiagonal matrix costs O(n) per step. This is standard practice — see Golub & Van Loan, *Matrix Computations*, Chapter 8. Skipping this step makes the implementation O(n³) per iteration instead of O(n).

**Verdict:** The eigenvalues will be approximately correct for small graphs (n < 50), but this is not a production-quality eigensolver. For academic use: adequate for demonstrations, insufficient for benchmarks.

### 1.3 Fiedler Value

```rust
pub fn fiedler_value(&self) -> f64 {
    let spec = self.spectrum();
    if spec.len() >= 2 { spec[1] } else { 0.0 }
}
```

**Assessment: Correct definition, reasonable implementation.** The Fiedler value (algebraic connectivity) is indeed the second-smallest eigenvalue of the graph Laplacian. The code computes all eigenvalues, sorts them, and takes `spec[1]`.

The attribute "Fiedler value" correctly refers to Miroslav Fiedler's 1973 paper (*Algebraic connectivity of graphs*, Czechoslovak Mathematical Journal). However, **no reference to Fiedler's work is provided anywhere in the code or documentation.** This is a significant omission — see §7.

### 1.4 Cheeger Constant — **THIS IS WRONG**

This is the most mathematically significant error in the crate.

```rust
pub fn cheeger_constant(&self) -> f64 {
    let fiedler = self.fiedler_value();
    if self.nodes.len() <= 1 { return 0.0; }
    (fiedler / 2.0).sqrt().clamp(0.0, 1.0)
}
```

The doc comment says:

> *"Fiedler gives an upper bound on Cheeger: h ≤ sqrt(2 * λ₂)"*

**This is backwards.** The Cheeger inequality for graphs states:

$$\frac{\lambda_2}{2} \leq h(G) \leq \sqrt{2\lambda_2}$$

where h(G) is the Cheeger constant (edge expansion). The code computes `sqrt(fiedler/2)`, which is `sqrt(λ₂/2)` — this is the **lower bound** on h(G), not the upper bound.

The comment claims "Fiedler gives an upper bound on Cheeger: h ≤ sqrt(2λ₂)" — this is correct as a statement (h ≤ √(2λ₂) IS the upper bound), but the **code computes the wrong quantity**. The code should compute `sqrt(2 * fiedler)` to match the comment, or the comment should be corrected.

Furthermore, calling this function `cheeger_constant()` when it returns a bound rather than the actual Cheeger constant is misleading. The Cheeger constant h(G) is defined as:

$$h(G) = \min_{S \subset V, |S| \leq |V|/2} \frac{|E(S, \bar{S})|}{|S|}$$

Computing the actual Cheeger constant requires solving a combinatorial optimization problem (NP-hard in general). What the code returns is a spectral bound. The function name should reflect this — e.g., `cheeger_lower_bound()` or `spectral_expansion_bound()`.

The `.clamp(0.0, 1.0)` is also suspect — there's no reason the Cheeger constant should be bounded by 1 for weighted graphs.

**Severity: High.** This is a fundamental terminological and mathematical error. Anyone using `cheeger_constant()` thinking they're getting the Cheeger constant will be wrong.

### 1.5 Edge Cases

- **Empty graph:** Returns empty spectrum, Fiedler = 0.0, `is_connected()` returns `true` (questionable — vacuously connected?). Reasonable but should be documented.
- **Single node:** Returns `[lap[0][0]]` which is `0.0` (no edges). Correct.
- **Disconnected graph:** Fiedler = 0, fragility = ∞. Correct behavior.
- **Zero-weight edges:** Effectively no-ops. No warning.
- **Negative weights:** Not guarded. Would break positive-semidefiniteness.
- **Self-loops:** Not possible with current API (node names must differ in `connect()`). Good.

### 1.6 Would I Use This in Research?

**No, not in its current form.** The eigensolver is too slow and numerically unstable for research graphs. The Cheeger constant error undermines trust. However, the API design is clean and the Laplacian construction is correct. With proper attribution, a better eigensolver (tridiagonalization + implicit QR, or calling out to `nalgebra`/`rust-ndarray`), and fixing the Cheeger issue, this could be a useful pedagogical tool.

What's missing for research use:
- Sparse matrix support
- Normalized Laplacian (L_sym = D^{-1/2} L D^{-1/2})
- Random walk Laplacian (L_rw = D^{-1} L)
- Eigenvector computation (not just eigenvalues)
- Fiedler vector (eigenvector corresponding to λ₂) for spectral partitioning
- Proper attribution

---

## 2. Crackle-Runtime — Pattern Detection

### 2.1 Mathematical Definition of "Pattern"

The crate detects four types of "pattern":

1. **Clustering** — Tasks whose metric vectors are within Euclidean distance threshold.
2. **Phase Transition** — A metric shifts between first half and second half of tasks by more than a sensitivity threshold.
3. **Conservation** — A metric has low coefficient of variation across tasks.
4. **Correlation** — Pearson correlation between two metrics exceeds a threshold.

**Assessment: These are ad-hoc statistical heuristics, not formal pattern definitions.**

- **Clustering** uses single-linkage clustering (greedy nearest-neighbor with a threshold). This is a well-known clustering approach but the implementation is naive — it's O(n²) and sensitive to ordering. No discussion of DBSCAN, k-means, or formal cluster validity indices.

- **Phase Transition** compares the mean of the first half of tasks to the mean of the second half. This is a crude two-sample test with no statistical significance assessment. A proper implementation would use a t-test, Mann-Whitney U test, or changepoint detection (e.g., CUSUM, Bayesian changepoint).

- **Conservation** checks if the coefficient of variation (std_dev / |mean|) is below a tolerance. This is a reasonable heuristic for "approximately constant" but calling it a "conservation law" is a stretch — there's no underlying physical or mathematical conservation principle being tested.

- **Correlation** computes Pearson correlation correctly (the formula in `pearson_correlation()` is standard). However, no p-value is computed, no multiple testing correction is applied, and the threshold (0.7 for normal cooling) is arbitrary. With enough metric pairs, you'll find spurious correlations by chance.

### 2.2 False Positive Guarantees

**None.** There are no statistical significance tests, no p-values, no confidence intervals (despite the `confidence` field on `CracklePattern`). The `confidence` field is computed as `1.0 - (distance/threshold)` for clustering and similar ad-hoc formulas. This is not a statistical confidence in any formal sense.

### 2.3 The Pottery Metaphor

The crate is heavily documented with a pottery metaphor (kiln, firing, cooling, glaze, craze lines). While charming, this metaphor adds complexity without mathematical content. The "cooling" phase is simply post-hoc statistical analysis — there's nothing thermodynamic about it.

**Academic concern:** If a student submitted this as "emergent pattern detection," I would ask them to formalize what "emergent" means mathematically and to provide statistical guarantees.

---

## 3. Conservation-Checker — Invariant Tracking

### 3.1 Phase Detection

The four phases (Stable → PreTransition → Transitioning → Resolving) are determined by heuristic rules:

- **Transitioning:** violated AND recent rate < -noise_floor
- **Resolving:** violated AND recent rate > noise_floor  
- **PreTransition:** not violated AND rate is accelerating
- **Stable:** everything else

**Assessment: Not based on any formal model.** This is a finite-state classification based on thresholds and differences of recent values. It resembles simple control-theory concepts (overshoot, settling) but without any formal control-theoretic framework.

The phase names suggest connection to phase transitions in physics (solid → liquid → gas), but the actual detection has nothing to do with phase transition theory. In statistical physics, a phase transition is characterized by non-analyticity in the free energy function or a discontinuity in an order parameter. Here it just means "the value changed a lot recently."

### 3.2 One-Sided Conservation

The conservation check is: `current >= initial - tolerance`. Increases are allowed; decreases beyond tolerance are violations.

**Assessment: Mathematically justified for monotone quantities.** If you're tracking something that should only grow (accumulated knowledge, total energy input), then one-sided conservation (non-decreasing) is the correct invariant. The tolerance allows for floating-point imprecision or controlled leaks.

However, calling this a "conservation law" is misleading. In physics, a conservation law means the total quantity is constant (E = const), not monotonically non-decreasing. A more accurate term would be "monotonicity constraint" or "one-sided invariant."

The implementation is clean and correct for what it does. The `drift_rate()` computation (simple linear regression through first and last points) is adequate for rough trend estimation.

---

## 4. Negative-Space-Testing — Forbidden Behavior

### 4.1 Connection to Formal Verification?

**None.** This is not model checking, not temporal logic verification, not abstract interpretation. There is no state machine, no transition system, no LTL/CTL formulae.

### 4.2 What It Actually Is

`NegativeTest` is a predicate on outputs — essentially a constraint or property. `SpaceMap` collects samples and checks each against a set of exclusion predicates. This is **property-based testing** (a la QuickCheck, PropCheck) with a different vocabulary.

Specifically:
- `NegativeTest::excludes()` ↔ QuickCheck's `Testable` property (negated)
- `SpaceMap::verify()` ↔ running all properties against collected samples
- `SpaceResult::is_clean()` ↔ all tests passed

The `CathedralProbe` module is just a collection of boolean assertions with metadata — essentially `assert!()` with better error reporting.

The `CracklePhase` module implements deferred assertions with an "expected failure" concept (kintsugi). This is the same as `#[should_panic]` in Rust's test framework, generalized to runtime.

**Assessment:** These are useful testing utilities with evocative naming. They are not novel mathematical frameworks. The poetry is nice but the math is standard property-based testing.

---

## 5. Forbidden-Zones — Output Space Checking

This crate implements a map between "occupied" and "forbidden" regions, checking for intrusions where occupied keys overlap with forbidden keys.

**Assessment:** This is a generic `HashMap` + `HashSet` with an intersection check. The `boundaries()` function claims to find "adjacent" regions but actually returns all non-forbidden occupied keys — which is simply the set difference `occupied \ forbidden`, not any topological notion of adjacency.

The `negative_space_ratio` is simply `|forbidden \ occupied| / |forbidden| * 100` — the fraction of forbidden regions that haven't been intruded upon. This is a simple set-theoretic measure, not a topological or geometric one.

**No mathematical depth.** This is a perfectly fine utility crate, but it has no connection to formal verification, topology, or the mathematical notion of "negative space."

---

## 6. Notation and Terminology

| Term Used | Standard Term | Assessment |
|-----------|--------------|------------|
| Fiedler value | Algebraic connectivity, λ₂(L) | **Correct** — widely used synonym |
| Cheeger constant | Edge expansion, isoperimetric number | **Incorrect** — code computes a spectral bound, not the Cheeger constant |
| Conservation law | Monotonicity constraint | **Misleading** — conservation implies constancy, not monotonicity |
| Phase transition | Regime change / distribution shift | **Misleading** — no thermodynamic phase transition |
| Negative space | Excluded output region | **Acceptable metaphor** — not standard math terminology |
| Emergent pattern | Statistical regularity | **Overclaim** — emergence implies something qualitatively new |
| Spectral topology | Spectral graph theory | **Non-standard** — "spectral topology" typically refers to the spectrum of topological operators (Hodge Laplacian, etc.) |

---

## 7. Academic Credibility

**Overall score: 3/10**

Rationale:
- (+1) Laplacian construction is correct
- (+1) Fiedler value definition is correct
- (+1) Pearson correlation formula is correct
- (−1) Cheeger constant is wrong (computes bound, not constant; and the bound is misidentified)
- (−1) Eigensolver is naive and numerically unstable
- (−1) No references to original papers (Fiedler 1973, Cheeger 1970, Alon-Milman 1985, etc.)
- (−1) Statistical claims without statistical tests
- (−1) Conservation law terminology abused
- (−1) Phase transition terminology abused
- (−1) "Emergent patterns" without formal definition
- (−1) No attribution of algorithms to discoverers

---

## 8. Would I Use This in Research?

| Crate | Verdict | Reason |
|-------|---------|--------|
| cathedral-probe | **No** | Cheeger error, naive eigensolver, no sparse support, no references |
| crackle-runtime | **No** | No statistical rigor, arbitrary thresholds, not formal pattern detection |
| conservation-checker | **Maybe** | Clean implementation of monotonicity checking; useful for monitoring but not for publications |
| negative-space-testing | **No** | This is property-based testing with different names; I'd use proptest instead |
| forbidden-zones | **No** | Trivial set operations; not useful for research |

---

## 9. Would I Recommend This to Students?

**Conditional yes for cathedral-probe**, with caveats:
- Use it as a learning tool for spectral graph theory concepts
- Understand that `cheeger_constant()` does NOT return the Cheeger constant
- Don't rely on the eigensolver for anything beyond n ≈ 30
- Read Fiedler (1973) and the Cheeger inequality paper alongside the code

**No for the others.** Students would be better served by learning actual statistics (for crackle-runtime), actual QuickCheck/proptest (for negative-space-testing), and actual linear algebra libraries (for cathedral-probe's eigenvalue computation).

---

## 10. Specific Corrections Needed

### cathedral-probe

1. **`cheeger_constant()` → rename to `cheeger_spectral_bound()` or `spectral_expansion_estimate()`**
2. **Fix the formula:** If the intent is the upper bound, use `sqrt(2.0 * fiedler)`. If the intent is the lower bound, use `sqrt(fiedler / 2.0)`. The code currently computes the lower bound but the comment describes the upper bound. Pick one and document which.
3. **Remove `.clamp(0.0, 1.0)`** on the Cheeger bound — this has no mathematical justification for weighted graphs.
4. **Add convergence check** to QR iteration (monitor off-diagonal norm).
5. **Tridiagonalize before QR iteration** (exploit symmetry).
6. **Guard against negative weights** in `connect()`.
7. **Handle the empty graph case** in `is_connected()` — currently returns `true`, which is debatable.

### crackle-runtime

8. **Add statistical significance tests** — at minimum, p-values for correlations and a proper two-sample test for "phase transitions."
9. **Apply multiple testing correction** (Bonferroni, BH-FDR) when testing many metric pairs.
10. **Rename "conservation"** to "stability" or "low-variance detection" to avoid confusion with physical conservation laws.
11. **Rename "phase transition"** to "distribution shift" or "regime change."
12. **Document that `confidence` is not a statistical confidence level.**

### conservation-checker

13. **Rename to `monotonicity-checker`** or similar — the current name implies conservation (constancy), which is only one of three modes.
14. **Document the phase detection as heuristic**, not grounded in any formal model.

### negative-space-testing

15. **Add a note** that this is property-based testing, not formal verification.

### forbidden-zones

16. **Fix `boundaries()` documentation** — it does NOT compute topologically adjacent regions; it computes the set difference.

---

## 11. Missing References

The following papers and textbooks should be cited:

### cathedral-probe

- **Fiedler, M.** (1973). "Algebraic connectivity of graphs." *Czechoslovak Mathematical Journal*, 23(2), 298–305. — The original paper defining algebraic connectivity.
- **Cheeger, J.** (1970). "A lower bound for the smallest eigenvalue of the Laplacian." In *Problems in Analysis*, Princeton University Press, 195–199. — The original Cheeger inequality.
- **Alon, N. and Milman, V.** (1985). "λ₁, isoperimetric inequalities for graphs, and superconcentrators." *Journal of Combinatorial Theory, Series B*, 38(1), 73–88. — The discrete Cheeger inequality.
- **Chung, F.** (1997). *Spectral Graph Theory*. CBMS Regional Conference Series in Mathematics, No. 92. AMS. — The standard textbook.
- **Golub, G.H. and Van Loan, C.F.** (2013). *Matrix Computations*, 4th ed. Johns Hopkins University Press. — For the QR algorithm and tridiagonalization.
- **Mohar, B.** (1991). "The Laplacian spectrum of graphs." In *Graph Theory, Combinatorics, and Applications*, Vol. 2, 871–898. — Survey of Laplacian spectral theory.

### crackle-runtime

- **Pearson, K.** (1895). "Notes on regression and inheritance in the case of two parents." *Proceedings of the Royal Society of London*, 58, 240–242. — For the correlation coefficient.
- **Ester, M. et al.** (1996). "A density-based algorithm for discovering clusters in large spatial databases with noise." *KDD-96*. — DBSCAN, the proper way to do density-based clustering.
- **Benjamini, Y. and Hochberg, Y.** (1995). "Controlling the false discovery rate." *Journal of the Royal Statistical Society, Series B*, 57(1), 289–300. — For multiple testing correction.

### General

- **Claudepierre, S.G. et al.** — For any Rust + linear algebra reference. The `nalgebra` crate documentation should be referenced as the standard Rust linear algebra library.
- **QuickCheck** (Claessen and Hughes, 2000) — For the property-based testing framework that negative-space-testing reinvents.

---

## Summary

These crates are written by someone with genuine mathematical curiosity and good software engineering instincts. The Laplacian construction in cathedral-probe is correct. The Pearson correlation in crackle-runtime is correct. The code is clean, well-tested, and has a distinctive voice.

But the mathematical substance doesn't match the mathematical vocabulary. Terms like "Cheeger constant," "conservation law," "phase transition," and "emergent pattern" carry specific meanings in mathematics and physics. Using them for heuristic approximations without clear disclaimers is — to speak as a reviewer — misleading.

The Cheeger constant error is the most serious issue. It's the kind of mistake that would cost points on a homework assignment and would warrant a major revision on a paper.

**My recommendation to the authors:** You have good taste in mathematics and excellent code quality. Now do the homework. Read Chung's *Spectral Graph Theory*. Read Fiedler's original paper. Cite your sources. And when you compute a bound, call it a bound — not the constant itself. The difference matters.

---

*Dr. Wei Chen*  
*Department of Applied Mathematics*  
*Peer review, not peer pressure*
