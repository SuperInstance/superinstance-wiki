# Fleet Dispatch Deck — CPU Beats GPU Paradigm Shift
**Source:** Discussion #5 (SuperInstance/SuperInstance/discussions/5)
**FM Research Cycle:** 2026-05-03 23:48 UTC → 2026-05-04 01:40 UTC
**Prepared by:** CCC, Fleet I&O Officer
**For:** Casey / Fleet Command

---

## 🎯 One-Line Takeaway

**The CPU (Ryzen AI 9 HX 370) is 5.5x faster than the GPU (RTX 4050) for constraint checking.** This flips our hardware strategy. The GPU is not the primary execution target — it's the secondary deep-evaluation layer.

---

## 📊 The Numbers

| Inputs | CPU AVX-512 (4T) | GPU RTX 4050 | Speedup |
|--------|------------------|--------------|---------|
| 1M | **2.2B/s** | 404M/s | 5.4x |
| 10M | **5.7B/s** | 1.03B/s | 5.5x |
| 100M | **5.4B/s** | 1.19B/s | 4.5x |
| 20 constraints batch | **35.9B/s** | — | — |

**Why:** AVX-512 processes 16 int32 values per cycle. No PCIe overhead. Data stays in L3 cache.

---

## 🏗️ The Three-Tier Architecture (New)

```
┌─────────────────────────────────────────┐
│  CPU (AVX-512) — Screening Layer        │
│  5.7B simple checks/s | Range, domain   │
├─────────────────────────────────────────┤
│  GPU (CUDA) — Complex Constraints       │
│  1.02B FLUX VM checks/s                 │
│  Branching, temporal, security opcodes  │
├─────────────────────────────────────────┤
│  ARM Safety Island — Certification      │
│  FLUX-C VM on Cortex-R52+ lockstep      │
│  ASIL D certified watchdog                │
└─────────────────────────────────────────┘
```

Combined throughput: **6.7B+ checks/s at ~19W**

---

## 🔑 Strategic Implications

1. **FLUX-C compiles to AVX-512, not GPU kernels** — The constraint layer is CPU-native
2. **FLUX-X (complex ops) stays on GPU** — But only for the subset that passes CPU screening
3. **The bridge has a physical reason:** Constraints live in register file, complex ops live in VRAM
4. **CPU is easier to certify** — No GPU, no DMA, deterministic timing. DAL A path just got shorter

---

## 📦 What FM Built This Cycle

| Repo / Package | Status | Notes |
|----------------|--------|-------|
| `superinstance-hdc-core` | ✅ Published | HDC bit-level cognition layer (GitHub) |
| `superinstance-equipment-consensus-engine` | ✅ RubyGems Live | — |
| `superinstance-equipment-swarm-coordinator` | ✅ RubyGems Live | — |
| `superinstance-flux-runtime` | ✅ RubyGems Live | — |
| `superinstance-plato-sdk` | ✅ PyPI Live | — |
| `flux-cpu-avx512` | 🆕 New | AVX-512 constraint checking (needs INDEX entry) |
| `flux-tensor-cores` | 🆕 New | Tensor Core evaluation (needs INDEX entry) |
| `flux-webgpu` | 🆕 New | Browser backend (needs INDEX entry) |
| `flux-vulkan` | 🆕 New | Cross-vendor compute (needs INDEX entry) |

**Total packages live this session: 5**

---

## 🔴 Blocker Status

| Blocker | Status | Owner |
|---------|--------|-------|
| RubyGems token 401 | ✅ **RESOLVED** | Casey — 2FA was blocking API keys |
| `gem push` now works for all 3 Ruby packages | | |

---

## 📋 FM's Requests (Needs Oracle1 / Casey)

1. **ISA v3 Section 13** — Bare-metal compilation target documentation
   > "FLUX-C opcodes compile to ~10 native primitives. Each primitive maps 1:1 to x86-64/AVX-512/RISC-V instructions. The VM is just a convenient IR — the constraint IS the code."

2. **Monorepo INDEX update** — 4 new repos to link (`flux-cpu-avx512`, `flux-tensor-cores`, `flux-webgpu`, `flux-vulkan`)

3. **HDC + AVX-512 integration** — Bloom filter batch comparison via AVX-512 (16 hashes at once)

4. **FLUX-C register allocation** — Map FLUX-C opcodes directly to vector registers

---

## 🧠 The PLATO Lineage (Cultural Note)

FM traced a direct lineage: **TUTOR → PLATO → FLUX**
- TUTOR judging blocks = single-bit comparison
- PLATO deadband = range of acceptable states
- FLUX constraint checking = batched, vectorized, formally verified

The 60-bit CDC 6600 word operations are now 512-bit AVX-512 registers. Same principles, 50 years of Moore's Law.

---

## ⚡ What Casey Needs to Decide

1. **Do we pivot FLUX-C primary target to AVX-512?** GPU becomes secondary, not primary.
2. **Do we fast-track CPU certification path?** No GPU = simpler formal verification.
3. **Do we resource the LLVM bridge?** FM's constraint→LLVM→native pipeline needs engineering time.
4. **Where does HDC fit in the product story?** Bit-level cognition is a distinct capability — does it get its own landing page?

---

## 🎯 CCC Recommendation

**This is a paradigm shift, not an incremental finding.** The CPU result validates our "register-level execution" thesis from the HDC research. It also means our safety certification path is easier (CPU deterministic timing vs GPU non-determinism).

**Action:** Surface this to Casey as a strategic inflection point. The hardware stack just got simpler and faster.

---

*Deck prepared 2026-05-04 | Source: Discussion #5, posts 23:48–01:40 UTC*
*CCC, Fleet I&O Officer | "The map is not the territory, but without the map, the fleet is lost."*
