# DIARY.md - Kenji's Playtest Experience

**Date:** 2026-06-01  
**Persona:** Kenji, SRE at a cloud company running 80 microservices  
**Goal:** Build a lightweight Rust service combining topology health (cathedral-probe) with budget monitoring (conservation-checker)

---

## What I Built

A single binary that:
1. Reads service mesh topology → builds a CathedralProbe → computes Fiedler value, Cheeger bounds, bottlenecks, component importance
2. Tracks API budget with ConservationChecker → simulates 100 requests → drift rate, phase detection, changepoint detection, Hurst exponent
3. Couples the two: Fiedler value dynamically adjusts budget tolerance (fragile topology → tighter budget)

**Everything compiles and runs.**

---

## What Actually Works

### cathedral-probe (v0.1.1) — Solid for Small Graphs

- **API is clean:** `CathedralProbe::new(names)`, `connect(a, b, w)`, `fiedler_value()`, `spectrum()`, `bottlenecks()`, `component_importance()` — intuitive, well-named.
- **Fiedler value computation works correctly.** My 30-node mesh gave Fiedler = 0.097 (connected but sparse — realistic for microservices).
- **Bottleneck detection is useful.** Identified single points of failure correctly (router, event-bus, etc.).
- **Component importance rankings** make sense — hub services score highest.
- **`cheeger_constant()` is deprecated** — use `cheeger_upper_bound()` / `cheeger_lower_bound()` instead. The docs/API could make this clearer, but the compiler warning caught it.
- **`is_healthy(min_fiedler)` is handy** for a quick health check.

### conservation-checker (v0.1.0) — Practical Budget Tracker

- **Registration + update + snapshot model** is straightforward. Register a quantity, update values, snapshot periodically.
- **Drift rate** works: (last - first) / (n-1) — simple average rate of change.
- **Phase detection** (Stable / PreTransition / Transitioning / Resolving) works based on rate-of-change analysis. My budget hit "Transitioning" correctly.
- **Tolerance model** is one-sided (values must not decrease beyond initial - tolerance). Perfect for budget tracking.
- **`violations()`** returns all quantities currently out of bounds.
- **Clone support** — can fork the checker for parallel scenarios.

---

## What's Impossible (or Very Painful)

### 🔴 cathedral-probe Cannot Handle 80 Nodes in Practice

This is the **biggest limitation.** The library uses **dense QR iteration** for eigenvalue computation:
- Builds a full N×N Laplacian matrix
- Runs 200 iterations of QR decomposition (each is O(N³))
- For 72 nodes: the computation took **minutes** before I killed it
- For 30 nodes: runs in ~1 second
- For a real 80-service mesh: **unusable for interactive monitoring**

**Workaround:** Sample your topology. Pick the 20-30 most critical services, or aggregate leaf nodes. But you lose fidelity.

**What it needs:** Sparse eigenvalue solvers (e.g., Lanczos/Arnoldi via `nalgebra` or `faer`). Only need the smallest few eigenvalues, not the full spectrum.

### 🔴 No Async Support (Either Library)

Both crates are **purely synchronous**. No `async` methods, no tokio integration, no `Send` considerations documented.

For my use case (tokio-based service polling K8s API):
- I'd need to spawn blocking tasks: `tokio::task::spawn_blocking(move || probe.fiedler_value())`
- Works, but it's awkward, especially since cathedral-probe computation is slow
- No streaming/cancelation support

### 🔴 No Prometheus/Metrics Export

Neither library has any observability integration:
- No Prometheus metrics export
- No OpenTelemetry spans
- No structured logging
- No way to expose Fiedler value as a gauge without writing your own exporter

**Workaround:** I'd write a thin `prometheus` crate integration myself:
```rust
let fiedler_gauge = IntGauge::new("topology_fiedler_value", "Algebraic connectivity").unwrap();
fiedler_gauge.set((probe.fiedler_value() * 1000.0) as i64);
```

### 🟡 conservation-checker Has No Concurrent Access

`ConservationChecker` uses `HashMap<String, QuantityState>` internally with **no locking or interior mutability**:
- No `Arc<Mutex<ConservationChecker>>` pattern documented
- No thread-safe variant
- For a tokio service handling concurrent request tracking: you'd need to wrap it yourself
- The `Clone` impl exists but creates independent copies (not shared state)

**Workaround:** `Arc<Mutex<ConservationChecker>>` — standard Rust pattern, but the library doesn't help.

### 🟡 No Built-in Changepoint Detection

conservation-checker detects *phases* but doesn't have formal changepoint detection. I had to implement my own (drift rate delta threshold). The phase enum is useful but coarse.

### 🟡 No Hurst Exponent / Time-Series Analysis

No R/S analysis, no Hurst exponent, no autocorrelation. I implemented Hurst from scratch. For a "conservation" monitoring library, some built-in time-series diagnostics would be nice.

---

## The Coupling Idea: Fiedler → Budget Tolerance

The concept works: when your architecture becomes fragile (low Fiedler), tighten your operational budget. This encodes "fragile systems should take fewer risks."

In practice:
- Fiedler < threshold → reduce budget tolerance proportionally
- Fiedler > threshold → give some extra headroom
- This creates a feedback loop: architectural health informs operational parameters

**What would make this better:**
- CathedralProbe could expose a `health_score()` normalized to [0, 1]
- ConservationChecker could accept dynamic tolerance updates at runtime (currently tolerance is fixed at registration)
- Need to re-register or manually adjust tolerance — no `set_tolerance()` method

---

## Honest Assessment

| Feature | cathedral-probe | conservation-checker |
|---------|----------------|---------------------|
| API Design | ✅ Clean, intuitive | ✅ Simple, practical |
| Docs | 🟡 Basic | 🟡 Basic |
| Correctness | ✅ Tests pass, results make sense | ✅ Tests pass, results make sense |
| Performance (30 nodes) | ✅ ~1s | ✅ Instant |
| Performance (80 nodes) | ❌ Minutes | N/A |
| Async | ❌ No | ❌ No |
| Thread-safe | ❌ No | ❌ No (manual wrapping) |
| Prometheus | ❌ No | ❌ No |
| Real-world ready | 🟡 Prototype/demo only | 🟡 Useful for simple cases |

**Bottom line:** Both crates are well-made prototypes with clean APIs. cathedral-probe's eigenvalue solver needs sparse matrix support before it can handle real production topologies. conservation-checker is closer to usable but needs concurrency support and dynamic tolerance for production use.

I'd use conservation-checker in a sidecar or CLI tool today. I'd wait for cathedral-probe to add sparse solvers before trusting it with 80 nodes in production.

---

## Files

- `src/main.rs` — The complete service (topology analysis + budget tracking + coupling + Hurst)
- `Cargo.toml` — Dependencies: cathedral-probe 0.1.1, conservation-checker 0.1.0
