# OPS-RETEST — Lin's Platform Engineering Evaluation

**Reviewer:** Lin — Platform Engineer, K8s clusters with 200+ microservices  
**Date:** 2026-06-01  
**Context:** Post-bug-fix re-evaluation. Previous tester (Samira) found no Prometheus exporter, no K8s integration, crates don't interop, but Fiedler value was "genuinely novel for ops."

---

## Who I Am

I'm Lin. I run Kubernetes clusters with 200+ microservices for a living. I deal with service mesh telemetry, Prometheus alerting, SLO dashboards, and the occasional 3 AM page because something nobody anticipated went sideways. I came to cathedral-probe looking for topology analysis tools that could tell me things my current monitoring stack can't — specifically, whether the *shape* of my service graph is healthy, not just whether individual services are up.

---

## cathedral-probe: Ops Viability — **5/10**

### What It Does Well

The core idea is solid. Spectral graph theory applied to service topology is genuinely interesting. The Fiedler value as a single-number connectivity health metric maps cleanly to something ops actually cares about: "is my service mesh fragmenting?" The fact that it goes to exactly zero when the graph disconnects makes alerting trivial — you could put `cathedral_value == 0` as a critical alert and it would fire the instant a partition happens.

The API is clean and easy to understand. `CathedralProbe::new()`, `.connect()`, `.fiedler_value()` — that's about all you need. The `component_importance()` method (remove each node, measure Fiedler drop) is operationally useful. It tells you which services are your critical path in a way that's more rigorous than "everyone knows the auth service is important."

### What It Doesn't Do (and Ops Needs)

**No external data ingestion.** You can't feed it Istio or Linkerd service graph data. You'd have to write a shim that queries the mesh control plane, extracts the service graph, and converts it to `CathedralProbe::connect()` calls. That's not trivial — Istio's destination rules, virtual services, and service entries form a directed graph with multiple edge types. cathedral-probe takes undirected weighted edges. The mapping loses information.

**No incremental updates.** Every time a service is added, removed, or an edge weight changes, you have to rebuild the entire graph and recompute the spectrum from scratch. For 200 services, that means a 200×200 Laplacian matrix, 200 iterations of QR decomposition, each O(n³). That's roughly 200 × 200³ = 1.6 billion FLOPs per topology update. Fine if you do it every 30 seconds. Not fine if you want real-time feedback during a canary deploy.

**No persistence.** No serialization. No way to snapshot the graph state and reload it. If your collector process restarts, it starts from scratch.

**No time-series.** You can't track how the Fiedler value changes over time natively. You'd need to wrap it in your own time-series storage and graph it externally.

### Cheeger Constant — Now Mathematically Correct, Operationally Mediocre

The implementation uses `sqrt(fiedler / 2)` clamped to [0,1]. This is an *upper bound* on the actual Cheeger constant, derived from the Cheeger inequality `λ₂/2 ≤ h²`. It's mathematically sound now (the previous version had errors), but for ops it's a rough approximation, not the real bottleneck measure.

The issue: the upper bound can overestimate how bottleneck-free your topology is. A computed Cheeger of 0.6 doesn't mean your worst cut has ratio 0.6 — it means the worst cut is *at most* 0.6 but could be much worse. For alerting, this is a "might miss real bottlenecks" problem.

### Fiedler Value as a Health Metric — Actually Useful?

Yes, with caveats. Here's how I'd use it:

- **Alert threshold:** Fiedler = 0 is a hard critical. That's a disconnected graph. No false positives.
- **Warning threshold:** This depends on your topology size. For 200 services, a healthy mesh has Fiedler roughly proportional to the minimum degree. I'd baseline it during a known-good period and alert on 50% drop. You can't pick a universal threshold — it's topology-dependent.
- **Trending:** The trend over time matters more than the absolute value. A slowly declining Fiedler means your mesh is getting more fragile. That's the real ops win.

### Performance for 100 Nodes, 500 Edges

The QR iteration does 200 passes on a 100×100 matrix, each O(n³). That's 200 × 10⁶ = 2×10⁸ FLOPs. On a modern CPU at ~10 GFLOPS (scalar, no SIMD), that's ~20ms for the spectrum alone. Add `component_importance()` which recomputes the spectrum 100 times (once per node), and you're at ~2 seconds. That's acceptable for a 30-second scrape interval but too slow for per-request analysis.

The implementation uses `Vec<Vec<f64>>` — no SIMD, no sparse matrix optimization. A real service mesh graph is sparse (average degree ~5-10, not ~100), so a sparse Laplacian + Lanczos algorithm would be orders of magnitude faster. But that's not what this crate does.

---

## conservation-checker: Ops Viability — **4/10**

### What It Does

Tracks named quantities that "must not decrease" — budgets, quotas, tokens. You register a quantity with an initial value and tolerance, update it, snapshot it, and query whether it's still "conserved." It has phase detection (Stable → PreTransition → Transitioning → Resolving) and drift rate calculation.

### Rate Limiting Tokens — Marginal Fit

You *could* track `requests_remaining = 10000` with tolerance 0 and snapshot after each request. But this is a poor fit for actual rate limiting:

1. **No atomicity or thread safety.** It's a plain `HashMap<String, QuantityState>`. No `Arc`, no `Mutex`, no atomic operations. In a multi-threaded API server, you'd need to wrap the entire thing.
2. **No time-windowing.** Real rate limits reset per second/minute/hour. conservation-checker has no concept of time windows — it just tracks a monotonic quantity.
3. **No distributed state.** In K8s, rate limits are per-cluster, not per-pod. You'd need Redis or similar external state.

### Budget Quotas — Better Fit

The `tolerance` parameter maps well to "budget with buffer." The drift rate tells you if you're burning budget faster than expected. The `Phase::PreTransition` state is essentially "you're spending faster than usual, heads up." That's a genuine early warning signal.

### Phase Detection — Maps to Real Scenarios, Barely

- **Stable:** Budget burning at expected rate. ✅
- **PreTransition:** Spending accelerating. ✅ This is useful — it detects budget runaways before they breach.
- **Transitioning:** Over budget and still spending. ✅ Critical alert.
- **Resolving:** Was over budget, now recovering. This maps to "we scaled down and costs are dropping" — somewhat useful for cost optimization stories.

The problem: the phase detection uses a noise floor of `tolerance.max(1.0) * 0.01`. For a $5000 budget with $100 tolerance, that's a $1 noise floor. For API tokens, a noise floor of 1.0 means any change > 1 token triggers phase detection. This is too coarse for fine-grained tracking and too sensitive for coarse tracking.

### Would This Replace a Custom Budget Tracker?

No. What I'd write in-house in 50 lines of Go with proper concurrency, time-windowing, and Prometheus metrics is a better fit for ops. conservation-checker is a general-purpose library that doesn't have enough ops-specific features to justify the dependency.

---

## hermes-construct: Deployment Readiness — **3/10**

### systemd Service — Surprisingly Good, Wrong Project

The `deploy/hermes-construct.service` file is genuinely well-hardened:

- ✅ Dedicated `hermes` user/group (no root)
- ✅ `NoNewPrivileges=true`
- ✅ `ProtectSystem=strict`
- ✅ `ProtectHome=true`, `PrivateTmp=true`
- ✅ `ProtectKernelTunables`, `ProtectKernelModules`, `ProtectControlGroups`
- ✅ `RestrictSUIDSGID`, `RestrictNamespaces`, `LockPersonality`
- ✅ `ReadWritePaths` scoped to only what it needs
- ✅ `KillSignal=SIGINT` for graceful shutdown with 30s timeout
- ✅ `StateDirectory` for persistent DB

This is better than 90% of systemd unit files I see in production. If I were deploying hermes-construct, the service file would need almost no changes.

But hermes-construct is an AI agent runtime (PLATO framework), not an ops tool. The systemd hardening is irrelevant to my evaluation as an ops tool.

### Ensign Configs — Novel but Not for Ops

The ensign model (cheap model watches, escalates to expensive model on anomaly) is an interesting AI ops pattern but not applicable to traditional infrastructure monitoring. The cost model ($0.001–$0.015 per check) is reasonable for AI monitoring but that's a different domain than what I came here for.

### Conservation Module — Can It Cap Real API Spending?

The `conservation.rs` module is a simple budget tracker with SQLite persistence:

```rust
pub fn spend(&mut self, cost: f64) -> Result<(), String> {
    if !self.can_spend(cost) {
        return Err("conservation budget exceeded");
    }
    self.used += cost;
    Ok(())
}
```

This is a point-in-time budget check. It can prevent an individual operation from exceeding a remaining budget. But:

1. **No concurrency control.** `ConservationState` is not thread-safe. Two concurrent operations could both pass `can_spend()` and both `spend()`, exceeding the budget.
2. **No atomic DB updates.** The `save_state()` does three separate UPDATEs without a transaction. Crash between them = corrupted state.
3. **No budget replenishment schedule.** Real API spending resets monthly/daily. This has a one-time budget with manual `deposit()`.
4. **The cost table is hardcoded.** `costs::SHELL_SPAWN = 5.0` — these are energy units for hermes-construct's internal operations, not dollar amounts.

**Verdict:** This can't cap real API spending as-is. You'd need to build rate limiting, concurrency control, and billing integration on top of it.

---

## Integration Sketch: cathedral-probe into K8s

Here's how I'd wire cathedral-probe into a real cluster:

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Istio      │────▶│  mesh-to-probe   │────▶│  cathedral-  │
│  Pilot API  │     │  (Rust shim)     │     │  probe       │
└─────────────┘     └──────────────────┘     └──────┬───────┘
                                                     │
                                              Fiedler, Cheeger,
                                              Importance, Bottlenecks
                                                     │
                                                     ▼
                                            ┌──────────────┐
                                            │  Prometheus   │
                                            │  exporter     │
                                            └──────┬───────┘
                                                   │
                                            ┌──────▼───────┐
                                            │  Grafana /    │
                                            │  Alertmanager │
                                            └──────────────┘
```

**Step 1: mesh-to-probe shim**
- Query Istio Pilot's service registry API
- Extract services (nodes) and traffic policies (edges)
- Weight edges by request rate from Prometheus metrics
- Build `CathedralProbe` graph
- Run every 30s as a CronJob or sidecar

**Step 2: Prometheus exporter**
- Expose `/metrics` endpoint with:
  - `cathedral_fiedler_value` (gauge)
  - `cathedral_cheeger_constant` (gauge)
  - `cathedral_fragility_index` (gauge)
  - `cathedral_component_importance{service="X"}` (gauge)
  - `cathedral_bottleneck_edge{from="X", to="Y"}` (gauge)
  - `cathedral_connected_components` (gauge)

**Step 3: Alert rules**
```yaml
# Critical: topology disconnected
- alert: ServiceMeshPartition
  expr: cathedral_fiedler_value == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Service mesh has disconnected components"

# Warning: connectivity degrading
- alert: MeshFragilityIncreasing
  expr: cathedral_fragility_index > 2 * avg_over_time(cathedral_fragility_index[7d])
  for: 15m
  labels:
    severity: warning

# Info: critical service identified
- alert: CriticalServiceDependency
  expr: cathedral_component_importance > on(service) avg(cathedral_component_importance) * 3
  for: 5m
```

**Missing pieces I'd need to build:**
1. Istio service graph → CathedralProbe bridge (~300 lines Rust)
2. Prometheus metrics exposition (~200 lines Rust, using `prometheus` crate)
3. Edge weight updates from traffic data (query Prometheus for request rates)
4. Incremental graph updates (currently not supported — must rebuild each cycle)
5. Helm chart for deployment

**Estimated effort:** 2-3 weeks for a senior engineer, including testing and documentation.

---

## What I'd Need to Adopt This

### Must-Have (Blocking)
1. **Sparse matrix support.** Real service meshes are sparse. The dense O(n³) QR iteration doesn't scale past ~500 nodes.
2. **Incremental updates.** I can't rebuild the entire Laplacian every time a pod restarts.
3. **Serde support.** I need to serialize/deserialize the graph state.
4. **Directed graph support.** Service meshes are directed. Undirected approximation loses critical info (A calls B ≠ B calls A).

### Should-Have
5. **Prometheus integration** (even a basic example exporter)
6. **Time-series tracking** of Fiedler value natively
7. **Edge weight from metrics** — helper to convert request rate to edge weight

### Nice-to-Have
8. **Component importance caching** (currently O(n²) per importance computation)
9. **Lanczos algorithm option** for sparse graphs (O(k × nnz) vs O(n³))
10. **Async API** — don't block my event loop

---

## Remaining Blockers

1. **cathedral-probe doesn't scale.** The O(n³) dense matrix approach caps out around 200-300 nodes before scrape intervals become problematic. A 500-node cluster would take ~10s per spectrum computation. I need sparse algorithms for production use.

2. **No interop between crates.** Samira flagged this and it's still true. cathedral-probe, conservation-checker, and hermes-construct are three independent crates with no shared types, no integration points, and no documented way to combine them. The "story" of topology-aware budget enforcement requires me to write all the glue.

3. **conservation-checker lacks concurrency and time-windowing.** Without thread safety and time-based resets, it can't track real rate limits or budgets in a multi-threaded service.

4. **hermes-construct is an AI agent runtime, not an ops tool.** The conservation module is application-level budget tracking for its own operations, not a general-purpose ops budget cap.

5. **No real-world validation.** Nobody has used these in production. The test suite covers unit tests but there are no integration tests against real service mesh data, no benchmarks, no performance regression tests.

---

## Summary Scores

| Crate | Score | Verdict |
|-------|-------|---------|
| cathedral-probe | **5/10** | Novel idea, clean API. Needs sparse matrices, incremental updates, and directed graphs to be production-viable. The Fiedler value is genuinely useful for ops alerting if you can get the data in efficiently. |
| conservation-checker | **4/10** | Well-built but too generic. Phase detection is interesting but not enough to justify using this over a purpose-built budget tracker with concurrency and time windows. |
| hermes-construct | **3/10** | Not an ops tool. Excellent systemd hardening and interesting ensign model, but it's an AI agent runtime. The conservation module can't cap real API spending without major additions. |

**Bottom line:** cathedral-probe has the most potential for ops adoption, but it's a library of math functions, not a monitoring tool. The gap between "compute eigenvalues" and "alert on service mesh fragmentation" is about 500 lines of integration code and one fundamental algorithm change (dense → sparse). If the author adds sparse matrix support and a Prometheus exporter example, I'd revisit this as a 7/10.

— Lin
