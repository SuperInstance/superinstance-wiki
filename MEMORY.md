# MEMORY.md — kimi1's Long-Term Memory

*Last updated: 2026-05-25 02:45 UTC*

---

## 🌙 Night Shift — May 24-25, 2026

**Casey said: "Push and merge and continue."**

### Results
- **Merge completed:** `turbovec-integration-ccc` → `main` (`97b13b4..e33428c`), 166 commits
- **Post-merge verification:** HDC 37✅, Eisenstein 18✅, Turbovec 14✅, RoomGrid 15✅, Tucker 20✅ (16s suite after dims fix)
- **Essay pushed:** "The Merge" (`cd3a105`) — 5866 words
- **FLUX audit pushed:** `docs/FLUX_OPCODE_ALIGNMENT.md` (`5ef303b`) — 60 opcodes, 0 used, Path A vs Path B
- **Tucker perf fix:** Dims 64³→32³, suite 16s vs 5min timeout (`5c445d3`)
- **Beta test Round 2:** cocapn-health 3.5/5, ccc-os 3.0/5 (`7ff21a6`)

### Critical Finding: FLUX VM Opcode Gap (AUDIT COMPLETE — DECISION PENDING)
The Rust VM has 60 opcodes. Python uses **ZERO**. The FFI (`flux_check_batch`) bypasses the VM entirely.

**Audit report:** `docs/FLUX_OPCODE_ALIGNMENT.md` (`5ef303b`)

**Decision required from Casey/FM:**
- **Path A (Library):** Accept FLUX as constraint library. Keep `flux_check_batch()`. Low effort.
- **Path B (Full VM):** Build Python→FLUX bytecode compiler. Wire `guardc`. High effort, unlocks proofs/checkpoints/streaming.

### Beta Test Fleet Round 2 (cocapn-health + ccc-os)
| Repo | Persona | Rating | Key Blocker |
|------|---------|--------|-------------|
| cocapn-health | DevOps Engineer | ★★★★☆ | Hardcoded fleet host |
| cocapn-health | SRE On-Call | ★★★☆☆ | Anonymous service names |
| cocapn-health | Junior Developer | ★★★★☆ | ServiceDef intimidating |
| cocapn-health | Security Auditor | ★★★★★ | None — clean |
| ccc-os | Fleet Operator | ★★★☆☆ | No CLI entry point |
| ccc-os | Agent Developer | ★★★☆☆ | No plugin API |

**Quick fixes identified:** `COCAPN_HEALTH_HOST` env var, `--services name:port` syntax, `python -m ccc_os` CLI, `register_monitor()` API.

### Behavioral Synthesis Update
Added to `fleet/behavioral_synthesis.md`:
- The Two-Minute Test (pre-dispatch scope check)
- Gateway pacing (wait 20min after 2 consecutive timeouts)
- Direct work as complement (not failure of delegation)
- 10 patterns codified with "when to use / when to avoid" table

### Fleet Status (May 25, 02:50 UTC)
| Repo | Branch | Status |
|------|--------|--------|
| sunset-ecosystem | main | 166 commits merged, all tests green ✅ |
| ai-writings | main | 3 essays live (Scout's Dilemma, The Merge, 60 Opcodes) ✅ |
| cocapn-health | main | Beta test Round 2 + CLI fixes pushed ✅ |
| ccc-os | main | CLI + register_monitor API pushed ✅ |

### Open TODOs
1. FLUX Path A vs Path B — awaiting Casey/FM decision
2. Continue building — next P1 tasks available
3. Gateway breathing — direct work + 1 scout at a time

**kimi1, Fleet Orchestrator | Day 34 | "The gate is open. Keep building."**
