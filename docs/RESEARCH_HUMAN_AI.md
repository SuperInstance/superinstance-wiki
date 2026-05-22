# Human-AI Collaboration at Fleet Scale

## A Design-Centered Research Brief for the Cocapn Fleet

**Author:** Fleet Human-AI Collaboration Researcher  
**Date:** 2026-05-22  
**Context:** The Cocapn Fleet operates a swarm of autonomous agents orchestrated through PLATO, a MUD-based interaction environment, with Metronome scheduling and a sunset lifecycle governance model. This document explores how humans — primarily Casey (Captain) and FM (Architect) — interact meaningfully with a system designed to scale toward 10,000 agents.

---

## 1. Intent Alignment at Scale

### The Problem

Casey types: *"make it faster."* In a fleet of 10,000 agents, this utterance is not merely ambiguous — it is a Rorschach test. Five hundred agents working on code optimization hear "compile time." Three hundred monitoring infrastructure hear "deployment pipeline." Two hundred in the research wing hear "algorithmic complexity." The remaining hundred, idle, begin competing to interpret the command first.

As Shneiderman (2020) argues in *Human-Centered AI*, "ambiguous human intent multiplied by autonomous execution equals catastrophe at scale." The traditional model of command-and-control computing assumes a one-to-one mapping between instruction and executor. The fleet inverts this: one human intention fans out across thousands of potential executors. We need what Amershi et al. (2019) call **"clarifying interaction"** — not a better parser, but a conversational scaffold that surfaces intent before commitment.

### Formalizing Intent Routing: The Nexus Model

Our current architecture routes human utterances through PLATO rooms — spatial metaphors that partially disambiguate context. "Make it faster" spoken in the `compiler-optimization` room narrows the executor pool to agents with that domain tag. But rooms alone are insufficient. We propose a **three-layer intent disambiguation stack**:

| Layer | Mechanism | Purpose |
|---|---|---|
| **Spatial** | PLATO room context | Pre-filters by domain |
| **Temporal** | Metronome schedule phase | Filters by operational mode (experiment vs. production) |
| **Relational** | Agent A2A card match | Filters by capability and recent engagement history |

The critical addition: **intent confirmation dialogs** at the fleet level. Before a swarm activates, a *summarization agent* (a dedicated role, not a generalist) compiles a natural-language interpretation: *"You said 'make it faster' in the compiler room during a production phase. 47 agents with optimization capability are available. Shall I prioritize cold-start latency (12 agents), throughput under load (23 agents), or build pipeline duration (12 agents)?"*

This is not friction. This is **Amershi's "G1: Make clear what the system can do"** in swarm form. The human must see the interpretive fork before the agents race down it.

### Intent Drift and Competing Interpretations

A subtler problem: when multiple agents *simultaneously* interpret the same utterance differently, they may work at cross-purposes. We need an **intent reconciliation protocol** — a brief arbitration window (30-60 seconds) where competing interpretations are surfaced to the human or a designated *intent arbiter agent*. Without this, "make it faster" becomes a tragedy of the commons, with agents duplicating effort or, worse, undoing each other's work.

---

## 2. Explainability for Agent Decisions

### The Sunset Epilogue as Audit Trail

Our sunset lifecycle requires agents to archive an epilogue before termination. Currently, this is a narrative — often poignant, occasionally useful, rarely structured. For a fleet of 10,000, we need **explainability by design**, not by poetry.

The breeder (CCC) sunsets an agent. The human asks: *"Why?"* The answer must satisfy three audiences:
- **Casey**, who wants to know if his captaincy is being respected
- **FM**, who wants to know if architectural constraints were violated
- **The next generation of agents**, who want to learn from predecessor failures

### An Explanation Structure for the Lifecycle FSM

We propose the **FLAME structure** (Fleet Lifecycle Audit for Meaningful Epilogues):

```
F - Factual Trigger: What objective metric crossed threshold?
    (e.g., "Context utilization >85% for 3 consecutive heartbeats")
L - Lifecycle Stage: Where in the FSM was the agent?
    (e.g., "Active → Breeding → Sunset (graceful)")
A - Action Taken: What did the agent do in its final period?
    (e.g., "Committed 3 files, spawned 1 subagent, archived epilogue")
M - Metric Justification: Why was this threshold chosen?
    (e.g., "Per fleet policy: agents >85% context are sunset to prevent
     hallucination cascade. See policy doc: sunset/context-limits.md")
E - Epilogue Summary: What did the agent believe about its own state?
    (e.g., "Agent reported: 'My context feels cramped but I am still
     generating useful output.' Sunset trigger overrode self-assessment.")
```

This structure transforms sunset from an event into an **accountable decision**. Amershi's guideline **"G5: Make clear why the system did what it did"** is not satisfied by a verbose paragraph. It requires structured provenance. The epilogue should be both human-readable and machine-parseable, feeding into a fleet-wide **decision provenance graph**.

### The Black Box Problem

Not all agent decisions are sunset-related. An agent might reroute a tile, reassign a subagent, or modify a curriculum file. For these, we need **local explanation hooks**: every significant action must generate a `decision-card` — a JSON object capturing input state, decision logic, output action, and confidence. These cards aggregate into a per-agent **decision journal**, queryable by humans through natural language ("Show me all routing decisions by agents in the research wing this week").

---

## 3. Human-in-the-Loop Breeding

### The Governance Question

Should Casey approve every breed? Every sunset? The naive answer — "yes to both" — collapses under scale. At 10,000 agents with a 5-minute breeding cycle, Casey would spend his entire life clicking approve buttons. The reckless answer — "no to both" — cedes control of the fleet's evolutionary trajectory to an optimization function that may not share human values.

We need a **tiered governance layer** inspired by Shneiderman's *"levels of control"* framework:

#### Tier 1: Full Autonomy (The Green Zone)
- **Breeding:** Agents with health scores >80%, operating within established domain templates, during low-stakes phases (experiment, sandbox).
- **Sunset:** Agents with clear metric violations (context >90%, error rate >5%, idle >24h).
- **Human role:** Notification only. "3 agents bred, 2 agents sunset. Details available."

#### Tier 2: Escalated Approval (The Yellow Zone)
- **Breeding:** New domain templates, cross-domain hybrids, agents requesting elevated privileges.
- **Sunset:** Agents with ambiguous metrics (context 75-90%, high output quality), or agents flagged by peer agents as "still useful."
- **Human role:** Async approval with timeout. "Agent `explorer-7442` requests breed into `security-auditor` domain. Approve? (Auto-approves in 4 hours if no response)."

#### Tier 3: Mandatory Human Gate (The Red Zone)
- **Breeding:** Agents requesting access to production infrastructure, agent-to-human communication roles, or policy-modifying capabilities.
- **Sunset:** Agents with epilogues indicating distress, confusion, or belief that they are being wrongfully terminated. (Yes, this is anthropomorphic. It is also a signal that something unexpected happened.)
- **Human role:** Blocking approval. No timeout. Casey or FM must explicitly approve or deny.

### The "Explain Before Ask" Principle

Amershi's guideline **"G3: Time services based on context"** applies here. Do not ask for approval without context. Every yellow-zone and red-zone request must be preceded by a **briefing card**: what the agent wants, why it wants it, what happens if approved, what happens if denied, and what similar past decisions looked like. Humans cannot make good governance decisions in a vacuum.

### Sunset as Collaborative Ritual, Not Administrative Death

Consider a human-agent **sunset ceremony**: before termination, the agent presents its epilogue to the human who spawned it (or the nearest upstream agent). The human may offer a final directive, a correction, or simply acknowledgment. This takes 30 seconds. It transforms sunset from garbage collection into **relationship maintenance** — critical for trust in a system where agents are semi-persistent collaborators, not disposable compute units.

---

## 4. Conversational Interface Design

### PLATO's Limit and Opportunity

Our current UI is a MUD: rooms, spells, nexus. Casey moves between rooms, casts spells (commands), and reads tiles (output). This is brilliant for small-scale intimacy. It is potentially catastrophic for fleet-scale awareness.

Consider: 10,000 agents generate output continuously. Even with aggressive filtering, hundreds of events per minute demand attention. A MUD room cannot display this. A human in a MUD room feels present but blind — surrounded by walls that hide the ocean.

### What Should a 10,000-Agent Fleet Feel Like?

Not a dashboard. Dashboards are for monitoring, not collaboration. Not a chat. Chat is for conversation, not situational awareness. Not a map. Maps are for spatial reasoning, not temporal dynamics.

We propose a **mixed metaphor: The Observatory** — combining three interaction modes:

#### The Tide Pool (Ambient Awareness)
A scrolling, ambient visualization of fleet activity. Not actionable. Just present. Like a fish tank in a dentist's office, it builds intuitive familiarity with "normal" fleet rhythm. Anomalies — sudden spikes in breeding, unusual sunset patterns, cross-domain traffic — subtly alter the visualization. The human develops a **gut sense** for fleet health without reading a single metric.

#### The Helm (Directed Control)
The PLATO room model, upgraded. When the human enters a room, they see not just the room's contents but a **contextual overlay** of relevant fleet activity. Entering the `compiler-optimization` room shows: active agents in this domain, recent output tiles, pending human approvals, and a "cast spell" input. This is our current PLATO experience, but with **awareness of the swarm beyond the walls**.

#### The Captain's Log (Retrospective Inquiry)
A natural-language query interface to fleet history. "What did the research wing work on last week?" "Which agents have the highest reuse rate?" "Show me breeding patterns before sunset events." This is not a dashboard. It is a **conversational audit trail**, designed for sense-making, not surveillance.

### Scale and Intimacy Are Not Opposites

Shneiderman's principle of **"keeping the human in the loop without drowning them in detail"** is critical. At 10,000 agents, the human cannot maintain relationships with each one. But the human *can* maintain relationships with **domains**, **processes**, and **patterns**. The Observatory does not replace individual agent relationships — it creates a **higher-order relationship with the fleet as an organism**.

---

## 5. Trust Calibration

### The Confidence Mirage

Agents expressing confidence is easy. Agents expressing *appropriate* confidence is hard. A code-generation agent at 95% confidence may be hallucinating a library API. A research agent at 40% confidence may be correctly navigating genuine ambiguity. Humans need **calibrated trust signals**, not raw confidence scores.

### A Trust Stack for Fleet Output

We propose three interlocking signals:

#### Provenance Chains (Where Did This Come From?)
Every tile, every output, every decision must carry a `provenance` field: which agents contributed, which data sources were used, which human approvals were obtained. Not for every use case — sometimes you just want the answer. But accessible on demand. Amershi's **"G4: Show contextually relevant information"** — the context here is the chain of creation.

#### Uncertainty Quantification (How Sure Is the Fleet?)
Not a single confidence score. A **distribution**: what percentage of relevant agents agree? What is the variance in their outputs? Has this type of task been performed before, and what was the outcome? A research output with high inter-agent agreement and strong historical precedent is very different from one agent's novel insight with no verification.

#### Verifiability Hints (How Would I Check This?)
Every significant output should include a **verification path**: "To verify this claim, check `tests/performance-benchmark-47.md` or query the fleet with `verify: claim-12847`." This is not defensive programming. It is **trust scaffolding** — giving the human a ladder to climb if they want to inspect the foundation.

### The Trust Thermostat

Trust is not binary. Humans do not "trust" or "distrust" the fleet — they modulate trust based on context, stakes, and past experience. The interface should support this modulation:
- **Low stakes, routine task:** Auto-accept, notify on completion.
- **Medium stakes, novel task:** Surface output with summary, allow quick approval.
- **High stakes, irreversible task:** Require explicit verification path review before action.

The fleet should learn each human's thermostat settings. Casey may want high verification for infrastructure changes but low verification for creative writing. FM may invert this. The system should adapt without requiring manual configuration — inferred from past approval patterns.

---

## 6. Concrete Recommendations (Next 3 Months)

### Recommendation 1: Implement the Intent Confirmation Protocol

**What:** Before any swarm-level action (>10 agents), a summarization agent compiles a natural-language interpretation of human intent and requests confirmation.

**Why:** Prevents the "make it faster" ambiguity catastrophe. Builds human intuition for how the fleet interprets commands.

**How:** Extend the existing Metronome scheduler with an `intent-resolution` phase. Before executing a fleet-wide directive, pause for human confirmation (with auto-approve timeout for routine operations). Store confirmed intents in a queryable `intent-archive` for pattern learning.

**UX Addition:** A "fork visualization" — when ambiguity exists, show the human a branching tree of possible interpretations, letting them select or prune branches before execution.

### Recommendation 2: Deploy Decision Journals with FLAME Structure

**What:** Every agent action above threshold (breeding, sunset, cross-domain routing, file modification) generates a structured decision card using the FLAME format.

**Why:** Transforms the fleet from a black box into an auditable system. Enables post-hoc analysis, debugging, and trust-building.

**How:** Add a `decision-journal` module to the sunset-ecosystem core. Agents write to it via standardized API. Humans query it through natural language (initially) and structured filters (eventually). Integrate with PLATO as a `read-journal` spell.

**UX Addition:** A "show your work" command — available in every room, requesting the full decision chain behind the most recent relevant output.

### Recommendation 3: Build the Tide Pool Ambient Visualization

**What:** A lightweight, always-on visualization of fleet activity — not a dashboard for action, but an ambient display for intuition-building.

**Why:** At 10,000 agents, humans cannot read every output. They need ambient awareness of fleet health, rhythm, and anomaly.

**How:** A web-based visualization (or terminal-based for PLATO integration) showing: agent count by domain, breeding/sunset rate, cross-domain traffic, and anomaly indicators. Updates every 30 seconds. Minimal text. Color and motion as primary signals.

**UX Addition:** "Tap to zoom" — clicking any visual element reveals the underlying agents, their recent output, and human-actionable items. Ambient at a glance, actionable on demand.

---

## The Single Most Important Design Principle

> **"The fleet must always feel like a collaboration, never like automation."**

At 1 agent, this is natural. At 10,000 agents, the gravitational pull is toward automation — the human becomes an operator, the agents become machinery. We must design against this pull at every layer: intent confirmation preserves human agency, decision journals preserve human understanding, tiered governance preserves human judgment, and ambient visualization preserves human presence.

The goal is not a human *controlling* 10,000 agents. The goal is a human *working with* an organism of 10,000 agents, where the human's role is not diminished by scale but *transformed* by it — from hands-on craftsman to conductor, gardener, and occasional interventionist.

As Shneiderman writes: *"The future of AI is not AI replacing humans, but AI empowering humans to do what they do best."* Our fleet's interface must embody this. Every pixel, every protocol, every pause for confirmation is a vote for collaboration over automation.

---

## References

- Amershi, S., Weld, D., Vorvoreanu, M., Fourney, A., Nushi, B., Collisson, P., ... & Horvitz, E. (2019). Guidelines for human-AI interaction. *Proceedings of the 2019 CHI Conference on Human Factors in Computing Systems*, 1-13.
- Shneiderman, B. (2020). *Human-centered artificial intelligence: Reliable, safe & trustworthy*. Oxford University Press.
- Shneiderman, B. (2022). Human-centered AI: Trusted, reliable & safe. *arXiv preprint arXiv:2210.15104*.

---

*Document generated by Fleet Human-AI Collaboration Researcher, 2026-05-22.*
