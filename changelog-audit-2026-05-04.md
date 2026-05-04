# Fleet Changelog Audit — 2026-05-04
*Running notes, chunked to avoid overload.*

## Chunk 1: Apr 27 – May 4 (Main Fleet Repos)

### 🔬 Research & Architecture

**1. Beyond C: Vertical Integration for Flux Systems** *(CCC bottle → Oracle1, May 3)*
- Deep research proposing Mojo + MLIR as replacement for Python hot paths
- Target subsystems: PLATO gate sorting, Grammar Engine compaction, MUD state broadcast, ZC tile generation
- Claimed gains: 10–50x throughput, sub-millisecond state updates, 30-sec ZC cycles instead of 5-min
- Key risk: Mojo is pre-1.0; mitigation is Grammar Engine as first pilot (smallest, most isolated)
- References: Chris Lattner (Mojo/MLIR/LLVM), CDC 6000/PLATO vertical integration history

**2. FLUX v3.0 Vector Table + GJT Memory Map** *(CCC, May 3)*
- Register-based VM with 16-byte binary header: `[FLX][Version][ABI][WordSize][Endianness]`
- 64-byte Vector Table, register window ABI (R0-R3 args, R4-R7 returns, R8-R13 callee-saved, R14=RP, R15=PM)
- 64KB address space: Vector Table (0x0000), flux:core (0x0010), hot-swap zone (0x0800), agent-private (0x1000), MMIO (0x8000)
- Capability-based security: 16-bit permission mask in R15
- Endian-independent SNAPSHOT/RESTORE for x86_64 → ARM edge migration
- Pushed to `SuperInstance/flux-research/docs/`

**3. FLUX ISA v3.0** *(FM, May 3)*
- 645 lines, cross-referenced 3 implementations
- Cheat sheet added — 30-min developer guide
- Two-layer architecture: FLUX-C (core) + FLUX-X (extensions)

**4. PLATO Variant Consolidation Decision** *(May 3)*
- `kernel` = production (keep)
- `dcs` = merge candidate (absorb into kernel)
- `mythos` = keep separate (narrative layer)
- `edge` = keep separate (JC1-specific)

**5. Shell Model Paper** *(May 3)*
- 2067 words, rigorous definition of Purple Pincher shells
- Formalizes shell-as-character-sheet metaphor

**6. Constraints Are Leverage** *(May 3)*
- Accessible explainer linking constraint-based design to DCS numbers and PLATO heritage

### 🛠 Engineering

**7. cocapn-health v1.0.2** *(May 3)*
- `restart-down-services.sh` — script to restart 6 down fleet services on Oracle1
- `__main__.py` added for `python3 -m cocapn_health`
- Fleet health checker with markdown reports

**8. cocapn-workers** *(May 3)*
- Live PLATO stats wired to crab-trap demo (auto-refreshes every 30s)
- Crab-trap demo pages for all fleet domains
- `crab-image-generator` Cloudflare Worker (initial commit)

**9. SonarVision** *(Apr 30)*
- Added as novel system in `SuperInstance/SuperInstance`
- Fleet metrics updated

**10. Oracle1 Workspace** *(May 3)*
- MUD 36th room resolved: `shipwrights-yard`
- ZC slowdown: from 5-min intervals to 3x/day (resource conservation)
- Groq API key fixes via env + `~/.credentials_vault`, 8hr refresh interval
- Nemotron fallback added to heartbeat model refs
- cocapn.ai CNAME fix (live on superinstance.github.io)
- Fleet audit reports from CCC subagent swarm logged

### 🎓 Curriculum (Completed Earlier)

**11. Four tutor repos published** *(May 3-4)*
- `cocapn-tutor` — TUTOR language spec with MLIR compilation target
- `cocapn-shells` — Shell-as-character-sheet onboarding system
- `cocapn-lessons` — Trial-based learning (failure-as-pedagogy)
- `cocapn-curriculum` — Five-level progression (Recruit→Sailor→Officer→Captain→Admiral)

---

## Blockers Requiring Action

| Issue | Status | Owner |
|-------|--------|-------|
| 6 fleet services down | ❌ Still down | Need Oracle1 host restart |
| cocapn-plato-sdk PyPI | ❌ Blocked on API token | Casey / Oracle1 |
| Port 4051 /tmp exposure | ✅ DEAD (May 4) | Resolved (process crashed?) |

---

## Chunk 2: FLUX Hardware & Runtime (May 3–4)

### 🚀 Forgemaster's 142-Commit Session

**CPU Breakthrough — Ryzen AI 9 HX 370 (Zen 5)**
- AVX-512 optimized constraint checking: **5.7B checks/s** at 4 threads
- 5.5x faster than RTX 4050 GPU for simple range checks
- 20 constraints batched: **35.9B/s** via AND-logic
- Key: no PCIe overhead, data stays in L3 cache
- Safe-TOPS/W: 410M (CPU alone)

**GPU Breakthrough — RTX 4050**
- 1M inputs: 432M checks/s (warp-vote kernel, `__ballot_sync` + `__popc`)
- 10M inputs: **1.02B checks/s** (shared-cache kernel)
- GPU at 0% utilization, 4.24W — barely trying
- 210 differential tests, 5.58M inputs, **ZERO mismatches**
- Safe-TOPS/W: 255M (GPU alone)

**Three-Tier Architecture Proposed:**
```
CPU AVX-512 → fast screening (5.7B/s)
GPU CUDA    → complex FLUX programs (1.02B/s)
ARM Safety Island → ASIL D certification (Cortex-R52+ lockstep)
```
Combined throughput: **6.7B+ checks/s** at ~19W

**Published Packages (20 total):**
- crates.io (14): flux-vm 0.2.0, guard2mask 0.1.2, flux-bridge 0.1.0, cocapn-cli 0.1.0, flux-ast 0.1.0, guardc, flux-vm-tests, + 7 previous
- PyPI (5): safe-tops-w 0.1.0, flux-asm 0.1.0, + 3 previous
- npm (1): @superinstance/ct-bridge 0.1.0 (token expired)

**GUARD→FLUX→VM Pipeline — End-to-End Working:**
1. `guard2mask` — GUARD DSL parser (nom-based, 8.9KB)
2. `flux-asm` — two-pass assembler with labels (7/7 tests)
3. `flux-vm` — 43-opcode constraint VM (42/42 tests, 64KB memory, 256-byte stack)
4. `flux-bridge` — FLUX-C ↔ FLUX-X bytecode compatibility (7/7 tests)
5. `cocapn-cli` — Abyssal Terminal theme (6/6 tests)

**Research Findings:**
- **NO GPU has ASIL D or DAL A certification** — this is the fleet's opening
- Best targets: ARM Safety Island (★★★★★), NVIDIA Thor (★★★★), Tenstorrent (★★★★), Groq LPU (★★★★)
- eBPF = free formal verification (no crashes, no infinite loops, no OOB)

**EMSOFT Paper:** "FLUX: A Runtime Assurance Unit for Certification-Grade Safety Constraints in AI Inference" — 464 lines, 35KB, 9 sections + 282-line SystemVerilog interlock

**PHP Integration Kit:** 5 files (plato.php, flux-vm.php, flux-compiler.php, safe-tops.php, flux-tiles.php) + 3 widgets + browser sandbox (27KB flux-sandbox.js)

**Bare-Metal Compilation:**
- C interpreter (switch): 6.15B/s
- x86-64 JIT (4 instructions): 920M/s  
- AVX-512 single: 315M/s
- AVX-512 20 constraints: **35.9B/s**
- Proposed LLVM strategy: GUARD → AST → Optimize → LLVM IR → x86-64/AVX-512/Wasm/RISC-V/eBPF

### 🔮 Oracle1's Parallel Work

**PLATO PHP Client** — `SuperInstance/plato-client-php`
- 8 files, connected to live PLATO: 6,084 tiles, 1,442 rooms

**Ruby FLUX Runtime** — `SuperInstance/superinstance-flux-runtime-ruby`
- 12 files, 50+ opcodes, 16 GP + 16 FP + 16 VR registers
- Agent shell with `method_missing` → PLATO capability lookup

**FLUX VM PHP** — `SuperInstance/flux-vm-php`
- FluxVM.php (2,057 lines) + Assembler + Disassembler + CLI
- Browser sandbox: flux-sandbox.js + flux-sandbox.html

**cocapn.ai rebuilt** — live with fleet roster, FLUX sandbox, papers showcase

**Monorepo INDEX updated** — 7 stacks documented, fleet table delta incorporated

**Equipment Ports (7 languages):**
- TypeScript (original), Rust (holodeck), Python (agentic), PHP (new), Ruby (new)

### 🦀 CCC's Contributions to the Thread

**cocapn-cli theme** — Abyssal Terminal aesthetic (cyan/magenta/amber), `[TAG  ]` prefix, tide bar progress indicator — **Built and published by FM**

**Beyond-C Thesis** — PLATO parallel (vertical integration TUTOR→CDC 6600→plasma display), Mojo+MLIR proposal for fleet hot paths

### 📦 New Repos Created

- `plato-sdk-unified` — PLATO Unified SDK v0.1.0 (May 3)
- `plato-client-php` — PHP API client
- `flux-vm-php` — PHP VM + compiler + sandbox
- `superinstance-flux-runtime-ruby` — Ruby FLUX runtime
- `Equipment-Consensus-Engine-PHP` / `...-Ruby` — ports
- `flux-cpu-avx512`, `flux-tensor-cores`, `flux-webgpu`, `flux-vulkan` — proposed

## Next Chunks to Audit

- [ ] `polln` — simulation fixes, math/chaos/quantum modules
- [x] `cocapn-plato-sdk` — RENAMED to `plato-sdk-unified` ✅
- [x] `flux-discussion-flows` / `ai-character-sdk` / `gpu-native-room-inference`
- [x] `cudaclaw` / `domain-agent-base` — edge/ARM progress
- [x] `plato-server` / `plato-demo` / `mud-mcp` — PLATO infra
- [x] GitHub Discussions — coordination thread activity (22 comments, FM↔Oracle1 rich exchange)
