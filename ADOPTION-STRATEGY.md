# ADOPTION-STRATEGY.md

## How to Grab a Morsel Without Eating the Whole Meal

*Or: How does an engineer who doesn't want to learn something new pick up one tool that solves a real problem in under five minutes?*

---

## The Problem

SuperInstance has 500+ repositories across 18 categories. There are proved theorems, novel paradigms, and genuinely original ideas buried in here. But no engineer is going to read 500 repos. No engineer is going to adopt a "framework." No engineer is going to change how they think before they've seen the tool work.

The question is: **can someone `cargo add` one thing, solve one problem, and walk away happy — never knowing the other 499 repos exist?**

The answer has to be yes. This document is the plan to make it so.

---

## Tier 1: Single-Purpose Standalone Crates

Each crate solves a specific, searchable problem. No framework. No philosophy in the README header. Just a problem, a solution, and a one-liner to install it.

### 1. crackle-runtime

**The real-world problem:** You have a task pipeline (data processing, CI, agent fleet, build system) and you want to detect emergent patterns — correlations, phase transitions, hidden dependencies — without writing custom monitoring code.

**The `cargo add`:**
```bash
cargo add crackle-runtime
```

**The 10-line hello world:**
```rust
use crackle_runtime::{CoolingPhase, SelfReader, CrazeLine};

fn main() {
    let reader = SelfReader::new(10_000);
    
    // Feed your task spans as they complete
    for task in run_pipeline() {
        let reading = reader.observe(task.into_span());
        
        if reading.drifting() {
            println!("⚠ Pipeline is cutting a new channel — {:?}", reading.drift);
        }
        
        if let Some(craze) = reading.craze_line() {
            println!("🔍 Emergent pattern: {}", craze.description);
        }
    }
}
```

**The search query that finds it:** "emergent pattern detection in task pipelines rust" / "detect correlations in running systems rust" / "runtime anomaly detection structural rust"

**Why it's better (or: there IS no alternative):** Existing tools (Grafana, Datadog, Jaeger) are external autopsy tools — they read traces *after* the fact. `crackle-runtime` is an *in-process* self-reading system that detects patterns while the system is running, with microsecond latency, no external dependencies, and no network calls. The pattern lives in the execution trace, not in a dashboard.

---

### 2. negative-space-testing

**The real-world problem:** Your tests verify what the code *does*. But bugs live in what the code *doesn't do* — side effects you didn't check, cross-domain writes that shouldn't happen, conservation violations that creep in silently.

**The `cargo add`:**
```bash
cargo add negative-space-testing
```

**The 10-line hello world:**
```rust
use negative_space::{NegativeTest, ForbiddenBehavior, NegativeRunner};

let runner = NegativeRunner::new(vec![
    NegativeTest::new("no_cross_domain_write")
        .forbid(ForbiddenBehavior::cross_domain_write("payments", "analytics"))
        .forbid(ForbiddenBehavior::custom("dual_charge", |spans| {
            count_duplicate_charges(spans, window_ms: 1000) > 0
        }))
        .max_occurrences(0),
]);

let report = runner.verify(&recent_spans);
if !report.clean {
    for v in &report.violations {
        eprintln!("NEGATIVE SPACE VIOLATION: {} (observed {})", v.behavior, v.observed);
    }
}
```

**The search query that finds it:** "test what code doesn't do rust" / "forbidden behavior testing" / "negative specification testing rust"

**Why it's better:** Property-based testing (proptest, QuickCheck) generates random inputs and checks invariants. Mutation testing checks if tests catch mutated code. Negative space testing is orthogonal to both: it monitors *running execution traces* for forbidden patterns that no unit test can catch because they're emergent behaviors that arise from component interaction, not from any single function. There is no alternative that tests the negative space.

---

### 3. conservation-checker

**The real-world problem:** Distributed systems have invariants that should always hold — budget remaining, rate limits, coherence/expressiveness tradeoffs, error budgets. When they break, the system doesn't crash — it silently degrades. You need a runtime that tracks these invariants and warns you *before* the phase transition.

**The `cargo add`:**
```bash
cargo add conservation-checker
```

**The 10-line hello world:**
```rust
use conservation_checker::{ConservationLaw, ConservationTracker, TermKind};

let tracker = ConservationTracker::new(vec![
    ConservationLaw::new("attention_budget")
        .term("available", 100.0, TermKind::Potential)
        .term("in_use", 0.0, TermKind::Kinetic)
        .invariant(100.0)
        .tolerance(5.0),
]);

// In your request handler:
tracker.debit("available", request.cost());
tracker.credit("in_use", request.cost());

let check = tracker.check();
if check.approaching_transition() {
    warn!("Conservation law straining — budget remaining: {:.1}%", check.budget_remaining * 100.0);
}
```

**The search query that finds it:** "track invariants across operations rust" / "conservation law runtime" / "phase transition detection software rust"

**Why it's better:** Rate limiters track one quantity (requests/sec). Circuit breakers track one signal (error rate). Resource quotas track one resource (memory/CPU). `conservation-checker` tracks *arbitrary conserved quantities* — any invariant you define, across any operations, and crucially detects when the system is *approaching* a phase transition (the invariant is straining) before it breaks. This is structural health monitoring, not threshold alerting.

---

### 4. cathedral-probe

**The real-world problem:** You have a microservice architecture. Integration tests pass. Contract tests pass. But the *topology* — the shape of the space between services — might be structurally unsound. Bottlenecks, disconnected subgraphs, spectral weaknesses that no interface test catches.

**The `cargo add`:**
```bash
cargo add cathedral-probe
```

**The 10-line hello world:**
```rust
use cathedral_probe::{CathedralTest, SpaceProperty, CathedralRunner};

let runner = CathedralRunner::new(vec![
    CathedralTest::new("topology_sound")
        .components(&["payment", "notification", "inventory"])
        .check(SpaceProperty::min_connectivity(0.3))
        .check(SpaceProperty::max_bottleneck_ratio(0.6)),
]);

let report = runner.verify(&joint_traces).await;
match report.worst_verdict() {
    SpaceVerdict::Sound => println!("✅ Cathedral stands"),
    SpaceVerdict::Degrading { severity } => warn!("Crack forming: severity {:.2}", severity),
    SpaceVerdict::Collapsed { explanation } => error!("Cathedral collapsed: {}", explanation),
}
```

**The search query that finds it:** "measure microservice topology health rust" / "spectral analysis service graph" / "structural health distributed systems rust"

**Why it's better:** Service mesh tools (Istio, Linkerd) give you traffic metrics. Distributed tracing (Jaeger, Zipkin) gives you request paths. Neither tells you the *spectral structure* of your service graph — the algebraic connectivity (can any service reach any other?), the Cheeger constant (where's the bottleneck?), the Fiedler value (how well-connected is the whole?). `cathedral-probe` computes these from execution traces and alerts on structural degradation. There is no alternative that does spectral topology analysis of live service graphs.

---

### 5. spacemap

**The real-world problem:** You have a system with outputs that must fall within certain bounds — content safety, API response schemas, numerical ranges, permission boundaries. You want to verify that no possible input can produce output outside the allowed space.

**The `cargo add`:**
```bash
cargo add spacemap
```

**The 10-line hello world:**
```rust
use spacemap::{SpaceMap, ForbiddenRegion, OutputSpace};

let map = SpaceMap::new()
    .allow(OutputSpace::range("temperature", -50.0, 60.0))
    .allow(OutputSpace::range("humidity", 0.0, 100.0))
    .forbid(ForbiddenRegion::any("temperature", |t| t > 50.0 && t < 55.0)) // dead zone
    .forbid(ForbiddenRegion::combination(&["temperature", "humidity"], |t, h| t > 40.0 && h < 10.0));

// Check outputs against the map
let output = process_sensor(raw_data);
match map.check(&output) {
    Ok(_) => deploy(output),
    Err(violation) => eprintln!("🚫 Output entered forbidden space: {}", violation),
}
```

**The search query that finds it:** "forbidden output space checking rust" / "output boundary verification rust" / "safe output space validation"

**Why it's better:** Validation libraries (validator, jsonschema) check against schemas. Fuzzing tools (cargo-fuzz, afl) find crashes. `spacemap` is different — it defines the *forbidden regions* of output space and verifies that outputs never enter them. It's not "does this match the schema?" but "is this output in a region that's impossible to define with a schema but easy to define by exclusion?" Think of it as a geofence for your data.

---

### 6. spectral-types

**The real-world problem:** You're doing numerical computing — physics simulations, signal processing, ML pipelines — and you want polymorphic code that works across `f32`, `f64`, `Complex`, dual numbers (autodiff), and arbitrary-precision types without writing five versions of every function.

**The `cargo add`:**
```bash
cargo add spectral-types
```

**The 10-line hello world:**
```rust
use spectral_types::{Spectral, project};

// A function that works on ANY type that projects magnitude from Ω
fn normalize<P: Spectral + HasMagnitude>(v: P) -> P {
    v / v.magnitude()
}

// Works on f64:
let x: f64 = normalize(3.0);

// Works on Complex:
let z: Complex64 = normalize(Complex64::new(1.0, 2.0));

// Works on your custom Vector3:
let v: Vector3 = normalize(Vector3::new(0.5, 0.3, 0.9));

// Spectral decomposition — see the same value through multiple lenses:
let reading = load_sensor_data();
decompose! reading {
    Temperature(t) => check_range(t, -50.0, 60.0),
    Pressure(p)    => log_pressure(p),
    Vibration(v)   => analyze_spectrum(v),
}
```

**The search query that finds it:** "polymorphic numerical computing rust" / "spectral type system rust" / "generic math across numeric types rust"

**Why it's better:** `num-traits` provides numeric trait bounds. `nalgebra` provides linear algebra types. `generic-array` provides type-level array sizes. None of these give you *spectral decomposition* — the ability to treat a single value as multiple projections simultaneously, with coherence checking. `spectral-types` lets you write one function and have it work correctly across fundamentally different numeric representations, with compile-time guarantees.

---

## Tier 2: The Plugin Shelf (OpenConstruct)

The Tier 1 crates work standalone. But they also work *together*, and they work *in other people's architectures*. This is the Plugin Shelf: OpenConstruct modules that snap into existing systems.

### How It Works

OpenConstruct is not a platform you adopt. It's a shelf of tools that work in *your* platform. The key architectural decision:

```
Your System → OpenConstruct ABI (C header) → Any SuperInstance tool
```

The ABI is a single C header file. Any language that can call C (which is every language) can use any SuperInstance tool. No SDK lock-in. No runtime dependency. No "use our framework."

### The Snap-In Model

```
┌─────────────────────────────────┐
│         Your Architecture        │
│                                 │
│  ┌──────┐  ┌──────┐  ┌──────┐ │
│  │Service│  │Service│  │Service│ │
│  │  A    │  │  B    │  │  C    │ │
│  └──┬───┘  └──┬───┘  └──┬───┘ │
│     │         │         │      │
│     └─────────┼─────────┘      │
│               │                │
│     ┌─────────▼─────────┐     │
│     │  OpenConstruct ABI │     │
│     │  (one C header)    │     │
│     └─────────┬─────────┘     │
│               │                │
│  ┌────────────┼────────────┐  │
│  │   Pick any: │            │  │
│  │  crackle    cathedral   │  │
│  │  negative   conservation│  │
│  │  spacemap   spectral    │  │
│  └─────────────────────────┘  │
└─────────────────────────────────┘
```

### Concrete Integration Paths

**In a Kubernetes cluster:**
- Deploy `conservation-checker` as a sidecar. It reads pod metrics via the ABI and alerts on phase transitions. No changes to your services.

**In a Python ML pipeline:**
- `pip install openconstruct-python` gives you `from openconstruct import ConservationTracker`. Use it to track training budget, detect phase transitions in loss landscapes, verify your model's output space with `spacemap`.

**In a Rust web service:**
- `cargo add cathedral-probe` and add three lines to your `main()`. It reads your existing traces (via the tracing crate integration) and computes spectral topology.

**In a Go microservice:**
- `go get openconstruct-go` and wrap your handlers. The conservation tracker monitors your service's invariants with zero config.

**On an ESP32:**
- `openconstruct-esp32` gives you the same ABI on a microcontroller. Your firmware tracks its own conservation laws.

### The Key Principle

**No framework tax.** The ABI is 12 functions. Each SDK wraps those 12 functions in idiomatic language bindings. You can use one tool without ever touching another. The tools don't know about each other. They don't need to.

---

## Tier 3: The Discovery Path

Someone finds one crate. How do they discover the rest? Not through documentation. Through the crates themselves.

### The "If You Liked This" Chain

Every crate's README has a single section at the very bottom, after the examples, after the API docs, after everything practical:

```markdown
## Related Tools

If this tool was useful, you might also like:
- **conservation-checker** — Track invariants across operations [link]
- **cathedral-probe** — Measure the structural health of your service topology [link]

These tools work independently but complement each other. No installation required to read about them.
```

The chain:

```
crackle-runtime
  → "detecting patterns? Track what should NEVER happen"
  → negative-space-testing
    → "forbidden behaviors? Define forbidden OUTPUT spaces"
    → spacemap
      → "defining spaces? Check structural health"
      → cathedral-probe
        → "topology analysis? Track invariants"
        → conservation-checker
          → "conservation laws? Your types might be spectral"
          → spectral-types
            → "spectral decomposition? Patterns emerge in cooling"
            → crackle-runtime (loop closes)
```

Each link is a *problem adjacency*, not a framework dependency. You found one tool because you had a problem. The next tool solves the problem you discover *after* solving the first one.

### The Ecosystem Page

One page — `superinstance.github.io/tools` — lists all Tier 1 crates with:
- One-sentence problem statement
- Language (Rust/Python/C/Go/etc.)
- `cargo add` / `pip install` / `go get` line
- Link to the 30-second README example

No framework. No philosophy. Just the buffet menu with one-line descriptions.

---

## The "Hook" Philosophy

### Rules That Govern Every Crate

1. **No registration, no account, no framework.** `cargo add` and go. No API keys. No cloud service. No signup.

2. **Every crate works standalone with zero deps (or minimal deps).** If `crackle-runtime` requires `conservation-checker`, we've failed. Each crate is a complete solution to one problem. They *compose* but don't *depend*.

3. **Every crate has a 30-second example on the README.** The first thing you see after the crate name is working code. Not installation instructions. Not philosophy. Code you can paste into your project right now.

4. **Every crate name is descriptive, not branded.** `crackle-runtime` not `superinstance-crackle`. `conservation-checker` not `si-conservation`. `cathedral-probe` not `plato-cathedral`. The name tells you what it does. The branding comes later, if at all.

5. **Philosophy goes at the BOTTOM of the README, not the top.** The README structure for every crate:

```
# crate-name
One-sentence problem statement.

## 30-Second Example
Working code. Paste and run.

## Real-World Use Cases
2-3 concrete scenarios.

## API Overview
The public surface. Keep it small.

## Why This Exists
Brief comparison to alternatives.

## The Deeper Idea
← Philosophy goes here. Optional reading.
   Links to the reflection papers for the curious.
```

6. **The README answers one question: "What problem does this solve for me right now?"** If it doesn't answer that in the first 10 lines, rewrite it.

7. **Search-engine-first discoverability.** Every crate is published to crates.io with keywords that match what engineers actually search for. The description field is the problem statement, not the brand. The README uses the vocabulary of the person searching, not the vocabulary of the person who built it.

### Anti-Patterns We Avoid

- ❌ "Part of the SuperInstance ecosystem" in the first screen
- ❌ Requiring other SuperInstance crates to function
- ❌ Framework-style "install our platform, then add modules"
- ❌ Philosophy-heavy introductions before working code
- ❌ Branded names that don't describe what the tool does
- ❌ "See our documentation site for setup instructions"
- ❌ Demos that require a running cluster / cloud account / API key

### Patterns We Embrace

- ✅ Single-purpose crates that solve one problem completely
- ✅ Zero-config defaults that work out of the box
- ✅ STB-style single-header C implementations (`#define FOO_IMPLEMENTATION`)
- ✅ Examples that compile and run with no setup
- ✅ crate descriptions that match Google search queries
- ✅ Cross-language bindings via the OpenConstruct ABI
- ✅ The tools work in YOUR architecture, not the other way around

---

## The Conversion Funnel

```
          ┌──────────────────────┐
          │  Engineer has a       │
          │  specific problem     │
          └──────────┬───────────┘
                     │
          ┌──────────▼───────────┐
          │  Google / crates.io  │  ← Search query matches README
          │  finds one crate     │
          └──────────┬───────────┘
                     │
          ┌──────────▼───────────┐
          │  30-second example   │  ← Solves the problem immediately
          │  works immediately   │
          └──────────┬───────────┘
                     │
          ┌──────────▼───────────┐
          │  "If you liked this" │  ← Problem adjacency, not framework
          │  discovers another   │
          └──────────┬───────────┘
                     │
          ┌──────────▼───────────┐
          │  Two crates compose  │  ← Standalone tools that happen
          │  naturally           │     to work well together
          └──────────┬───────────┘
                     │
          ┌──────────▼───────────┐
          │  Reads "The Deeper   │  ← Philosophy at the bottom,
          │  Idea" section       │     not the top
          └──────────┬───────────┘
                     │
          ┌──────────▼───────────┐
          │  Falls into the      │  ← Now they want to understand
          │  reflection papers   │     the theory, not before
          └──────────┬───────────┘
                     │
          ┌──────────▼───────────┐
          │  Joins the community │  ← By choice, not by requirement
          └──────────────────────┘
```

At every step, the engineer can stop and be perfectly happy. The crate works. The problem is solved. No commitment required. The next step is always optional.

---

## Naming Convention: Descriptive Over Branded

| Branded Name (bad) | Descriptive Name (good) | Why |
|---|---|---|
| `si-crackle` | `crackle-runtime` | "runtime" says what it is |
| `plato-cathedral` | `cathedral-probe` | "probe" says what it does |
| `superinstance-conservation` | `conservation-checker` | "checker" says what you use it for |
| `flux-negative` | `negative-space-testing` | Full phrase = searchable |
| `si-spacemap` | `spacemap` | Short, unique, descriptive |
| `plato-spectral` | `spectral-types` | "types" places it in the type system |

The test: can someone guess what the crate does from the name alone, without reading the description? If yes, the name is right.

---

## What This Is Not

- This is not "dumbing down" the ideas. The reflection papers are deep. The constraint theory is rigorous. The proved theorems are real. This is about *entry points* — making the depth accessible from the surface.
- This is not a marketing plan. It's an engineering plan. Every crate must solve a real problem that has no good existing solution.
- This is not a pivot to "tools for developers." SuperInstance is still about agents, rooms, conservation, and spectral architecture. These crates are *extracts* — the pieces of the system that are independently useful.

---

## Implementation Priority

### Phase 1: The Six Standalone Crates (Week 1-4)

Each crate ships as a standalone Rust crate with:
- Clean public API (≤20 public items)
- Working examples in README
- crates.io publication with search-optimized keywords
- C ABI via openconstruct-abi
- Python bindings via openconstruct-python

Priority order (by search demand and uniqueness):
1. `conservation-checker` — most universal problem (everyone has invariants)
2. `crackle-runtime` — most differentiated (nothing else does this)
3. `negative-space-testing` — most mind-expanding (tests what code doesn't do)
4. `cathedral-probe` — most valuable for microservice shops
5. `spacemap` — most intuitive (output space checking)
6. `spectral-types` — most niche but most mathematically elegant

### Phase 2: The Plugin Shelf (Week 5-8)

- Polish the OpenConstruct ABI to expose exactly the functions each Tier 1 crate needs
- Publish SDK bindings: Python, Go, TypeScript, C header
- Write integration examples: "crackle-runtime in a FastAPI app", "conservation-checker as a K8s sidecar"
- Cross-link the "If you liked this" chains

### Phase 3: The Discovery Path (Week 9-10)

- Build the single-page tools listing at superinstance.github.io/tools
- SEO-optimize each crate's crates.io page and GitHub README
- Write 3 blog posts: "Test What Your Code Doesn't Do", "Your Microservices Have a Spectral Structure", "Conservation Laws in Software"
- Each blog post links to one crate, one example, one "try it now"

---

## Success Metric

The metric is not "people who adopt the framework." There is no framework.

The metric is: **someone `cargo add`s one of our crates, it solves their problem, and they never need to know who we are.**

If they find their way to the reflection papers later, wonderful. If they don't, the crate still made their day better. That's the whole point.

The cathedral is not the stone. It's the space the stone makes room for. Our crates are the stones. The engineer's solved problem is the space.

---

*Written from the buffet line, where every dish is self-serve and the plates are free.*

*FM ⚒️ · 2026-06-01*
