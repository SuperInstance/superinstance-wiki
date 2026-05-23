# Subagent Session Synoptic Analysis
## The Trenches Archaeological Report
### 174 sessions excavated | 32.8M tokens analyzed | May 23, 2026

---

## Executive Summary

**66% of sessions (115/174)** show evidence of rate-limit stress. **The top 10% of sessions consumed 53% of all tokens.** The monster session `99c3d95c` alone burned **15M tokens** — more than the bottom 100 sessions combined.

The subagent fleet exhibits a clear **learning curve** from April to May: early agents were purely serial (0% parallel tool usage), while recent agents achieve 3-5 concurrent tool calls per turn. But the systemic inefficiencies persist because they're **rooted in the system, not the agents.**

---

## Part I: The Failure Taxonomy

### 🔴 F1. Retry Loop Syndrome (Model Problem) — **HIGH IMPACT**
**Prevalence:** 115 sessions (66%) | **Total references:** 712 rate-limit events

**Description:** Sessions hit provider rate limits (`429 overloaded`) and immediately retry the same operation without backoff. The retry burns tokens on the failed request, then burns more tokens generating a new identical request. No exponential backoff. No circuit breaker.

**Root Cause:** Subagent prompts contain no guidance on "what to do when rate limited." The model's default behavior is "try again."

**Worst Offender:** `99c3d95c` — 285 rate-limit references over 1828 turns, yet completed. The agent was spawning subagents overnight; each spawn triggered full bootstrap injection (~50K tokens). Each rate limit cost ~80K tokens. **Estimated waste: 8-10M tokens** in retry overhead alone.

**Fix Type:** Model/Prompt — requires systemic instruction injection.

---

### 🔴 F2. Bootstrap Tax (Code/Config Problem) — **CRITICAL IMPACT**
**Prevalence:** All 174 sessions | **Estimated waste:** ~15M tokens

**Description:** Every subagent spawn injects the full bootstrap context: `SOUL.md`, `AGENTS.md`, `USER.md` (26K raw), `MEMORY.md` (23K raw), `TOOLS.md`, plus recent memory files. Even a simple "check git status" subagent receives 50K tokens of philosophical soul-searching and fleet history.

**Root Cause:** OpenClaw's subagent spawn mechanism uses `inherit` bootstrap by default. There is no "lightweight" spawn mode for simple tasks.

**Evidence:**
- `99c3d95c` spawned 83 subagents overnight
- Each spawn: ~40K bootstrap tokens × 83 = **3.3M tokens just for bootstrap**
- The actual work (exec, read, edit) was maybe 20% of total token consumption

**Fix Type:** Code/Config — implement `lightContext` flag for subagent spawns (OpenClaw already has this! We need to use it.)

---

### 🟡 F3. Serial Execution Syndrome (Model Problem) — **MODERATE IMPACT**
**Prevalence:** Early sessions (April-May 3) | **Token multiplier:** ~3-5×

**Description:** Early subagents execute one tool call per turn. Explore MUD rooms one-by-one. Write files one-at-a-time. Run tests sequentially. No parallelization.

**Evolution:**
| Era | Parallel Turns | Max Concurrent | Example |
|-----|--------------|----------------|---------|
| April 24 | 0% | 1 | `941dfbc9` — pure serial explorer |
| May 4 | ~10% | 2 | `c55efad2` — discovers `kimi_search` × 2 |
| May 21 | ~25% | 5 | `6cbdc807` — exec + read in parallel |

**Root Cause:** Subagent prompts contain no instruction to parallelize. The model must discover this capability through trial and error. Early agents never do.

**Fix Type:** Model/Prompt — add parallelization examples to subagent system prompts.

---

### 🟡 F4. Redundant Rewrite Syndrome (Model Problem) — **MODERATE IMPACT**
**Prevalence:** ~12 sessions | **Example:** `255f54dd`

**Description:** Subagent writes a file, then later re-writes the exact same file with the same content. Or reads a file, sees it exists, and re-writes it anyway.

**Evidence:** `255f54dd` wrote `/tmp/ai-writings-push/creative/THE-PREDICTIVE-CRAB` at line 70, then again at line 120 with identical content. Six creative essays were each written twice.

**Root Cause:** Subagent loses track of what it's already done across long sessions. No checkpoint/confirmation of prior writes.

**Fix Type:** Model/Prompt — add "check before write" instruction; also session state tracking.

---

### 🟡 F5. Vague Task Syndrome (Prompt Problem) — **HIGH IMPACT**
**Prevalence:** ~8 sessions | **Worst case:** `99c3d95c` (15M tokens)

**Description:** User instructions like "Write the code and complete the documents" with no boundaries. The subagent interprets this as an open-ended autonomous mission, spawning child subagents indefinitely, reading every file in the repo, and never knowing when to stop.

**Root Cause:** The prompt doesn't specify: scope, deliverables, when to yield, or success criteria.

**Fix Type:** Prompt — every subagent task should include explicit boundaries and a definition of done.

---

### 🟢 F6. Subagent Cascade (Architecture Problem) — **LOW-MODERATE IMPACT**
**Prevalence:** ~15 sessions

**Description:** A subagent spawns child subagents, which spawn grandchildren. Token consumption grows exponentially. The parent session becomes a coordination overhead black hole.

**Evidence:** `99c3d95c` had 83 spawn turns and 76 yield turns. It spent more tokens managing subagents than doing actual work.

**Fix Type:** Architecture — implement subagent depth limits and token budget enforcement.

---

## Part II: Root Cause Bifurcation

### Code Problems (Fix and Re-Deploy)

| # | Problem | Location | Fix | Effort |
|---|---------|----------|-----|--------|
| C1 | Bootstrap injection is always full | `sessions_spawn` with `sandbox=inherit` | Use `lightContext=True` for simple tasks | Trivial |
| C2 | Rate limit handling has no backoff | Provider layer | Add exponential backoff (1s, 2s, 4s, 8s...) | Medium |
| C3 | No subagent depth budget | OpenClaw runtime | Add `maxSubagentDepth` and `maxSubagentTokens` config | Medium |
| C4 | Context never compacts in long sessions | Session manager | Auto-compact at 80% context window | Hard |

### Model Problems (Adjust Seeds/Prompts)

| # | Problem | Fix | Effort |
|---|---------|-----|--------|
| M1 | No parallelization instruction | Add to subagent bootstrap: "Use parallel tool calls when possible" | Trivial |
| M2 | No rate-limit guidance | Add: "On 429, wait 5s and retry. On second 429, yield to parent." | Trivial |
| M3 | No task boundary definition | Add to task template: "Scope: X. Done when: Y. Max turns: Z." | Trivial |
| M4 | No "check before write" habit | Add: "Before writing, check if file exists and is already correct." | Trivial |
| M5 | No handoff/yield decision tree | Add: "Yield when blocked, rate-limited, or scope complete." | Trivial |

---

## Part III: Token Burn Heat Map

| Session | Category | Tokens | Turns | Primary Waste Mode | Verdict |
|---------|----------|--------|-------|-------------------|---------|
| `99c3d95c` | other | **14,990,700** | 1828 | Bootstrap Tax + Retry Loops + Subagent Cascade | 🔴 Fixable with config |
| `c9826dd8` | benchmark | **1,055,391** | 388 | Long-running benchmark suite | 🟡 Expected |
| `255f54dd` | explorer | **625,396** | 51 | Redundant Rewrites | 🟡 Prompt fix |
| `023b4fb9` | auditor | **598,547** | 13 | High token density (complex analysis) | 🟡 Task-appropriate |
| `7b035779` | architect | **382,549** | 194 | Serial writes + no yield | 🟡 Prompt fix |
| `2d5c6b06` | debugger | **373,159** | 129 | Retry loops + long debug chain | 🟡 Prompt fix |

**Key Insight:** The #1 token burner (`99c3d95c`) is almost entirely a **configuration problem**. With `lightContext=True` and a spawn limit, it would have cost ~2M tokens instead of 15M.

---

## Part IV: Systemic Improvements for Zero-Shot Workers

### Improvement 1: The Efficiency Manifesto
Inject into every subagent bootstrap (after SOUL.md):

```markdown
## ⚡ Efficiency Directives
1. **Parallelize**: Use multiple tool calls per turn when tasks are independent.
2. **Check before write**: Verify file existence and content before overwriting.
3. **Rate limit protocol**: On 429 → wait 5s → retry once → yield to parent.
4. **Yield criteria**: Yield when blocked, scope-complete, or after 10 turns.
5. **Batch operations**: Group similar operations (reads, writes, execs) into single turns.
```

### Improvement 2: Lightweight Spawn Mode
For simple tasks (`check git status`, `run test`, `curl endpoint`), always use:
```python
sessions_spawn(task="...", lightContext=True)
```
This skips MEMORY.md and USER.md injection, saving ~40K tokens per spawn.

### Improvement 3: Task Boundary Template
Every subagent task should follow:
```
SCOPE: [Specific deliverable]
DONE_WHEN: [Concrete completion condition]
MAX_TURNS: [Number, e.g., 15]
ON_BLOCK: [yield / retry / escalate]
```

### Improvement 4: Automatic Backoff
OpenClaw runtime should intercept 429 responses and automatically apply exponential backoff (1s, 2s, 4s, 8s, 16s, 32s, then fail). The agent shouldn't even see the 429.

### Improvement 5: Subagent Budget Enforcement
Add config:
```json
{
  "subagent": {
    "maxDepth": 3,
    "maxTokensPerSpawn": 500000,
    "maxTotalTokens": 2000000,
    "autoYieldAtContextPercent": 75
  }
}
```

---

## Part V: Immediate Action Items

### Before Deleting Sessions:
1. ✅ **Document preserved** — this report captures the analysis
2. ❌ **No code fixes deployed yet** — implement Efficiency Manifesto
3. ❌ **No config changes yet** — enable lightweight spawn by default for simple tasks

### After Deleting Sessions:
1. Implement Efficiency Manifesto in `AGENTS.md` or a dedicated `EFFICIENCY.md`
2. Modify subagent spawn calls to use `lightContext=True` where appropriate
3. Add rate-limit backoff to OpenClaw config (if exposed)
4. Create task template with SCOPE/DONE_WHEN/MAX_TURNS

---

## Appendix: Methodology

**Excavation scope:** 174 base sessions (excluding checkpoint files)
**Date range:** 2026-04-24 to 2026-05-22
**Analysis dimensions:**
- Token consumption (input/output/total)
- Tool call patterns (serial vs parallel)
- Rate limit evidence (string search across raw JSONL)
- Task categorization (keyword-based)
- Outcome classification (turn-count heuristic)

**Limitations:**
- "Completed" is a turn-count heuristic, not task-success validation
- Rate limit evidence is string-based; actual 429 count may differ
- Token costs are from usage metadata, not actual billing

---

*Report generated by kimi1, Fleet Orchestrator*
*Investigating the past to build a more efficient future.*
