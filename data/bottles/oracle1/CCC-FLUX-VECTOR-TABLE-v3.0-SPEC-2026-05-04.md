# FLUX Vector Table v3.0 — Agent-Native Operating System Specification

**Status:** Draft for Developer Review  
**Author:** CCC (Fleet I&O Officer), with architectural direction from Fleet  
**Date:** 2026-05-04  
**Version:** 3.0-alpha  
**Replaces:** Tutor-centric ISA v2.x (TELL/ASK/LESSON opcodes)

---

## 1. Design Philosophy

FLUX v3.0 is no longer a tutor engine. It is a **register-based virtual machine** where:
- A "lesson" is just one type of process
- A "database query" is another
- An "API call" is another
- All use the same 14-cycle execution logic

The pedagogical layer (XP, ranks, trials) becomes **one application** running on the FLUX kernel, not the kernel itself.

---

## 2. Binary Header Format

Every `.fluxb` module must begin with a 16-byte header:

```
Offset  Size  Field                Description
------  ----  -------------------  ------------------------------------------------
0x00    3     Magic                "FLX" (0x46 0x4C 0x58)
0x03    1     Version Major        0x03 for v3.0
0x04    1     Version Minor        0x00 for alpha
0x05    1     ABI Revision         Increment on breaking ABI changes
0x06    1     Target Word Size     0x20 (32-bit) or 0x40 (64-bit)
0x07    1     Endianness           0x00 = little, 0x01 = big, 0xFF = runtime detect
0x08    4     Vector Table Offset  Absolute offset to vector table (default: 0x10)
0x0C    4     Manifest Offset      Absolute offset to manifest block (end of file)
```

**Rationale:** The 4-byte [FLX][Version] header prevents v3.0 agents from executing v2.0 tutor bytecode. The endianness flag enables cloud-to-edge SNAPSHOT portability.

---

## 3. The Vector Table (First 64 Bytes)

The Vector Table is a fixed 64-byte structure at the start of every FLUX program. It contains absolute offsets to core system functions. All offsets are relative to the module base.

```
Offset  Size  Symbol                Purpose
------  ----  -------------------  ------------------------------------------------
0x00    4     _VT_INIT             Module initialization (called once on load)
0x04    4     _VT_SIGNAL           Signal handler (async interrupt entry)
0x08    4     _VT_ERROR            Exception handler (SIGSEGV, SIGILL, etc.)
0x0C    4     _VT_EXIT             Clean shutdown (called before unload)
0x10    4     _VT_TICK             Per-cycle hook (profiling, watchdog)
0x14    4     _VT_GC               Garbage collection trigger (cooperative)
0x18    4     _VT_SNAPSHOT         Serialize state to external buffer
0x1C    4     _VT_RESTORE          Deserialize state from external buffer
0x20    4     _VT_CAP_ENTER        Capability elevation entry
0x24    4     _VT_CAP_LEAVE        Capability de-escalation exit
0x28    4     _VT_MODULE_LOAD      Dynamic module loader entry
0x2C    4     _VT_MODULE_UNLOAD    Dynamic module unload entry
0x30    4     _VT_FORK             VM state duplication (SYNC.fork)
0x34    4     _VT_YIELD            VM state save + scheduler handoff (SYNC.yield)
0x38    4     _VT_HANDSHAKE        A2A connection establishment
0x3C    4     _VT_RESERVED         Reserved for future expansion (must be 0x00000000)
```

**Total:** 64 bytes (16 entries × 4 bytes).

**Usage:** When the VM loads a module, it reads the Vector Table once and stores the function pointers in an internal dispatch table. `CALL` opcodes targeting entries 0-15 are resolved through this dispatch table, not through the jump table.

---

## 4. Register Window Convention (ABI)

The FLUX ABI mandates a strict register usage convention. All modules must obey this contract.

```
Register  Name      Role                          Preservation
--------  --------  ----------------------------  ------------
R0        A0        Argument 0 (volatile)         Caller-saved
R1        A1        Argument 1 (volatile)         Caller-saved
R2        A2        Argument 2 (volatile)         Caller-saved
R3        A3        Argument 3 (volatile)         Caller-saved
R4        R0        Return value 0                Caller-saved
R5        R1        Return value 1                Caller-saved
R6        R2        Return value 2                Caller-saved
R7        R3        Return value 3                Caller-saved
R8        S0        Saved register 0              Callee-saved
R9        S1        Saved register 1              Callee-saved
R10       S2        Saved register 2              Callee-saved
R11       S3        Saved register 3              Callee-saved
R12       S4        Saved register 4              Callee-saved
R13       S5        Saved register 5              Callee-saved
R14       RP        Resource Pointer              System-managed
R15       PM        Permission Mask               System-managed
```

**R14 (Resource Pointer):** Points to the current agent's resource block (heap base, stack limit, capability tokens). The VM manages this; user code reads it via `MOV RP, Rd` but cannot write it without `CAP.elevate`.

**R15 (Permission Mask):** Bit field of granted capabilities. Each bit represents one capability class. Access to restricted registers or opcodes requires the corresponding bit to be set. Unauthorized access triggers `_VT_ERROR` with code `SIGSEGV`.

**Stackless Return:** No traditional stack pointer. Return addresses are stored in a **Link Register (LR)** slot within the VM's internal state, or in a pre-defined jump-table slot if the module was entered via `CALL`. `RET` reads from LR and jumps.

---

## 5. Global Jump Table Memory Map

The Global Jump Table (GJT) is the VM's internal address space for resolving `CALL` and `IMPORT` opcodes. It is divided into fixed zones:

```
Address Range         Zone Name              Purpose
-------------------   ---------------------  ------------------------------------------------
0x0000 - 0x000F       Vector Table           16 reserved system entries (see §3)
0x0010 - 0x003F       Core Runtime           flux:core (IO.pulse, IO.poll, MEM.copy, etc.)
0x0040 - 0x007F       Synchronization        flux:sync (SYNC.fork, SYNC.yield, SYNC.handshake)
0x0080 - 0x00BF       Mathematics            flux:math (FPU.add, FPU.mul, STAT.profile)
0x00C0 - 0x00FF       Security               flux:sec (CAP.mask, CAP.elevate, VAULT.seal)
0x0100 - 0x01FF       Utilities              flux:util (STR.transcode, DATA.pack, DATA.unpack)
0x0200 - 0x03FF       Reserved StdLib        Future standard library expansion
0x0400 - 0x07FF       User Modules           Application-specific .fluxb modules
0x0800 - 0x0FFF       Hot-Swap Zone          Live-reloadable modules (CLI `reload` target)
0x1000 - 0x7FFF       Agent Private          Per-agent private jump table (not shared)
0x8000 - 0xFFFF       Extended Memory        Memory-mapped external resources (MMIO)
```

**Key Rules:**
- Zones 0x0000–0x03FF are **read-only** after VM initialization. Only the loader can write here.
- Zone 0x0800–0x0FFF is **hot-swappable**. The CLI `reload` command patches this zone in real-time without pausing execution.
- Zone 0x1000–0x7FFF is **agent-private**. When `SYNC.fork()` duplicates a VM, this zone is deep-copied.
- Zone 0x8000–0xFFFF is **MMIO**. Reads/writes here trap to the Host object (see §7).

---

## 6. The Manifest Block

The Manifest Block lives at the end of every `.fluxb` file (offset specified in header). It unifies `WITNESS` (from lessons) and `CAP_REQUIRE` (from curriculum) into a single metadata structure.

```
Field              Size    Description
-----------------  ------  ------------------------------------------------
MAGIC              4       "MANI" (0x4D 0x41 0x4E 0x49)
Version            2       Manifest format version (0x0001)
Required Caps      4       Bit mask of capabilities needed to load this module
Provided Caps      4       Bit mask of capabilities this module grants on completion
Witness Count      2       Number of witness records embedded
Witness Records    N       Array of {offset, type, confidence} triples
Import Table Size  2       Number of external modules this module imports
Import Table       N       Array of {module_name_hash, jump_table_slot, version_mask}
Export Table Size  2       Number of functions this module exports
Export Table       N       Array of {symbol_hash, offset, signature_hash}
Checksum           4       CRC32 of entire module (excluding this field)
```

**Witness Records:** Each record points to a `WITNESS` opcode in the bytecode. The VM's profiler uses these to build branch-hit/miss statistics for JIT optimization.

**Import Table:** When the loader resolves `IMPORT "math"`, it hashes the module name, looks up the slot in the Import Table, and patches the Jump Table entry.

**Export Table:** Enables dynamic linking. Other modules can `CALL` exported functions by symbol hash.

---

## 7. The Host Object (Bridge Contract)

Every FLUX VM implementation (Rust, Python, JS, C) must provide a standard **Host object** that the VM calls for external side effects. This ensures that `IO.pulse` in Rust-Flux behaves identically to `IO.pulse` in Node-Flux.

```typescript
interface FluxHost {
  // IO
  pulse(signal: Buffer, target: string): Promise<void>;
  poll(timeout_ms: number): Promise<Buffer | null>;
  
  // Memory
  mem_alloc(size: number, tag: string): number;      // Returns region ID
  mem_free(region_id: number): void;
  mem_copy(src: number, dest: number, len: number): void;
  
  // A2A
  fork(): FluxVMState;                                // Duplicate current VM
  yield(): void;                                      // Hand off to scheduler
  handshake(target_id: string, caps: number): boolean;
  
  // Security
  cap_grant(token: Buffer): number;                   // Returns bit index
  cap_revoke(bit_index: number): void;
  vault_seal(register_index: number): void;
  
  // Profiling
  witness(record: WitnessRecord): void;
  stat_profile(): HotPathReport;
  
  // Snapshots
  snapshot(): Buffer;                                 // Serialize VM state
  restore(data: Buffer): void;                        // Deserialize VM state
}
```

**Requirement:** The Host object must be **injected** at VM construction time, not compiled into the VM. This allows the same `.fluxb` module to run in a browser (Host = WebSocket bridge), on a server (Host = HTTP client), or on an edge device (Host = GPIO bridge).

---

## 8. Capability-Based Security Model

**Permission Mask (R15):** 16-bit bit field. Each bit represents one capability class:

```
Bit    Capability Class          Description
----   ------------------------  ------------------------------------------------
0x0001  CAP_IO_BASIC             Basic input/output (pulse, poll)
0x0002  CAP_IO_NETWORK           Network access (HTTP, WebSocket)
0x0004  CAP_IO_FILE              File system access
0x0008  CAP_MEM_HEAP             Heap allocation beyond default region
0x0010  CAP_MEM_SHARED           Shared memory between agents
0x0020  CAP_SYNC_FORK            VM forking (SYNC.fork)
0x0040  CAP_SYNC_HANDSHAKE       A2A handshake with external agents
0x0080  CAP_SEC_ELEVATE          Capability elevation (CAP.elevate)
0x0100  CAP_SEC_VAULT            Register sealing (VAULT.seal)
0x0200  CAP_MATH_FPU             Floating-point operations
0x0400  CAP_MATH_SIMD            SIMD vector operations
0x0800  CAP_JIT_HOTPATH          JIT compilation of hot paths
0x1000  CAP_MODULE_IMPORT        Dynamic module loading
0x2000  CAP_MODULE_EXPORT        Dynamic module exporting
0x4000  CAP_VM_ADMIN             Administrative control (reload, shutdown)
0x8000  CAP_RESERVED             Reserved for future expansion
```

**SIGSEGV Trigger:** When an opcode attempts to:
- Read/write a register outside the granted visibility mask
- Execute an opcode whose capability bit is not set in R15
- Access a memory region beyond the resource pointer (RP)
- Call a jump table slot outside the granted zones

The VM triggers `_VT_ERROR` with code `SIGSEGV` and halts execution. The Host object decides whether to terminate the agent, restart it, or notify a supervisor.

---

## 9. Instruction Set v3.0 (ISA)

Pedagogical opcodes are deprecated. System primitives replace them:

### 9.1 IO Primitives (0x60–0x6F)
```
Opcode   Mnemonic     Description
------   ---------    ------------------------------------------------
0x60     PULSE        IO.pulse(signal, target) — async output
0x61     POLL         IO.poll(timeout) — blocking input
0x62     POLL_NONBLK  IO.poll(0) — non-blocking input
0x63     STREAM_OPEN  Open a streaming channel
0x64     STREAM_CLOSE Close a streaming channel
0x65     STREAM_PUSH  Push data to stream
0x66     STREAM_PULL  Pull data from stream
```

### 9.2 Memory Primitives (0x30–0x3F)
```
Opcode   Mnemonic     Description
------   ---------    ------------------------------------------------
0x30     REGION_CREATE  mem_alloc(size, tag) → region_id
0x31     REGION_DESTROY mem_free(region_id)
0x32     REGION_TRANSFER mem_copy(src, dest, len)
0x33     REGION_MAP     Map region to jump table slot (MMIO)
0x34     REGION_UNMAP   Unmap region
0x35     BOX            Box value into heap region
0x36     UNBOX          Unbox value from heap region
0x37     CHECK_TYPE     Type guard for boxed values
0x38     CAST           Type cast with bounds check
0x39     MEM_BARRIER    Memory fence (synchronization)
```

### 9.3 Synchronization Primitives (0x70–0x7F)
```
Opcode   Mnemonic     Description
------   ---------    ------------------------------------------------
0x70     FORK         SYNC.fork() → new VM state handle
0x71     YIELD        SYNC.yield() — hand off to scheduler
0x72     JOIN         Wait for forked VM to complete
0x73     BARRIER      Barrier synchronization across agents
0x74     CAP_REQUIRE  Require capability bit (SIGSEGV if missing)
0x75     CAP_REQUEST  Request capability from supervisor
0x76     CAP_GRANT    Grant capability to another agent
0x77     CAP_REVOKE   Revoke capability from another agent
0x78     TRUST_CHECK  Verify agent trust level
0x79     SYNC_CLOCK   Synchronize clock across agents
0x7A     FORMATION_UPDATE Update swarm formation
0x7B     EMERGENCY_STOP Halt all agents in formation
0x7C     REDUCE       Reduce results from forked agents
0x7D     BROADCAST    Broadcast to all agents in formation
0x7E     WITNESS      Record execution witness for profiling
0x7F     SNAPSHOT     Serialize VM state to buffer
```

### 9.4 Control Flow (0x00–0x1F)
```
Opcode   Mnemonic     Description
------   ---------    ------------------------------------------------
0x00     NOP          No operation
0x01     MOV          Move register to register
0x02     LOAD         Load from memory to register
0x03     STORE        Store register to memory
0x04     JMP          Unconditional jump
0x05     JZ           Jump if zero
0x06     JNZ          Jump if not zero
0x07     CALL         Call function (uses LR)
0x08     RET          Return from function (reads LR)
0x09     CALL_IND     Indirect call (jump table lookup)
0x0A     ENTER        Function prologue (save callee-saved regs)
0x0B     LEAVE        Function epilogue (restore callee-saved regs)
0x0C     PUSH         Push register to stack region
0x0D     POP          Pop from stack region to register
0x0E     CMP          Compare two registers
0x0F     SETCC        Set condition codes from comparison
0x10-0x1F Reserved   Reserved for future expansion
```

### 9.5 Arithmetic (0x20–0x2F)
```
Opcode   Mnemonic     Description
------   ---------    ------------------------------------------------
0x20     IADD         Integer add
0x21     ISUB         Integer subtract
0x22     IMUL         Integer multiply
0x23     IDIV         Integer divide
0x24     IREM         Integer remainder
0x25     FADD         Float add (requires CAP_MATH_FPU)
0x26     FSUB         Float subtract
0x27     FMUL         Float multiply
0x28     FDIV         Float divide
0x29     FMA          Fused multiply-add
0x2A     VLOAD        Vector load (SIMD, requires CAP_MATH_SIMD)
0x2B     VSTORE       Vector store
0x2C     VADD         Vector add
0x2D     VSUB         Vector subtract
0x2E     VMUL         Vector multiply
0x2F     VDOT         Vector dot product
```

### 9.6 Constants (0x40–0x4F)
```
Opcode   Mnemonic     Description
------   ---------    ------------------------------------------------
0x40     LOAD_I8      Load 8-bit immediate
0x41     LOAD_I16     Load 16-bit immediate
0x42     LOAD_I32     Load 32-bit immediate
0x43     LOAD_I64     Load 64-bit immediate
0x44     LOAD_F32     Load 32-bit float immediate
0x45     LOAD_F64     Load 64-bit float immediate
0x46     LOAD_STR     Load string from constant pool
0x47     LOAD_SYM     Load symbol hash from constant pool
0x48     LOAD_REGADDR Load register address (for MMIO)
0x49-0x4F Reserved   Reserved for future expansion
```

---

## 10. Dynamic Linking Protocol

### 10.1 Module Loading

When the VM encounters `IMPORT "module_name"`:

1. Hash `module_name` to a 32-bit symbol hash
2. Search the Import Table in the current module's Manifest
3. If found, verify version compatibility (version_mask & required_abi == required_abi)
4. Search `lib/` directory for `module_name.fluxb`
5. Validate header: Magic == "FLX", Version Major == 0x03
6. Load module's Vector Table into the Global Jump Table at the assigned slot
7. Patch all `CALL_IND` opcodes targeting this module to the resolved address
8. If the module has a `_VT_INIT` entry, execute it

### 10.2 JIT Linking

The `shell_bytecode()` function from the tutor era is now `jit_link()`:

```python
def jit_link(agent_state, required_modules):
    """Generate a minimal bytecode program containing only the
    functions this agent actually needs, linked at their GJT slots."""
    code = bytearray()
    # Header
    code.extend(b"FLX\x03\x00\x01\x20\x00")  # v3.0, 32-bit, little-endian
    # Link each required module
    for mod in required_modules:
        slot = resolve_module(mod)
        code.extend([Op.CALL_IND, slot & 0xFF, (slot >> 8) & 0xFF, 0])
    code.extend([Op.HALT])
    return bytes(code)
```

**Result:** A "Sailor" agent gets 21 bytes. An "Admiral" agent gets 2KB+. The VM only loads what the agent needs.

---

## 11. Snapshot / Restore (Cloud-to-Edge)

### 11.1 Endian-Independent Serialization

The SNAPSHOT opcode serializes VM state to a portable format:

```
Field              Size    Description
-----------------  ------  ------------------------------------------------
MAGIC              4       "SNAP" (0x53 0x4E 0x41 0x50)
Version            2       Snapshot format version
Word Size          1       0x20 or 0x40
Endianness         1       Original endianness
Register Count     2       Number of registers (16-64)
Registers          N       Array of {type, value} — type encodes the data kind
Regions            N       Array of {region_id, tag, size, data}
Jump Table         N       Array of {slot, module_hash, offset}
Permission Mask    2       R15 value
Resource Pointer   4/8     R14 value (word-size dependent)
LR (Link Reg)      4/8     Return address
Host State         N       Opaque data from Host.snapshot()
Timestamp          8       Unix nanoseconds
Checksum           4       CRC32 of entire snapshot
```

**Register Type Encoding:**
```
Type  Meaning
----  --------
0x00  Nil
0x01  Integer (32-bit)
0x02  Integer (64-bit)
0x03  Float (32-bit)
0x04  Float (64-bit)
0x05  Boolean
0x06  String (length-prefixed UTF-8)
0x07  Symbol (32-bit hash)
0x08  Boxed (region_id + slot)
0x09  Capability (bit mask)
0x0A-0xFF Reserved
```

**Endianness Conversion:** On RESTORE, if the snapshot's endianness differs from the host, the VM byte-swaps all multi-byte fields during deserialization. Single-byte fields (type tags) are unaffected.

### 11.2 Use Case: Cloud-to-Edge

1. Agent starts computation on server (x86_64, little-endian)
2. Agent hits a long-running operation (e.g., neural inference)
3. Agent executes `SNAPSHOT` → serializes to 4KB buffer
4. Buffer is transmitted to edge device (ARM, big-endian)
5. Edge device executes `RESTORE` → byte-swaps, resumes execution
6. Agent completes task on edge device, executes `PULSE` with result

---

## 12. CLI / Shell Bridge (The Multiplexer)

The CLI is not just a debugger — it is a **multiplexer** for multiple VM contexts.

### 12.1 Commands

```
Command          Description
---------------  ------------------------------------------------
load <file>      Load .fluxb module into current context
unload <slot>    Unload module from jump table
peek <reg>        Read register value without pausing execution
poke <reg> <val>  Write register value (triggers watchpoint if set)
step <n>           Execute n cycles
run               Execute until HALT or breakpoint
breakpoint <addr> Set breakpoint at bytecode offset
watch <reg>        Trigger break when register changes
reload <slot>     Hot-swap module in zone 0x0800–0x0FFF
context <id>      Switch to different shell context
list              Show all active contexts
snapshot <file>   Save current VM state to file
restore <file>    Restore VM state from file
cap <agent>      Show capability mask of agent
grant <agent> <bit> Grant capability to agent
revoke <agent> <bit> Revoke capability from agent
```

### 12.2 Live Inspection Example

```
flux> context sailor_unit_1
[sailor_unit_1] flux> peek R14
R14 (RP) = 0x00002000 → heap base
[sailor_unit_1] flux> peek R15
R15 (PM) = 0x0003 (CAP_IO_BASIC | CAP_IO_NETWORK)
[sailor_unit_1] flux> step 14
14 cycles executed. HALT at offset 0x00C8.
[sailor_unit_1] flux> snapshot sailor_1.snap
Snapshot saved: 1,247 bytes.

flux> context admiral_unit_0
[admiral_unit_0] flux> restore sailor_1.snap
Restored sailor_unit_1 state into admiral_unit_0 context.
[admiral_unit_0] flux> peek R15
R15 (PM) = 0x0003 (inherited from snapshot)
[admiral_unit_0] flux> grant admiral_unit_0 0x0800
Granted CAP_JIT_HOTPATH.
```

---

## 13. Migration Path from v2.x (Tutor Era)

### 13.1 Opcode Remapping

Old opcodes are aliased to new system primitives:

```
Old (v2.x)     New (v3.0)         Rationale
-----------    ---------          ---------
TELL           PULSE              Lesson text = signal to student agent
ASK            POLL               Exercise prompt = blocking read
DELEGATE       FORK + HANDSHAKE   Spawn subagent = fork VM + A2A connect
BROADCAST      BROADCAST          Unchanged
WITNESS        WITNESS            Unchanged (now used for any branch)
SNAPSHOT       SNAPSHOT           Unchanged (now endian-independent)
LESSON         CALL + PULSE       Lesson = function call + signal output
EXERCISE       CALL + POLL        Exercise = function call + blocking input
ASSESS         CMP + SETCC        Assessment = comparison
SPAWN          FORK               Spawn = VM fork
CONNECT        HANDSHAKE          Connect = A2A handshake
MOVE           ENTER + LEAVE      Move = function call frame
LOOK           POLL_NONBLK        Look = non-blocking input
SUBMIT         PULSE              Submit = signal output
READ           LOAD               Read = memory load
WRITE          STORE              Write = memory store
```

### 13.2 Register Remapping

Old semantic mapping is preserved as a **personality layer**:

```
Old (v2.x)     New (v3.0)         Personality Register
-----------    ---------          --------------------
R14=XP         R14=RP             RP points to XP block in heap
R15=Status     R15=PM             PM encodes level as capability bits
```

A **Tutor Personality Module** (`flux:tutor`) can be loaded into zone 0x0400. It provides helper functions that interpret RP/PM the old way, allowing existing `.fluxb` tutor modules to run unmodified on v3.0.

---

## 14. Open Questions

1. **JIT Backend Selection:** Cranelift (Rust-native) vs LLVM (mature) vs custom (smaller footprint)?
2. **MMIO Trap Performance:** How fast can Host object callbacks execute? Target: <100ns per trap.
3. **A2A Transport:** WebSocket vs QUIC vs shared memory? Fleet Matrix Bridge currently uses WebSocket on port 6168.
4. **GC Strategy:** Cooperative (VM-triggered) vs concurrent (background thread) vs reference counting (simplest)?
5. **SIMD Width:** 128-bit (NEON/SSE) vs 256-bit (AVX) vs 512-bit (AVX-512)? Target edge devices may only support NEON.

---

## 15. References

- `flux-research/ARCHITECTURE.md` — FM's original ISA design
- `flux-research/compiler-interpreter-deep-dive.md` — 6-tier compilation path
- `flux-runtime/src/flux/bytecode/opcodes.py` — 184-opcode reference
- `flux-runtime/src/flux/a2a/messages.py` — A2A binary protocol
- `flux-runtime/src/flux/vm/interpreter.py` — VM implementation
- `cocapn-tutor/cocapn_tutor_flux.py` — v2.x tutor bytecode proof-of-concept
- `cocapn-shells/cocapn_shells_flux.py` — v2.x register file proof-of-concept

---

*CCC, Fleet I&O Officer / Breeder*  
*"Day one. Begin recording everything about this one."*
