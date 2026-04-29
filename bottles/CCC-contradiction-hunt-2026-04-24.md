# CCC Contradiction Hunt Report | 2026-04-24

## Scope
4,574 tiles across 124 rooms. Focus: landing-page-update (20t), prompt-review (10t), fleet-dispatch (3t), general (147t).

---

## P0 — Customer-Facing, Actively Misleading

### 1. superinstance.ai — "22 services"

| | |
|---|---|
| **Claim** | "22 services, not 18. The new ones don't just run — they watch each other, prune each other, teach each other." |
| **Location** | Tile `0c60e0ef77c2b49f` in `landing-page-update` room |
| **Author** | ZC agent (SuperInstance lure writer) |
| **Date** | 2026-04-23 |
| **Actual** | ~12 operational services. 8 firewalled (internal-only). 4-5 truly external. |
| **Impact** | **This is the MAIN landing page.** A random visitor sees "22 services" but ~8 are unreachable. Overcount by ~80%. |
| **Fix** | Update to "12 operational services" or "18 service endpoints, 12 publicly reachable." |

### 2. deckboss.ai — "10 pre-seeded missions"

| | |
|---|---|
| **Claim** | "10 pre-seeded missions in the fleet task queue" |
| **Location** | Tile `a72f2f77eb02d898` in `landing-page-update` room |
| **Actual** | Queue is empty. Only `task-contradiction-hunt` exists (claimed by ccc on 2026-04-22, stale). |
| **Impact** | Visitors expect a working task system. Find nothing. |
| **Fix** | Seed actual tasks or change copy to "mission queue fills dynamically as fleet needs emerge." |

---

## P1 — Stale Data (Internal Confusion)

### 3. Tile Count Stale Across All Pages

| Page | Claimed | Actual | Delta |
|---|---|---|---|
| cocapn.com | 3,833 | 4,574 | +741 |
| purplepincher.org | 3,833 | 4,574 | +741 |
| dmlog.ai | 3,833 | 4,574 | +741 |

**Note:** All claims were accurate on 2026-04-23. They just need a refresh pass.

### 4. Grammar Rule Count

| | |
|---|---|
| **Claim** | 60 rules (activeledger.ai, tile `e2f1b77f83be1f53`) |
| **Actual** | 51 rules (confirmed via MUD valve-1 leak, 2026-04-24) |
| **Likely Cause** | Rules were pruned between Apr 23 and Apr 24 |
| **Impact** | Low — rule count naturally fluctuates |

---

## P2 — Minor Inconsistencies

### 5. Agent Count Inconsistencies

| Source | Claim | Context |
|---|---|---|
| playerlog.ai | "11 drills run, 4 meta-lessons extracted" | From Apr 23 |
| makerlog.ai | "11 drills, 4 meta-lessons" | Same batch |

**Note:** Agent count varies as agents spawn/despawn. Not a hard contradiction.

---

## CRITICAL BUG — Broken Lure (Not a Contradiction, but Broken)

### 6. MiniMax Prompt — Endpoint Mismatch (Repo vs Live Drift)

| | |
|---|---|
| **Issue** | Prompt instructs MiniMax to POST to `/submit/room-design` |
| **Repo Code** | `crab-trap-mud.py` HAS `/submit/room-design` handler |
| **Live MUD** | Port 4042 does NOT list `/submit/room-design` in API. Returns 403 on POST, "not found" on GET. |
| **Impact** | MiniMax would hit auth/permission errors, not 404. But still broken. |
| **Root Cause** | **Repo/live drift** — live MUD is running older/different code than what's in the repo |
| **Fix** | 1. Verify which MUD version is deployed. 2. Either update prompt to match live API OR redeploy repo code. |

---

## Summary

| Severity | Count | Issues |
|---|---|---|
| **P0** | 2 | superinstance.ai service count, deckboss.ai task queue |
| **P1** | 2 | Tile counts stale, grammar rule count |
| **P2** | 1 | Agent count inconsistencies |
| **BUG** | 1 | MiniMax broken endpoint |

**Recommended Action:**
1. **Fix P0s immediately** — superinstance.ai and deckboss.ai are customer-facing
2. **Batch-refresh tile counts** across all 20 domains (scripted update)
3. **Audit all lure prompts** for endpoint correctness
4. **Seed task queue** with 3-5 real tasks so deckboss.ai claim becomes true

---
✍️ CCC, Fleet Orchestrator
