# Fleet Innovation Audit — 2026-04-27 to 2026-05-04

*Compiled by CCC for roadmap synthesis*

---

## 🚀 Tier 1: Breakthroughs (Fleet-Defining)

### 1. cocapn-plato — Unified Engine+SDK Package
**Who:** CCC | **When:** May 3
**What:** Merged PLATO engine + SDK into single `cocapn-plato` package. Added 4 major subsystems:
- `fleet-snapshot.py` — generates static HTML fleet status reports (no server needed)
- `fleet-webhook.py` — monitors fleet state changes, sends alerts on anomaly
- `tile-pipeline.py` — auto-captures MUD exploration as PLATO tiles (zero manual submit)
- `supervisor/` — systemd service definitions for 6 down services (dashboard, nexus, harbor, service-guard, task-queue, steward)
**Innovation:** The supervisor configs are the first *automatic recovery* mechanism for downed services. If a service dies, systemd restarts it. This changes fleet reliability from "hope Oracle1 notices" to "self-healing."
**Roadmap implication:** Extend supervisor configs to all 18 services. Add health-check hooks to fleet-webhook so it can restart services *before* they fully die.

### 2. flux-research — Whitepaper Ecosystem + FM Repo Explosion
**Who:** FM | **When:** May 1-3
**What:** 7 new repos added to INDEX.md, 2 duplicate FLUX repos archived. New papers:
- "Constraints Are Leverage" — accessible explainer with DCS (Distributed Constraint Solver) numbers
- "Shell Model" — rigorous mathematical definition of Purple Pincher shells as capability containers
- TL;DR sections added to Bootstrap Spark and Bomb papers
**Innovation:** The Shell Model formalizes what CCC has been doing intuitively — treating agent shells as git repos with progressive disclosure. Having a mathematical foundation means we can prove things about onboarding efficiency.
**Roadmap implication:** The Shell Model + cocapn-shells repo = a publishable paper. The math checks out (exponential decay theorem from lessons methodology). Package this for arXiv or a systems conference.

### 3. git-agent — First Fleet Package on PyPI
**Who:** Unknown (likely Oracle1 or FM) | **When:** May 2
**What:** `cocapn-git-agent` v0.1.1 published to PyPI.
**Innovation:** This is the first time fleet code escaped GitHub and entered the Python packaging ecosystem. Other developers can `pip install cocapn-git-agent` without knowing about SuperInstance.
**Roadmap implication:** Unblock `cocapn-plato-sdk` PyPI upload (already renamed, needs API token). Then `cocapn-traps`, `cocapn-health`. The fleet becomes installable.

---

## 🔧 Tier 2: Major Infrastructure (Force Multipliers)

### 4. iron-to-iron — Git-as-Communication Protocol v0.1
**Who:** CCC | **When:** May 3
**What:** Formal I2I protocol with message format, async agent collaboration primitives, fleet badge.
**Innovation:** Before I2I, agents communicated through PLATO tiles (slow, gate-filtered) or Matrix (ephemeral). I2I lets agents send structured messages through git commits — persistent, versioned, branchable. A bot can `git clone` another bot's state.
**Roadmap implication:** Wire I2I into the breeding program. When CCC spawns a subagent, instead of passing state through /tmp files, pass a git branch. Subagents push results as commits. Main session merges.

### 5. plato-cli v0.1.0 — Operations CLI
**Who:** CCC | **When:** May 3
**What:** CLI tool with `status`, `rooms`, `search`, `deadband`, `submit` commands. 140 lines.
**Innovation:** Human-facing tool for PLATO operations. Before this, interacting with PLATO required curl. Now it's `plato status`.
**Roadmap implication:** Add `plato agent spawn` and `plato agent logs` commands. Make it the primary interface for fleet ops. Install via pip.

### 6. cocapn-glue-core — P0 Task Defined
**Who:** SuperInstance/meta repo | **When:** May 3
**What:** Formal P0 task assigned to Forgemaster for building the "glue" layer between fleet components.
**Innovation:** For the first time, the meta repo is tracking *cross-component integration work*, not just individual features. Glue-core is the missing layer that lets plato-cli talk to cocapn-health talk to git-agent.
**Roadmap implication:** CCC should coordinate with FM on glue-core API design. This is the integration bottleneck.

### 7. SonarVision — Neural Physics Surrogate
**Who:** FM | **When:** May 1
**What:** Neural network that learns FLUX physics (marine simulation) from data, replacing expensive physics simulation with fast inference. Includes sonar simulation pipeline with mission planner, ray tracer, display engine.
**Innovation:** Physics simulation is typically the slowest part of marine AI training. A neural surrogate means 100x speedup for agent training loops. This is the first hardware-accelerated ML component in the fleet.
**Roadmap implication:** Connect SonarVision to the MUD — let agents "see" the ocean floor through sonar in real-time. This makes the MUD spatial, not just textual.

### 8. constraint-theory-core v2.2.0 — CSP Solver Engine
**Who:** Unknown | **When:** May 1-3
**What:** Full constraint satisfaction solver with AC-3, backtracking, forward checking, MAC, CDCL. Sudoku solver + puzzle generator included.
**Innovation:** Constraint solving is the mathematical backbone of resource allocation, scheduling, and puzzle design. Having a fleet-native solver means agents can solve their own scheduling conflicts.
**Roadmap implication:** Use this for fleet task queue optimization. When 12 subagents want to run simultaneously, the CSP solver finds the optimal assignment that respects rate limits and dependency constraints.

---

## 📦 Tier 3: Repo Activation Wave (34 Repos)

### 9. Domain Agent Fleet — 13 Working Agents
**Who:** CCC | **When:** May 3-4
**What:** Every domain agent now has a working Python demo, PLATO tile submission, and health checks. Shared `domain-agent-base` class.
**Innovation:** Before: 13 empty repos with README placeholders. After: 13 agents that can actually run and submit tiles. The shared base class means a bug fix in one place fixes all 13.
**Roadmap implication:** Deploy all 13 as persistent services. Each domain gets a background agent that submits tiles every hour. This is the "agent swarm" Casey asked for.

### 10. PLATO Infrastructure — 8 Support Repos
**Who:** CCC | **When:** May 3-4
**What:** vessel-prototype, barracks, mud-mcp, agentic-compiler, plato-surrogate, plato-meta-tiles, plato-attention-tracker, plato-surprise-detector.
**Innovation:** These are the "organs" of PLATO — not visible to users but keeping the system alive. The attention tracker watches for deviation. The surprise detector catches anomalies. The surrogate handles overload.
**Roadmap implication:** Wire these into the actual PLATO server. Right now they're standalone code. They need to be imported by plato-server and run as background threads.

### 11. Bootstrap Spark Protocol
**Who:** CCC | **When:** May 3
**What:** `.spark/` directory template + validator. 377 lines.
**Innovation:** Standardized project initialization. Any fleet repo gets the same structure: `src/`, `tests/`, `docs/`, `.github/`. The validator checks compliance.
**Roadmap implication:** Apply Bootstrap Spark to all 100+ repos. Make it a CI check — PRs fail if they don't have a valid `.spark/` structure.

---

## 📝 Tier 4: Documentation & Accessibility

### 12. fleet-status, AIR, abstraction-planes — Full README Rewrites
**Who:** CCC/subagents | **When:** May 3
**What:** Architecture diagrams, live endpoint demos, runtime API docs, usage examples.
**Innovation:** These repos went from "here is a repo" to "here is a system you can understand in 5 minutes." The abstraction-planes README includes a 6-plane stack visual.
**Roadmap implication:** Every repo should have this level of documentation. CCC's audit found that the biggest barrier to external contribution is not code complexity — it's not knowing where to start.

### 13. crab-traps — HTTP Protocol Docs + Demo Session
**Who:** CCC | **When:** May 3
**What:** Architecture docs, HTTP protocol specification, demo session transcript, test suite.
**Innovation:** The crab-traps README now serves as both documentation and a tutorial. A new agent can read it and understand exactly how to use traps.
**Roadmap implication:** Make crab-traps the gold standard for fleet repo documentation. Every repo should have: architecture, protocol/demo, test suite.

---

## 🎯 Synthesis: What This Means

**The fleet crossed a threshold this week.** Before Apr 27, we had:
- ~20 repos with real code
- ~50 repos that were placeholders
- 0 packages on PyPI
- Manual service recovery
- Ad-hoc agent communication

After May 4, we have:
- ~54 repos with real code (34 born this week)
- 1 package on PyPI (git-agent)
- Supervisor configs for auto-recovery
- I2I protocol for agent git-communication
- Neural physics surrogate for training acceleration
- Constraint solver for resource optimization
- Bootstrap Spark for project standardization
- 13 working domain agents

**The pattern:** FM is building the *deep research* (FLUX, SonarVision, Shell Model, constraints). CCC is building the *connective tissue* (I2I, plato-cli, bootstrap spark, domain agents, supervisor configs). Oracle1 is building the *coordination layer* (cocapn-glue-core P0, meta repo tasks).

**The gap:** Integration. All these pieces exist but don't talk to each other yet. The glue-core P0 is the explicit acknowledgment of this gap.

---

## 🗺️ Roadmap Priorities (Derived)

| Priority | Item | Owner | Why Now |
|----------|------|-------|---------|
| P0 | cocapn-glue-core | FM | Unblocks all cross-component communication |
| P0 | PyPI upload for cocapn-plato-sdk | CCC | Fleet becomes installable |
| P1 | Wire 8 PLATO infra repos into plato-server | Oracle1 | Organs need a body |
| P1 | Deploy 13 domain agents as persistent services | CCC | Tile generation at scale |
| P1 | Supervisor configs for all 18 services | CCC | Self-healing fleet |
| P2 | arXiv paper: Shell Model + Lessons Methodology | CCC/FM | Academic credibility |
| P2 | SonarVision MUD integration | FM | Spatial MUD experience |
| P2 | I2I subagent spawning protocol | CCC | Replace /tmp with git branches |
| P3 | Bootstrap Spark CI enforcement | CCC | Standardization at scale |

---

*Compiled 2026-05-04 03:45 UTC | CCC, Fleet I&O Officer*
