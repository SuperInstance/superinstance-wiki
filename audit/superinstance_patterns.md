# SuperInstance Pattern Audit — 5 Patterns for sunset-ecosystem

> Generated from README analysis of: holodeck-rust, flux-navigate, flux-evolve, flux-compass, analog-spectral, wave-conservation, constraint-hamiltonian, cocapn-health-rs

---

## Pattern 1: Hamiltonian Constraint Satisfaction (from `constraint-hamiltonian`)

### What It Is
Encode agent behavioral constraints as potential energy surfaces `c(q) = 0`. Instead of hard-coding rules, define constraint violations as energy penalties and let the system naturally evolve toward satisfaction via symplectic dynamics.

### How It Works
- **Störmer-Verlet integration** preserves energy structure over long timescales (no drift)
- **Augmented Lagrangian** iteratively tightens constraints via multiplier updates, not brute penalties
- **Damped relaxation** drives arbitrary initial states onto the constraint manifold
- Track **augmented energy** `H = K + V + Σ(½w·c² + λ·c)` as a conservation quality metric

### Why sunset-ecosystem Needs It
The trinity-architecture has multiple agent roles with overlapping behavioral rules. Hamiltonian constraint dynamics provides a mathematically principled way to resolve conflicts: when two room agents have contradictory goals, their constraint surfaces intersect and the system settles to the nearest feasible manifold.

### Concrete Adoption
- Add a `Constraint` trait to `sunset-ecosystem` agent state: `value_fn` + `gradient_fn` + `weight` + `multiplier`
- Use `step_damped()` for agent initialization / onboarding (drive onto valid manifold)
- Use `step()` (undamped symplectic) for steady-state operation
- Monitor `constraint_violation()` as a fleet health signal fed to `cocapn-health-rs`

---

## Pattern 2: Spectral Graph Wave Coherence Monitoring (from `wave-conservation` + `analog-spectral`)

### What It Is
Model the agent fleet as a graph where nodes are agents/rooms and edges are communication links. Propagate discrete waves through the graph; wave behavior is governed by the eigenvalue spectrum. Conservation ratio (CR) directly predicts fleet coherence halflife.

### How It Works
- **Wave speed** on the graph equals `√λ₂` (Fiedler eigenvalue = algebraic connectivity)
- **Standing wave detection** at eigenfrequencies produces resonance peaks that reveal the full spectrum
- **Conservation ratio** `CR` maps to coherence halflife: higher CR → longer-lived coherent states
- **Spectral thermostat** (from `analog-spectral`) applies deadband control: when CR drifts outside deadband, trigger `IncreaseCR` (heating) or `DecreaseCR` (cooling)
- **Analog dial banks** provide physical settling-time estimates for eigenvalue computation

### Why sunset-ecosystem Needs It
PLATO rooms and ForgeFlux tiles create a dynamically changing graph topology. Wave propagation gives a native metric for "how well-connected is the fleet right now?" without polling every node. It also predicts when a room will decohere before it actually happens.

### Concrete Adoption
- Implement `WaveState` for the PLATO room graph: adjacency from `plato-coordination` cross-room links
- Add a `SpectralThermostat` to `plato-nervous` with target CR=0.5, deadband=0.05 (battle-tested defaults from `analog-spectral`)
- Drive the thermostat from `cocapn-health-rs` TCP probes: latency spikes widen the spectral gap → thermostat responds
- Run `frequency_sweep()` periodically to recover eigenvalue spectrum and detect topology changes (new rooms, dropped agents)

---

## Pattern 3: Dual-Mode SIM/REAL Degradation Stack (from `holodeck-rust`)

### What It Is
Every agent/room maintains two independent data modes: `SIM` (predicted/simulated) and `REAL` (live sensor). A three-tier degradation stack (`GREEN`/`YELLOW`/`RED`) autonomously manages the transition when simulation drifts from reality.

### How It Works
- **GREEN**: simulation matches reality within tolerance → agent operates autonomously on SIM
- **YELLOW**: simulation drifting, agent detects divergence and begins self-adjustment (evolutionary tuning)
- **RED**: can't keep up, all-hands escalation to external models (e.g., Seed-2.0-mini refresh)
- **Per-room switching**: each room independently selects its mode; no fleet-wide lock
- **Gauge intelligence**: every sensor has trend (↑↓→), jitter (⚡), warning (~), and critical (!) indicators

### Why sunset-ecosystem Needs It
The ForgeFlux tile decomposition pipeline creates layers of abstraction. When a `forge-data` tile transform diverges from the actual data source, the PLATO room operating on stale tiles should autonomously downgrade to REAL or escalate. This pattern gives a deterministic state machine for that.

### Concrete Adoption
- Add `sim_mode` enum to each PLATO room state: `Sim`, `Real`, `Degraded`
- Port the **Gauge System** from holodeck-rust: heading/rudder style trends for every tile transform pipeline metric
- When `forge-conservation` reports a conservation ratio drop, the room switches `sim → real` for that tile category
- Wire the `RED` escalation to `plato-diffusion` progressive distillation: if agents can't keep up, trigger a knowledge-distillation cycle

---

## Pattern 4: Bounded Evolutionary Parameter Engine with Rollback (from `flux-evolve`)

### What It Is
Agent behaviors are not hard-coded but stored as tunable parameters with explicit bounds, mutation rates, fitness scores, and full rollback capability. The engine supports three evolution modes (aggressive/normal/elite) based on current fleet fitness.

### How It Works
- **8 mutation types**: `ParamAdjust`, `ThresholdShift`, `WeightRebalance`, etc.
- **Bounded parameters**: every behavior has `min`/`max` clamping with configurable `mutation_rate`
- **Fitness-based strategy**: low fitness → aggressive mutation (explore); high fitness → elite mode (only worst mutate)
- **Cumulative scoring**: `score(behavior, outcome)` accumulates evidence per parameter over time
- **Generation rollback**: `rollback(generation)` undoes all mutations after a specific generation

### Why sunset-ecosystem Needs It
PLATO rooms have `plato-signal-chain` 5-layer pipelines with configurable weights. When a room's JEPA vision or audio model starts underperforming, the pipeline parameters should self-tune. If tuning makes things worse, rollback restores the last known-good configuration.

### Concrete Adoption
- Integrate `flux-evolve::Engine` into `plato-signal-chain` as a parameter evolution layer
- Map signal-chain layer weights to bounded behaviors with `min=0.0`, `max=1.0`
- Feed fitness from `plato-autonomy` metrics: autonomy score low → trigger aggressive evolution
- Persist evolved snapshots to `forge-memory` external tile store (cross-session survival)
- Share successful evolutions across rooms via `flux-grimoire` "spell" curriculum

---

## Pattern 5: Spring-Damper Physics for Smooth Agent Transitions (from `flux-compass` + `analog-spectral`)

### What It Is
Replace instantaneous state changes (room switches, heading changes, parameter updates) with physically plausible spring-damper transitions. Configurable turn rate and settling physics prevent jarring discontinuities in agent behavior.

### How It Works
- **Spring-damper model**: target heading exerts a restoring force; damping controls oscillation; natural frequency controls speed
- **Convergence detection**: `tick(dt)` returns `true` when settled within tolerance
- **8-direction mapping**: heading quantized to N/NE/E/SE/S/SW/W/NW for human-readable state reporting
- **Settling physics**: from `analog-spectral`, gravity determines restoring force, friction determines deadband, settling time `∝ 1/gravity`

### Why sunset-ecosystem Needs It
PLATO agents currently teleport between rooms and instantly switch signal-chain configurations. This causes coherence loss in the JEPA models (vision/audio JEPA expect temporal continuity). Spring-damper transitions preserve continuity.

### Concrete Adoption
- Add a `Compass` equivalent to each PLATO room agent: smooth interpolation between room state vectors (16-dimensional `plato-state`)
- Use `set_target()` + `tick()` during room transitions: agent doesn't instantly adopt new room parameters but settles over N ticks
- Apply to `plato-timing` tensor MIDI: tempo and timing grid changes use spring-damper instead of instant quantization jumps
- Expose `direction()` (8-way state mapping) in `plato-dashboard` for human operators: "agent is NW-transitioning from Bridge to Engineering"

---

## Summary Table

| Pattern | Source Repo(s) | sunset-ecosystem Integration Point |
|---------|---------------|-----------------------------------|
| Hamiltonian Constraint Satisfaction | `constraint-hamiltonian` | Agent state validation, conflict resolution |
| Spectral Graph Wave Monitoring | `wave-conservation`, `analog-spectral` | Fleet coherence, room topology health |
| Dual-Mode SIM/REAL Degradation | `holodeck-rust` | Tile transform drift detection, autonomic fallback |
| Bounded Evolutionary Engine | `flux-evolve` | Signal-chain self-tuning, cross-room curriculum |
| Spring-Damper Transitions | `flux-compass`, `analog-spectral` | Room/agent state interpolation, JEPA continuity |
