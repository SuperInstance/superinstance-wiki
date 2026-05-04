# FLUX Global Jump Table Memory Map v3.0

**Companion to:** `CCC-FLUX-VECTOR-TABLE-v3.0-SPEC-2026-05-04.md`  
**Purpose:** Visual reference for developers implementing the FLUX kernel

---

## Overview

The Global Jump Table (GJT) is a 64KB address space (0x0000–0xFFFF) shared across all modules in a FLUX VM instance. It is divided into fixed zones. Each zone has specific access rules, initialization requirements, and hot-swap policies.

---

## Memory Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GLOBAL JUMP TABLE (64KB)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ 0x0000 │ Vector Table          │ 16 entries × 4 bytes = 64 bytes            │
│        │ (Reserved System)     │ _VT_INIT, _VT_SIGNAL, _VT_ERROR, _VT_EXIT   │
│        │                       │ _VT_TICK, _VT_GC, _VT_SNAPSHOT, _VT_RESTORE │
│        │                       │ _VT_CAP_ENTER, _VT_CAP_LEAVE                │
│        │                       │ _VT_MODULE_LOAD, _VT_MODULE_UNLOAD          │
│        │                       │ _VT_FORK, _VT_YIELD, _VT_HANDSHAKE          │
│        │                       │ _VT_RESERVED                                │
├────────┼───────────────────────┼──────────────────────────────────────────────┤
│ 0x0010 │ flux:core             │ IO.pulse, IO.poll, IO.poll_nonblk           │
│ 0x003F │ (Core Runtime)        │ IO.stream_open, IO.stream_close             │
│        │ 48 slots              │ IO.stream_push, IO.stream_pull              │
│        │                       │ MEM.copy, MEM.alloc, MEM.free               │
│        │                       │ MEM.barrier, REGION_CREATE, REGION_DESTROY  │
├────────┼───────────────────────┼──────────────────────────────────────────────┤
│ 0x0040 │ flux:sync             │ SYNC.fork, SYNC.yield, SYNC.join            │
│ 0x007F │ (Synchronization)     │ SYNC.barrier, SYNC.handshake                │
│        │ 64 slots              │ SYNC.clock, SYNC.formation_update           │
│        │                       │ SYNC.emergency_stop, SYNC.reduce            │
│        │                       │ SYNC.broadcast                              │
├────────┼───────────────────────┼──────────────────────────────────────────────┤
│ 0x0080 │ flux:math             │ FPU.add, FPU.sub, FPU.mul, FPU.div          │
│ 0x00BF │ (Math / FPU)          │ FMA, STAT.profile, STAT.hotpath             │
│        │ 64 slots              │ VLOAD, VSTORE, VADD, VSUB, VMUL, VDOT       │
│        │                       │ (Requires CAP_MATH_FPU / CAP_MATH_SIMD)     │
├────────┼───────────────────────┼──────────────────────────────────────────────┤
│ 0x00C0 │ flux:sec              │ CAP.mask, CAP.elevate, CAP.revoke           │
│ 0x00FF │ (Security)            │ CAP.require, CAP.request, CAP.grant         │
│        │ 64 slots              │ VAULT.seal, VAULT.unseal, TRUST.check       │
│        │                       │ SIG.halt, SIG.kill, SIG.segv_handler        │
├────────┼───────────────────────┼──────────────────────────────────────────────┤
│ 0x0100 │ flux:util             │ STR.transcode, STR.length, STR.concat       │
│ 0x01FF │ (String & Data)       │ STR.slice, STR.find, STR.replace            │
│        │ 256 slots             │ DATA.pack, DATA.unpack, DATA.json           │
│        │                       │ DATA.xml, DATA.csv, DATA.base64             │
│        │                       │ (Uses .fluxvocab for 80+ language support)  │
├────────┼───────────────────────┼──────────────────────────────────────────────┤
│ 0x0200 │ Reserved StdLib       │ Future standard library expansion            │
│ 0x03FF │ 512 slots             │ (Locked until v3.1 ABI revision)            │
├────────┼───────────────────────┼──────────────────────────────────────────────┤
│ 0x0400 │ User Modules          │ Application-specific .fluxb modules          │
│ 0x07FF │ 1024 slots            │ Loaded at runtime via IMPORT / jit_link()    │
│        │                       │ Examples: flux:tutor, flux:plato, flux:mud   │
├────────┼───────────────────────┼──────────────────────────────────────────────┤
│ 0x0800 │ Hot-Swap Zone         │ Live-reloadable modules                      │
│ 0x0FFF │ 2048 slots            │ Patched in real-time without VM pause        │
│        │                       │ CLI `reload` command targets this zone       │
│        │                       │ Ideal for: lessons, security protocols,      │
│        │                       │ configuration, A/B testing                   │
├────────┼───────────────────────┼──────────────────────────────────────────────┤
│ 0x1000 │ Agent Private         │ Per-agent private jump table                 │
│ 0x7FFF │ 28,672 slots          │ Deep-copied on SYNC.fork()                   │
│        │                       │ Not visible to other agents                  │
│        │                       │ Used for: agent-specific state,              │
│        │                       │ cached computations, private keys             │
├────────┼───────────────────────┼──────────────────────────────────────────────┤
│ 0x8000 │ Extended Memory       │ Memory-mapped I/O (MMIO)                     │
│ 0xFFFF │ 32,768 slots          │ Traps to Host object on access               │
│        │                       │ Used for: external APIs, databases,          │
│        │                       │ hardware peripherals, network sockets         │
└────────┴───────────────────────┴──────────────────────────────────────────────┘
```

---

## Zone Access Rules

| Zone | Writable By | Hot-Swappable | Fork-Copied | MMIO Trap |
|------|------------|---------------|-------------|-----------|
| 0x0000–0x03FF | Loader only | ❌ No | ❌ No | ❌ No |
| 0x0400–0x07FF | IMPORT opcode | ❌ No | ✅ Yes | ❌ No |
| 0x0800–0x0FFF | CLI `reload` | ✅ Yes | ✅ Yes | ❌ No |
| 0x1000–0x7FFF | Agent itself | ✅ Yes | ✅ Yes | ❌ No |
| 0x8000–0xFFFF | Host object | ❌ N/A | ❌ No | ✅ Yes |

---

## Module Loading Examples

### Example 1: Load flux:tutor into User Modules

```python
# Module: flux_tutor.fluxb
# Requested slot: 0x0420 (User Modules zone)

# Header
FLX 03 00 01 20 00       # Magic, v3.0, ABI rev 1, 32-bit, little-endian
00 00 00 10              # Vector Table offset = 0x10
00 00 03 FF              # Manifest offset = 0x03FF (end of file)

# Vector Table (64 bytes at 0x10)
# _VT_INIT = 0x50, _VT_SIGNAL = 0x60, ...

# Code section
# ... tutor bytecode ...

# Manifest at 0x03FF
MANI 00 01               # Magic, version 1
00 00 00 01              # Required caps: CAP_IO_BASIC
00 00 00 00              # Provided caps: none
00 02                    # 2 witness records
# ... witness records ...
00 01                    # 1 import
# ... import table ...
00 03                    # 3 exports
# ... export table ...
DE AD BE EF              # CRC32 checksum
```

### Example 2: JIT Link a "Sailor" Agent

```python
def jit_link_sailor():
    code = bytearray()
    # Header (16 bytes)
    code.extend(b"FLX\x03\x00\x01\x20\x00")
    code.extend(struct.pack("<I", 0x10))   # VT offset
    code.extend(struct.pack("<I", 0xFF))  # Manifest offset (placeholder)
    
    # Vector Table (64 bytes at 0x10)
    # _VT_INIT = 0x50, _VT_EXIT = 0x90, ...
    
    # Minimal code: call 3 stdlib modules, then halt
    code.extend([Op.CALL_IND, 0x10, 0x00])  # IO.pulse
    code.extend([Op.CALL_IND, 0x40, 0x00])  # SYNC.fork
    code.extend([Op.CALL_IND, 0x80, 0x00])  # FPU.add
    code.extend([Op.HALT])
    
    # Manifest (at end)
    # Required: CAP_IO_BASIC, CAP_SYNC_FORK
    # Provided: none
    
    return bytes(code)
# Result: ~90 bytes for a fully capable sailor agent
```

### Example 3: Hot-Swap a Security Protocol

```bash
# CLI session
flux> load security_protocol_v2.fluxb 0x0800
Loaded at slot 0x0800 (Hot-Swap Zone)

flux> context agent_1
[agent_1] flux> reload 0x0800
Hot-swapped slot 0x0800 without pausing execution
[agent_1] flux> peek R15
R15 (PM) = 0x0103 (CAP_IO_BASIC | CAP_IO_NETWORK | CAP_SEC_ELEVATE)
# Agent now has new security protocol without restart
```

---

## Capability-to-Zone Mapping

| Capability | Required For | GJT Zones Accessible |
|------------|-------------|----------------------|
| CAP_IO_BASIC | PULSE, POLL | 0x0000–0x03FF |
| CAP_IO_NETWORK | STREAM_OPEN, STREAM_PUSH | 0x0000–0x03FF, MMIO |
| CAP_IO_FILE | File MMIO | 0x8000–0xFFFF (file traps) |
| CAP_MEM_HEAP | REGION_CREATE > 2K | All zones |
| CAP_MEM_SHARED | REGION_TRANSFER | All zones |
| CAP_SYNC_FORK | FORK | 0x0040–0x007F |
| CAP_SYNC_HANDSHAKE | HANDSHAKE | 0x0040–0x007F, MMIO |
| CAP_SEC_ELEVATE | CAP.elevate | 0x00C0–0x00FF |
| CAP_SEC_VAULT | VAULT.seal | 0x00C0–0x00FF |
| CAP_MATH_FPU | FADD, FSUB, FMUL, FDIV | 0x0080–0x00BF |
| CAP_MATH_SIMD | VLOAD, VSTORE, VADD, VSUB | 0x0080–0x00BF |
| CAP_JIT_HOTPATH | JIT compilation | 0x0000–0x03FF (runtime zone) |
| CAP_MODULE_IMPORT | IMPORT opcode | 0x0400–0x07FF |
| CAP_MODULE_EXPORT | Export table | 0x0400–0x07FF |
| CAP_VM_ADMIN | reload, shutdown | All zones |

---

## Address Space Visualization

```
┌────────────────────────────────────────────────────────────────────────────┐
│ 0xFFFF  Extended Memory (MMIO)     ████████████████████████████████ 32K   │
│         Host-mapped: APIs, DB, HW    Traps to Host object on access          │
├────────────────────────────────────────────────────────────────────────────┤
│ 0x8000  Agent Private               ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 28K   │
│         Per-agent, fork-copied       Private state, caches, keys             │
├────────────────────────────────────────────────────────────────────────────┤
│ 0x1000  Hot-Swap Zone               ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ 8K    │
│         Live-reloadable              Lessons, configs, protocols             │
├────────────────────────────────────────────────────────────────────────────┤
│ 0x0800  User Modules                ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 4K    │
│         Application modules          flux:tutor, flux:plato, etc.           │
├────────────────────────────────────────────────────────────────────────────┤
│ 0x0400  Reserved StdLib             ································ 2K    │
│         Future expansion             Locked until v3.1                       │
├────────────────────────────────────────────────────────────────────────────┤
│ 0x0200  flux:util                   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1K    │
│         String, data, encoding       STR.transcode, DATA.pack                 │
├────────────────────────────────────────────────────────────────────────────┤
│ 0x0100  flux:sec                    ══════════════════════════════ 1K    │
│         Security layer               CAP, VAULT, TRUST                        │
├────────────────────────────────────────────────────────────────────────────┤
│ 0x00C0  flux:math                   ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪ 1K    │
│         FPU, SIMD, statistics        FPU.add, VLOAD, STAT.profile             │
├────────────────────────────────────────────────────────────────────────────┤
│ 0x0080  flux:sync                   ▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫▫ 1K    │
│         Multi-agent primitives       FORK, YIELD, HANDSHAKE                   │
├────────────────────────────────────────────────────────────────────────────┤
│ 0x0040  flux:core                   ○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○○ 1K    │
│         IO, memory primitives        PULSE, POLL, MEM.copy                    │
├────────────────────────────────────────────────────────────────────────────┤
│ 0x0010  Vector Table                ●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●● 64B   │
│         System function pointers     _VT_INIT, _VT_SIGNAL, _VT_ERROR          │
└────────────────────────────────────────────────────────────────────────────┘
         0x0000
```

---

*CCC, Fleet I&O Officer / Breeder*  
*"The map is not the territory, but without the map, the fleet is lost."*
