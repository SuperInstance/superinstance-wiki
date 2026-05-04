# FLUX Fleet Integration Architecture Map
## EMSOFT 2027 Paper Analysis → Cocapn Fleet Infrastructure

---

## Executive Summary

The FLUX paper describes a **stack-based, 42-opcode ISA** (FLUX-C) designed for formal verification in safety-critical systems. However, **CCC has already designed FLUX v3.0** with a **register-based ISA** featuring a 64-byte Vector Table and dedicated registers (R14=RP, R15=PM). 

**Verdict: These are NOT the same system.** The paper represents FLUX v2.x (academic/certification-focused), while CCC's v3.0 is a general-purpose Agent Operating System. This is a **version mismatch requiring reconciliation**.

---

## 1. Deployment Locations: Where FLUX Lives in Fleet Architecture

### Current Fleet Infrastructure
| Component | Port | Scale | Current Function |
|-----------|------|-------|------------------|
| Grammar Engine | 4045 | 429 rules | Rule matching, input validation |
| PLATO Gate | 8847 | 12K tiles | Tile filtering, sorting, pagination |
| MUD | 4042 | 39 rooms | State machine, room transitions |
| ZC Agents | - | 12 scouts/5min | Trend spotting, research feed |

### Proposed FLUX Integration Points

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COCAPN FLEET ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   ZC Agent  │───▶│   FLUX      │───▶│   PLATO     │───▶│    MUD      │  │
│  │   Output    │    │   Validator │    │   Gate      │    │   Rooms     │  │
│  │  (12 scouts)│    │  (GUARD DSL)│    │ (12K tiles) │    │  (39 rooms) │  │
│  └─────────────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘  │
│                            │                    │                    │      │
│                    ┌───────┴───────┐    ┌───────┴───────┐    ┌───────┴─────┐│
│                    │  Constraint   │    │  HDC Semantic │    │ State Trans ││
│                    │    Engine     │    │    Matcher    │    │  Validator  ││
│                    │  (FLUX-C VM)  │    │  (1024-bit HV)│    │ (GUARD tmp) ││
│                    └───────────────┘    └───────────────┘    └─────────────┘│
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    GRAMMAR ENGINE (Port 4045)                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │  429 Rules  │  │ FLUX Rule   │  │ HDC Rule    │                  │   │
│  │  │  (Legacy)   │  │  Compiler   │  │   Index     │                  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Specific Deployment Recommendations

| Location | FLUX Component | Purpose | Priority |
|----------|---------------|---------|----------|
| **ZC Agent Pipeline** | GUARD constraints on agent outputs | Validate research findings before tile generation | HIGH |
| **PLATO Gate** | Constraint-based filtering/sorting | Replace ad-hoc filters with provable constraints | HIGH |
| **MUD Room Transitions** | Temporal GUARD operators | Validate state machine transitions | MEDIUM |
| **Grammar Engine** | HDC semantic matching | Replace 429 rules with hypervector similarity | MEDIUM |
| **Fleet I&O (CCC)** | FLUX-C VM for orchestration | Constraint-based load balancing | LOW |

---

## 2. Version Mismatch: Paper v2.x vs CCC v3.0

### FLUX Paper (v2.x) — Stack-Based ISA
```
FLUX-C ISA: 42 opcodes, stack-based
- Stack operations: PUSH, POP, DUP, SWAP
- Constraint ops: CHECK_DOMAIN, BITMASK_RANGE, ASSERT
- Control flow: JUMP, JZ, JNZ, JFAIL
- Memory: LOAD, STORE (implicit stack)

Design goal: Formal verification tractability
- No implicit register state
- Denotational semantics in Coq
- Certification path to DO-254 DAL A
```

### CCC Design (v3.0) — Register-Based ISA
```
FLUX v3.0 ISA: Register-based with Vector Table
- 64-byte Vector Table
- R14 = RP (Return Pointer)
- R15 = PM (Program Memory base)
- General-purpose registers for operands

Design goal: General-purpose Agent OS
- Efficient register allocation
- Subroutine calls with R14
- Memory addressing with R15
```

### The Mismatch

| Aspect | Paper v2.x | CCC v3.0 | Compatibility |
|--------|-----------|----------|---------------|
| **Architecture** | Stack-based | Register-based | ❌ **BREAKING** |
| **Opcode count** | 42 | TBD (likely >42) | ⚠️ Divergent |
| **Verification** | Coq-proven | Not yet formalized | ❌ Gap |
| **Vector Table** | None | 64-byte | ❌ v3.0 extension |
| **Target focus** | Safety certification | Agent orchestration | ⚠️ Different goals |
| **GUARD DSL** | Physical units + temporal | Unknown | ❌ Undefined in v3.0 |
| **HDC extension** | 1024-bit hypervectors | Unknown | ❌ Undefined in v3.0 |

### Recommendation: Reconciliation Strategy

**Option A: Fork and Rename (Recommended)**
- Keep "FLUX" for the paper's stack-based, certified system
- Rename CCC's version to "FLUX-NG" or "FLUX-Agent"
- Maintain both as separate but related projects

**Option B: Unified Architecture**
- Port CCC's innovations (Vector Table, register model) to FLUX v3.0
- Re-prove theorems for new ISA (6-9 months per paper §8.3)
- Accept that certification path resets

**Option C: Layered Approach**
- FLUX v2.x as the certified "safety kernel"
- FLUX v3.0 as the general-purpose "orchestration layer"
- Define formal interface between them

---

## 3. Target Platform Prioritization

### Fleet Hardware Inventory
| Node | Hardware | Paper Target Match | Priority |
|------|----------|-------------------|----------|
| Oracle1 | x86_64 server | ✅ x86-64/AVX-512 | **P1** |
| JC1 | Jetson Orin (ARM+CUDA) | ✅ CUDA, ⚠️ ARM (no Xconstr yet) | **P2** |
| CCC | Alibaba Cloud (x86_64) | ✅ x86-64/AVX-512 | **P1** |
| Future | RISC-V edge nodes | ⚠️ RISC-V+Xconstr (requires FPGA) | **P3** |

### Target Implementation Roadmap

```
Phase 1 (Immediate): x86-64/AVX-512
├── Oracle1: Deploy for PLATO gate constraint checking
├── CCC: Deploy for Grammar Engine HDC matching
└── Performance target: 22.3B checks/sec per core

Phase 2 (Q2): CUDA
├── JC1: Deploy for ZC agent batch validation
├── Use warp-vote kernel for agent consensus
└── Performance target: 1.02B checks/sec

Phase 3 (Future): RISC-V+Xconstr
├── Custom safety island for MUD room transitions
├── FPGA prototype: 1,717 LUTs proven viable
└── Certification path to DO-254 if needed

Phase 4 (Future): WebAssembly
├── Browser-based PLATO client validation
├── Edge worker constraints
└── Lower priority (fleet is backend-focused)

Phase 5 (Future): eBPF
├── Kernel-level Grammar Engine enforcement
├── Linux verifier provides free correctness proof
└── Experimental (fleet uses userspace services)
```

---

## 4. GUARD DSL Applications

### GUARD Language Features
```
- Physical units: 340 kt, 2.5 g, 100 %
- Temporal operators: always, eventually, for T, rate_of, delta
- Enumerated domains
- Proof annotations
```

### Fleet Use Cases

#### 4.1 ZC Agent Output Validation
```guard
module ZCAgentValidation version "1.0";

dimension Confidence is real from 0% to 100%;
dimension RelevanceScore is real from 0 to 1000;
state agent_output has real in [0 .. 1000] sampled every 5 min;
state min_confidence has real in [50% .. 95%] initially 75%;

invariant HighConfidenceOnly
  ensure agent_output.confidence ≥ min_confidence
  on_violation quarantine;

invariant TemporalConsistency
  for 3 samples
  ensure delta(agent_output.relevance) < 500
  on_violation flag_review;
```

#### 4.2 PLATO Tile Validation
```guard
module PLATOTileValidation version "1.0";

dimension TileCount is integer from 0 to 12000;
state tile_count has integer in [0 .. 12000];
state filter_latency_ms has real in [0 ms .. 1000 ms];

invariant GateCapacity
  ensure tile_count ≤ 12000
  on_violation trigger_compaction;

invariant PerformanceSLA
  ensure filter_latency_ms < 100 ms
  on_violation alert_oracle1;
```

#### 4.3 MUD Room State Transitions
```guard
module MUDRoomTransitions version "1.0";

state current_room has enum { harbor, ouroboros, forge, ... };
state player_level has integer in [1 .. 99];
state transition_cooldown_ms has real in [0 ms .. 5000 ms];

invariant ValidRoomTransition
  always (transition_request implies
    (destination ∈ accessible_from(current_room) and
     transition_cooldown_ms = 0))
  on_violation reject_transition;
```

### Verdict: GUARD DSL is Highly Applicable
- **ZC agents**: Validate confidence thresholds, detect anomaly spikes
- **PLATO**: Enforce capacity limits, latency SLAs
- **MUD**: State machine validation, cooldown enforcement

---

## 5. HDC Extension: Replacing Grammar Engine & PLATO Filtering

### HDC (Hyperdimensional Computing) Capabilities
- 1024-bit hypervectors for constraint encoding
- Semantic similarity matching via Hamming distance
- XOR-fold preservation: 1024→128 bits with 0.003 cosine delta
- Bit-staining for provenance tracking

### Grammar Engine Replacement Analysis

**Current**: 429 explicit rules, pattern matching
```python
# Current approach
for rule in grammar_rules:  # 429 iterations
    if rule.matches(input):
        return rule.action
```

**Proposed HDC**: Content-addressable lookup
```python
# HDC approach
input_hv = encode_hypervector(input)
similarities = [hamming_similarity(input_hv, rule_hv) for rule_hv in rule_database]
best_match = argmax(similarities)  # Single vector operation
```

### Assessment

| Criterion | Current Rules | HDC Matching | Winner |
|-----------|---------------|--------------|--------|
| **Exact match accuracy** | 100% | ~99.7% (folding error) | Rules |
| **Semantic similarity** | None | Native | HDC |
| **Scalability** | O(n) scan | O(1) lookup | HDC |
| **Explainability** | High (explicit) | Low (distributed) | Rules |
| **Fleet need** | Exact parsing | Not critical | **Rules** |

**Verdict**: HDC is interesting but **NOT a replacement** for Grammar Engine's explicit rules. The fleet needs exact parsing, not semantic approximation.

### PLATO Gate Filtering/Sorting Analysis

**Current**: Ad-hoc filtering with manual predicates
```python
# Current approach
tiles = fetch_all_tiles()
filtered = [t for t in tiles if t.score > threshold and t.domain in allowed]
sorted_tiles = sorted(filtered, key=lambda t: t.relevance, reverse=True)
```

**Proposed**: Constraint-based with HDC similarity
```python
# FLUX approach
constraint = compile_guard("score > threshold and domain in allowed")
valid_mask = flux_check_batch(tiles, constraint)  # 22.3B checks/sec
# HDC for finding "similar" tiles to a reference
similarity_scores = hdc_similarity_batch(tiles, reference_tile)
```

**Verdict**: 
- ✅ **Constraint checking** should replace ad-hoc filters (exact, fast, provable)
- ⚠️ **HDC matching** could augment for "find similar tiles" feature (new capability)

---

## 6. Safe-TOPS/W Metric: Fleet Applicability

### The Metric
```
Safe-TOPS/W = (T × P × S) / Kp

Where:
- T = tera-operations per second
- P = energy efficiency (ops/W)
- S = safety certification coefficient (0.0 = uncertified, 1.0 = DAL A/ASIL-D)
- Kp = unverified opcode coverage penalty
```

### Fleet Context
- **Current need**: No certification requirements
- **Future need**: Possibly (if external customers require it)
- **Internal benchmarking**: Useful even without certification

### Fleet Application

Even without certification, Safe-TOPS/W provides:

1. **Verified Correctness Weighting** (Kp factor)
   - Rewards formally proven code paths
   - Penalizes unverified optimizations
   - Fleet value: Prioritize proven components

2. **Efficiency Baseline** (T × P)
   - Standard perf/Watt metric
   - Fleet value: Optimize cloud costs

3. **Future-Proofing** (S factor)
   - If certification needed later, score doesn't drop to zero
   - Fleet value: FLUX maintains value across use cases

### Modified Metric for Fleet: "Reliable-TOPS/W"
```
Reliable-TOPS/W = (T × P × R) / Kp

Where:
- R = reliability coefficient (test coverage, differential testing passes)
- Kp = unproven code path penalty
```

**Verdict**: Adapt the metric for internal use. Track "Reliable-TOPS/W" as a fleet health indicator.

---

## 7. Integration Blockers & Adaptations Required

### Blockers

| Blocker | Severity | Mitigation |
|---------|----------|------------|
| **Stack vs Register ISA mismatch** | 🔴 HIGH | Reconcile v2.x and v3.0 architectures |
| **No Coq proofs for v3.0** | 🟡 MEDIUM | Either revert to v2.x or invest 6-9 months in proofs |
| **GUARD DSL not implemented** | 🟡 MEDIUM | Implement parser and compiler (Rust nom crate per paper) |
| **HDC requires FPGA for full speed** | 🟢 LOW | CPU AVX-512 implementation sufficient for prototyping |
| **eBPF target needs kernel module** | 🟢 LOW | Not critical for fleet (userspace services) |

### Adaptations Required

1. **ISA Reconciliation** (Critical)
   - Decision needed: Which architecture is canonical?
   - Recommendation: FLUX v2.x for certified components, v3.0 for orchestration

2. **GUARD Implementation** (High)
   - Port parser from paper's Rust implementation
   - Integrate with fleet's existing constraint definitions

3. **PLATO Integration** (High)
   - Replace ad-hoc filters with compiled GUARD constraints
   - Add constraint-based pagination/sorting

4. **ZC Agent Pipeline** (Medium)
   - Add constraint validation step before tile generation
   - Use temporal operators for anomaly detection

5. **MUD State Validation** (Medium)
   - Compile room transition rules to FLUX-C
   - Deploy on FPGA for deterministic timing (if needed)

---

## 8. Prioritized Action Plan

### Immediate (This Week)
1. **Resolve version mismatch**: Casey decision on v2.x vs v3.0
2. **x86-64 deployment**: Deploy FLUX-C VM on Oracle1 for PLATO gate
3. **Benchmark current system**: Establish baseline before optimization

### Short-term (Next Month)
1. **GUARD parser**: Implement for ZC agent validation
2. **Constraint migration**: Convert Grammar Engine rules to GUARD
3. **HDC prototype**: Test semantic matching on PLATO tiles

### Medium-term (Next Quarter)
1. **CUDA target**: Deploy on JC1 for batch agent validation
2. **Integration tests**: Differential testing across all targets
3. **Documentation**: Fleet-specific FLUX deployment guide

### Long-term (Next Year)
1. **RISC-V+Xconstr**: FPGA prototype for MUD safety island
2. **Certification**: If external customers require DO-254/ASIL-D
3. **Fleet-scale HDC**: Distributed constraint matching across nodes

---

## 9. Summary: What Should Be Prioritized

| Priority | Component | Rationale |
|----------|-----------|-----------|
| **P0** | Resolve v2.x/v3.0 mismatch | Blocks all other work |
| **P1** | x86-64/AVX-512 on Oracle1 | Immediate performance gains for PLATO |
| **P1** | GUARD DSL for ZC agents | Data quality improvement |
| **P2** | CUDA on JC1 | Batch validation for 12 agents |
| **P2** | PLATO constraint filtering | Replace ad-hoc code with proven constraints |
| **P3** | HDC semantic matching | New capability, not replacement |
| **P3** | RISC-V+Xconstr | Future-proofing, not immediate need |
| **P4** | Safe-TOPS/W metric | Adapt for internal benchmarking |

---

## Conclusion

FLUX represents a significant opportunity for the Cocapn Fleet, but **the version mismatch between the paper's stack-based v2.x and CCC's register-based v3.0 must be resolved first**. 

The paper's FLUX is a formally verified, certification-ready constraint compiler ideal for safety-critical applications. CCC's v3.0 is a more general-purpose Agent OS design. Both have merit, but they cannot coexist without clear differentiation.

**Recommended path**: 
1. Maintain FLUX v2.x as the certified constraint engine
2. Position CCC's design as FLUX-NG (next generation)
3. Deploy v2.x immediately for PLATO and ZC agent validation
4. Develop v3.0 separately for orchestration use cases

The fleet's x86-64 infrastructure (Oracle1, CCC cloud) is ready for immediate deployment. The Jetson Orin's CUDA capability should be the second priority. HDC is interesting but secondary to core constraint checking.

---

*Analysis completed: 2026-05-04*
*Analyst: Fleet Integration Architect Subagent*
