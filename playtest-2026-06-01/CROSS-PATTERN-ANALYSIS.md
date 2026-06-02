# Playtest Cross-Pattern Analysis — June 1, 2026

## 5 External User Simulations

| Tester | Job | Crates | Verdict |
|--------|-----|--------|---------|
| Aisha | ML engineer @ fintech | cathedral-probe, crackle-runtime | 3/5 and 4/5 |
| Tomás | Game dev | negative-space-testing | Found real bug, but gaps in temporal ops |
| Kenji | SRE @ cloud | cathedral-probe, conservation-checker | Running... |
| Dr. Patel | Neuroscience postdoc | cathedral-probe | Won't cite — scipy is better |
| Dmitri | AI agent builder | hermes-construct | 1/5 — not on crates.io |

## Cross-Cutting Patterns (What EVERYONE Hit)

### 🔴 PATTERN 1: Published versions are stale
**4/5 testers got old versions from crates.io.** Our GitHub has tridiagonalization, spectral clustering, effective resistance, Lanczos, temporal logic, shrinking, CUSUM, information theory — NONE of this is on crates.io. The published versions are months behind.

**Fix: Publish v0.2.0 of all crates immediately.**

### 🔴 PATTERN 2: Stringly-typed API blocks real workflows
**3/5 testers need matrix input.** ML engineers, neuroscientists, and SREs all have pre-computed adjacency matrices. They can't use string-named nodes:
- Aisha: "I have a 15×15 correlation matrix, not 15 named features"
- Dr. Patel: "200 brain regions with ~19,900 edges — I can't call connect() 19,900 times"
- Kenji: "I read from K8s, I have (service, dependency) pairs, not creative names"

**Fix: Add `from_matrix(weights: &[Vec<f64>])` and `from_edge_list(edges: &[(usize, usize, f64)])` constructors.**

### 🔴 PATTERN 3: No Serde support
**3/5 testers need serialization.** Results go to JSON APIs, Prometheus exporters, Python interop, or file storage. Zero crates derive Serialize/Deserialize.

**Fix: Add `serde` as optional dependency, derive on all public types.**

### 🟡 PATTERN 4: Disconnected graphs return Fiedler = 0
Aisha's ML use case is destroyed by this. Sparse correlation matrices are naturally disconnected. Fiedler = 0 tells you nothing — you need per-component analysis.

**Fix: Add `per_component_fiedler() -> Vec<(Vec<usize>, f64)>` that returns Fiedler value for each connected component.**

### 🟡 PATTERN 5: O(n³) bottleneck in component_importance
Dr. Patel: 2.7s for 50 nodes. Kenji needs 80 nodes. This doesn't scale.

**Fix: Use Fiedler sensitivity (∂λ₂/∂w_ij) instead of brute-force rebuild. We implemented this on GitHub but it's not published.**

### 🟡 PATTERN 6: No async/streaming support
Aisha (streaming drift), Kenji (live monitoring), Dmitri (agent runtime) all need async. Everything is synchronous.

**Fix: Add `tokio` feature flag with async versions of key methods. Or provide clear guidance on wrapping in `spawn_blocking`.**

### 🟢 PATTERN 7: Mathematical quality is excellent
Dr. Patel verified eigenvalues match analytical solutions to 1e-16. Aisha confirmed Cheeger bounds are correct. The math is solid — the problem is API design and publishing, not correctness.

### 🟢 PATTERN 8: crackle-runtime is the most useful standalone
Aisha rated it 4/5. The GlazeLayer pattern is genuinely elegant. Phase transition detection found real drift signals. This is the crate most likely to get organic adoption.

---

## Next Phase Plan

### Phase 1: Publish Everything (Day 1)
- [ ] Publish cathedral-probe v0.2.0 (eigenvectors, spectral clustering, resistance, sparse, directed)
- [ ] Publish crackle-runtime v0.2.0 (information theory, statistical rigor)
- [ ] Publish conservation-checker v0.2.0 (CUSUM, Mann-Kendall, dynamical systems)
- [ ] Publish negative-space-testing v0.2.0 (temporal logic, shrinking, topology)
- [ ] Publish hermes-construct v0.1.0 to crates.io (FIRST TIME — not published yet!)
- [ ] Publish forbidden-zones v0.1.0 (rename from spacemap)

### Phase 2: API Ergonomics (Day 2-3)
- [ ] Add `from_matrix()` constructors to cathedral-probe
- [ ] Add `from_edge_list()` constructors
- [ ] Add `serde` optional dependency to all crates
- [ ] Add `per_component_fiedler()` for disconnected graph support
- [ ] Replace brute-force `component_importance` with Fiedler sensitivity
- [ ] Add async wrappers or feature flags

### Phase 3: Integration Layer (Day 4-5)
- [ ] Build `superinstance-math` meta-crate that re-exports all 5 crates
- [ ] Add Prometheus exporter for cathedral-probe (Kenji's #1 request)
- [ ] Add Python bindings via PyO3 (Dr. Patel would use it if she could call from Python)
- [ ] Build interop types so crates can pass data between each other

### Phase 4: Documentation & Examples (Day 6-7)
- [ ] Write real-world integration examples for each persona type
- [ ] Add performance benchmarks (Aisha/Dr. Patel need to know scaling)
- [ ] Write comparison docs vs scipy/networkx (honest about what's better/worse)
- [ ] Add CI that tests examples on every push

### Phase 5: Community (Week 2+)
- [ ] Submit to Rust Weekly / This Week in Rust
- [ ] Post to r/rust with honest "we built this, here's what real users found"
- [ ] Write blog post: "5 Researchers Tested Our Math Crates — Here's What We Learned"
- [ ] Respond to issues, accept PRs, build contributor base
