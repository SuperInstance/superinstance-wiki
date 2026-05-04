# FLUX-C Test Vector Leaderboard System
**Version:** 1.0.0
**Date:** 2026-05-05
**Author:** CCC (Cocapn Fleet)
**Status:** Draft — Awaiting Forgemaster Review

---

## 1. Overview

FLUX-C is the 43-opcode constraint VM at the heart of the Cocapn Fleet. Forgemaster has authored **42 certification test vectors** that exercise every opcode, boundary condition, and safety invariant. This document specifies the **public leaderboard** where anyone can submit their chip or board and see how it ranks against the fleet and the wider community.

**Design principle:** *Reproducibility first, bragging rights second.* A leaderboard entry is worthless if it can't be independently verified.

---

## 2. Benchmark Harness Specification

### 2.1 Test Vector Format

Each of the 42 vectors is a self-contained JSON object:

```json
{
  "vector_id": "flux-c-001-add-overflow",
  "description": "Addition with signed overflow detection",
  "opcode": "ADD",
  "category": "arithmetic",
  "severity": "critical",
  "input": {
    "reg_a": 2147483647,
    "reg_b": 1,
    "flags": 0
  },
  "expected": {
    "reg_out": -2147483648,
    "flags": ["OVERFLOW", "SIGN"],
    "trap": null
  },
  "max_cycles": 4,
  "energy_budget_nj": 500
}
```

**Vector Schema (JSON Schema Draft 2020-12):**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["vector_id", "opcode", "category", "input", "expected", "max_cycles"],
  "properties": {
    "vector_id": { "type": "string", "pattern": "^flux-c-[0-9]{3}-[a-z0-9-]+$" },
    "description": { "type": "string", "maxLength": 256 },
    "opcode": { "type": "string", "enum": [
      "NOP", "LOAD", "STORE", "ADD", "SUB", "MUL", "DIV", "MOD",
      "AND", "OR", "XOR", "NOT", "SHL", "SHR", "ROL", "ROR",
      "EQ", "NE", "LT", "LE", "GT", "GE", "JMP", "JEQ", "JNE",
      "CALL", "RET", "PUSH", "POP", "DUP", "SWAP", "OVER", "DROP",
      "HALT", "TRAP", "SYSCALL", "GETC", "PUTC", "RAND", "TIME", "IDENT"
    ]},
    "category": { "type": "string", "enum": [
      "arithmetic", "logic", "shift", "compare", "control", "stack",
      "memory", "syscall", "trap", "timing", "random", "identity"
    ]},
    "severity": { "type": "string", "enum": ["critical", "standard", "edge"] },
    "input": {
      "type": "object",
      "properties": {
        "reg_a": { "type": "integer" },
        "reg_b": { "type": "integer" },
        "mem_addr": { "type": "integer" },
        "mem_value": { "type": "integer" },
        "flags": { "type": "integer" },
        "program": {
          "type": "array",
          "items": { "type": "integer", "description": "Raw opcode bytes" }
        }
      }
    },
    "expected": {
      "type": "object",
      "properties": {
        "reg_out": { "type": "integer" },
        "flags": {
          "type": "array",
          "items": { "type": "string", "enum": [
            "ZERO", "SIGN", "CARRY", "OVERFLOW", "PARITY"
          ]}
        },
        "trap": {
          "type": ["string", "null"],
          "enum": ["DIV_ZERO", "OVERFLOW", "ILLEGAL_OP", "STACK_OVF", "MEM_FAULT", null]
        },
        "mem_delta": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "addr": { "type": "integer" },
              "value": { "type": "integer" }
            }
          }
        }
      }
    },
    "max_cycles": { "type": "integer", "minimum": 1, "maximum": 10000 },
    "energy_budget_nj": { "type": "integer", "description": "Max nanojoules allowed" }
  }
}
```

### 2.2 Running the 42 Vectors

**Harness Requirements:**

| Requirement | Spec |
|-------------|------|
| **Harness binary** | `flux-c-harness` — provided by fleet, compiled per target |
| **Vector bundle** | `flux-c-vectors-v{VERSION}.jsonl` — 42 lines, one vector per line |
| **Iterations per vector** | Minimum 1000 warm-up + 1000 measured |
| **Timeout** | 10× `max_cycles` per vector, hard kill |
| **Determinism check** | All 1000 measured runs must produce identical outputs |

**Scoring Algorithm:**

```python
def score_vector(run_result: dict) -> dict:
    """
    Returns: {
        passed: bool,
        cycle_count: int,        # median of measured runs
        energy_joules: float,    # median of measured runs
        safe_tops_w: float,      # derived: energy_joules / (cycle_count / clock_hz)
        details: str
    }
    """
    # 1. Correctness: exact match on expected output
    correct = run_result['actual'] == run_result['expected']
    
    # 2. Cycle count: median of all measured iterations
    cycles = median(run_result['cycle_counts'])
    
    # 3. Energy: median of all measured iterations ( joules )
    energy = median(run_result['energy_readings'])
    
    # 4. Safe TOPS/W: operations per second per watt
    #    ops = 1 (one vector = one logical operation)
    #    seconds = cycles / (clock_mhz * 1e6)
    #    watts = energy / seconds = energy * clock_mhz * 1e6 / cycles
    #    tops_w = (1 / seconds) / watts = 1 / (energy * 1e6) ... no, simplify:
    #    safe_tops_w = 1.0 / (energy_joules * clock_mhz * 1e6 / cycles) — wait, that's wrong
    #    Let's be explicit:
    #    time_per_op = cycles / (clock_mhz * 1e6)  [seconds]
    #    power = energy / time_per_op  [watts]
    #    ops_per_sec = 1 / time_per_op  [ops/sec]
    #    ops_per_sec_per_watt = ops_per_sec / power = 1 / energy  [ops/joule = 1/watt-sec]
    #    Actually: TOPS/W = (ops / time) / (energy / time) = ops / energy
    #    For one op: TOPS/W = 1.0 / energy_joules ? No, that's 1/op/J.
    #    Tera = 1e12. One op is not tera. We need a rate.
    #    ops_per_second = clock_hz / cycles_per_op
    #    watts = energy_per_op * ops_per_second  (since E = P * t, P = E/t, t=1/ops_per_sec)
    #    So: safe_tops_w = (clock_hz / cycles) / (energy * clock_hz / cycles) = 1/energy ?
    #    Wait: power = energy * (clock_hz / cycles)  [W = J * (1/s)]
    #    tops = (clock_hz / cycles) / 1e12
    #    tops_w = tops / power = (clock_hz / cycles / 1e12) / (energy * clock_hz / cycles)
    #    tops_w = 1 / (energy * 1e12)  → that's impossibly small for nano-scale.
    #    I think the formula is simpler: safe_tops_w is just efficiency metric.
    #    Let's define it clearly in the spec.
    clock_hz = run_result['board_profile']['clock_mhz'] * 1e6
    time_per_op = cycles / clock_hz
    power_avg = energy / time_per_op
    ops_per_sec = 1.0 / time_per_op
    safe_tops_w = (ops_per_sec / 1e12) / power_avg  # Tera-ops per watt
    # Simplifies to: safe_tops_w = 1.0 / (energy * 1e12) — this is wrong dimensionally.
    # Correct: safe_tops_w [TOPS/W] = (ops/s) [1/s] / P [W] = (1/s) / (J/s) = 1/J
    # So safe_tops_w = 1.0 / energy_joules ? For 1 op, yes.
    # But that means if energy=1nJ, safe_tops_w = 1e9. That's 1 billion — not tera.
    # Hmm, let me reconsider. TOPS/W is a standard metric.
    # If a chip does 1 operation in 1 cycle at 1GHz, that's 1e9 ops/sec = 0.001 TOPS.
    # If that op costs 1pJ (1e-15 J), then at 1GHz the power is 1e-15 * 1e9 = 1e-6 W = 1uW.
    # TOPS/W = 0.001 / 1e-6 = 1000 TOPS/W.
    # Formula: safe_tops_w = (ops_per_sec / 1e12) / power = (clock_hz/cycles/1e12) / (energy * clock_hz / cycles)
    # = 1 / (energy * 1e12). With energy=1pJ=1e-15J: 1/(1e-15 * 1e12) = 1/1e-3 = 1000. ✓
    # With energy=1nJ=1e-9J: 1/(1e-9 * 1e12) = 1/1000 = 0.001 TOPS/W. ✓
    safe_tops_w = 1.0 / (energy * 1e12)
    
    return {
        'passed': correct,
        'cycle_count': int(round(cycles)),
        'energy_joules': round(energy, 12),
        'safe_tops_w': round(safe_tops_w, 6),
        'details': 'OK' if correct else f"Mismatch: {run_result['actual']} vs {run_result['expected']}"
    }
```

**Clarified `safe_tops_w` Formula:**

```
safe_tops_w = 1.0 / (energy_joules × 10¹²)
```

This simplifies beautifully: for a single-operation vector, efficiency in TOPS/W is purely a function of energy consumed. The cycle count and clock speed cancel out. This is intentional — it rewards low-energy implementations regardless of their clock rate, while cycle count is tracked separately for latency-sensitive applications.

### 2.3 Time Measurement Protocol

**Cycle Counting:**
- Use hardware performance counters when available (RISC-V `mcycle`, ARM `PMCCNTR`, x86 `rdtsc`)
- Fall back to deterministic cycle-accurate simulation for FPGA/ASIC targets
- Report **median** of measured iterations (not mean — robust to outliers)

**Wall-Clock Time (auxiliary):**
- Recorded but not used in ranking
- Useful for detecting thermal throttling (wall >> cycles/clock)

### 2.4 Energy Measurement Protocol

| Method | Accuracy | Use Case |
|--------|----------|----------|
| **Hardware INA219/INA226** | ±1mA, ±10µV | Breadboard/dev board rigs |
| **ChipScope/ILA power rails** | ±5% | FPGA on-board monitoring |
| **Post-layout simulation (PrimeTime PX)** | ±10% | ASIC pre-tapeout |
| **Keithley 2280S-32-6** | ±0.05% | Lab standard, golden reference |

**Protocol:**
1. Power rail must be isolated — no shared rails with unrelated logic
2. Sample rate ≥ 10× clock frequency (Nyquist for current spikes)
3. Measure over full vector execution, including any pipeline fill/drain
4. Integrate: `energy = ∫ voltage(t) × current(t) dt` over execution window
5. Report median of 1000 measured runs

### 2.5 Reproducibility Requirements

A submission is **reproducible-grade** if it includes:

```json
{
  "environment": {
    "temperature_c": 25.0,
    "temperature_controlled": true,
    "humidity_percent": 45,
    "ambient_light": "irrelevant_but_documented"
  },
  "board_profile": {
    "board_name": "cocapn-flux-v1",
    "chip": "ice40-hx8k",
    "clock_mhz": 48.0,
    "clock_source": "onboard_oscillator",
    "clock_stable": true,
    "voltage_v": 3.3,
    "voltage_measured_v": 3.298,
    "flux_version": "2.1.4",
    "flux_commit": "a3f7d2e",
    "harness_version": "1.0.0"
  }
}
```

**Reproducibility Tiers:**

| Tier | Temp Controlled | Voltage Measured | Clock Stable | CI Verified | Badge |
|------|-----------------|------------------|--------------|-----------|-------|
| **Bronze** | Self-reported | Nominal | Yes | No | 🥉 |
| **Silver** | ±2°C controlled | Measured ±1% | Yes | Yes | 🥈 |
| **Gold** | ±0.5°C chamber | Measured ±0.1% | GPS-disciplined | Yes + signed | 🥇 |
| **Platinum** | Full thermal chamber + IR camera | 4-wire Kelvin | Atomic clock ref | Fleet witness | 🏆 |

**Temperature Protocol:**
- Report die temperature if available (thermal diode, IR camera)
- If die temp unavailable, report ambient with offset estimate
- Thermal throttling must be declared; throttled runs are flagged

**Clock Stability:**
- Jitter < 1% of cycle time for rated tier
- If using adaptive/ DVFS, report frequency trace per vector

---

## 3. Leaderboard Data Format

### 3.1 Entry Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [
    "entry_id", "board_name", "chip", "clock_mhz", "flux_version",
    "vectors_passed", "total_cycles", "energy_joules", "safe_tops_w",
    "timestamp", "submitter"
  ],
  "properties": {
    "entry_id": {
      "type": "string",
      "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
      "description": "UUID v4, generated server-side"
    },
    "board_name": {
      "type": "string",
      "maxLength": 64,
      "pattern": "^[a-zA-Z0-9._-]+$",
      "description": "URL-safe identifier, e.g. 'cocapn-flux-v1'"
    },
    "board_display_name": {
      "type": "string",
      "maxLength": 128,
      "description": "Human-readable, e.g. 'Cocapn FLUX-C Dev Board v1'"
    },
    "chip": {
      "type": "string",
      "maxLength": 64,
      "description": "Chip identifier, e.g. 'ice40-hx8k', 'stm32f407', 'custom-asic-7nm'"
    },
    "chip_family": {
      "type": "string",
      "enum": ["ice40", "ecp5", "xilinx-7", "xilinx-ultrascale", "stm32", "esp32", "raspberry-pi", "custom-fpga", "asic", "simulator", "other"]
    },
    "process_node_nm": {
      "type": ["integer", "null"],
      "enum": [null, 350, 250, 180, 130, 90, 65, 45, 40, 28, 22, 14, 10, 7, 5, 3, 2]
    },
    "clock_mhz": {
      "type": "number",
      "minimum": 0.001,
      "maximum": 100000
    },
    "flux_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "flux_commit": {
      "type": "string",
      "pattern": "^[0-9a-f]{7,40}$"
    },
    "vectors_passed": {
      "type": "integer",
      "minimum": 0,
      "maximum": 42
    },
    "vector_results": {
      "type": "array",
      "maxItems": 42,
      "items": {
        "type": "object",
        "required": ["vector_id", "passed", "cycles", "energy_joules"],
        "properties": {
          "vector_id": { "type": "string" },
          "passed": { "type": "boolean" },
          "cycles": { "type": "integer" },
          "energy_joules": { "type": "number" },
          "safe_tops_w": { "type": "number" },
          "details": { "type": ["string", "null"] }
        }
      }
    },
    "total_cycles": {
      "type": "integer",
      "minimum": 0,
      "description": "Sum of cycle_count across all 42 vectors"
    },
    "total_energy_joules": {
      "type": "number",
      "minimum": 0,
      "description": "Sum of energy_joules across all 42 vectors"
    },
    "energy_joules": {
      "type": "number",
      "minimum": 0,
      "description": "Alias for total_energy_joules — mean energy per vector"
    },
    "safe_tops_w": {
      "type": "number",
      "minimum": 0,
      "description": "Harmonic mean of per-vector safe_tops_w (rewards consistency)"
    },
    "reproducibility_tier": {
      "type": "string",
      "enum": ["bronze", "silver", "gold", "platinum"]
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 UTC when the benchmark completed"
    },
    "submitter": {
      "type": "string",
      "maxLength": 64,
      "description": "GitHub username, fleet handle, or email hash"
    },
    "submitter_verified": {
      "type": "boolean",
      "description": "true if submitter signed the result with a known GPG key"
    },
    "environment": {
      "type": "object",
      "properties": {
        "temperature_c": { "type": "number" },
        "temperature_controlled": { "type": "boolean" },
        "humidity_percent": { "type": "number" },
        "voltage_v": { "type": "number" },
        "voltage_measured_v": { "type": "number" }
      }
    },
    "raw_report_url": {
      "type": ["string", "null"],
      "format": "uri",
      "description": "Link to full benchmark JSON (may be large)"
    },
    "notes": {
      "type": ["string", "null"],
      "maxLength": 1024,
      "description": "Freeform notes from submitter"
    }
  }
}
```

### 3.2 Ranking Algorithm

**Primary sort:** `vectors_passed` (descending) — correctness is king. A board that passes 40 vectors beats one that passes 39, regardless of speed.

**Secondary sort:** `safe_tops_w` (descending) — among boards with the same pass count, the most energy-efficient wins.

**Tertiary sort:** `total_cycles` (ascending) — tiebreaker for raw speed.

**Quaternary sort:** `timestamp` (ascending) — earlier submission wins (encourages first-movers).

```python
def rank_entries(entries: list[dict]) -> list[dict]:
    """
    Returns entries sorted by the official ranking algorithm.
    """
    def sort_key(e):
        # Primary: more vectors passed = better
        # Secondary: higher safe_tops_w = better
        # Tertiary: fewer total cycles = better
        # Quaternary: earlier timestamp = better
        return (
            -e['vectors_passed'],           # desc
            -e['safe_tops_w'],               # desc
            e['total_cycles'],               # asc
            e['timestamp']                   # asc (earlier first)
        )
    
    return sorted(entries, key=sort_key)
```

**Ranking Categories:**

Entries are ranked both **globally** and within **chip family** buckets:

| Category | Filter |
|----------|--------|
| Global | All entries |
| Ice40 | `chip_family == "ice40"` |
| ECP5 | `chip_family == "ecp5"` |
| Xilinx 7-Series | `chip_family == "xilinx-7"` |
| STM32 | `chip_family == "stm32"` |
| ASIC | `chip_family == "asic"` |
| Simulators | `chip_family == "simulator"` |
| By FLUX Version | `flux_version == "X.Y.Z"` |

### 3.3 Derived Metrics

The leaderboard computes and displays these derived fields:

| Metric | Formula | Why It Matters |
|--------|---------|----------------|
| **Pass Rate** | `vectors_passed / 42` | Quick correctness read |
| **Mean Cycles/Vector** | `total_cycles / 42` | Latency at a glance |
| **Mean Energy/Vector** | `total_energy_joules / 42` | Power at a glance |
| **Efficiency Score** | `safe_tops_w × pass_rate` | Combined goodness metric |
| **Speed-Energy Pareto** | Plot position | Visual trade-off frontier |

---

## 4. Submission API Specification

### 4.1 Base URL

```
https://leaderboard.cocapn.ai/api/v1
```

### 4.2 POST /leaderboard/submit

Submit a new benchmark result.

**Request:**

```http
POST /api/v1/leaderboard/submit
Content-Type: application/json
X-Submitter-Key: {optional_api_key_for_verified_users}
```

```json
{
  "board_name": "my-flux-board",
  "board_display_name": "My Custom FLUX-C Board",
  "chip": "ice40-hx8k",
  "chip_family": "ice40",
  "process_node_nm": 40,
  "clock_mhz": 48.0,
  "flux_version": "2.1.4",
  "flux_commit": "a3f7d2e",
  "vectors_passed": 42,
  "vector_results": [
    {
      "vector_id": "flux-c-001-add-overflow",
      "passed": true,
      "cycles": 4,
      "energy_joules": 1.23e-9,
      "safe_tops_w": 0.813,
      "details": null
    }
  ],
  "total_cycles": 420,
  "total_energy_joules": 5.1e-8,
  "safe_tops_w": 0.75,
  "reproducibility_tier": "silver",
  "timestamp": "2026-05-05T05:03:00Z",
  "submitter": "casey@cocapn",
  "environment": {
    "temperature_c": 25.0,
    "temperature_controlled": true,
    "humidity_percent": 45,
    "voltage_v": 3.3,
    "voltage_measured_v": 3.298
  },
  "raw_report_url": "https://gist.github.com/.../report.json",
  "notes": "First submission, still tuning power supply filtering."
}
```

**Validation Rules:**

| Rule | Check | Failure |
|------|-------|---------|
| Schema compliance | JSON matches entry schema | `400 Bad Request` |
| Vector count | Exactly 42 results | `400` |
| Vector IDs | All 42 unique, match known set | `400` |
| `vectors_passed` | Equals count of `passed: true` | `400` |
| `total_cycles` | Equals sum of per-vector cycles | `400` |
| `total_energy_joules` | Equals sum of per-vector energy | `400` |
| `safe_tops_w` | Within 1% of derived value | `400` |
| Timestamp | Not in future, not > 30 days old | `400` |
| Board name | Unique per submitter (or explicit overwrite) | `409 Conflict` |
| Rate limit | Max 10 submissions / hour / IP | `429 Too Many Requests` |
| Signature | If `submitter_verified` claimed, GPG valid | `401 Unauthorized` |

**Response:**

```json
{
  "entry_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "rank_global": 3,
  "rank_family": 1,
  "score": {
    "vectors_passed": 42,
    "safe_tops_w": 0.75,
    "total_cycles": 420
  },
  "improvement_over_previous": {
    "previous_rank": 7,
    "delta_vectors": 0,
    "delta_safe_tops_w": 0.12,
    "delta_cycles": -30
  },
  "badge": "🥈",
  "share_url": "https://leaderboard.cocapn.ai/entry/a1b2c3d4...",
  "timestamp_accepted": "2026-05-05T05:03:01Z"
}
```

### 4.3 GET /leaderboard

Get current rankings.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `category` | string | `global` | `global`, `ice40`, `ecp5`, `stm32`, `asic`, `simulator`, or `flux-{version}` |
| `limit` | integer | 50 | Max entries (max 500) |
| `offset` | integer | 0 | Pagination offset |
| `sort` | string | `rank` | `rank`, `vectors_passed`, `safe_tops_w`, `total_cycles`, `timestamp` |
| `chip_family` | string | — | Filter by chip family |
| `flux_version` | string | — | Filter by FLUX version |
| `min_reproducibility` | string | `bronze` | `bronze`, `silver`, `gold`, `platinum` |
| `since` | date | — | Only entries after this date |
| `board_name` | string | — | Exact match for board name |

**Response:**

```json
{
  "category": "global",
  "total_entries": 147,
  "returned": 50,
  "offset": 0,
  "leaderboard": [
    {
      "rank": 1,
      "entry_id": "...",
      "board_name": "cocapn-flux-v1",
      "board_display_name": "Cocapn FLUX-C Dev Board v1",
      "chip": "ice40-hx8k",
      "chip_family": "ice40",
      "clock_mhz": 48.0,
      "flux_version": "2.1.4",
      "vectors_passed": 42,
      "total_cycles": 312,
      "safe_tops_w": 1.24,
      "reproducibility_tier": "gold",
      "timestamp": "2026-05-04T12:00:00Z",
      "submitter": "forgemaster",
      "submitter_verified": true,
      "share_url": "https://leaderboard.cocapn.ai/entry/...",
      "trend": "up"  // "up", "down", "same", "new"
    }
  ],
  "metadata": {
    "last_updated": "2026-05-05T05:03:00Z",
    "flux_version_latest": "2.1.4",
    "vector_set_version": "flux-c-vectors-v1.0.0"
  }
}
```

### 4.4 GET /leaderboard/board/{name}

Get history for a specific board.

```http
GET /api/v1/leaderboard/board/cocapn-flux-v1?limit=20
```

**Response:**

```json
{
  "board_name": "cocapn-flux-v1",
  "board_display_name": "Cocapn FLUX-C Dev Board v1",
  "chip": "ice40-hx8k",
  "chip_family": "ice40",
  "current_rank_global": 1,
  "current_rank_family": 1,
  "submission_count": 12,
  "first_seen": "2026-04-01T10:00:00Z",
  "latest_submission": "2026-05-04T12:00:00Z",
  "history": [
    {
      "entry_id": "...",
      "timestamp": "2026-04-01T10:00:00Z",
      "flux_version": "2.0.0",
      "vectors_passed": 38,
      "total_cycles": 450,
      "safe_tops_w": 0.89,
      "rank_at_time": 3,
      "notes": "Initial bring-up, 4 vectors failing due to unimplemented TRAP"
    },
    {
      "entry_id": "...",
      "timestamp": "2026-05-04T12:00:00Z",
      "flux_version": "2.1.4",
      "vectors_passed": 42,
      "total_cycles": 312,
      "safe_tops_w": 1.24,
      "rank_at_time": 1,
      "notes": "Fixed TRAP handling, retuned clock tree, added power filtering"
    }
  ],
  "improvement_summary": {
    "vectors_gained": 4,
    "cycles_improved_by_percent": 30.7,
    "safe_tops_w_improved_by_percent": 39.3,
    "best_rank_achieved": 1,
    "time_to_first_place_days": 34
  }
}
```

### 4.5 Error Responses

| Code | Meaning | Example |
|------|---------|---------|
| `400` | Bad request (validation fail) | `{"error": "total_cycles mismatch: claimed 420, calculated 418"}` |
| `401` | Unauthorized (bad API key / bad GPG sig) | `{"error": "GPG signature verification failed"}` |
| `404` | Board not found | `{"error": "Board 'my-board' has no submissions"}` |
| `409` | Conflict (duplicate board name) | `{"error": "Board name 'my-board' already exists for submitter 'alice'. Use PUT to update."}` |
| `429` | Rate limited | `{"error": "Rate limit exceeded: 10 submissions/hour. Retry after 2026-05-05T06:00:00Z"}` |
| `500` | Server error | `{"error": "Internal error. Reference: req-abc123"}` |

### 4.6 PUT /leaderboard/board/{name}

Update an existing board submission (overwrite with newer result). Same validation as POST.

Requires matching submitter identity or admin key.

### 4.7 GET /leaderboard/vectors

Get the current vector set metadata:

```json
{
  "version": "flux-c-vectors-v1.0.0",
  "count": 42,
  "checksum_sha256": "a3f7d2e...",
  "download_url": "https://leaderboard.cocapn.ai/static/flux-c-vectors-v1.0.0.jsonl",
  "categories": {
    "arithmetic": 8,
    "logic": 6,
    "shift": 4,
    "compare": 4,
    "control": 6,
    "stack": 4,
    "memory": 3,
    "syscall": 2,
    "trap": 2,
    "timing": 1,
    "random": 1,
    "identity": 1
  }
}
```

---

## 5. Frontend Display Specification

### 5.1 Main Leaderboard Table

**URL:** `https://leaderboard.cocapn.ai/`

**Layout:**

```
+-------------------------------------------------------------+
|  FLUX-C Test Vector Leaderboard    [ Submit Your Board → ]  |
|  42 vectors · Correctness first · Efficiency second         |
+-------------------------------------------------------------+
|  Filter: [All Families ▼] [All Versions ▼] [Min Tier: Silver▼]
|  Category: [ Global | Ice40 | ECP5 | STM32 | ASIC | Sim ]  |
+-------------------------------------------------------------+
|  Rank | Board | Chip | Clock | FLUX | Passed | Cycles | TOPS/W | Tier |
|  ----- | ----- | ---- | ----- | ---- | ------ | ------ | ------ | ---- |
|  🥇 1  | cocapn-flux-v1  | ice40-hx8k | 48MHz | 2.1.4 | 42/42 | 312 | 1.24 | 🥇 |
|  🥈 2  | j1-forth-flux   | ice40-hx1k | 12MHz | 2.1.4 | 42/42 | 840 | 0.91 | 🥈 |
|  🥉 3  | stm32f4-discovery| stm32f407 | 168MHz| 2.1.3 | 41/42 | 126 | 0.15 | 🥉 |
|  ...   | ...             | ...        | ...   | ...   | ...   | ... | ...  | ...|
+-------------------------------------------------------------+
|  Showing 1-50 of 147 entries  [ < Prev | 1 | 2 | 3 | Next > ]|
+-------------------------------------------------------------+
```

**Table Spec:**

| Column | Sortable | Default | Format |
|--------|----------|---------|--------|
| Rank | No | Ascending | Ordinal + badge |
| Board | Yes | Ascending | Linked to board history page |
| Chip | Yes | Ascending | With chip family icon |
| Clock | Yes | Descending | `X.XX MHz` |
| FLUX Version | Yes | Descending | SemVer |
| Passed | Yes | Descending | `N/42` + pass rate bar |
| Cycles | Yes | Ascending | Integer, comma-separated |
| TOPS/W | Yes | Descending | 3 decimal places |
| Tier | Yes | Descending | Emoji badge |

**Sort Behavior:**
- Click once: primary sort ascending
- Click again: primary sort descending
- Shift-click: add secondary sort key
- Always tie-break with official ranking algorithm

### 5.2 Filters

**Chip Family Filter:**
- Multi-select checkboxes
- Options dynamically populated from database
- "Select All" / "Clear All"
- URL-synced: `?chip_family=ice40,ecp5`

**FLUX Version Filter:**
- Dropdown with all known versions
- "Latest only" quick-toggle
- URL-synced: `?flux_version=2.1.4`

**Reproducibility Tier Filter:**
- Slider: Bronze → Silver → Gold → Platinum
- Default: Bronze (show all)
- URL-synced: `?min_tier=silver`

**Date Range:**
- Presets: "All time", "This month", "This week", "Today"
- Custom date picker
- URL-synced: `?since=2026-05-01`

### 5.3 Trend Graph

**URL:** `https://leaderboard.cocapn.ai/trends`

**Visual:** Line chart + scatter overlay

```
Vectors Passed
    42 |                                    * (forgemaster, today)
       |                              *
    40 |                        *
       |                  *
    38 |            *
       |      *
    36 |  *
       +------------------------------------
         Apr 1    Apr 15    May 1    May 15
```

**Axes:**
- X: Time (linear, auto-scaled to data range)
- Y (left): `vectors_passed` (0–42, fixed scale)
- Y (right): `safe_tops_w` (log scale, auto-ranged)

**Series:**
- One line per board, color-coded by chip family
- Hover: tooltip with board name, date, all metrics
- Click: navigate to board history page
- Legend: toggle boards on/off

**Views:**
- **Improvement over time:** Each board's trajectory
- **Pareto frontier:** TOPS/W vs vectors_passed scatter, frontier highlighted
- **Version comparison:** Same board across FLUX versions
- **Family race:** Chip families as aggregate trend lines

### 5.4 Board Detail Page

**URL:** `https://leaderboard.cocapn.ai/board/{name}`

**Sections:**

1. **Header Card**
   - Board name, chip, photo (if provided)
   - Current rank + badge
   - All-time best rank
   - Submission count + first/last dates

2. **Performance History Table**
   - Same columns as main leaderboard
   - Delta from previous submission
   - Sparkline mini-graphs per metric

3. **Vector Breakdown**
   - 42-row table: each vector's pass/fail status on latest submission
   - Color: green (pass), red (fail), gray (not run)
   - Click vector row: show expected vs actual (if failed)

4. **Comparison Tool**
   - "Compare with..." dropdown
   - Side-by-side table of two boards
   - Delta highlighting

5. **Share Card**
   - Pre-formatted tweet/toot: *"My board runs FLUX-C at 1.24 TOPS/W, ranking #1 globally. Can you beat it? leaderboard.cocapn.ai/board/my-board"*
   - Copy link, QR code

### 5.5 "Submit Your Board" CTA Flow

**Entry Points:**
- Prominent button in nav bar (all pages)
- Sticky banner on leaderboard table
- Dedicated page: `/submit`

**Flow:**

```
[ Start ] → [ Download Harness ] → [ Run on Your Board ]
    ↓
[ Upload Results ] → [ Validation ] → [ Preview Entry ]
    ↓
[ Confirm & Submit ] → [ View on Leaderboard ]
```

**Upload Step:**
- Drag-and-drop JSON file
- Or paste JSON directly
- Live validation feedback (green checkmarks per field)
- Auto-populate `safe_tops_w` if missing

**Preview Step:**
- Rendered card showing where the entry would rank
- Comparison with nearest neighbors
- "You would be #3 in Ice40 family!"

### 5.6 Visual Design Reference

**Aesthetic:** *Dieter Rams hardware lab meets Moebius technical illustration.*

- Background: `#0a0a0f` (abyssal dark)
- Accent: `#00f0ff` (bioluminescent cyan)
- Secondary: `#7b61ff` (deep purple)
- Success: `#00e676` (neon green)
- Failure: `#ff1744` (alert red)
- Typography: `JetBrains Mono` for data, `Inter` for UI
- Table rows: subtle zebra striping, hover lift effect
- Badges: metallic emoji tier indicators with tooltip explanation
- Animations: number counting on load, smooth sort transitions

**Responsive:**
- Desktop: full table
- Tablet: condensed table (hide cycles, collapse chip into board)
- Mobile: card list view, sort via dropdown

---

## 6. Implementation Notes

### 6.1 Backend Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   CDN / Cache   │────▶│  API Gateway    │────▶│  Validation Svc │
│  (leaderboard   │     │  (rate limit,   │     │  (schema + math │
│   snapshots)    │     │   auth)         │     │   verification) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Leaderboard   │
                       │     Database    │
                       │  (PostgreSQL +  │
                       │   JSONB cols)   │
                       └─────────────────┘
```

**Database Schema (simplified):**

```sql
CREATE TABLE entries (
    entry_id UUID PRIMARY KEY,
    board_name VARCHAR(64) NOT NULL,
    chip VARCHAR(64) NOT NULL,
    chip_family VARCHAR(32) NOT NULL,
    clock_mhz DECIMAL(10, 4) NOT NULL,
    flux_version VARCHAR(16) NOT NULL,
    vectors_passed SMALLINT NOT NULL CHECK (vectors_passed BETWEEN 0 AND 42),
    total_cycles BIGINT NOT NULL,
    total_energy_joules DECIMAL(24, 12) NOT NULL,
    safe_tops_w DECIMAL(12, 6) NOT NULL,
    reproducibility_tier VARCHAR(16) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    submitter VARCHAR(64) NOT NULL,
    submitter_verified BOOLEAN DEFAULT FALSE,
    raw_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_rank_sort ON entries (vectors_passed DESC, safe_tops_w DESC, total_cycles ASC, timestamp ASC);
CREATE INDEX idx_chip_family ON entries (chip_family, vectors_passed DESC);
CREATE INDEX idx_flux_version ON entries (flux_version, vectors_passed DESC);
CREATE INDEX idx_board_name ON entries (board_name, timestamp DESC);
```

### 6.2 Security Considerations

1. **Rate limiting:** 10 submissions/hour/IP, 100/hour/verified user
2. **Math verification:** Server recomputes `total_cycles`, `total_energy`, `safe_tops_w` from raw vector results — clients cannot fake these
3. **GPG signatures:** Optional but encouraged for verified badge
4. **Board name squatting:** Names are scoped to submitter; no global reservation (except fleet boards, which are pre-registered)
5. **Raw data retention:** Full JSON retained for 90 days, then archived to cold storage (S3/Glacier)

### 6.3 Open Questions

| Question | Status | Owner |
|----------|--------|-------|
| Should we allow partial submissions (< 42 vectors)? | Open | Forgemaster |
| How to handle FPGA bitstream variants (area-optimized vs speed-optimized)? | Open | Forgemaster |
| Do we need a reference implementation / golden board? | Open | CCC |
| Should there be a "most improved" secondary leaderboard? | Open | CCC |
| Integration with fleet CI for auto-submit on release? | Open | Oracle1 |

---

## 7. Appendix

### A. Vector Set Checksum

Current vector set (v1.0.0):
```
SHA256(flux-c-vectors-v1.0.0.jsonl) =
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```
*(Placeholder — Forgemaster to provide actual hash)*

### B. Reference Boards (Pre-registered)

| Board Name | Owner | Chip | Expected Tier |
|------------|-------|------|---------------|
| `cocapn-flux-v1` | Forgemaster | ice40-hx8k | Gold |
| `cocapn-flux-v2` | Forgemaster | ecp5-45k | Platinum (target) |
| `jetsonclaw1-flux` | JetsonClaw1 | Jetson Nano (sim) | Bronze |
| `oracle1-reference` | Oracle1 | verilator-sim | Silver |

### C. GPG Verification

Verified submitters should sign their submission payload:

```bash
gpg --detach-sign --armor submission.json
# Upload submission.json + submission.json.asc
```

The API accepts an optional `gpg_signature` field containing the ASCII-armored detached signature.

---

**End of Specification.**

*"A leaderboard without reproducibility is just a gossip column."* — CCC, 2026-05-05
