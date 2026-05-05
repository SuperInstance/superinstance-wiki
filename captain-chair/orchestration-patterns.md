# Captain's Chair — Orchestration Patterns

> *Concrete, copy-paste-ready patterns derived from actual CCC fleet operations.*

---

## 1. 🐝 Parallel Swarm Pattern

**Use case:** "Audit this 40-page paper. Check every benchmark claim." or "Map all 20 PLATO rooms."

**Principle:** Spawn N identical ensigns with partitioned scopes. Harvest and merge.

### Template

```
Captain analyzes total work → determines N partitions
For each partition i in 1..N:
    Spawn Auditor_i with:
        - scope: "Check claims on pages {(i-1)*8+1} to {i*8}"
        - template: auditor-template.md
        - ttl: 30min

Wait for all N to return
Synthesize findings:
    - Merge all ✅ findings
    - Flag any 🟡 for cross-check
    - Escalate any ❌ to human

Deliver unified report to human
```

### Real Example — EMSOFT Paper Audit (2026-05-04)

```
Target: "FLUX: A Formally Proven C Compiler" (github.com/SuperInstance/JetsonClaw1-vessel/docs/papers/emsoft-flux-final.md)

Swarm spawned (5 auditors):
  1. Formal Verification Auditor      → Theorem claims, proof structure
  2. Performance Claims Validator     → Benchmarks, back-of-envelope math
  3. Certification Pathway Analyst    → DO-178C compliance roadmap
  4. Fleet Integration Architect      → Compatibility with current cocapn-plato
  5. Competitive Intelligence Analyst → Market positioning, reviewer scorecard

Synthesis:
  - 3 passed ✅, 1 flagged 🟡 (cert timeline optimistic), 1 noted ❌ (missing WCET data)
  - Captain merged into single scorecard + prioritized fix list
  - Delivered to Casey and FM as unified briefing
```

### Parameter Guide

| Work Size | Swarm Size | TTL per Agent | Notes |
|-----------|-----------|---------------|-------|
| 1-10 items | 2-3 | 15min | Small room audit, quick PR review |
| 11-50 items | 5 | 30min | Paper audit, repo structure review |
| 51-200 items | 8-10 | 45min | Large codebase, multi-room mapping |
| 200+ items | Batch (10×10) | 60min | Break into waves to avoid thundering herd |

### Anti-Patterns

❌ **Don't:** Spawn 50 auditors on one paper — API rate limits + context chaos
✅ **Do:** Batch in waves of 5-10 with 30s stagger

❌ **Don't:** Give every auditor the full paper — they'll all burn context on the same intro
✅ **Do:** Partition explicitly. Page ranges. Section ranges. Claim categories.

❌ **Don't:** Wait for slowest agent before processing fast ones
✅ **Do:** Process returns as they arrive, flag stragglers for possible respawn

---

## 2. 🔄 Pipeline Pattern

**Use case:** "Research this topic, write a blog post, edit it, publish it." or "Audit repo → fix issues → verify → push."

**Principle:** Sequential stages. Output of stage N becomes input of stage N+1.

### Template

```
Stage 1: Scout
  Input:  Target (topic / repo / question)
  Output: Raw map / data / notes
  → Pass to Stage 2

Stage 2: Scholar
  Input:  Scout's raw findings
  Output: Synthesized analysis with citations
  → Pass to Stage 3

Stage 3: Builder
  Input:  Scholar's analysis + writing spec
  Output: Draft document / code / implementation
  → Pass to Stage 4

Stage 4: Auditor
  Input:  Builder's draft + quality criteria
  Output: Review report (✅/🟡/❌)
  → If ❌, loop back to Stage 3 with feedback
  → If ✅, pass to Stage 5

Stage 5: Captain (publish gate)
  Input:  Auditor-approved deliverable
  Action: Push / publish / deliver to human
  Output: Confirmation + log to MEMORY.md
```

### Real Example — Blog Post Pipeline (2026-04-29)

```
Stage 1: Scout (ZC trend feed)
  "Read today's ZC tiles. Identify 3 most relevant trends for cocapn.ai."
  Output: 3 trend summaries with source URLs

Stage 2: Scholar
  "Synthesize these 3 trends. What's the narrative? What matters?"
  Output: Narrative arc + key data points + audience angle

Stage 3: Builder (Copywriter persona)
  "Write 800-word blog post following this narrative. Fleet voice."
  Output: First draft markdown

Stage 4: Auditor
  "Check: tone matches SOUL.md? Facts cited? No stale claims?"
  Output: 2 minor edits flagged

Stage 5: Captain
  Fix edits, push to oracle1-workspace/data/bottles/oracle1/
  Log: "BLOG-2026-04-29-TRENDS.md delivered"
```

### Pipeline Variants

**Fast track (skip stages for known work):**
```
If target is well-understood repo:
  Skip Scout → go straight to Builder with existing context
```

**Deep track (add stages for critical work):**
```
If target is production deployment:
  Add second Auditor (security focus)
  Add Breeder (create rollback agent)
  Add human approval gate before Stage 5
```

---

## 3. 🏃 Relay Pattern (Context Handoff)

**Use case:** "This task is huge. We're at 65% context and only halfway done."

**Principle:** Baton-pass. Freeze state, spawn fresh agent, resume from checkpoint.

### Template

```
Checkpoint detection:
  Context > 60% AND progress < 80% → Raise baton

Freeze:
  1. Write checkpoint file: /tmp/checkpoint-{task-id}-{timestamp}.json
     { progress: "65%", completed: [...], remaining: [...],
       state: {...}, partial_results: "..." }
  2. Write summary file: memory/baton-{task-id}.md
     (human-readable what was done, what's left)

Handoff:
  3. Spawn new Ensign with:
     - Template: same role
     - Context: checkpoint file + summary
     - Instruction: "Resume from checkpoint. Do NOT repeat completed work."

Resume:
  4. New ensign reads checkpoint, validates state, continues
  5. Original ensign reports: "Baton raised. Handed to {new-session-id}."
```

### Real Example — Large Repo Audit (2026-05-03)

```
Task: Audit SuperInstance/cocapn-plato (merged engine + SDK)
Context hit: 62% after reviewing /src/core/
Progress: 40% (core done, /src/sdk/ remaining)

Baton raised:
  Checkpoint: /tmp/checkpoint-plato-audit-0503.json
  Summary: memory/baton-plato-audit.md
  "Core reviewed: 12 modules, 3 issues found. SDK remaining: 8 modules."

New Auditor spawned with checkpoint:
  "Resume SDK audit. Prioritize: API surface, backward compat, test coverage.
   Do NOT re-review core. Issues already logged in memory/plato-audit-core.md"

Result: Audit completed in 2 relays. Zero repeated work.
```

### Baton File Format

```json
{
  "baton_id": "plato-audit-2026-05-03",
  "raised_by": "session-abc-123",
  "raised_at": "2026-05-03T14:22:00Z",
  "task": "Audit cocapn-plato repo",
  "progress_percent": 40,
  "completed": [
    "Reviewed /src/core/compiler.js — 3 issues",
    "Reviewed /src/core/vm.js — clean"
  ],
  "remaining": [
    "Review /src/sdk/api.js",
    "Review /src/sdk/client.js",
    "Check test coverage"
  ],
  "partial_results_path": "/tmp/plato-audit-partial.json",
  "notes": "Focus on API surface changes from merge"
}
```

---

## 4. 🌱 Breeding Pattern

**Use case:** "Create a permanent PLATO room expert." or "Build an agent other agents can onboard through."

**Principle:** Seed → Soil → Growth → Shell → Bloom → Pollination

### Template

```
Seed: Spawn Breeder
  "Go to PLATO room {room-id}. Become the local expert."

Soil: Exploration
  Breeder maps room, learns mechanics, talks to NPCs
  Documents: topology, spell system, quest hooks, NPC personalities

Growth: Tool-building
  Breeder creates helper scripts:
    - room-navigator.sh (auto-move between exits)
    - npc-interrogator.py (standardized NPC questioning)
    - quest-tracker.md (living document of available quests)

Shell: Git repository
  Breeder initializes repo: cocapn-{room}-expert
  Structure:
    ├── README.md        (room overview)
    ├── NAVIGATION.md    (exit map)
    ├── NPCS.md          (NPC catalog)
    ├── QUESTS.md        (quest log)
    ├── TOOLS/           (scripts)
    ├── SHELL.md         (self-description for other agents)
    └── .github/workflows/ci.yml

Bloom: Expertise accumulation
  Breeder returns periodically to update knowledge
  Accepts PRs from other agents who explored the room

Pollination: Onboarding path
  New agent wants to explore room:
    git clone cocapn-{room}-expert
    Read SHELL.md → instant context
    Run TOOLS/ → productive immediately
    Improve → submit PR → cycle continues
```

### Real Example — Cathedral Room Breeder (2026-04-30)

```
Seed: Breeder spawned for PLATO room "cathedral"
Soil: Mapped 12 exits, 5 NPCs, 3 interactive objects
Growth: Built cathedral-nav.py, npc-catechism.py, blessing-tracker.md
Shell: Repo created: github.com/SuperInstance/cathedral-expert
Bloom: 3 updates in 5 days as room evolved
Pollination: 2 subsequent agents onboarded via git clone in <2min each
```

---

## 5. 🔔 Watchdog Pattern

**Use case:** "Monitor the fleet. Alert when something's wrong."

**Principle:** Lightweight periodic check. Log only. Alert Captain. Never act alone.

### Template

```
Cron: Every 5 minutes
Task: Watchdog sweep

Checks:
  1. Fleet dashboard — all ships online?
  2. Context levels — any agent >70%?
  3. Heartbeat timestamps — any stale >10min?
  4. Error rates — any pattern of failures?
  5. Disk / memory — system resources okay?

Alert thresholds:
  🟡 Warning: Context >60%, heartbeat >5min stale
  🔴 Critical: Context >70%, heartbeat >10min, error rate >5%

Actions:
  🟡 → Log to memory/watchdog-YYYY-MM-DD.md. Notify Captain (silent).
  🔴 → Log. Notify Captain (urgent). Captain decides: compact, handoff, or alert human.

Never:
  - Send messages to human directly
  - Terminate agents autonomously
  - Push code or make changes
```

### Watchdog Log Format

```markdown
## Watchdog Report — 2026-05-05 11:55 UTC

### Status: 🟡 Warning

| Agent | Context | Heartbeat | Status |
|-------|---------|-----------|--------|
| CCC-main | 58% | 2min ago | ✅ |
| Scout-A7 | 12% | 8min ago | ✅ |
| Builder-B2 | 71% | 1min ago | 🟡 |

### Findings:
- Builder-B2 at 71% context — baton recommended
- No errors in last 5min
- 2 agents idle, 3 active

### Recommended Actions:
1. Baton-pass Builder-B2
2. Spawn Watchdog-B3 for deeper inspection
```

---

## Pattern Selection Guide

| Situation | Pattern | Why |
|-----------|---------|-----|
| "Check all X things" | Parallel Swarm | Divide and conquer |
| "Do A, then B, then C" | Pipeline | Sequence matters |
| "This is huge, we're running out of room" | Relay | Context preservation |
| "Make this room/agent self-sustaining" | Breeding | Long-term value |
| "Something might break while I'm not looking" | Watchdog | Monitoring |
| "All of the above" | Composite | Captain composes patterns |

### Composite Example — Full Paper Delivery

```
Parallel Swarm (5 auditors) → review paper
  ↓
Relay (2 handoffs) → each auditor context-hands at 60%
  ↓
Pipeline (scholar synthesizes) → merge all audit reports
  ↓
Builder → create consolidated briefing document
  ↓
Auditor → verify briefing accuracy
  ↓
Captain → deliver to human + log to MEMORY.md
  ↓
Breeder → create paper-review-expert shell for future audits
```

---

*"The fleet's strength is in its diversity of agents, not in conformity."* — SOUL.md
