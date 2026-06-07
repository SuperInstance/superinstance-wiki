# Ecosystem Review Diary

**Reviewer:** Nadia
**Date:** 2026-06-01
**Context:** Evaluating four crates from the SuperInstance org for potential use as dependencies in my workflow (spectral clustering, petgraph extensions, graph analysis tooling).

---

## Who I Am

I'm Nadia. I maintain 12 crates on crates.io — spectral clustering utilities, petgraph extensions, a sparse matrix toolkit, and a handful of graph algorithm crates. My most popular crate has ~800 downloads/month. I care about API ergonomics, minimal dependency trees, good documentation, and not embarrassing myself when someone reads my Cargo.toml on docs.rs.

I've seen bad crates. I've published bad crates. I know the difference.

---

## Per-Crate Review

### 1. cathedral-probe (0.1.0)

**What it does:** Spectral graph analysis — Laplacian eigenvalues, Fiedler value, Cheeger constant, component importance, bottleneck detection. For weighted undirected graphs of named components.

**API Design: 7/10**

The API is genuinely usable. `CathedralProbe::new(vec!["a", "b", "c"])` then `probe.connect("a", "b", 1.0)` then `probe.fiedler_value()` — that's the right shape. Named components instead of integer indices is a deliberate ergonomics choice, and I respect it.

What bugs me:
- The main type is called `CathedralProbe`, not `Graph` or `Probe` or `SpectralGraph`. It's a structural type masquerading as a domain-specific type. If I import this, every file reads `CathedralProbe` where I'd naturally write `Graph`. The name fights the API.
- No `Debug` or `Clone` impl on the main type. I see `clone_shallow()` as a private method — why not just derive `Clone`?
- No iterator over edges. No way to inspect edge weights after insertion.
- `connect()` silently ignores unknown node names. Should probably panic or return Result.
- The QR iteration is O(n³) per step × 200 steps. For a graph with 20+ nodes, this is going to be slow. No warning about scalability.

**Documentation: 8/10**

The crate-level doc is solid — explains what spectral topology analysis is, what the Laplacian is, and why you'd care. The README is excellent: clear table of metrics, real-world use cases, full API reference that actually matches the code. This is above-average crate documentation.

Missing: no `#![warn(missing_docs)]`, so internal methods are undocumented. No changelog. No CONTRIBUTING.md. The claim "Works on `no_std` targets with `alloc`" in the README is **false** — there's no `#![no_std]` attribute, and `std::collections::HashMap` is used. This would annoy me if I trusted it and then couldn't compile for my embedded target.

**Tests: 7/10**

26 tests, all passing. Good coverage of the happy paths — connected graphs, disconnected graphs, edge cases (empty, single node, zero weight). The test for a 20-node graph is nice.

Missing: no property-based tests, no benchmarks, no tests for the QR decomposition itself (the core algorithm!), no tests for numerical precision beyond rough `> 0.5` assertions. The spectrum assertions are surprisingly loose — for K₃, the eigenvalues are exactly {0, 3, 3}, but the test just checks `spec[1] > 1.0`. This tells me the author knows their QR iteration isn't converging precisely.

**Cargo.toml: 6/10**

Has name, version, edition, description, license, repository, keywords, categories. That's the basics.

Missing: no `readme` field (README.md exists but isn't declared), no MSRV, no `rust-version`. The empty `[dev-dependencies]` section is fine but looks like a placeholder. Categories `"algorithms"` and `"science"` are reasonable.

**Naming: 5/10**

"cathedral-probe" is poetic but not searchable. If I'm looking for spectral graph analysis in Rust, I'd search "laplacian", "spectral", "graph eigenvalue" — not "cathedral". The name tells me about the author's aesthetic, not what the crate does.

---

### 2. crackle-runtime (0.1.0)

**What it does:** Task execution framework where tasks produce named metrics, then a "cooling" phase detects emergent patterns — clustering, phase transitions, conservation laws, correlations.

**API Design: 8/10**

This is the most well-designed API in the set. The pottery metaphor (fire/cool/kiln/glaze) is consistent throughout and actually maps well to the operations:

- `Kiln::new(ThermalProfile::fast_cooling())` → build the runtime
- `kiln.fire_and_record(task)` → execute tasks
- `kiln.cool()` → detect patterns
- `GlazeLayer::new(task).with_derived_metric(...)` → decorator pattern for enriched metrics

The `CrackleTask` trait is clean: `fire()` is required, `cool()` and `label()` have sensible defaults. `TaskOutput<T>` with builder-pattern `with_metric()` is idiomatic.

The `ThermalProfile` builder is nice — `.without_clustering().without_correlations()` for disabling detectors. `CoolingRate` enum with named variants instead of magic numbers.

Issues:
- `fire_task()` doesn't record the task — only `fire_and_record()` does. This is confusing API surface. Why have both? The naming doesn't make the distinction clear.
- `CrackleError` exists but is never returned anywhere. All methods panic instead. The error type is dead code.
- `GlazeBatch` is marked `#[allow(dead_code)]` throughout — it's clearly unfinished.
- The `cool()` closure on `CrackleTask` receives `all_metrics` but there's no documentation about when/how to use it.

**Documentation: 9/10**

Outstanding. The crate-level doc tells a story. The README has badges (crates.io, docs.rs), a working 30-second example, a clear table of pattern types, real-world use cases, full API reference, and a "Philosophy" section that actually connects to the design.

Every public type has doc comments with examples. The module structure (error, glaze, kiln, patterns, profile, task) is logical and well-separated.

One issue: the README example uses `p.kind().to_uppercase()` in the ci_patterns example, but `PatternKind` doesn't implement `Display` with uppercase. **This example doesn't compile.** That's a CI gap.

**Tests: 9/10**

~70+ tests across unit and integration levels. Tests for every detector (clustering, phase transition, conservation, correlation), edge cases (empty metrics, negative values, very large values, 100 tasks), and integration tests for full fire→cool cycles.

The Pearson correlation tests are good — perfect positive, perfect negative, no correlation, constant X, too few pairs. This is real numerical testing, not just happy-path asserts.

The test where patterns are verified to be sorted by confidence is a nice touch. The `GlazeLayer` integration tests cover the decorator pattern.

Missing: benchmarks (QR clustering could be slow), property-based tests.

**Cargo.toml: 5/10**

Missing `description` is present actually, but the example that doesn't compile is a problem. No `readme` field. No MSRV. Categories `"algorithms"` and `"development-tools"` are OK but `"development-tools::profiling"` might be more accurate.

The crate name says "runtime" which implies async, threads, or an event loop. This is actually a synchronous, single-threaded library. The name is misleading.

**Naming: 4/10**

"crackle-runtime" — "runtime" suggests tokio, async-std, or an executor. This is none of those things. It's a pattern detection library. "crackle-detect" or "crackle-patterns" would be more honest. The pottery metaphor is beautiful but makes the crate harder to find.

---

### 3. negative-space-testing (0.1.0)

**What it does:** Testing framework with five components — SpaceMap (forbidden output regions), NegativeTest (exclusion trait), ConservationChecker (monotonicity tracking), CracklePhase (deferred assertions), CathedralProbe (inter-component relationship testing).

**API Design: 9/10**

This is genuinely good API design. Each component does one thing:

- `SpaceMap<T>` — generic, chainable, fluent API. `add_samples()`, `exclude_fn()`, `verify()`. The `openness()` metric is clever.
- `NegativeTest` trait — minimal, two methods. Clean.
- `ConservationChecker` — `track_non_decreasing()`, `track_non_increasing()`, `track_conserved()`, `record()`, `check()`. The naming is self-documenting.
- `CracklePhase` — `defer()`, `defer_crack()`, `cool()`. The `CrackleOutcome` enum with `Smooth`/`Craze`/`Kintsugi`/`UnexpectedSmooth` is creative but actually useful.
- `CathedralProbe` — `probe()`, `verify()`, `all_sound()`. Simple and composable.

The `#![warn(missing_docs)]` is enforced. Every public item is documented. Types implement `Default` and `Debug` where appropriate. `#[must_use]` on result types. This is a crate author who cares about their users.

Issues:
- The `ConservationChecker` here is different from the standalone `conservation-checker` crate (see below). This is confusing for users — which one do I use?
- `SpaceMap` uses `Box<dyn Fn>` for exclusions, which means it's not `Send`/`Sync`. This limits use in async contexts.
- `CathedralProbe` also uses `Box<dyn Fn>` — same issue.
- The `Monotonicity` enum's `Conserved` variant conflicts with the method name `is_conserved()` in the result type. Mild naming collision.

**Documentation: 9/10**

Outstanding README with badges, working examples for all five components, a "Putting It Together" section that shows how they compose, real-world use cases, and installation instructions. The crate-level docs explain the philosophy clearly.

Every module has doc comments. Every public type has examples. The doc examples compile and pass (5 doc-tests, all green).

The philosophy section is well-written and doesn't get in the way of the technical content.

**Tests: 9/10**

91 unit tests + 6 integration tests = 97 total. This is thorough. Tests cover:
- Empty maps, single samples, bulk samples
- Multiple exclusions, overlapping exclusions
- Chained builder calls
- String-typed maps (generics work)
- All `CrackleOutcome` variants
- Conservation violations at tolerance boundaries
- Integration: simulated ML training loop combining all five components

The integration tests are particularly strong — they demonstrate real usage patterns and catch inter-component issues.

**Cargo.toml: 7/10**

Has all required fields plus `readme`. Categories `"development-tools::testing"` is correct. Keywords are reasonable.

Missing: MSRV, no `license-file` (uses standard MIT). No CI badge despite having tests worth running.

**Naming: 5/10**

"negative-space-testing" is too long (23 chars). crates.io names should be snappy. "negspace", "negative-test", or "absence-test" would be better. The name also doesn't tell you this is about five different testing approaches — it sounds like it's just about "negative testing" in the QA sense.

---

### 4. conservation-checker (0.1.0)

**What it does:** One-sided conservation law tracker — quantities that must not decrease (with tolerance), plus drift detection and phase analysis.

**API Design: 7/10**

Clean and straightforward: `register()`, `update()`, `is_conserved()`, `violations()`, `snapshot()`, `phase()`, `drift_rate()`.

The `Phase` enum (`Stable`, `PreTransition`, `Transitioning`, `Resolving`) is genuinely useful — it's not just a boolean but gives you trajectory information. `Display` is implemented for `Phase`, which is nice for logging.

Issues:
- Every method that takes a quantity name panics if it's not registered. This is a strong opinion — `Result` would be more forgiving. At minimum, document the panic behavior in the method doc comments (currently undocumented).
- `snapshot()` records the current value into history, but `update()` doesn't auto-snapshot. This means you can `update()` and forget to `snapshot()`, leading to stale history. The separation is intentional but error-prone.
- `reset_baseline()` resets initial to current but doesn't clear history, which could confuse `drift_rate()` and `phase()`.
- The `drift_rate()` implementation is just `(last - first) / (n-1)` — a simple linear regression. No mention of this in docs, and it's misleading for non-monotonic sequences.

**Documentation: 6/10**

The README is good — has badges, examples, real-world use cases, API reference, design principles. But the crate-level doc comment is just `#![deny(unsafe_code)]` — no module-level documentation at all. This shows up as a blank page on docs.rs.

No doc comments on any public method. `register()`, `update()`, `is_conserved()` — nothing. For a crate that wants to be depended upon, this is a significant gap.

**Tests: 8/10**

53 tests — excellent. Tests cover:
- Construction and registration
- Updates (including unknown names, same value, higher value)
- Conservation checks (strict, tolerant, boundary cases)
- Snapshot mechanics
- Drift rate calculation
- Phase detection (all four phases)
- Integration scenarios (budget tracking, token depletion)
- `Clone` independence
- Panic behavior (`should_panic` tests)

The edge case testing is solid — tolerance boundaries (exactly at, just past), zero tolerance, large tolerance, negative values. This is someone who thinks about edge cases.

**Cargo.toml: 6/10**

Has name, version, edition, license, description, repository, keywords, categories, example declarations. No `readme` field (README.md exists). No MSRV.

The examples (`basic.rs`, `budget_tracking.rs`) are simple but demonstrate the core use case well.

**Naming: 6/10**

"conservation-checker" is descriptive but generic. "budget-tracker" or "monotone-checker" would be more specific. The name works, though — it's searchable and tells you what it does.

The confusing part: there's a `ConservationChecker` in both `negative-space-testing` and this standalone crate, and they have **different APIs**. The neg-space one uses `track_non_decreasing()` / `record()`, this one uses `register()` / `update()`. If both end up in the same dependency tree, that's going to confuse users.

---

## Ecosystem Compatibility

### cathedral-probe + petgraph?

Not directly compatible. `CathedralProbe` has its own graph representation (`Vec<String>` nodes, `Vec<(usize, usize, f64)>` edges). There's no conversion from `petgraph::Graph` or `petgraph::DiGraph`. To use this with petgraph, I'd need to write my own adapter. For my use case (spectral analysis of petgraph structures), I'd be better off extracting the Laplacian and QR decomposition code and applying it to petgraph's adjacency matrix directly.

The Laplacian builder is O(n²) in memory (dense matrix), which doesn't scale. petgraph handles sparse graphs naturally. For anything beyond 50-100 nodes, this crate's dense representation is the wrong approach.

### crackle-runtime dependency tree?

Zero dependencies. That's excellent — no transitive dependency risk. I could add it without bloating anyone's lockfile.

But would I use it? The task abstraction is opinionated. I'd need to wrap my existing computation in `CrackleTask`, produce `TaskOutput<f64>` with named metrics, and run everything through a `Kiln`. That's a non-trivial adoption cost for what's essentially clustering + correlation detection.

### Serde support?

None of the four crates support Serde. `CathedralProbe`, `CracklePattern`, `ConservationChecker`, `SpaceMap` — none have `#[derive(Serialize, Deserialize)]` behind a feature flag. If I want to serialize results to JSON (for logging, API responses, testing artifacts), I'd need to write my own wrapper types.

This is a real gap. Most production Rust code that deals with metrics and analysis results needs serialization.

---

## Publish Quality

| Crate | Compiles | Tests Pass | Doc Examples | README | Badges | LICENSE |
|-------|----------|------------|--------------|--------|--------|---------|
| cathedral-probe | ✅ | ✅ 26/26 | 0 doc-tests | ✅ | ❌ | In Cargo.toml only |
| crackle-runtime | ⚠️ Example fails | ✅ lib tests | 0 doc-tests | ✅ | ✅ | LICENSE file |
| negative-space-testing | ✅ | ✅ 97/97 | ✅ 5/5 | ✅ | ✅ | LICENSE file |
| conservation-checker | ✅ | ✅ 53/53 | 0 doc-tests | ✅ | ❌ | LICENSE file |

**cathedral-probe:** Claims `no_std` support in README but uses `std::collections::HashMap`. This is a documentation bug that could waste someone's time.

**crackle-runtime:** The `ci_patterns.rs` example doesn't compile (`PatternKind` has no `to_uppercase()` method). If `cargo test` doesn't build examples, this slips through. CI should run `cargo test --examples`.

**negative-space-testing:** The only crate where everything works out of the box — tests, doc tests, integration tests, examples. This is the one that clearly had CI running.

**conservation-checker:** Works but has no crate-level documentation and no doc comments on methods. On docs.rs, this would look like a hollow shell despite having good internals.

---

## Would I Depend On This?

**cathedral-probe: No.** The QR implementation is educational but not production-quality. No sparse matrix support, O(n³) eigenvalue computation, no numerical stability guarantees beyond 200 iterations of Wilkinson-shifted QR. For spectral graph analysis, I'd use `nalgebra` + `petgraph` and compute the Laplacian eigenvalues with `nalgebra::linalg::SymmetricEigen`. It's more code to wire up but the numerical methods are battle-tested.

Also, the false `no_std` claim in the README would make me distrust other claims.

**crackle-runtime: Maybe, with caveats.** The pattern detection is interesting and the API is well-designed. Zero dependencies is a strong selling point. If I had a batch processing pipeline where I wanted to detect correlations between metrics, I'd consider it.

But the broken example worries me — it suggests CI doesn't test examples, which suggests other things might be broken that just aren't tested. The dead `CrackleError` type and the unfinished `GlazeBatch` suggest this is more prototype than production.

**negative-space-testing: Yes, as a dev-dependency.** This is genuinely useful. The `SpaceMap` type alone is worth the dependency — defining forbidden output regions and verifying nothing intruded is something I've handwritten a dozen times. The `CracklePhase` deferred assertion pattern is clever for integration tests. The `CathedralProbe` inter-component testing is exactly the kind of thing that catches bugs unit tests miss.

97 tests, all passing, including integration tests. Doc examples that compile. `#![warn(missing_docs)]` enforced. This is a crate I'd trust.

**conservation-checker: Probably not standalone.** If I'm already using `negative-space-testing` (which has its own `ConservationChecker`), I wouldn't add a second crate with a different API that does a subset of the same thing. The standalone crate is slightly more feature-rich (phase detection, drift rate, snapshot history) but not enough to justify two competing types in my dependency tree.

---

## Top 3 Things to Fix (Per Crate)

### cathedral-probe
1. **Fix the false `no_std` claim** — either actually support it (replace `HashMap` with `BTreeMap` or `Vec` lookups) or remove the claim from README
2. **Implement `Debug` and `Clone`** on `CathedralProbe` — bare minimum trait impls
3. **Use sparse matrix representation** — the dense Laplacian is unusable beyond ~50 nodes

### crackle-runtime
1. **Fix the broken example** (`ci_patterns.rs: PatternKind` has no `to_uppercase()`) and add `cargo test --examples` to CI
2. **Remove or use `CrackleError`** — either return `Result` from fallible methods or delete the dead error type
3. **Rename from "runtime"** to something that doesn't imply async/threads — "crackle-detect" or "crackle-patterns"

### negative-space-testing
1. **Make `SpaceMap` and `CathedralProbe` `Send`/`Sync`** — replace `Box<dyn Fn>` with a concrete closure type or use `Box<dyn Fn + Send + Sync>`
2. **Shorten the crate name** — "negspace" or "neg-test" would be easier to type and remember
3. **Add Serde support** behind a feature flag — test results are useless if you can't serialize them

### conservation-checker
1. **Add crate-level documentation** — the docs.rs landing page is blank without it
2. **Add doc comments to all public methods** — `register()`, `update()`, `is_conserved()` are currently undocumented
3. **Reconcile with `negative-space-testing::ConservationChecker`** — two crates in the same org with the same type name but different APIs is confusing

---

## The One Crate I'd Actually Use

**negative-space-testing.**

It solves a real problem I've had repeatedly — defining and verifying negative constraints on outputs. The `SpaceMap<T>` type alone is worth adding as a dev-dependency. The composition of all five components (SpaceMap + NegativeTest + ConservationChecker + CracklePhase + CathedralProbe) gives me a testing vocabulary I didn't have before.

97 passing tests. Doc examples that compile. `#![warn(missing_docs)]`. Zero dependencies. Reasonable crate size (1.8K lines including tests). This is the work of someone who actually uses their own code.

The other three crates are interesting explorations — especially crackle-runtime's pattern detection metaphor — but they're not ready for me to depend on. cathedral-probe needs real numerical methods behind it. crackle-runtime needs to prove its CI works. conservation-checker needs to decide whether it's standalone or part of negative-space-testing.

---

*Nadia's diary, 2026-06-01. Signed off after cloning, reading, building, testing, and forming opinions. The cathedral is not the stone. But sometimes the stone needs better documentation.*
