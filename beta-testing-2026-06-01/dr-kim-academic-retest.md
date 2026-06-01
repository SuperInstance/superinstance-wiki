# Academic Re-Test: cathedral-probe v0.1.1

**Reviewer:** Dr. Sarah Kim, Postdoctoral Researcher, Spectral Graph Theory  
**Date:** 2026-06-01  
**Re-reviewing:** Corrections requested by Dr. Chen (original score: 3/10)

---

## Dr. Chen's Fixes: Verification

### 1. Cheeger Constant Fix ✅ Verified

- `cheeger_upper_bound()` correctly computes **√(2·λ₂)** — confirmed at line 146: `(2.0 * fiedler).sqrt()`
- `cheeger_lower_bound()` correctly computes **λ₂/2** — confirmed at line 153: `self.fiedler_value() / 2.0`
- `cheeger_constant()` is properly **deprecated** with `#[deprecated]` and a clear note explaining the old error (lines 161-163)
- Doc comments accurately state the Cheeger inequality: λ₂/2 ≤ h(G) ≤ √(2·λ₂)
- The deprecation note explicitly documents the old incorrect formula (√(λ₂/2)) and the correction

**Verdict:** Thoroughly fixed. This was Dr. Chen's most critical finding, and the author addressed it correctly with proper deprecation migration.

### 2. References Added ✅ Verified

All four references are present:
- **Fiedler (1973)** — Algebraic connectivity of graphs ✅
- **Chung (1997)** — Spectral Graph Theory ✅
- **Mohar (1989)** — Isoperimetric numbers of graphs ✅
- **Alon & Milman (1985)** — λ₁, isoperimetric inequalities ✅

References appear both in `README.md` (under "Mathematical References") and in the doc comments for `cheeger_upper_bound()` (lines 137-141). Citations are complete with journal names, volume/issue numbers, and page ranges.

### 3. No-std Claim Removed ❌ NOT Fixed

The README still states: *"Zero dependencies. Works on `no_std` targets with `alloc`."*

The crate does **not** use `#![no_std]` in `src/lib.rs`. This claim is false and misleading. A simple search for `no_std` in the README returns a match.

**Verdict:** This is an actionable misrepresentation. Either remove the claim or actually support `no_std`.

### 4. Tests Pass ✅ Verified

- `cargo test`: **27 tests passed, 0 failed** ✅
- `cargo clippy -- -D warnings`: **Clean, no warnings** ✅

### 5. Cheeger Inequality Documentation ✅ Verified

The doc comments correctly state the two-sided Cheeger inequality. The upper and lower bound methods are clearly documented with the inequality chain.

---

## Remaining Issues from Dr. Chen's 16 Corrections

### Issue A: Naive QR Eigensolver Without Tridiagonalization
**Severity: Moderate for pedagogical use, High for production**

The eigensolver (lines 78-109) applies QR iteration directly to the dense Laplacian matrix with 200 fixed iterations and a Wilkinson shift. It does **not** reduce to tridiagonal form first (via Householder reflections or Givens rotations), which is the standard optimization.

**Assessment:** For a pedagogical crate, this is **acceptable**. The algorithm is correct in principle, just O(n³·iterations) instead of O(n²·iterations) with tridiagonalization. The code is easier to read without the extra step. For graphs with >100 nodes, performance will degrade noticeably, but the crate doesn't claim to handle large graphs.

**Rating: Acceptable for v0.1.x pedagogical scope.** Would need addressing for a v1.0 claiming production use.

### Issue B: No Convergence Check
**Severity: Low-Moderate**

The QR iteration runs for a fixed 200 iterations regardless of whether the eigenvalues have converged. There is no early termination or convergence criterion.

**Assessment:** 200 iterations with Wilkinson shifts is almost certainly sufficient for the small graphs (2-20 nodes) used in the test suite. For pedagogical purposes, this is fine. A production eigensolver should check off-diagonal norms, but the cost here is just wasted cycles on small matrices.

**Rating: Acceptable for pedagogical scope.** A `TODO` comment noting this would be responsible.

### Issue C: Loose Test Tolerances
**Severity: Low**

Tests use assertions like `spec[0].abs() < 0.5` (line 316) and `spec[1] > 0.5` (line 317) for eigenvalue checks. For a 3-node complete graph, the eigenvalues are analytically {0, 3, 3}, so `> 0.5` is very loose.

**Assessment:** The tests verify **correct sign/magnitude ordering** rather than numerical precision. This is a valid testing philosophy for a pedagogical crate — it confirms the algorithm isn't catastrophically wrong. Tighter tolerances (e.g., `abs() < 1e-6` for the zero eigenvalue, `abs(spec[1] - 3.0) < 0.01`) would increase confidence but aren't strictly necessary.

**Rating: Acceptable but not ideal.** Would recommend tightening in a future PR.

### Issue D: No Sparse Matrix Support
**Severity: Not a bug — scope question**

The Laplacian is stored as a dense `Vec<Vec<f64>>` matrix. For large graphs, this is O(n²) memory.

**Assessment:** The crate is explicitly positioned as a spectral topology analyzer for "component graphs" — software dependency/communication graphs, not large-scale social networks. These typically have 5-100 nodes. Dense storage is perfectly appropriate for this use case.

**Rating: Out of scope.** Not a defect. Sparse support would be a feature for a different target audience.

---

## New Academic Score

| Criterion | Dr. Chen's Score | My Score | Notes |
|-----------|-----------------|----------|-------|
| Mathematical correctness | 1/10 | **7/10** | Cheeger inequality now correct; bounds properly implemented |
| References & attribution | 1/10 | **8/10** | Four canonical references properly cited |
| Algorithm quality | 2/10 | **5/10** | QR with Wilkinson shift, but no tridiagonalization |
| Code quality | 3/10 | **7/10** | Clean, well-documented, clippy-clean |
| Testing rigor | 3/10 | **5/10** | 27 tests, but loose tolerances |
| Documentation accuracy | 2/10 | **5/10** | False `no_std` claim remains |

**Overall: 6/10** (up from Dr. Chen's 3/10)

The jump is justified: the most critical mathematical error (Cheeger constant) is thoroughly fixed, references are solid, and the code is clean. The remaining issues are mostly scope/performance concerns, not mathematical errors.

---

## Would I Recommend This to Students NOW?

**Yes, conditionally.**

I would recommend cathedral-probe v0.1.1 to students in an introductory spectral graph theory or network science course, with the following caveats:

1. **Explain the Cheeger inequality fix** as a case study in why mathematical correctness matters — the deprecation migration is actually a great teaching example.
2. **Note the eigensolver limitations** — students should understand this is QR iteration without tridiagonalization, and why that matters for larger graphs.
3. **Ignore the `no_std` claim** — it's inaccurate.

For a graduate-level course on numerical linear algebra or a production use case, I would **not** recommend this crate. The eigensolver is too naive and the test tolerances too loose for rigorous work.

---

## Honest Assessment

The author responded well to Dr. Chen's review. The Cheeger constant fix is thorough — not just a patched formula, but a proper deprecation with documentation of the error. The reference additions are complete and correctly formatted.

The remaining `no_std` claim is a puzzling oversight. It was presumably in Dr. Chen's list of corrections, yet it persists. This suggests either the author missed it or actively chose to keep it (perhaps planning `no_std` support?). Either way, it should be removed or made true.

The eigensolver is what it is: a straightforward QR implementation that works for small graphs. It's not going to win any benchmarking contests, but for a crate that exists to teach spectral graph concepts, it does the job. The Wilkinson shift is a nice touch — it shows the author knows the basics of QR acceleration.

**Bottom line:** The crate went from "mathematically wrong" to "mathematically correct, computationally naive." For a v0.1.x pedagogical tool, that's a solid improvement. The author should remove the `no_std` claim and consider adding convergence checking, but the core spectral methods are now sound.

---

*Dr. Sarah Kim*  
*Postdoctoral Researcher, Spectral Graph Theory*  
*Re-test completed 2026-06-01*
