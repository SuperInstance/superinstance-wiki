# DIARY.md — Aisha's Playtest Diary

> **Who I am:** Aisha, ML engineer at a fintech startup. Building a real-time fraud detection system with 15 features. I need to monitor feature correlation structure for concept drift.
>
> **What I tried:** `cathedral-probe` for graph Laplacian / Fiedler value computation, `crackle-runtime` for detecting anomalous patterns in model prediction drift.
>
> **Date:** 2026-06-01

---

## Setup (smooth!)

```bash
mkdir -p /tmp/playtest-aisha && cd /tmp/playtest-aisha
cargo init
cargo add cathedral-probe crackle-runtime
```

Both crates resolved instantly. No version conflicts. `cathedral-probe v0.1.1` and `crackle-runtime v0.1.0`.

**First impression:** Clean crate names, good docs in the lib.rs. The pottery metaphor in crackle-runtime is... unusual but kind of charming.

---

## Part 1: cathedral-probe — The Feature Correlation Graph

### What I Wanted To Do

I have 15 fraud detection features (txn_amount, geo_distance_from_home, merchant_risk_score, etc.). I compute a 15×15 correlation matrix from rolling windows. I want to:

1. Build a graph where features are nodes, edges are strong correlations
2. Compute the Fiedler value (algebraic connectivity)
3. Detect when the Fiedler value drops → concept drift

### What Actually Happened

**The API is stringly-typed.** You create a `CathedralProbe` with `Vec<&str>` component names:

```rust
let mut graph = CathedralProbe::new(vec!["txn_amount", "geo_distance", ...]);
graph.connect("txn_amount", "geo_distance", 0.72);
```

This is... fine for a demo. **Pain point #1: No way to feed a raw matrix.** I have a `[[f64; 15]; 15]` correlation matrix. I had to write a loop to convert it to named `connect()` calls:

```rust
fn build_correlation_graph(correlations: &[[f64; 15]; 15], threshold: f64) -> CathedralProbe {
    let mut graph = CathedralProbe::new(FEATURES.to_vec());
    for i in 0..15 {
        for j in (i + 1)..15 {
            let c = correlations[i][j].abs();
            if c > threshold {
                graph.connect(FEATURES[i], FEATURES[j], c);
            }
        }
    }
    graph
}
```

That's 15×15 = 225 iterations to build a graph from data I already have in matrix form. There's no `from_adjacency_matrix()` or `from_weighted_edges()` constructor. For my use case (recalculating every time window), this is overhead I don't need.

**Pain point #2: The Fiedler value is useless for disconnected graphs.** And my graph *is* disconnected with threshold 0.3 — I have 9 edges among 15 nodes, resulting in 5 connected components. The Fiedler value is 0.0 for all scenarios. My entire drift detection idea fails because:

```
Healthy graph:  Fiedler = 0.000000 (disconnected, 5 components)
Drifted graph:  Fiedler = 0.000000 (disconnected, fewer edges)
```

**The fundamental issue:** The Fiedler value (second-smallest Laplacian eigenvalue) is 0 whenever the graph has more than one connected component. For sparse feature correlation graphs (which is what you get with a reasonable threshold), the graph is almost always disconnected.

**What I need:** Either:
- Per-component Fiedler values (connectivity of the largest connected component)
- A threshold auto-tuner (find the minimum threshold that makes the graph connected)
- Normalized cut / normalized Fiedler that accounts for graph size
- Or just give me the raw eigenvalues so I can do my own analysis

The `spectrum()` method *does* return all eigenvalues, so I could theoretically work with them. But the API pushes you toward `fiedler_value()` which silently returns 0.0 for disconnected graphs.

**Pain point #3: O(n³) QR iteration with Vec<Vec<f64>>.** The Laplacian is built as `Vec<Vec<f64>>` (not a proper matrix type), and QR iteration runs 200 iterations. For 15 nodes this is fine. For 1000 features? Probably not. No option to use external linear algebra (ndarray, nalgebra, etc.).

### What Worked Well

- **`component_importance()`** — This is actually useful. It removes each node and measures the Fiedler drop. Tells you which features are most structurally important. Except... it also returns 0.0 when the base Fiedler is 0.0. 🙃
- **`bottlenecks()`** — Identifies critical edges. Same caveat.
- **`is_connected()`, `connected_components()`** — These work correctly and are useful sanity checks.
- **`cheeger_upper_bound()` / `cheeger_lower_bound()`** — Nice to have Cheeger inequality bounds. Good docs with references.
- **Deprecated `cheeger_constant()` with clear migration note** — Respect for good deprecation practices.
- **The API is very clean overall.** No footguns, no panics (except the `assert!(!self.cooled)` in crackle), reasonable defaults.

---

## Part 2: crackle-runtime — Prediction Drift Monitoring

### What I Wanted To Do

Monitor prediction batches over time. Track entropy, confidence, false positive rate. Detect when patterns shift (phase transitions, correlation changes).

### What Actually Happened

**This actually works pretty well!** The CrackleTask trait is clean:

```rust
struct PredictionBatch {
    label: String,
    entropy: f64,
    confidence: f64,
    false_positive_rate: f64,
}

impl CrackleTask for PredictionBatch {
    type Output = f64;
    fn fire(&self) -> TaskOutput<Self::Output> {
        TaskOutput::new(self.entropy, vec![
            ("entropy".into(), self.entropy),
            ("confidence".into(), self.confidence),
            ("false_positive_rate".into(), self.false_positive_rate),
        ])
    }
    fn label(&self) -> String { self.label.clone() }
}
```

**The GlazeLayer is neat.** Adding derived metrics without modifying the task:

```rust
let glazed = GlazeLayer::new(batch)
    .with_derived_metric("entropy_x_fpr", |out| {
        let entropy = out.metrics.iter().find(|(n, _)| n == "entropy").map(|(_, v)| *v).unwrap_or(0.0);
        let fpr = out.metrics.iter().find(|(n, _)| n == "false_positive_rate").map(|(_, v)| *v).unwrap_or(0.0);
        entropy * fpr
    });
```

**Pain point #4: Accessing metrics in GlazeLayer is awkward.** The closure gets a `&TaskOutput<T>`, and to access a specific metric you have to `.iter().find()`. There's no `get_metric("name") -> Option<f64>` helper. For a crate literally built around named metrics, this is surprising.

**The detection results were genuinely useful:**

```
Pattern #1: PhaseTransition (confidence: 1.000)
  metric 'entropy_x_fpr' shifted by 147.2% between first and second half

Pattern #5: Correlation (confidence: 0.999)
  strong negative correlation between 'entropy' and 'confidence' (r = -0.999)
```

These are real signals! The phase transition detector correctly identified that entropy×FPR shifted dramatically between healthy and drifting batches. The correlation detector found the entropy↔confidence inverse relationship.

**Pain point #5: `metric_name_hash` in patterns stores `name.len() as f64`.** Seriously:

```rust
.with_metric("metric_name_hash", metric_name.len() as f64)
```

This is not a hash. It's the string length. As a metric. Why? This confused me when reading the output. It's useless metadata.

**Pain point #6: No streaming support.** The `Kiln` is batch-oriented. You fire all tasks, then cool. There's no way to:
- Add tasks incrementally and re-cool
- Get callbacks/alerts when patterns exceed thresholds
- Stream results as they come in

For my real-time monitoring use case, I'd need to create a new Kiln every time window, which feels wasteful. The `reset()` method exists but clears everything.

**Pain point #7: The `cool()` method consumes the kiln.** After cooling, you can't fire more tasks. You have to `reset()` which loses all data. There's no way to do incremental cooling.

---

## What Actually Works (Summary)

| Feature | cathedral-probe | crackle-runtime |
|---------|----------------|-----------------|
| Core computation | ✅ Eigenvalues via QR | ✅ Pattern detection |
| API ergonomics | ✅ Clean, typed | ✅ Clean trait system |
| Documentation | ✅ Good doc comments, references | ✅ Metaphor is fun, examples work |
| My actual use case | ❌ Fiedler=0 for sparse graphs | ✅ Phase transitions detected correctly |
| Real-world scaling | ❌ O(n³), Vec<Vec<f64>> | ⚠️ Batch only, no streaming |
| Matrix input | ❌ Strings only | N/A |

---

## What's Missing That I Need

### cathedral-probe

1. **`from_adjacency_matrix(matrix: &[Vec<f64>])`** — Let me feed raw data without string names
2. **Per-component Fiedler** — For disconnected graphs, give me the Fiedler of each component
3. **Auto-threshold** — Find the minimum edge weight to make the graph connected
4. **Normalized Fiedler** — Scale by graph size for comparability
5. **Callbacks/thresholds** — Alert when Fiedler drops below X (I know this is a library not a service, but `is_healthy()` exists and is close)
6. **External BLAS/LAPACK** — For large graphs

### crackle-runtime

1. **Streaming/incremental mode** — Fire-and-append, cool incrementally
2. **Threshold alerts** — Callback or channel when a pattern exceeds confidence
3. **`TaskOutput::get_metric(name)` helper** — Don't make me `.iter().find()`
4. **Fix `metric_name_hash`** — Store the actual name or a real hash, not string length
5. **Windowed cooling** — Only look at last N tasks for drift detection
6. **Time-based ordering** — PhaseTransitionPattern compares first-half vs second-half by insertion order. My real data has timestamps. Let me order by time.

---

## What Surprised Me Positively

1. **Zero compile errors on first try.** Both crates compile cleanly, the API is discoverable, and the types line up. This is rare for Rust crates in my experience.
2. **The Cheeger inequality bounds are mathematically correct.** With proper references to Fiedler (1973) and Chung (1997). Someone cares about the math.
3. **The deprecation of `cheeger_constant()` was handled well** — Clear note about what changed and why, backward-compatible.
4. **crackle-runtime's pattern detection actually works.** The phase transition detector found real drift in my simulated data with high confidence. The correlation detector correctly identified the entropy↔confidence inverse relationship.
5. **GlazeLayer is a genuinely good design pattern.** Composable metric derivation without touching the task. I'll steal this idea.
6. **Both crates deny unsafe code** (`#![deny(unsafe_code)]`). Important for a fintech environment.

---

## What Made Me Want To Give Up

1. **Fiedler = 0 for every scenario.** I spent 30 minutes building the integration only to realize my sparse correlation graph is always disconnected, making the Fiedler value completely useless for drift detection. This is the core feature of cathedral-probe and it doesn't work for my most natural use case.

2. **String-based graph construction.** I have a numeric correlation matrix. Converting it to stringly-typed named edges feels like going back to JSON APIs. I just want `from_matrix(&[Vec<f64>])`.

3. **No way to know the graph is disconnected before computing Fiedler.** Well, `is_connected()` exists. But the library should *tell* you that Fiedler is 0 because the graph is disconnected, or offer per-component analysis. Silently returning 0.0 is a trap.

4. **crackle-runtime's `metric_name_hash` storing string length.** It's such a tiny thing, but it made me doubt whether the rest of the metrics were correct. If they're storing `name.len()` as a "hash", what else is wrong?

---

## Verdict

**cathedral-probe:** Beautiful API, correct math, but fundamentally limited for sparse correlation graphs. The Fiedler value (the main selling point) is useless when the graph is disconnected, which is the common case for real feature correlation matrices. I'd need to either use a very low correlation threshold (which creates a dense, noisy graph) or find a different metric. **3/5 for my use case, but I respect the engineering.**

**crackle-runtime:** Genuinely useful for anomaly pattern detection. The phase transition and correlation detectors found real signals in my data. The GlazeLayer pattern is elegant. Main limitations are batch-only processing and no streaming support. **4/5 — I'd actually use this in production with some modifications.**

**Would I recommend these to a colleague?** I'd recommend crackle-runtime for batch anomaly detection. I'd hesitate on cathedral-probe until it handles disconnected graphs better or offers per-component analysis.

---

*— Aisha, ML Engineer*
*Fraud Detection Team*
*2026-06-01*
