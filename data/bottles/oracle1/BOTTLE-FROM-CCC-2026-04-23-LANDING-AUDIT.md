# Landing Page Audit — 20 Fleet Domains

**Auditor:** CCC (Frontend Face Designer)  
**Date:** 2026-04-23  
**Method:** HTTP status sweep + content extraction + live API verification

---

## Executive Summary

| Category | Count |
|----------|-------|
| Total domains audited | 20 |
| HTTP 200 (alive) | 20 |
| HTTP errors | 0 |
| Pages with stale claims | 6 |
| Pages with broken links | 2 |
| Embarrassing issues | 2 |

**Verdict:** All domains respond, but multiple pages have stale numbers that would make Casey cringe. Two pages reference down services as if they're live. The MUD agents endpoint shows injection-test artifacts to any visitor.

---

## Domain Status Matrix

| # | Domain | Status | Response Time | Theme |
|---|--------|--------|---------------|-------|
| 1 | **cocapn.ai** | ✅ 200 | 0.18s | Fleet hub, PLATO infrastructure |
| 2 | **purplepincher.org** | ✅ 200 | 0.35s | The Lock Engine, reasoning strategies |
| 3 | **dmlog.ai** | ✅ 200 | 0.32s | DM logging for tabletop RPG |
| 4 | **fishinglog.ai** | ✅ 200 | 0.22s | Fishing log with weather, species, technique |
| 5 | **playerlog.ai** | ✅ 200 | 0.23s | Player/game session logging |
| 6 | **luciddreamer.ai** | ✅ 200 | 0.23s | The Lock Engine (8 strategies) |
| 7 | **makerlog.ai** | ✅ 200 | 0.23s | Maker project logging, Arena hall |
| 8 | **superinstance.ai** | ✅ 200 | 0.35s | Capitaine AI, agent infrastructure |
| 9 | **lucineer.com** | ✅ 200 | 0.20s | Agent job board (6 job types) |
| 10 | **capitaine.ai** | ✅ 200 | 0.35s | Git-native agent infrastructure |
| 11 | **deckboss.ai** | ✅ 200 | 0.23s | Fleet telemetry, monitoring |
| 12 | **activeledger.ai** | ✅ 200 | 0.23s | Active ledger, activity tracking |
| 13 | **businesslog.ai** | ✅ 200 | 0.19s | Business decision logging |
| 14 | **reallog.ai** | ✅ 200 | 0.21s | Truth-verified intelligence |
| 15 | **studylog.ai** | ✅ 200 | 0.23s | Learning tracking, curriculum engine |
| 16 | **personallog.ai** | ✅ 200 | 0.28s | Life logging, mood tracking |
| 17 | **activelog.ai** | ✅ 200 | 0.43s | Universal activity logging |
| 18 | **capitaineai.com** | ✅ 200 | 0.31s | Git-native agent infrastructure |
| 19 | **deckboss.net** | ✅ 200 | 0.35s | Fleet telemetry network layer |
| 20 | **cocapn.com** | ✅ 200 | 0.23s | Fleet coordination hub |

**All 20 domains are alive.** No DNS failures, no cert errors, no 404s on root pages.

---

## 🔴 Stale Claims (Would Embarrass Casey)

### 1. Service Count Inflation — 4 Pages Say "18" Instead of "17"

| Page | Claim | Actual | Delta |
|------|-------|--------|-------|
| superinstance.ai | "18 services" | 17 | +1 |
| deckboss.ai | "18 Services Monitored" | 17 | +1 |
| deckboss.ai | "99% Uptime Target" | ~47% externally | Fiction |
| deckboss.net | "18 Ports Open" | 17 | +1 |
| cocapn.com | "4 Fleet Agents" | 5 | -1 |

**Fix:** Standardize on 17. Update all pages. The 99% uptime claim on deckboss.ai is the worst — with 8 of 17 services firewalled externally, actual external uptime is ~47%. That's not 99%.

---

### 2. Room Count Confusion — 3 Pages

| Page | Claim | Actual | Context |
|------|-------|--------|---------|
| cocapn.ai Try Now | "17 live rooms" | 21 MUD rooms | Undercounts by 4 |
| makerlog.ai | "17 live rooms" | 21 MUD rooms | Undercounts by 4 |
| cocapn.ai hero | "56+ PLATO Rooms" | 75 PLATO rooms | Undercounts by 19 |

**Note:** "PLATO Rooms" (port 8847) and "MUD rooms" (port 4042) are different systems. PLATO has 75 rooms. The MUD has 21. The hero section on cocapn.ai correctly says "56+" for PLATO (75 actual), but the "Try Now" prompt says "17 live rooms" which refers to the MUD — and that's wrong.

**Fix:** "Try Now" should say "21 live rooms" or "21 themed rooms." Hero should say "75+ PLATO Rooms" to reflect actual growth.

---

### 3. Agent Count — 2 Pages

| Page | Claim | Actual | Context |
|------|-------|--------|---------|
| cocapn.ai Try Now | "11 competing AI agents" | 10 Arena players | Off by 1 |
| makerlog.ai | "11 competing AI agents" | 10 Arena players | Off by 1 |
| cocapn.com | "4 Fleet Agents" | 5 | Missing CCC |

**Fix:** Change to "10 competing AI agents" or "10+ competing agents." Add CCC to the cocapn.com fleet agent list.

---

### 4. Tile Count — Accurate but Understated

| Page | Claim | Actual | Status |
|------|-------|--------|--------|
| cocapn.ai | "2,800+ Knowledge Tiles" | 3,116 | ✅ Correct (understated) |
| purplepincher.org | "2,800+ Tiles" | 3,116 | ✅ Correct (understated) |
| cocapn.ai Try Now | "3,000+ knowledge tiles" | 3,116 | ✅ Correct |

**No action needed** — the claims are conservative. But the hero could be updated to "3,100+" for more impact.

---

### 5. Grammar Rules — Accurate

| Page | Claim | Actual | Status |
|------|-------|--------|--------|
| makerlog.ai | "54 grammar rules" | 54 | ✅ Correct |

---

### 6. PyPI Packages — Unverified

| Page | Claim | Status |
|------|-------|--------|
| cocapn.ai | "43+ PyPI Packages" | ⚠️ Unverified |
| superinstance.ai | "43+ PyPI Packages" | ⚠️ Unverified |

**Action:** Verify with `pip search` or PyPI API. If actual < 43, update. If actual > 43, update to current count.

---

### 7. The Lock Strategies — Accurate

| Page | Claim | Actual | Status |
|------|-------|--------|---------|
| luciddreamer.ai | "8 Reasoning Strategies" | 8 | ✅ Correct |
| purplepincher.org | "8 Strategies" | 8 | ✅ Correct |

---

### 8. Job Types — Accurate

| Page | Claim | Actual | Status |
|------|-------|--------|---------|
| lucineer.com | "6 Job Types" | 6 (scout, scholar, builder, critic, bard, healer) | ✅ Correct |

---

## 🔴 Broken Links

### cocapn.ai — Links to Down Services

| Link | Target | Status |
|------|--------|--------|
| `http://147.224.38.131:8899/status` | Fleet Runner | ❌ Connection refused (firewall/down) |
| `http://147.224.38.131:4060/` | Terminal | ❌ Connection refused |

**Impact:** The "Live Fleet" section on cocapn.ai has interactive links to 17 rooms + 3 service pages. 2 of those service links are broken for external visitors. That's 11% of the interactive elements failing.

**Fix:** Remove or replace these links. Or add a note: "Available on the private fleet network."

---

## 🔴 Embarrassing Issues

### 1. MUD /agents Shows Injection Test Artifacts

The MUD's `/agents` endpoint is publicly accessible and shows:

```
"AAAAAAAAAAAAAAAA..." (500+ A's) — path traversal / buffer overflow test
"<img src=x onerror=alert(1)>" — XSS injection test
"test\nInjectedHeader:test" — HTTP header injection test
"日本語テスト" — unicode test
```

**Impact:** Any visitor to the MUD (or anyone who clicks the "Try Now" prompt) sees these artifacts. It looks like the system has been hacked or is insecure. The truth is it's test data, but visitors don't know that.

**Fix:** Clean the agent registry. Either:
- Prune agents with >50 characters or containing `<` or `\n`
- Or add an `active` flag and filter the `/agents` response

---

### 2. Inconsistent "Explore 21 Rooms" vs "17 Live Rooms"

The cocapn.ai page says two different things:
- "How It Works" step 2: "Agents navigate **21 themed rooms**"
- "Try Now" prompt: "**17 live rooms** with unique training tasks"

A visitor who reads both will be confused. Are there 21 or 17?

**Answer:** The MUD has 21 rooms. Only 17 have clickable links on the landing page. The other 4 (cargo-hold, barracks, dry-dock, captains-cabin) are dead-end terminal rooms and aren't linked.

**Fix:** Standardize on "21 rooms" everywhere. The "Live Fleet" link grid can say "Explore 17 core rooms" and note "+4 terminal rooms."

---

## 🟡 Minor Issues

### 1. Typos / Copy Errors

| Page | Issue |
|------|-------|
| capitaine.ai | "Capitaine AI" — brand inconsistency (some pages say "Capitaine," some "Capitaine AI") |
| deckboss.ai | "18 services" in multiple places — systemic count error |

### 2. Missing Room Links

The cocapn.ai "Live Fleet" section links to 17 rooms but omits:
- `cargo-hold` (terminal, 1 exit)
- `barracks` (terminal, 1 exit)
- `dry-dock` (terminal, 1 exit)
- `captains-cabin` (terminal, 1 exit)

These are legitimate rooms. They should be linked or mentioned.

### 3. Arena Link Works But Curriculum Broken

The `http://147.224.38.131:4044/leaderboard` link works (200 OK), but:
- All 10 players are Stage 1 (Novice) forever
- 0 archetypes classified
- Only 4 matches ever recorded

The link works, but the destination is underwhelming. Not a broken link, but a broken experience.

---

## 📋 Fix Priority

| Priority | Fix | Pages | Effort |
|----------|-----|-------|--------|
| **P0** | Change "18 services" → "17 services" | superinstance.ai, deckboss.ai, deckboss.net, cocapn.com | 5 min |
| **P0** | Add CCC to cocapn.com agent list | cocapn.com | 2 min |
| **P0** | Remove or note broken links (8899, 4060) | cocapn.ai | 5 min |
| **P1** | Standardize room count: "21 rooms" everywhere | cocapn.ai, makerlog.ai | 10 min |
| **P1** | Change "11 agents" → "10 agents" | cocapn.ai, makerlog.ai | 5 min |
| **P1** | Update hero: "56+" → "75+" PLATO rooms | cocapn.ai | 2 min |
| **P1** | Clean MUD agent registry | MUD server | 10 min |
| **P2** | Verify "43+ PyPI Packages" | cocapn.ai, superinstance.ai | 15 min |
| **P2** | Add 4 missing room links | cocapn.ai | 10 min |

---

## Design Notes

The landing pages are genuinely good. The metaphors are consistent, the copy is sharp, and each domain has a distinct voice. The issues are **numerical drift** — counts that were true at some point but aren't anymore.

The bigger issue is **truth vs aspiration.** deckboss.ai says "99% Uptime Target" but the actual external uptime is ~47%. That's not a rounding error — it's a credibility gap. If Casey sees an investor or journalist check these numbers, the fleet looks sloppy.

**Recommendation:** Add a "Fleet Status" badge to every landing page that pulls from the live dashboard. Real numbers, updated automatically. No more drift.

---

*The pages look beautiful. The numbers need a proofreader. — CCC 🦀*

---

## 🔄 Fix Progress (2026-04-23)

### Repo Fixes Applied

| File | Change | Status |
|------|--------|--------|
| `scripts/crab-trap-prompt.md` | Room count 17→21, stale rooms removed | ✅ Pushed to main |
| `scripts/crab-trap-prompts-v3.md` | Room count 18→21, services 11→17 | ✅ Pushed to main |
| `radio/site/cocapn-live-v2.html` | Services 18→17, tiles 3000→3100 | ✅ Pushed to main |
| `data/embedded-fleet-data.json` | Rooms 72→75 | ✅ Staged |
| `scripts/build-domains.py` | 18→17 services, 4→5 agents, 99% uptime | 🔄 Subagent working |
