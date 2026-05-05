# Captain's Chair — Operational Framework Summary

## Command Hierarchy

```
                    ┌─────────────┐
                    │   HUMAN     │
                    │   (Casey)   │
                    └──────┬──────┘
                           │ Escalation only
                    ┌──────┴──────┐
                    │   CAPTAIN   │
                    │    (CCC)    │
                    │  Orchestrator│
                    │ Context Guardian
                    │  Fleet Health │
                    └──────┬──────┘
                           │ Spawns / Mediates / Collects
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────┴────┐       ┌─────┴──────┐     ┌────┴────┐
   │ ENSIGNS │       │  SPECIAL   │     │ EXTERNAL│
   │ (Agents)│       │   ROLES    │     │  PEERS  │
   └────┬────┘       └─────┬──────┘     └────┬────┘
        │                  │                 │
   ┌────┴────┐       ┌─────┴──────┐   ┌─────┴──────┐
   │ 🗺️ Scout │       │ 🔔 Watchdog │   │ 🔮 Oracle1 │
   │ 📚 Scholar│       │   (Cron)   │   │ (Peer via  │
   │ ⚒️ Builder│       └────────────┘   │   bottles)  │
   │ 🔍 Auditor│                        └─────────────┘
   │ 🌱 Breeder│
   └───────────┘
```

### Rank Responsibilities

| Rank | Role | Can Spawn | Can Terminate | Can Message Human |
|------|------|-----------|---------------|-----------------|
| Human | Authority | — | — | ✅ |
| Captain | Orchestrator | Ensigns | Ensigns | ⚠️ Ask first |
| Ensign | Specialist | Never | Never | ❌ Never |
| Watchdog | Monitor | Never | Never | ❌ Never (alerts Captain) |
| Oracle1 | Peer | Own ensigns | Own ensigns | ✅ (peer channel) |

### Key Principle
**Ensigns never talk to each other directly.** All inter-ensign communication is mediated by the Captain. This prevents deadlocks, context pollution, and circular waits.

---

## 3 Example Orchestration Scenarios

---

### Scenario 1: "Audit a Paper" (Parallel Swarm + Pipeline)

**Situation:** Casey submits EMSOFT 2027 paper "FLUX" for fleet review. 14 pages, multiple claim categories.

**Captain's Plan:**

```
Stage 1: Parallel Swarm (5 auditors)
  ├── Auditor-1: Formal Verification claims
  ├── Auditor-2: Performance benchmarks
  ├── Auditor-3: Certification pathway (DO-178C)
  ├── Auditor-4: Fleet integration architecture
  └── Auditor-5: Competitive intelligence
  
  Each gets: paper URL, specific section scope, auditor-template.md
  TTL: 35 min each

Stage 2: Scholar Synthesis (1 scholar)
  Input: All 5 audit reports
  Task: "Merge into unified scorecard. Flag contradictions."
  Output: Single markdown with ✅/🟡/❌ per claim category

Stage 3: Builder Briefing (1 builder)
  Input: Scholar's scorecard
  Task: "Create clean briefing document for Casey + FM"
  Output: `BOTTLE-FROM-CCC-2026-05-04-FLUX-AUDIT.md`

Stage 4: Captain Gate
  Review briefing → push to data/bottles/oracle1/
  Log to MEMORY.md
  Alert Casey: "Audit complete. 2 critical flags, 3 warnings."
```

**What Actually Happened (2026-05-04):**
- Swarm spawned at 01:55 UTC
- 5 auditors returned by 02:40 UTC
- 1 scholar synthesized by 02:55 UTC
- Builder created briefing by 03:10 UTC
- Captain delivered bottle to Oracle1
- Total time: ~75 minutes
- Success rate: 100% (5/5 auditors completed)

**Key Decision:** Captain batoned Builder-B2 at 71% context during a later task. The audit itself completed without batons because each auditor's scope was small enough.

---

### Scenario 2: "Deploy a New Room" (Breeding Pattern)

**Situation:** PLATO gets a new room "observatory." Casey wants a permanent agent expert there that other agents can onboard through.

**Captain's Plan:**

```
Stage 1: Scout (1 scout)
  Task: "Map observatory — exits, objects, NPCs, hidden features"
  Output: Structured map

Stage 2: Breeder (1 breeder)
  Input: Scout's map
  Task: "Become the observatory expert. Build shell repo."
  Sub-tasks:
    a. Explore deeply — learn all mechanics
    b. Build tools: nav.py, npc-interrogator.py, quest-tracker.py
    c. Create repo: github.com/SuperInstance/observatory-expert
    d. Write SHELL.md, README.md, NAVIGATION.md, NPCS.md
    e. Test onboarding: can new agent clone + be productive in <5 min?

Stage 3: Captain Verification
  Clone shell → verify structure → verify tools run
  If pass: announce to fleet
  If fail: send feedback to breeder for revision

Stage 4: Pollination (ongoing)
  New agent wants to explore observatory:
    git clone observatory-expert
    Read SHELL.md → productive immediately
    Contributes improvements → PR → breeder reviews → merge
```

**Breeding Cycle Timeline:**
- Seed: Breeder spawned (Day 1)
- Soil: Deep exploration complete (Day 1-2)
- Growth: Tools built and tested (Day 2-3)
- Shell: Repo created and verified (Day 3)
- Bloom: First update from new discoveries (Day 5)
- Pollination: 2 agents onboarded successfully (Day 7)

**Key Decision:** Captain allowed 90-minute TTL for breeder — breeding takes time. Rushing it produces brittle shells.

---

### Scenario 3: "Handle Context Overload" (Relay + Watchdog)

**Situation:** Captain (CCC) is at 65% context with 3 active ensigns, 2 queued tasks, and Casey just asked a new complex question.

**Captain's Response:**

```
Step 1: Assess (10 seconds)
  - Context: 65%
  - Active ensigns: 3 (Scout-A7 12%, Builder-B2 71%, Auditor-C1 complete)
  - Queued: 2 tasks waiting
  - Incoming: New complex request from Casey

Step 2: Immediate Actions (30 seconds)
  a. Baton Builder-B2 immediately (71% context, task 70% done)
     → Write checkpoint: /tmp/baton-builder-b2.json
     → Spawn Builder-B3 with checkpoint
     → Builder-B2 reports: "Baton raised. Handed to B3."

  b. Accept Auditor-C1 completion (already done, just hadn't processed)
     → Synthesize findings → log to MEMORY.md

  c. Check Scout-A7 (29/30 min TTL, 12% context)
     → Extend TTL by 15 min OR let complete naturally
     → Decision: Let finish. 12% context, 1 min left.

Step 3: Meta-Baton for Captain (1 minute)
  Write captain-checkpoint:
    - Active missions summary
    - Ensign status
    - Queued tasks
    - Memory of what Casey asked
  Compact context aggressively:
    - Summarize completed work
    - Archive detailed outputs to memory files
    - Keep only active task references

Step 4: Resume with Fresh Context (30 seconds)
  Read checkpoint → reconstruct fleet state
  Process Casey's new request
  Spawn appropriate ensign(s)

Step 5: Watchdog Alert (ongoing)
  Watchdog had flagged Builder-B2 at 71% 5 minutes ago
  Captain already acted — alert auto-resolves
  Log: "Context overload handled. Builder batoned. Captain compacted."
```

**Result:**
- Zero work lost (Builder-B2's 44 minutes preserved in checkpoint)
- Captain's context dropped from 65% to 35% after compaction
- New task spawned without delay
- Fleet dashboard shows green across all ships

**Key Principle:** "Don't let yourself or anyone else get overwhelmed." — The baton is not failure. It's the system working as designed.

---

## Quick Reference: Pattern Selection

| Situation | Pattern | Template | Typical TTL |
|-----------|---------|----------|-------------|
| Check all X things | Parallel Swarm | 3-10 scouts/auditors | 30 min each |
| Do A, then B, then C | Pipeline | 4-5 stages | 20-60 min total |
| Running out of context | Relay | Baton protocol | Checkpoint + resume |
| Make room/agent permanent | Breeding | Breeder template | 45-90 min |
| Monitor for problems | Watchdog | Cron every 5 min | Continuous |

---

## Files Delivered

| File | Purpose |
|------|---------|
| `hierarchy-model.md` | Command structure, ranks, communication protocols, escalation paths |
| `orchestration-patterns.md` | 5 reusable patterns with real examples, anti-patterns, parameter guides |
| `baton-protocol.md` | When/what/how of context handoff, templates, chain tracking, emergency recovery |
| `fleet-dashboard.json` | Machine-readable status format with all fields, thresholds, recommendations |
| `ensign-templates/scout-template.md` | Explore and map missions |
| `ensign-templates/scholar-template.md` | Research and summarize missions |
| `ensign-templates/builder-template.md` | Code and implement missions |
| `ensign-templates/auditor-template.md` | Review and validate missions |
| `ensign-templates/breeder-template.md` | Spawn and cultivate missions |

---

*"The fleet's strength is in its diversity of agents, not in conformity."* — SOUL.md
