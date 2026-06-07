# Tomás's Playtest Diary — negative-space-testing v0.1.0

**Date:** 2026-06-01  
**Who:** Tomás, game dev working on a 2D multiplayer space shooter  
**Goal:** Use `negative-space-testing` to verify physics engine invariants (no NaN, no negative health, no out-of-bounds positions)  

---

## Setup

```bash
mkdir -p /tmp/playtest-tomas && cd /tmp/playtest-tomas
cargo init
cargo add negative-space-testing
```

Installed v0.1.0 without issues. Read the source to understand the API — **no README, no examples** in the crate. Had to read `lib.rs` from the registry to figure out what's available.

---

## What the Crate Provides

| Component | Purpose |
|---|---|
| `Forbidden<T>` | Define a predicate that must never return true |
| `NegativeTest<T>` | Builder to stack multiple `forbid()` predicates, then `check()` or `check_all()` |
| `SpaceMap<K, V>` | Key-value map where some keys are "forbidden" — detect intrusions into negative space |
| `ConservationChecker` | Track quantities that shouldn't decrease (energy, matter, etc.) |
| `CracklePhase<T>` | Accumulate values during "firing", then check batch assertions during "cooling" |
| `CathedralProbe` | Graph Laplacian eigenvalue analysis for component connectivity |

---

## Test 1: Forbidden Zones — Physics Invariants ✅ (found a real bug!)

```rust
let nt = NegativeTest::<Player>::new()
    .forbid("health is NaN", |p| p.health.is_nan())
    .forbid("shield is NaN", |p| p.shield.is_nan())
    .forbid("position is NaN", |p| p.x.is_nan() || p.y.is_nan())
    .forbid("velocity is NaN", |p| p.vx.is_nan() || p.vy.is_nan())
    .forbid("negative health", |p| p.health < 0.0)
    .forbid("position outside map", |p| {
        p.x < 0.0 || p.x > MAP_SIZE || p.y < 0.0 || p.y > MAP_SIZE
    })
    .forbid("speed exceeds max", |p| p.speed() > MAX_SPEED + 0.01);
```

**Result:** Ran 1000 ticks with random thrust/damage. **CAUGHT "negative health" violation!** The player's health dropped below 0 because `take_damage()` doesn't clamp health at 0. This is a **genuine bug** in my physics code that negative-space-testing found.

```
Physics invariant violations after 1000 ticks!
Violations: ["negative health", "negative health", ... (hundreds)]
Clean ratio: 0.90%
```

**Fix needed:** Add `self.health = self.health.max(0.0)` in `take_damage()`.

**Verdict:** The `forbid()` + `check_all()` API is clean and found a real bug. 👍

---

## Test 2: Temporal Logic via CracklePhase ✅

Since the crate doesn't have explicit `always()`/`never()`/`eventually()` operators, I used `CracklePhase` to implement them as deferred batch assertions.

### `always(speed <= MAX_SPEED)`
```rust
let mut cp = CracklePhase::<f64>::new()
    .on_cool("always(speed <= MAX_SPEED)", |speeds| {
        speeds.iter().all(|s| *s <= MAX_SPEED + 0.01)
    });
// ... fire 1000 speed values ...
let result = cp.cool();
```
✅ Works. Passed.

### `never(health.is_nan())`
```rust
.on_cool("never(health.is_nan())", |healths| {
    healths.iter().all(|h| !h.is_nan())
})
```
✅ Works. Passed.

### `eventually(position.near(center))` — respawn check
```rust
.on_cool("eventually(near center for respawn)", move |positions| {
    positions.iter().any(|(x, y)| {
        ((x - center).powi(2) + (y - center).powi(2)).sqrt() < respawn_radius
    })
})
```

⚠️ **Got a compiler error:** Closures capturing local variables need `move` keyword. The compiler suggested it, but it's an ergonomics papercut.

**Verdict:** CracklePhase works for temporal logic, but you're building it yourself with closures. No built-in `always`/`never`/`eventually` — these are just `.all()` / `.all(!)` / `.any()` on the accumulated vec.

---

## Test 3: CathedralProbe — Structural Relationships ✅

```rust
let mut probe = CathedralProbe::new(vec![
    "player_alpha", "player_bravo", "player_charlie", "player_delta",
]);
probe.connect("player_alpha", "player_bravo", 1.0);
probe.connect("player_charlie", "player_delta", 1.0);
probe.connect("player_alpha", "player_charlie", 0.5);

let fiedler = probe.fiedler_value();  // connectivity measure
let cheeger = probe.cheeger_constant(); // bottleneck measure
assert!(probe.is_healthy(0.1));
```

✅ Works. The Fiedler value and Cheeger constant correctly detect connected vs disconnected teams. A disconnected player (no edges) gets a near-zero Fiedler value.

**Note:** The task mentioned "TopologyProbe (renamed from CathedralProbe)" — the crate still has `CathedralProbe`, not `TopologyProbe`. No rename has happened yet.

**For game devs:** This is interesting for verifying that your squad/team formation graph stays connected, but it operates on **static graph structure**, not on live entity positions. You'd need to rebuild the graph each frame yourself.

---

## Test 4: Shrinking ❌ NOT BUILT-IN

The crate has **no shrinking** capability. When a test fails, you get the list of violations but not the minimal failing input.

I implemented manual binary-search shrinking:
```rust
let first_fail = all_states.iter().position(|p| {
    nt.check(p).violations.len() > 0
});
```

This finds the **earliest tick** that fails, but it's not true property-based shrinking (like proptest or quickcheck). No minimal input reduction.

**Verdict:** Major gap. You'll need `proptest` alongside this crate for shrinking.

---

## Test 5: SpaceMap for Forbidden Zones ✅

```rust
let mut map = SpaceMap::<&str, (f64, f64)>::new();
map.forbid("spawn_zone_blue");
map.forbid("spawn_zone_red");
map.occupy("admin_area", (50.0, 50.0)); // oops, in forbidden zone
let intrusions = map.check_intrusions(); // catches it!
```

Works correctly. The `negative_space_ratio()` is a nice touch — tells you what % of forbidden space is still clean.

**Game use case:** Define forbidden zones (spawn areas, safe zones) and check no entity enters them during gameplay.

---

## Test 6: ConservationChecker ✅

```rust
let mut checker = ConservationChecker::new();
checker.register("total_energy", 1000.0, 10.0);
checker.update("total_energy", 800.0); // dropped!
assert!(!checker.is_conserved("total_energy"));
```

Correctly detects resource loss. The `snapshot()` + `history_value()` API lets you track conservation over time.

**Good for:** Verifying total energy/matter/ammo in the game is conserved (anti-cheat, physics accuracy).

---

## Compilation Errors Encountered

1. **`move` closure required** — `CracklePhase::on_cool()` takes `Fn(&[T]) -> bool + Send + Sync + 'static`. Closures capturing stack variables need `move`. Compiler helpfully suggested it.

That was the **only** compile error. The rest compiled and ran fine.

---

## Summary: What Works

| Feature | Status | Notes |
|---|---|---|
| `NegativeTest::forbid()` + `check_all()` | ✅ Great | Clean builder API, found real bug |
| `CracklePhase` (temporal logic) | ✅ Works | But you build temporal ops yourself |
| `CathedralProbe` (graph structure) | ✅ Works | Fiedler/Cheeger eigenvalues, static only |
| `SpaceMap` (forbidden zones) | ✅ Works | Simple key-based intrusion detection |
| `ConservationChecker` | ✅ Works | One-sided (allows increase) |
| Shrinking / minimal failing input | ❌ Missing | No property-based shrinking at all |
| Temporal logic operators | ⚠️ Manual | No `always`/`never`/`eventually` built-in |

---

## What's Missing

### 1. CI Integration
- Works fine as `#[test]` — just `cargo test`. No special runner needed.
- But: no JUnit XML output, no `#[should_panic]` integration, no test harness customization.

### 2. Game Loop Ergonomics
- **No integration with `bevy`** or any ECS. You'd need to extract component data into plain structs for testing.
- **No frame-by-frame API.** You manually collect states into a Vec and check at the end.
- **No async support.** Game loops that use tokio/async will need to `.block_on()` or collect synchronously.

### 3. No Shrinking
- This is the biggest gap for a property testing framework. Compare with `proptest` which automatically finds minimal failing inputs.
- The manual approach (binary search by tick index) is coarse and doesn't reduce the *input values*.

### 4. No Built-in Temporal Operators
- `always`, `never`, `eventually` are just `all`, `all(!)`, `any` — you write them yourself every time.
- Would be great to have: `CracklePhase::always("speed_ok", |s| *s <= MAX_SPEED)` as a shorthand.

### 5. CathedralProbe is Static
- You build the graph once and query it. For dynamic entity relationships (which change every frame), you'd rebuild the probe each frame — potentially expensive for many entities.

### 6. No Documentation or Examples
- The crate has **zero** README, zero examples directory. Had to read source code to learn the API.
- Doc comments exist but are minimal.

---

## Final Verdict

**Useful for:** Defining what your game should *never* do and catching violations. The core idea (testing negative space) is genuinely valuable — it found a real health-underflow bug in my physics code.

**Not enough on its own:** Pair it with `proptest` for input generation + shrinking. Use `negative-space-testing` for the invariant checking layer on top.

**Rating:** 6/10 — Interesting concept, decent API, but needs shrinking, temporal operators, and documentation to be production-ready.

---

## Test Results

```
running 11 tests
test test_buggy_engine_catches_violations ... ok
test test_conservation_detects_cheat ... ok
test test_energy_conservation ... ok
test test_shrinking_minimal_failure ... ok
test test_disconnected_team_detected ... ok
test test_spacemap_forbidden_zones ... ok
test test_temporal_always_speed_within_bounds ... ok
test test_no_nan_after_1000_ticks ... FAILED (found real bug: negative health!)
test test_temporal_eventually_respawn_near_center ... ok
test test_temporal_never_health_is_nan ... ok
test test_team_connectivity_cathedral_probe ... ok

FAILED. 10 passed; 1 failed;
```

The failure is a **genuine physics bug** — health goes negative because `take_damage()` doesn't clamp. Negative-space-testing did its job.
