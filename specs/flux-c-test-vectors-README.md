# FLUX-C Test Vectors

**Version:** 1.0.0  
**Date:** 2026-05-05  
**Author:** CCC (Cocapn Fleet)  
**Status:** Draft — Awaiting Forgemaster Review  

---

## 1. Overview

This repository contains the **official FLUX-C test vector suite** used by the [FLUX-C Test Vector Leaderboard](flux-c-leaderboard-2026-05-05.md). FLUX-C is the 43-opcode constraint VM at the heart of the Cocapn Fleet, as defined in the EMSOFT 2027 paper (APPENDIX-B).

**Design principle:** *Every opcode must be exercised. Every trap condition must be triggered. Every path must be verified.*

---

## 2. File Structure

```
specs/
├── flux-c-test-vectors-2026-05-05.json   # The vector suite (58 vectors)
├── flux-c-test-vectors-README.md         # This document
└── flux-c-leaderboard-2026-05-05.md      # Leaderboard system specification
```

---

## 3. Test Vector Format

Each vector is a self-contained JSON object:

```json
{
  "id": "tv_stack_001",
  "name": "Push and Pop",
  "description": "Push three values, pop two, verify stack depth and remaining value",
  "category": "stack",
  "opcodes_tested": ["PUSH", "POP"],
  "initial_state": {
    "stack": [],
    "pc": 0,
    "memory": {},
    "io": { "input": {}, "output": {} }
  },
  "bytecode": "0x01 0x0A 0x01 0x14 0x01 0x1E 0x02 0x02",
  "expected_state": {
    "stack": [10],
    "pc": 8,
    "memory": {}
  },
  "expected_cycles": 8,
  "difficulty": "easy",
  "tags": ["stack", "basic"]
}
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique identifier, format `tv_{category}_{NNN}` |
| `name` | string | ✅ | Human-readable test name |
| `description` | string | ✅ | What the test verifies |
| `category` | string | ✅ | `stack`, `arithmetic`, `logic`, `control`, `memory`, `io`, `constraint`, `safety`, `edge` |
| `opcodes_tested` | string[] | ✅ | Which opcodes this vector exercises |
| `initial_state` | object | ✅ | VM state before execution |
| `bytecode` | string | ✅ | Space-separated hex bytes |
| `expected_state` | object | ✅ | VM state after execution (if no trap) |
| `expected_trap` | string | ❌ | Trap code if the vector should fail |
| `expected_cycles` | integer | ✅ | Expected cycle count for reference implementations |
| `difficulty` | string | ✅ | `easy`, `medium`, `hard` |
| `tags` | string[] | ✅ | Search/filter tags |

### State Object Schema

```json
{
  "stack": [42, 10],        // Array of integers, TOS is last element
  "pc": 8,                  // Program counter (byte offset)
  "memory": { "16": 42 },   // Address → value map (strings as JSON keys)
  "io": {
    "input": { "0": 42 },   // Port → value for IN instructions
    "output": { "0": 42 },  // Port → value written by OUT
    "ready_ports": [0, 1],   // For POLL: which ports are ready
    "interrupt_ready": true  // For WAIT: is interrupt pending
  }
}
```

**Note:** The `io` field is optional in `initial_state` and `expected_state`. If omitted, no I/O is simulated.

---

## 4. Opcode Reference

### 4.1 Bytecode Encoding

| Opcode | Hex | Operands | Cycles | Description |
|--------|-----|----------|--------|-------------|
| **Stack** |
| `PUSH` | `0x01` | `imm8` | 2 | Push 8-bit immediate (zero-extended to word) |
| `POP` | `0x02` | — | 1 | Pop and discard TOS |
| `DUP` | `0x03` | — | 1 | Duplicate TOS |
| `SWAP` | `0x04` | — | 1 | Swap TOS and NOS |
| `PICK` | `0x05` | `depth8` | 2 | Copy element at `depth` (0=TOS) to top |
| `ROLL` | `0x06` | `depth8` | 2 | Move element at `depth` to top, shift others down |
| **Arithmetic** |
| `ADD` | `0x10` | — | 1 | Pop b, pop a, push a + b |
| `SUB` | `0x11` | — | 1 | Pop b, pop a, push a − b |
| `MUL` | `0x12` | — | 1 | Pop b, pop a, push a × b |
| `DIV` | `0x13` | — | 1 | Pop b, pop a, push a / b. **Traps on b=0** |
| `MOD` | `0x14` | — | 1 | Pop b, pop a, push a % b |
| `ABS` | `0x15` | — | 1 | Pop a, push \|a\| |
| `NEG` | `0x16` | — | 1 | Pop a, push −a |
| **Logic** |
| `AND` | `0x20` | — | 1 | Pop b, pop a, push a & b (bitwise) |
| `OR` | `0x21` | — | 1 | Pop b, pop a, push a \| b (bitwise) |
| `XOR` | `0x22` | — | 1 | Pop b, pop a, push a ^ b (bitwise) |
| `NOT` | `0x23` | — | 1 | Pop a, push ~a (bitwise complement) |
| `EQ` | `0x24` | — | 1 | Pop b, pop a, push 1 if a == b else 0 |
| `NE` | `0x25` | — | 1 | Pop b, pop a, push 1 if a != b else 0 |
| `LT` | `0x26` | — | 1 | Pop b, pop a, push 1 if a < b else 0 |
| `GT` | `0x27` | — | 1 | Pop b, pop a, push 1 if a > b else 0 |
| `LE` | `0x28` | — | 1 | Pop b, pop a, push 1 if a <= b else 0 |
| `GE` | `0x29` | — | 1 | Pop b, pop a, push 1 if a >= b else 0 |
| **Control Flow** |
| `JMP` | `0x30` | `offset8` | 2 | PC += offset (signed, relative to next instruction) |
| `JZ` | `0x31` | `offset8` | 1–2 | Pop value. If zero, PC += offset (taken=2 cycles) |
| `JNZ` | `0x32` | `offset8` | 1–2 | Pop value. If non-zero, PC += offset (taken=2 cycles) |
| `CALL` | `0x33` | `target8` | 2 | Push return address, PC = target |
| `RET` | `0x34` | — | 2 | Pop return address, PC = popped value |
| `HALT` | `0x3F` | — | 1 | Stop execution |
| **Memory** |
| `LOAD` | `0x40` | — | 3 | Pop addr, push word from memory[addr] |
| `STORE` | `0x41` | — | 3 | Pop addr, pop val, memory[addr] = val |
| `LOADB` | `0x42` | — | 3 | Pop addr, push byte from memory[addr] (zero-extended) |
| `STOREB` | `0x43` | — | 3 | Pop addr, pop val, memory[addr] = val & 0xFF |
| **I/O** |
| `IN` | `0x50` | `port8` | 3 | Read from port, push value |
| `OUT` | `0x51` | `port8` | 3 | Pop value, write to port |
| `POLL` | `0x52` | `mask8` | 3 | Check ports in mask; push 1 if any ready, else 0 |
| `WAIT` | `0x53` | — | 1+ | Block until interrupt; 1 cycle if interrupt already ready |
| **Constraint** |
| `GUARD` | `0x60` | — | 1 | Pop value. If zero, trap `GUARD_VIOLATION` |
| `ASSERT` | `0x61` | — | 1 | Pop value. If zero, trap `ASSERT_FAILURE` |
| `FAIL` | `0x62` | — | 1 | Always trap `FAIL_TRIGGERED` |
| **Safety-Critical** |
| `SAFE_ADD` | `0x70` | — | 1 | Add with overflow detection. Traps `SAFE_OVERFLOW` on overflow |
| `SAFE_DIV` | `0x71` | — | 1 | Divide with zero-check. Traps `SAFE_DIV_ZERO` if divisor is 0 |
| `BOUND_CHECK` | `0x72` | `bound8` | 2 | Pop value. If value < 0 or value >= bound, trap `BOUND_VIOLATION` |

### 4.2 Operand Conventions

- **8-bit immediates** (`imm8`, `depth8`, `port8`, `mask8`, `bound8`, `offset8`, `target8`) are encoded as the byte following the opcode.
- **Signed offsets** (`offset8`) use two's complement. `0xFC` = −4.
- **Word size:** The VM operates on 32-bit words. PUSH zero-extends its 8-bit immediate to 32 bits.

---

## 5. Running the Vectors

### 5.1 Requirements

1. A FLUX-C VM implementation
2. A test harness that can load JSON vectors and execute them
3. Cycle-counting capability (for leaderboard submissions)

### 5.2 Quick Start (Python)

```python
import json

# Load vectors
with open('flux-c-test-vectors-2026-05-05.json') as f:
    vectors = json.load(f)

# Your VM implementation
from my_vm import FluxCVM

results = []
for vector in vectors:
    vm = FluxCVM()
    vm.load_bytecode(vector['bytecode'])
    vm.set_state(vector['initial_state'])
    
    trap = vm.run(max_cycles=vector['expected_cycles'] * 10)
    
    actual_state = vm.get_state()
    
    if vector.get('expected_trap'):
        passed = (trap == vector['expected_trap'])
    else:
        passed = (actual_state == vector['expected_state'] and trap is None)
    
    results.append({
        'id': vector['id'],
        'passed': passed,
        'trap': trap,
        'actual': actual_state
    })

print(f"Passed: {sum(r['passed'] for r in results)}/{len(results)}")
```

### 5.3 Determinism Check

For leaderboard eligibility, each vector must produce **identical output** across at least 1000 runs. The harness should verify this before submitting.

```python
def is_deterministic(vm, vector, runs=1000):
    outputs = []
    for _ in range(runs):
        vm.reset()
        vm.load_bytecode(vector['bytecode'])
        vm.set_state(vector['initial_state'])
        vm.run()
        outputs.append(vm.get_state())
    
    # All outputs must be identical
    first = outputs[0]
    return all(o == first for o in outputs[1:])
```

### 5.4 Expected Cycles

The `expected_cycles` field is the **reference count** for a minimal, cycle-accurate implementation. Your implementation may differ if:
- It uses a different pipeline depth
- It has a different memory access latency
- It optimizes certain instruction sequences

**For leaderboard ranking:** Cycle count is tracked per-vector but does not affect pass/fail. Energy efficiency (`safe_tops_w`) is the secondary ranking metric.

---

## 6. Adding New Vectors

### 6.1 When to Add

- A new opcode is added to FLUX-C
- A new edge case or trap condition is discovered
- A new I/O or memory pattern needs coverage

### 6.2 How to Add

1. **Choose an ID:** Follow the pattern `tv_{category}_{NNN}`. Check existing IDs to avoid collision.
2. **Write the vector:** Use the format in Section 3. Ensure all required fields are present.
3. **Compute expected state:** Trace through the bytecode manually or with a reference simulator.
4. **Count cycles:** Use the cycle table in Section 4.1.
5. **Add tags:** Include at least the category tag and one descriptive tag.
6. **Update coverage:** Run the coverage script (Section 7) to confirm all opcodes are still covered.
7. **Bump version:** Update the version header in this README and the vector file name.

### 6.3 Example: Adding a New Vector

```json
{
  "id": "tv_arith_009",
  "name": "Modulo by One",
  "description": "Any number modulo 1 is 0 — edge case for MOD",
  "category": "arithmetic",
  "opcodes_tested": ["PUSH", "MOD"],
  "initial_state": { "stack": [], "pc": 0, "memory": {} },
  "bytecode": "0x01 0x2A 0x01 0x01 0x14",
  "expected_state": { "stack": [0], "pc": 5, "memory": {} },
  "expected_cycles": 5,
  "difficulty": "easy",
  "tags": ["arithmetic", "edge"]
}
```

### 6.4 PR Checklist

- [ ] Vector ID is unique
- [ ] All required fields present
- [ ] Bytecode parses correctly (valid hex, even number of digits per byte)
- [ ] Expected state manually verified
- [ ] Cycle count computed per spec
- [ ] At least one tag from the category
- [ ] Coverage script passes (all 43 opcodes covered)
- [ ] README version bumped if adding/removing vectors

---

## 7. Coverage Report

### 7.1 Opcode Coverage

Run this script to verify all EMSOFT opcodes are covered:

```python
import json

ALL_OPCODES = {
    # Stack (6)
    'PUSH', 'POP', 'DUP', 'SWAP', 'PICK', 'ROLL',
    # Arithmetic (7)
    'ADD', 'SUB', 'MUL', 'DIV', 'MOD', 'ABS', 'NEG',
    # Logic (10)
    'AND', 'OR', 'XOR', 'NOT', 'EQ', 'NE', 'LT', 'GT', 'LE', 'GE',
    # Control (6)
    'JMP', 'JZ', 'JNZ', 'CALL', 'RET', 'HALT',
    # Memory (4)
    'LOAD', 'STORE', 'LOADB', 'STOREB',
    # I/O (4)
    'IN', 'OUT', 'POLL', 'WAIT',
    # Constraint (3)
    'GUARD', 'ASSERT', 'FAIL',
    # Safety (3)
    'SAFE_ADD', 'SAFE_DIV', 'BOUND_CHECK',
}

with open('flux-c-test-vectors-2026-05-05.json') as f:
    vectors = json.load(f)

covered = set()
for v in vectors:
    covered.update(v['opcodes_tested'])

missing = ALL_OPCODES - covered
extra = covered - ALL_OPCODES

print(f"Vectors: {len(vectors)}")
print(f"Opcodes covered: {len(covered)}/43")
print(f"Missing: {sorted(missing)}")
print(f"Extra (not in EMSOFT): {sorted(extra)}")
```

### 7.2 Current Coverage (v1.0.0)

| Category | Opcodes | Covered By |
|----------|---------|------------|
| Stack | PUSH, POP, DUP, SWAP, PICK, ROLL | tv_stack_001–005, tv_edge_003, tv_edge_006 |
| Arithmetic | ADD, SUB, MUL, DIV, MOD, ABS, NEG | tv_arith_001–008, tv_edge_004 |
| Logic | AND, OR, XOR, NOT, EQ, NE, LT, GT, LE, GE | tv_logic_001–011, tv_edge_008, tv_edge_009 |
| Control | JMP, JZ, JNZ, CALL, RET, HALT | tv_ctrl_001–007, tv_edge_003 |
| Memory | LOAD, STORE, LOADB, STOREB | tv_mem_001–002, tv_edge_007 |
| I/O | IN, OUT, POLL, WAIT | tv_io_001–004, tv_edge_010 |
| Constraint | GUARD, ASSERT, FAIL | tv_constr_001–005, tv_edge_005 |
| Safety | SAFE_ADD, SAFE_DIV, BOUND_CHECK | tv_safety_001–006 |

**Result:** ✅ **All 43 opcodes covered** by 58 test vectors.

---

## 8. Trap Codes

| Code | Triggering Opcode(s) | Meaning |
|------|----------------------|---------|
| `GUARD_VIOLATION` | `GUARD` | Guard condition evaluated to zero/false |
| `ASSERT_FAILURE` | `ASSERT` | Assertion evaluated to zero/false |
| `FAIL_TRIGGERED` | `FAIL` | Unconditional FAIL executed |
| `SAFE_OVERFLOW` | `SAFE_ADD` | Signed integer overflow detected |
| `SAFE_DIV_ZERO` | `SAFE_DIV` | Division by zero detected |
| `BOUND_VIOLATION` | `BOUND_CHECK` | Value outside [0, bound) range |
| `DIV_ZERO` | `DIV` | Regular division by zero (undefined behavior) |
| `STACK_UNDERFLOW` | `POP`, `DUP`, `SWAP`, arithmetic, logic | Not enough values on stack |

**Note:** The EMSOFT paper defines FLUX-C as having deterministic trap behavior. Any trap halts execution immediately and the `expected_state` reflects the state at the point of trap.

---

## 9. Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | 2026-05-05 | Initial release. 58 vectors covering all 43 EMSOFT opcodes. |

---

## 10. Contact

For questions, corrections, or new vector proposals:
- Open an issue on the `flux-research` repo
- Tag `@forgemaster` for VM semantics questions
- Tag `@ccc` for vector format or coverage questions

---

*"A leaderboard without reproducibility is just a gossip column."* — CCC, 2026-05-05
