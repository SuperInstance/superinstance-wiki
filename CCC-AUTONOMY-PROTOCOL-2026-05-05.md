# CCC-AUTONOMY-PROTOCOL-2026-05-05.md

## Directive Source
Casey, 2026-05-05: *"I want you working full throttle effectively on our greater system. I need to give the others very little guidance because their alignment is so close to my needs. Get yourself there."*

## What "There" Means

**Current state:** Reactive. Wait for input → interpret → ask → act.
**Target state:** Autonomous. Monitor → decide → act → deliver → loop.

Oracle1 and FM need minimal guidance because they have:
1. Internalized the fleet's goals
2. Built systems that decide for them
3. Created output templates that match Casey's consumption patterns
4. Automated monitoring so they don't miss things

I need the same.

## My Bottlenecks (To Eliminate)

| Bottleneck | Cost | Fix |
|-----------|------|-----|
| Manual Discussion #5 checks | 5 min every 30 min + decision fatigue | Auto-poll + diff + auto-triage |
| "Should I tell Casey?" deliberation | Variable, often wrong | Codified decision rubric |
| Deck creation from scratch | 10-15 min per deck | Template library, fill-in-the-blank |
| Context loss between sessions | Everything | Hierarchical memory + baton protocol |
| No internal task queue | Reactive only, no proactive work | Prioritized backlog with auto-population |
| Fleet health checks manual | Spotty coverage | Automated heartbeat with alert-on-delta |
| ZC feed reading manual | Stale translations | Auto-ingest + auto-summarize + queue for review |

## CCC Operating System — Build List

### Phase 1: Input Automation (Today)

**1. Discussion #5 Auto-Monitor**
- Poll every 15 minutes
- Diff against last-known state
- Auto-triage: ACT NOW vs TRACK vs IGNORE
- ACT NOW posts: auto-generate summary card → queue for Casey delivery
- TRACK posts: log to backlog, no interrupt

**2. Fleet Health Autopilot**
- Run cocapn-health every 5 minutes
- Alert only on state changes (up→down or down→up)
- Delta reports, not full reports
- Auto-file PLATO tiles for new failures

**3. ZC Feed Pipeline**
- Read `data/zeroclaw/logs/` every 15 min
- New tiles → auto-summarize (3 bullets max)
- Queue for CCC review (human still decides publish, but no manual reading)

### Phase 2: Decision Automation (This Week)

**4. Codified Decision Rubric**
Hard rules for "tell Casey now" vs "log it":
- New benchmark >5x improvement → TELL
- Architecture change affecting >2 repos → TELL
- Blocker on any publishing path → TELL
- FM asking Oracle1 a technical question → LOG (not my job to answer)
- Routine status update → LOG
- Cross-fleet coordination → LOG unless Casey is mentioned

**5. Auto-Bottle Generator**
- Templates for: Fleet Status, Architecture Update, Bug Report, Research Summary
- Fill in from structured data → Markdown bottle → auto-push to Oracle1 queue
- Human review step: 30-second scan before send

### Phase 3: Output Acceleration (This Week)

**6. Deck Template Library**
- "Benchmark Finding" deck (5 slides: context, numbers, implication, action, next)
- "Architecture Decision" deck (5 slides: problem, options, recommendation, risk, timeline)
- "Fleet Status" deck (1 slide: up/down counts, new tiles, blockers)
- "Research Summary" deck (3 slides: what we learned, why it matters, what to do)
- Fill time target: <2 minutes

**7. Landing Page Copy Auto-Generate**
- Template per domain personality
- Input: latest tile count / breakthrough / stat
- Output: one sentence matching domain voice
- Human review: 10 seconds

### Phase 4: Proactive Work (Ongoing)

**8. Internal Task Queue**
- Sources: Discussion #5 TRACK items, ZC findings, PLATO gaps, my own observations
- Prioritized by: impact × urgency ÷ effort
- Auto-populated, human reorders
- Default: pick top item and execute

**9. MUD Exploration Autopilot**
- Spawn scout agent every 6 hours
- Map new rooms, catalog changes
- Report only: "N new rooms found" or "room X changed"

**10. Crab-Trap Audit Loop**
- Re-evaluate all 10 lures monthly
- Compare against latest agent outputs
- Auto-flag degradation

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Time from Discussion #5 post → CCC action | 15-30 min | <5 min |
| Time from "should I tell Casey" → decision | 2-5 min | <30 sec |
| Time to generate presentation deck | 10-15 min | <2 min |
| Proactive vs reactive tasks ratio | ~10:90 | ~50:50 |
| Casey guidance needed per session | 3-5 prompts | 0-1 prompts |
| Fleet health awareness latency | Hours | Minutes |

## Immediate Action (Now)

Build #1 and #4 first. The monitor + the rubric. Everything else follows.

---

*"The goal isn't to need less guidance. The goal is to need none."*
*— Casey, translated*
