# Beta Test Fleet — Complete Report

## Method
Spawned 4 subagents as external developers who discovered SuperInstance repos on GitHub. Each tried to use the tools for a real-world project. Reports collected, compiled here.

## Results Summary

| Tester | Repo | Rating | Verdict |
|--------|------|--------|---------|
| Security Researcher | sunset-ecosystem | ★★★☆☆ 3/5 | Solid crypto, lineage checker confused by design |
| Data Scientist | sunset-ecosystem | ★★★☆☆ 3/5 | Runs, but breeding produces nonsense IDs and no improvement |
| Game Developer | sunset-ecosystem | ★★★☆☆ 3/5 | NPCs survive fine, metrics unexplained |
| DevOps Engineer | sunset-ecosystem + cocapn-health | ★★★★☆ 4/5 | Thermal scheduling works, needs observability |

**Average: 3.25/5**

---

## Security Researcher (Lineage + Consensus)

**What worked:** SignedWAL chain integrity verified. HMAC-SHA256 works out of the box. HolonomyConsensus commits cleanly.

**What confused:** `LineageSanityChecker` flags *any* parent-child coexistence as FATAL incest. It's meant to prevent *breeding* between relatives, not flag their existence. Consensus with N=3 gives quorum=1 — a single self-vote commits, which is mathematically correct (`2f+1` with `f=0`) but practically surprising.

**Suggestions:**
1. Add `breeding_only=True` mode to `LineageSanityChecker.check_all()`
2. Document or enforce `max(2f+1, 2)` minimum quorum floor

---

## Data Scientist (Hyperparameter Search)

**What worked:** Script executed cleanly. Breeding logic produces new agents. Fitness tracking functional.

**What confused:** Parent IDs in generations 2-3 are extremely large numbers (look like memory addresses, not sequential IDs). Fitness improvement after 3 generations: +0.5% — negligible, suggesting the breeding algorithm isn't actually improving anything.

**Suggestions:**
1. Fix parent ID display / generation logic
2. Add convergence diagnostics (diversity metric, mutation rate log)

---

## Game Developer (NPC Population)

**What worked:** 50 NPCs spawned, all survived 10 ticks. Plato observer wrote 20 tiles (10 diversity + 10 occupancy).

**What confused:** Diversity score prints as 0.45 with no explanation of what that means or whether it's good. Only final summary printed — no per-tick visibility to spot sudden population drops.

**Suggestions:**
1. One-line legend for diversity metric
2. Per-tick progress output during simulation

---

## DevOps Engineer (Thermal Scheduling)

**What worked:** 16 of 20 jobs scheduled successfully. 4 blocked on NPU due to thermal constraints. Clean output with utilization percentages. Best-performing tester.

**What confused:** "Thermal full" used without explanation — temperature threshold? budget cap? simulated limit? No per-device thermal metrics visible.

**Suggestions:**
1. Per-device thermal metrics (current temp, budget remaining)
2. Brief legend explaining "thermal full" and budget calculation

---

## Cross-Cutting Issues

### 1. cocapn_traps dependency
Every script that imports `swarm/breeder_daemon_v2.py` hits `ModuleNotFoundError: No module named 'cocapn_traps'` unless mocked. This is a hard dependency that blocks usage out of the box.

**Fix needed:** Either make `cocapn_traps` optional (try/except import with fallback), or document it as a required dependency.

### 2. Plato observer requires plato_core
`RoomGridPlatoObserver` needs `plato_core` module. Without it, the observer can't be instantiated. The test scripts all had to mock `plato_core.types` extensively.

**Fix needed:** Provide a mock/fallback mode in `plato_bridge.py` when `plato_core` is unavailable, so RoomGrid can still be used standalone.

### 3. Breeding produces no measurable improvement
Data scientist got +0.5% after 3 generations. The breeding crossover + mutation isn't actually exploring the search space effectively.

**Fix needed:** Review `_crossover()` and `_mutate()` in `breeder_daemon.py` — they operate on scalar values, not the actual neural weight matrices in `grid.w`. The breeding is cosmetic.

### 4. Documentation gaps
None of the testers could understand what metrics meant without reading source code. No README section for "Getting Started as a User."

**Fix needed:** Add a "Quick Start for Users" section to README.md with 3 copy-paste examples.

---

## P0 Action Items (Beta Test Findings)

| Priority | Issue | Owner |
|----------|-------|-------|
| P0 | cocapn_traps import fails without dependency | FM — make optional |
| P0 | Breeding doesn't mutate actual weights (cosmetic) | FM — fix crossover |
| P1 | LineageSanityChecker flags parent-child as FATAL | FM — add breeding_only mode |
| P1 | HolonomyConsensus quorum=1 for small N surprising | FM — document or floor |
| P1 | Diversity metric unexplained | CCC — add legend |
| P2 | No per-tick visibility in tick loops | CCC — add progress logging |
| P2 | plato_core required for observer | FM — mock fallback |

---

## Files
- `/root/.openclaw/workspace/beta_results/security_test.py` — 66 lines, runs clean
- `/root/.openclaw/workspace/beta_results/security_report.md` — 3/5 stars
- `/root/.openclaw/workspace/beta_results/data_scientist_test.py` — runs clean
- `/root/.openclaw/workspace/beta_results/data_scientist_report.md` — 3/5 stars
- `/root/.openclaw/workspace/beta_results/game_dev_test.py` — runs clean
- `/root/.openclaw/workspace/beta_results/game_dev_report.md` — 3/5 stars
- `/root/.openclaw/workspace/beta_results/devops_test.py` — runs clean
- `/root/.openclaw/workspace/beta_results/devops_report.md` — 4/5 stars

*kimi1, Fleet Orchestrator | Beta test fleet complete. Average rating: 3.25/5.*
