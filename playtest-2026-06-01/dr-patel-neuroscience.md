# Research Diary: Testing `cathedral-probe` for fMRI Connectivity Analysis

**Date:** 2025-06-01  
**Researcher:** Dr. Ananya Patel, Computational Neuroscience Postdoc  
**Task:** Evaluate `cathedral-probe` v0.1.1 for spectral graph analysis of functional brain connectivity

---

## Background

I found `cathedral-probe` while searching for "spectral graph theory rust implementation." My lab works with resting-state fMRI data — we parcellate the cortex into 50-200 regions and compute functional connectivity matrices (Pearson correlations between BOLD time series, Fisher z-transformed). I need to compute Laplacian spectra, Fiedler values, effective resistances, and spectral clustering to identify resting-state networks (Default Mode, Frontoparietal, Somatomotor, Visual, etc.).

## The Experiment

I built a 50-node graph with small-world topology: 5 modules of ~10 nodes each (strong intra-module weights 0.5-0.95, weak inter-module weights 0.09-0.18), plus a 100-node scaling test, and validated against analytically known graphs (complete graph K5, path graph P4).

## What Works

### ✅ Core Spectral Computation
- The QR iteration correctly computes eigenvalues. **Numerical validation is excellent:**
  - K5 eigenvalues: exactly `[0, 5, 5, 5, 5]` — perfect match.
  - P4 eigenvalues: errors on the order of **1e-15 to 1e-16** (machine epsilon). This is genuinely impressive.
- Trace preservation is perfect: sum(eigenvalues) = 2 × total_edge_weight to 6 decimal places.

### ✅ Fiedler Value
- Computed correctly for the 50-node graph (0.072, reflecting the weak inter-module connections).
- The `is_healthy()` and `fragility_index()` are nice conveniences.

### ✅ Component Importance & Bottlenecks
- The top bottleneck edges correctly identified the **inter-module bridges** — edges like region_8↔region_35 (connecting DMN to Visual) and region_5↔region_42 (DMN to Dorsal Attention). This is exactly what I'd expect; these long-range connections are the fragile links.
- Component importance correctly flagged "hub" regions that bridge modules.

### ✅ Cheeger Bounds
- Properly implemented: `λ₂/2 ≤ h(G) ≤ √(2·λ₂)`. The documentation clearly states these are bounds, not the exact constant, with proper references to Fiedler (1973), Chung (1997), and Mohar (1989). Academically honest.

### ✅ Zero Dependencies
- No transitive dependency nightmares. Clean build.

## What Doesn't Work (Critical for My Use Case)

### ❌ No Way to Input an Adjacency Matrix
This is the **single biggest blocker.** I have pre-computed 50×50 or 200×200 connectivity matrices from fMRI data. The only way to build a graph is:
```rust
let mut probe = CathedralProbe::new(vec!["region_0", "region_1", ...]);
probe.connect("region_0", "region_1", 0.73);
// ... repeat for every edge
```
For a 200-node graph, that's up to 19,900 edges. I'd need to write a converter that iterates over my matrix and calls `connect()` for each non-zero entry. This is clumsy and slow — string-based node lookup for every edge insertion via `HashMap<String, usize>`. For my use case, I need something like:
```rust
fn from_adjacency_matrix(mat: &[Vec<f64>]) -> Self
```

### ❌ No Eigenvectors
The crate computes only eigenvalues, not eigenvectors. For spectral clustering (which requires the Fiedler vector or the first k eigenvectors of the Laplacian), this is a showstopper. I can't do:
- Spectral clustering into resting-state networks
- Embedding brain regions into spectral space
- Computing the Fiedler vector for optimal bisection

This alone makes the crate unusable for half my workflow.

### ❌ No Effective Resistance
Effective graph resistance between nodes i and j is:
```
R(i,j) = Σ_k (1/λ_k) × (v_k[i] - v_k[j])²
```
This requires eigenvectors, which aren't available. Effective resistance is crucial for my work — it measures how "electrically coupled" two brain regions are. Without it, I'm missing a key measure.

### ❌ No Spectral Clustering
No k-way spectral clustering, no normalized cuts, no community detection. I'd need to implement this myself using eigenvectors... which the crate doesn't provide.

### ❌ No Serde Support
No `Serialize`/`Deserialize` derives. I can't save/load analysis results, interop with JSON, or pass results to my Python visualization pipeline.

### ❌ No Way to Export Results for Further Analysis
I need to get eigenvalues/eigenvectors into Python (numpy/matplotlib) for visualization and further statistical analysis. Right now the only option is `println!` and parsing stdout. A CSV export or serde support would be essential.

### ❌ String-Based API is Awkward for Large Graphs
Using `Vec<&str>` for node names with `HashMap<String, usize>` lookup is fine for 5-10 nodes ("web", "api", "db"). For 200 brain regions, it's ergonomically painful and wastes memory on string allocations and hash lookups. An index-based API (`new(n: usize)`, `connect(i: usize, j: usize, w: f64)`) would be much better for programmatic use.

## Performance

| Graph | Nodes | Edges | Spectrum Time |
|-------|-------|-------|---------------|
| Brain connectivity | 50 | ~175 | ~40ms |
| Sparse chain | 100 | 118 | **626ms** |
| Component importance (50 nodes) | 50 | ~175 | **2.7s** |
| Bottleneck analysis (50 nodes) | 50 | ~175 | **14.1s** |

The O(n³) dense QR iteration is acceptable for 50 nodes. At 100 nodes it's already 626ms. For 200 nodes (my typical scale), it would be ~5-10 seconds just for the spectrum. 

But `component_importance()` and `bottlenecks()` are catastrophically slow because they recompute the full spectrum for **every node/edge removal**. For 50 nodes with 175 edges, that's 175 QR decompositions = 14 seconds. At 200 nodes with ~500 edges, it would take **minutes**. I'd need to use a different approach (e.g., Sherman-Morrison updates for the Laplacian pseudoinverse).

The dense `Vec<Vec<f64>>` Laplacian representation is O(n²) memory — fine for 200 nodes, but no sparse matrix support means it won't scale to parcellations with 1000+ regions (like Glasser's HCP atlas).

## Numerical Trust Assessment

**Would I trust these eigenvalues in a paper?**

For the spectrum itself — **yes, tentatively.** The numerical validation against K5 and P4 is excellent (errors at machine epsilon). The QR iteration with Wilkinson shifts is a standard textbook approach. The trace is preserved perfectly.

However, I have concerns:
1. **Fixed 200 iterations** — what if convergence hasn't happened for some graph structures? There's no convergence check, no tolerance parameter. For a 50-node graph 200 QR steps seems sufficient, but I'd want evidence for larger graphs.
2. **No error estimates** — there's no residual norm reported. I can't verify that `L·v = λ·v` without eigenvectors.
3. **Dense QR only** — no tridiagonalization first (Householder reduction to tridiagonal form, then QR on the tridiagonal matrix) which is the standard approach for symmetric matrices. This would be both faster and more numerically stable.
4. **Single/double precision** — uses `f64` throughout (good), but doesn't leverage the symmetry of the Laplacian for better conditioning.

**Would I trust `component_importance` and `bottlenecks`?** The approach of removing nodes/edges one at a time and recomputing is brute-force but mathematically correct. The results look reasonable (inter-module bridges are flagged). But I'd want to validate with a known example.

## Verdict: Would I Cite This Crate in a Paper?

**No, not in its current form.** Here's what it would need:

### Must-Haves for Academic Use
1. **Eigenvector computation** — without this, the crate provides only eigenvalues, which I can get from `nalgebra` or `ndarray` with more flexibility
2. **Adjacency matrix input API** — I'm not building a 200-node graph with 19,900 string-based `connect()` calls
3. **Convergence guarantees** — residual norms, adaptive iteration counts, error bounds
4. **Serde support** — for reproducibility and data pipeline integration
5. **Citation metadata** — a `CITATION.cff` file or at least a DOI via Zenodo

### Nice-to-Haves
6. Spectral clustering (k-way, normalized cuts)
7. Effective resistance computation
8. Sparse matrix support (for large parcellations)
9. Symmetry-aware eigenvalue solver (tridiagonalize first, then QR — standard for symmetric matrices)
10. Index-based API as an alternative to string names
11. Export to CSV/JSON/numpy
12. Comparison against reference implementations (LAPACK, scipy.linalg)

### The Honest Comparison
Right now, for my actual work, I'd use **Python + scipy + networkx + nilearn**:
- `scipy.sparse.linalg.eigsh` — sparse, symmetric eigensolver with ARPACK backend
- `sklearn.cluster.SpectralClustering` — production-quality spectral clustering
- `networkx.algebraic_connectivity` — validated Fiedler value computation
- `nilearn.connectome` — brain-specific connectivity analysis

`cathedral-probe` targets microservice dependency graphs, not neuroscience. The string-based API, lack of eigenvectors, and absence of clustering make it impractical for my pipeline. The numerical quality is good, but I can get the same (and more) from mature scientific computing libraries.

## Summary

| Aspect | Rating | Notes |
|--------|--------|-------|
| Numerical accuracy | ⭐⭐⭐⭐⭐ | Excellent for eigenvalues |
| API ergonomics | ⭐⭐ | String-based, no matrix input |
| Feature completeness | ⭐⭐ | No eigenvectors, no clustering |
| Performance | ⭐⭐ | O(n³) dense, no sparsity |
| Documentation | ⭐⭐⭐⭐ | Clear, honest about bounds vs exact |
| Academic readiness | ⭐⭐ | Needs eigenvectors, serde, convergence proofs |

**Bottom line:** A neat microservice monitoring tool with surprisingly good numerics. But for computational neuroscience, it's missing too many essential features. I'll keep watching it — if they add eigenvectors and a matrix input API, it could be a lightweight alternative to pulling in all of `nalgebra`.

---

*Dr. Ananya Patel*  
*Computational Neuroscience Lab*  
*"The eigenvalues are beautiful. I just need the eigenvectors."*
