# SuperInstance GPU Dispatch Architecture
## Complete RTX 4050 ↔ CUDAclaw Integration Spec v1.0

**Date:** 2026-05-31  
**Target Hardware:** NVIDIA RTX 4050 Laptop GPU (SM 8.9, 20 SMs, 7.0 GB VRAM, 24 MB L2, 192 GB/s)  
**Host CPU:** AMD Ryzen AI 9 HX 370 (12C/24T, AVX-512 + VNNI + FMA, 16 MB L3)  
**Dispatch Core:** CUDAclaw 32K LOC — volatile writes (~50 ns), unified memory command queues, persistent warp-level kernels, SmartCRDT consensus, cell agents, ML feedback, NVRTC runtime compilation, DNA mutation  
**Bridge Crate:** `lau-cudaclaw-bridge` (GpuDispatch trait)  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Hardware Topology & Memory Budget](#2-hardware-topology--memory-budget)
3. [CUDAclaw Dispatch Primitives](#3-cudaclaw-dispatch-primitives)
4. [Layer 1 — Conservation Spectral Framework](#4-layer-1--conservation-spectral-framework)
5. [Layer 2 — Constraint Ecosystem](#5-layer-2--constraint-ecosystem)
6. [Layer 3 — Cocapn Fleet](#6-layer-3--cocapn-fleet)
7. [Layer 4 — PLATO Nervous System](#7-layer-4--plato-nervous-system)
8. [Layer 5 — ForgeFlux](#8-layer-5--forgeflux)
9. [Layer 6 — Grand Pattern](#9-layer-6--grand-pattern)
10. [Layer 7 — Shell System / Hermes](#10-layer-7--shell-system--hermes)
11. [Layer 8 — lau-* Math](#11-layer-8--lau--math)
12. [Layer 9 — lau-* Physics](#12-layer-9--lau--physics)
13. [Unified Command Queue Schema](#13-unified-command-queue-schema)
14. [Kernel Variant Selection Matrix](#14-kernel-variant-selection-matrix)
15. [Appendix: GpuDispatch Implementations](#15-appendix-gpudispatch-implementations)

---

## 1. Executive Summary

This document specifies how all 9 layers of the SuperInstance ecosystem dispatch compute to the RTX 4050 through CUDAclaw's unified memory command queue. Every layer implements `GpuDispatch` from `lau-cudaclaw-bridge`. The architecture exploits:

- **Volatile dispatch** (~50 ns submit latency) for fire-and-forget workloads
- **Persistent warp-cooperative kernels** for CRDT, agent, and scheduling workloads
- **One-shot NVRTC kernels** for PDE, FFT, and matrix workloads that exceed warp capacity
- **Unified memory** for zero-copy data sharing between Rust host and CUDA device
- **ML feedback loop** (CUDAclaw `execution_log` → `success_analyzer` → `dna_mutator`) to evolve kernel parameters per layer

**Design constraint:** 7.0 GB VRAM is tight for a 280-repo ecosystem. We adopt a **unified memory paging** model with hot data resident on device and cold data migrated on demand by the CUDA driver. The L2 cache (24 MB) is treated as a critical shared resource; kernels are tuned for L2 residency.

---

## 2. Hardware Topology & Memory Budget

```
┌─────────────────────────────────────────────────────────────────┐
│  AMD Ryzen AI 9 HX 370                                          │
│  ├── 12C/24T @ ~5.1 GHz boost                                   │
│  ├── AVX-512 (512-bit SIMD) + VNNI + FMA                        │
│  ├── 48 KB L1d/core, 1 MB L2/core, 16 MB L3 shared              │
│  └── DDR5/LPDDR5x host memory ──┐                               │
│                                 │ PCIe 4.0 x8 (~16 GB/s)        │
│  ┌──────────────────────────────┴─────────────────────────────┐ │
│  │  RTX 4050 Laptop GPU                                       │ │
│  │  ├── Ada Lovelace SM 8.9                                   │ │
│  │  ├── 20 SMs × 128 CUDA cores/SM = 2,560 CUDA cores         │ │
│  │  ├── 80 Tensor Cores (4th-gen, FP8/FP16/BF16)              │ │
│  │  ├── 20 RT Cores (3rd-gen)                                 │ │
│  │  ├── 24 MB L2 cache                                        │ │
│  │  ├── 192 GB/s memory bandwidth (96-bit bus)                │ │
│  │  ├── 7.0 GB VRAM (GDDR6)                                   │ │
│  │  └── NVRTC / CUDA 12.x runtime                             │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Memory Budget Allocation (7.0 GB)

| Pool | Size | Purpose |
|------|------|---------|
| `Unified Command Queues` | 64 MB | 1024-slot ring buffers × 4 priority streams |
| `SmartCRDT Cell Store` | 128 MB | Spreadsheet / agent cell grids (SoA) |
| `lau-Math Workspace` | 1.5 GB | PDE grids, FFT buffers, matrix tiles |
| `lau-Physics Workspace` | 1.5 GB | Navier-Stokes fields, Maxwell grids, wavefunctions |
| `PLATO State Vectors` | 512 MB | Room embeddings, JEPA latent buffers |
| `ForgeFlux Tiles` | 256 MB | Compressed tile atlases, decomposition buffers |
| `Cocapn Fleet Health` | 128 MB | Consensus vectors, health scoring tables |
| `Grand Pattern Graph` | 256 MB | Cellular adjacency, edge weights, PageRank |
| `Shell/Hermes Dispatch` | 64 MB | Agent dispatch schedules, priority heaps |
| `Spectral Eigenvalue` | 256 MB | Laplacian operator, eigenvector buffers |
| `Constraint MLIR` | 128 MB | Harmonic tension buffers, dialect tensor memory |
| `NVRTC Cache + PTX` | 128 MB | Runtime-compiled kernels, DNA-mutated variants |
| `ML Feedback Ring` | 64 MB | Execution logs, success histograms |
| **Reserved / Slack** | **2.1 GB** | Driver overhead, runtime growth, safety margin |

---

## 3. CUDAclaw Dispatch Primitives

### 3.1 VolatileDispatcher (Hot Path)

```rust
// ~50 ns submit; no locks, no cudaDeviceSynchronize on hot path
pub struct VolatileDispatcher {
    queue_ptr: *mut CommandQueueHost,  // Unified Memory
    cached_head: u32,
    next_id: AtomicU32,
}

impl VolatileDispatcher {
    pub fn submit_volatile(&mut self, mut cmd: Command) -> Result<u32, Error> {
        let cmd_id = self.next_id.fetch_add(1, Ordering::SeqCst);
        cmd.id = cmd_id;
        let head_idx = (self.cached_head % QUEUE_SIZE as u32) as usize;
        unsafe {
            ptr::write_volatile(&mut queue.commands[head_idx], cmd);
            let new_head = (self.cached_head + 1) % QUEUE_SIZE as u32;
            ptr::write_volatile(&mut queue.head, new_head);
            ptr::write_volatile(&mut queue.status, QueueStatus::Ready as u32);
        }
        self.cached_head = new_head;
        Ok(cmd_id)
    }
}
```

### 3.2 Persistent Kernel Model

The GPU runs a single persistent kernel (`persistent_worker`) launched with 1 block / 1 thread at system init. Inside the kernel:

- **Warp 0, Lane 0:** Polls `queue.head` via `volatile` + `__threadfence_system()`
- **Lanes 1–31:** Idle until broadcast via `__shfl_sync()`
- On command arrival: Lane 0 broadcasts command type + payload pointer
- All 32 lanes process in parallel (warp-cooperative)
- Lane 0 writes `queue.tail` and signals completion

For workloads that need more than 32 threads (matmul, PDE, FFT), the persistent kernel enqueues a **child grid** via CUDA dynamic parallelism or signals the host to launch a one-shot kernel on a secondary stream.

### 3.3 Command Encoding

```rust
#[repr(C, packed(4))]
pub struct Command {
    pub cmd_type: u32,      // 0–3
    pub id: u32,            // 4–7
    pub timestamp: u64,     // 8–15
    pub data_a: f64,        // 16–23
    pub data_b: f64,        // 24–31
    pub result: f64,        // 32–39
    pub batch_data: u64,    // 40–47  // unified memory pointer to payload
}
```

`batch_data` is the universal pointer slot. For large payloads (matrices, grids, graphs), the host allocates a `UnifiedBuffer<T>` and passes its device pointer in `batch_data`. The kernel dereferences it directly—zero copy.

---

## 4. Layer 1 — Conservation Spectral Framework

### What Gets Dispatched
- **Laplacian eigenvalue computation** (sparse symmetric matrices up to 10⁶ × 10⁶)
- **Spectral clustering** (k-means on eigenvectors)
- **Graph Fourier transforms** (GFT on conservation networks)

### CUDAclaw Connection
```rust
impl GpuDispatch for SpectralDispatch {
    fn label(&self) -> &str { "SpectralDispatch" }

    fn dispatch(&self, ctx: &DispatchContext) -> Result<DispatchResult> {
        // Encode as CommandType::Custom with sub-op 0x1001
        let cmd = Command::new(CommandType::Custom, ctx.next_id())
            .with_data(0x1001, self.matrix_nnz as f64)
            .with_batch_data(self.unified_csr_ptr);
        ctx.volatile_dispatcher.submit_volatile(cmd)
    }
}
```

### GPU Kernel
- **Type:** One-shot (not persistent) — Lanczos iteration needs thousands of thread blocks
- **Launch config:** `<<< (n + 255)/256, 256 >>>` for SpMV; `<<< 20, 256 >>>` for Gram-Schmidt orthogonalization (one block per SM)
- **Warp usage:** Warp-level reduction for dot products; `__shfl_down_sync` for partial sums

### Memory Layout
- **CSR matrix:** Device-only (unified memory allocated, then prefetched to device with `cudaMemPrefetchAsync`)
- **Krylov vectors:** Unified (host needs to inspect convergence)
- **Eigenvectors:** Staged to host only when converged

### Expected Speedup
| Operation | CPU (AVX-512) | GPU RTX 4050 | Speedup |
|-----------|---------------|--------------|---------|
| SpMV (1M×1M, 10M nnz) | 12 ms | 0.8 ms | **15×** |
| Lanczos step (k=100) | 180 ms | 12 ms | **15×** |
| Full spectrum (20 eigenpairs) | 4.2 s | 280 ms | **15×** |

### GpuDispatch Integration
```rust
pub struct SpectralDispatch {
    pub csr: UnifiedBuffer<CsrRow>,
    pub vals: UnifiedBuffer<f64>,
    pub n: usize,
    pub k: usize, // eigenpairs requested
}
```

---

## 5. Layer 2 — Constraint Ecosystem

### What Gets Dispatched
- **Harmonic tension computation** (MLIR dialect lowering to tensor ops)
- **Constraint satisfaction propagation** (parallel AC-3 on GPU)
- **Geometric twin validation** (tensor contraction against constraint mask)

### CUDAclaw Connection
```rust
impl GpuDispatch for ConstraintDispatch {
    fn dispatch(&self, ctx: &DispatchContext) -> Result<DispatchResult> {
        let cmd = Command::new(CommandType::Custom, ctx.next_id())
            .with_data(0x2001, self.tension_dim as f64)
            .with_batch_data(self.unified_tensor_ptr);
        ctx.volatile_dispatcher.submit_volatile(cmd)
    }
}
```

### GPU Kernel
- **Type:** Persistent for light constraint checks; one-shot for full tensor contractions
- **Persistent variant:** Warp-cooperative `crdt_write_cell`-style pattern where each lane evaluates one constraint clause
- **One-shot variant:** Tiled matrix multiply (constraint matrix × variable vector) using SM 8.9 Tensor Cores in FP16/BF16 accumulation

### Memory Layout
- **Constraint tensor:** Unified memory with `cudaMemAdviseSetReadMostly` (read by many warps, written rarely)
- **Variable state:** Device-only (hot); synced to host only on checkpoint
- **Tension scores:** Unified (host MLIR pass reads them to decide next rewrite)

### Expected Speedup
| Operation | CPU | GPU | Speedup |
|-----------|-----|-----|---------|
| Harmonic tension (1M vars) | 45 ms | 2.5 ms | **18×** |
| AC-3 propagation | 120 ms | 8 ms | **15×** |
| Tensor contraction (4D) | 800 ms | 40 ms | **20×** |

### GpuDispatch Integration
```rust
pub struct ConstraintDispatch {
    pub op: ConstraintOp, // HarmonicTension | Ac3Propagate | TensorContract
    pub tensor: UnifiedBuffer<f64>,
    pub shape: Vec<usize>,
    pub mask: UnifiedBuffer<u32>, // bit-mask per variable
}
```

---

## 6. Layer 3 — Cocapn Fleet

### What Gets Dispatched
- **Fleet consensus** (SmartCRDT merge across 20+ agents)
- **Health scoring** (parallel reduction over agent heartbeat vectors)
- **Anomaly detection** (small neural network forward pass per agent)

### CUDAclaw Connection
The Cocapn Fleet uses CUDAclaw's **native SmartCRDT engine**. Each fleet agent maps to a `CellAgent` in the GPU grid.

```rust
impl GpuDispatch for FleetConsensusDispatch {
    fn dispatch(&self, ctx: &DispatchContext) -> Result<DispatchResult> {
        // Direct CRDT edit command — processed by persistent kernel
        let edit = SpreadsheetEdit {
            cell_id: CellID { row: self.fleet_id, col: self.agent_id },
            new_type: CellValueType::Number,
            numeric_value: self.health_score,
            timestamp: self.lamport_clock,
            node_id: self.node_id,
            ..Default::default()
        };
        ctx.volatile_dispatcher.submit_spreadsheet_edit(cells_ptr, edit)
    }
}
```

### GPU Kernel
- **Type:** Persistent (always resident)
- **Consensus:** `warp_recalculate_cells` from `crdt_engine.cuh` — each lane merges one cell's version vector
- **Health scoring:** Warp-parallel reduction (`__shfl_down_sync`) over 32 heartbeat metrics per agent

### Memory Layout
- **Fleet grid:** Unified memory SoA (`CellAgentSoA`) — host reads health scores, GPU writes them
- **Consensus log:** Device-only ring buffer (256 KB per fleet node)
- **CRDT state:** Unified memory with `cudaMemAdviseSetPreferredLocation(device)`

### Expected Speedup
| Operation | CPU | GPU | Speedup |
|-----------|-----|-----|---------|
| CRDT merge (1K cells) | 3 ms | 80 µs | **37×** |
| Health reduction (20 agents × 64 metrics) | 200 µs | 5 µs | **40×** |
| Anomaly NN (20 × 128→64→1) | 1.2 ms | 60 µs | **20×** |

### GpuDispatch Integration
```rust
pub struct FleetConsensusDispatch {
    pub fleet_id: u32,
    pub agent_id: u32,
    pub health_score: f64,
    pub lamport_clock: u64,
    pub node_id: u32,
}

impl GpuDispatch for FleetHealthDispatch {
    fn estimated_flops(&self) -> u64 {
        // 20 agents × 64 metrics = 1280 reductions
        1280
    }
}
```

---

## 7. Layer 4 — PLATO Nervous System

### What Gets Dispatched
- **Room state vector embedding** (high-dimensional state → compressed latent)
- **JEPA prediction** (Joint Embedding Predictive Architecture forward + loss)
- **Attention routing** (sparse attention over room graph)

### CUDAclaw Connection
```rust
impl GpuDispatch for PlatoJepaDispatch {
    fn dispatch(&self, ctx: &DispatchContext) -> Result<DispatchResult> {
        let cmd = Command::new(CommandType::Custom, ctx.next_id())
            .with_data(0x4001, self.batch_size as f64)
            .with_batch_data(self.unified_jepa_ptr);
        ctx.volatile_dispatcher.submit_volatile(cmd)
    }
}
```

### GPU Kernel
- **Type:** One-shot with persistent micro-batching
- **JEPA encoder:** Tiled matmul (layers 512→256→128) using `lau-cuda-kernels` matmul PTX
- **Predictor:** Warp-cooperative LSTM cell unrolling (32 timesteps per warp)
- **Loss backward:** Only forward is on GPU; backward stays on CPU (PyTorch/ TinyGrad interop) unless NVRTC compains a custom backward kernel

### Memory Layout
- **State vectors:** Unified (host needs to serialize to room DB)
- **JEPA weights:** Device-only (loaded once at init, 12 MB total)
- **Attention mask:** Unified (sparse CSR, updated by host graph changes)

### Expected Speedup
| Operation | CPU | GPU | Speedup |
|-----------|-----|-----|---------|
| Room embed (batch 64) | 18 ms | 1.1 ms | **16×** |
| JEPA forward (batch 64) | 45 ms | 2.8 ms | **16×** |
| Sparse attention (4K rooms) | 220 ms | 14 ms | **16×** |

### GpuDispatch Integration
```rust
pub struct PlatoJepaDispatch {
    pub state_vectors: UnifiedBuffer<f32>,
    pub batch_size: usize,
    pub predictor_steps: usize,
}

impl GpuDispatch for PlatoJepaDispatch {
    fn uses_gpu(&self) -> bool { true }
    fn estimated_flops(&self) -> u64 {
        // (512*256 + 256*128) * 2 * batch
        let params = (512*256 + 256*128) as u64;
        params * 2 * self.batch_size as u64
    }
}
```

---

## 8. Layer 5 — ForgeFlux

### What Gets Dispatched
- **Tile decomposition** (quadtree/octree spatial subdivision)
- **Compression** (wavelet transform per tile, entropy coding on CPU)
- **Delta encoding** (parallel diff across tile atlases)

### CUDAclaw Connection
```rust
impl GpuDispatch for ForgeFluxDispatch {
    fn dispatch(&self, ctx: &DispatchContext) -> Result<DispatchResult> {
        let cmd = Command::new(CommandType::Custom, ctx.next_id())
            .with_data(0x5001, self.tile_count as f64)
            .with_batch_data(self.unified_tile_ptr);
        ctx.volatile_dispatcher.submit_volatile(cmd)
    }
}
```

### GPU Kernel
- **Type:** One-shot
- **Decomposition:** Parallel quadtree build — each thread claims a leaf node via `atomicCAS` on a node allocation counter
- **Wavelet:** Lifting scheme in shared memory (tiles of 16×16 pixels, 256 threads)
- **Delta:** Element-wise subtraction kernel (`ElementOp::Sub` via `MathBridge`)

### Memory Layout
- **Tile atlas:** Unified (host uploads new tiles, GPU reads/writes compressed)
- **Quadtree nodes:** Device-only (rebuilt each frame)
- **Wavelet coefficients:** Staged to host for entropy coding (CPU does Huffman/ANS)

### Expected Speedup
| Operation | CPU | GPU | Speedup |
|-----------|-----|-----|---------|
| Quadtree build (64K tiles) | 35 ms | 2.2 ms | **16×** |
| 2D wavelet (4K×4K) | 180 ms | 9 ms | **20×** |
| Delta encode (4K×4K) | 12 ms | 0.5 ms | **24×** |

### GpuDispatch Integration
```rust
pub struct ForgeFluxDispatch {
    pub op: ForgeOp, // Decompose | Wavelet | Delta
    pub tiles: UnifiedBuffer<Tile>,
    pub atlas: UnifiedBuffer<f32>, // RGBA or depth
}
```

---

## 9. Layer 6 — Grand Pattern

### What Gets Dispatched
- **Cellular graph simulation** (cellular automata on graph neighborhoods)
- **PageRank / diffusion** (power iteration on adjacency)
- **Community detection** (Louvain method — label propagation on GPU)

### CUDAclaw Connection
```rust
impl GpuDispatch for GrandPatternDispatch {
    fn dispatch(&self, ctx: &DispatchContext) -> Result<DispatchResult> {
        let cmd = Command::new(CommandType::Custom, ctx.next_id())
            .with_data(0x6001, self.node_count as f64)
            .with_batch_data(self.unified_graph_ptr);
        ctx.volatile_dispatcher.submit_volatile(cmd)
    }
}
```

### GPU Kernel
- **Type:** Persistent for small graphs (< 32K nodes, processed in warp bursts); one-shot for large graphs
- **Cellular update:** Warp-cooperative — each lane handles one neighbor in the adjacency list
- **PageRank:** One-shot, grid-stride loop over edges (coalesced CSR access)
- **Label propagation:** One-shot, each thread claims a node, scans neighbors in shared memory

### Memory Layout
- **Adjacency CSR:** Device-only (large, read-many)
- **Node states:** Unified (host visualizer reads colors/labels)
- **Edge weights:** Device-only

### Expected Speedup
| Operation | CPU | GPU | Speedup |
|-----------|-----|-----|---------|
| Cellular step (100K nodes, avg deg 8) | 8 ms | 0.3 ms | **27×** |
| PageRank (1M nodes, 10M edges, 50 iter) | 2.5 s | 120 ms | **21×** |
| Label propagation (1M nodes) | 4.0 s | 180 ms | **22×** |

### GpuDispatch Integration
```rust
pub struct GrandPatternDispatch {
    pub op: GraphOp,
    pub graph: UnifiedBuffer<Graph>, // CSR format
    pub node_states: UnifiedBuffer<u32>,
}
```

---

## 10. Layer 7 — Shell System / Hermes

### What Gets Dispatched
- **Agent dispatch scheduling** (priority queue merge, conflict resolution)
- **Route planning** (parallel Dijkstra / A* from multiple agent sources)
- **Resource allocation** (auction algorithm on GPU)

### CUDAclaw Connection
The Shell System uses CUDAclaw as a **scheduler accelerator**. It dispatches scheduling commands at very high frequency (potentially >100K commands/sec), so the volatile path is critical.

```rust
impl GpuDispatch for HermesScheduleDispatch {
    fn dispatch(&self, ctx: &DispatchContext) -> Result<DispatchResult> {
        // Fire-and-forget: no sync needed; GPU updates schedule bitmap
        let cmd = Command::new(CommandType::Custom, ctx.next_id())
            .with_data(0x7001, self.priority as f64)
            .with_batch_data(self.unified_schedule_ptr);
        ctx.volatile_dispatcher.submit_volatile(cmd)
    }
}
```

### GPU Kernel
- **Type:** Persistent (always resident) — the scheduler kernel is part of the core persistent worker
- **Priority merge:** Warp-level bitonic sort on 32-element schedule chunks
- **Route planning:** One-shot wavefront expansion (BFS in shared memory) launched by persistent kernel when batch size > threshold

### Memory Layout
- **Schedule bitmap:** Unified memory (host submits jobs, GPU assigns slots)
- **Agent routes:** Device-only (written by GPU, bulk-copied to host on request)
- **Resource prices:** Unified (auction needs host visibility for logging)

### Expected Speedup
| Operation | CPU | GPU | Speedup |
|-----------|-----|-----|---------|
| Priority merge (1K tasks) | 350 µs | 12 µs | **29×** |
| Multi-source BFS (100 sources) | 25 ms | 1.5 ms | **17×** |
| Auction round (500 agents × 50 resources) | 18 ms | 0.9 ms | **20×** |

### GpuDispatch Integration
```rust
pub struct HermesScheduleDispatch {
    pub priority: u32,
    pub agent_id: u64,
    pub task_descriptor: UnifiedBuffer<u8>,
}

impl GpuDispatch for HermesScheduleDispatch {
    fn estimated_flops(&self) -> u64 { 0 } // scheduling is memory-bound
}
```

---

## 11. Layer 8 — lau-* Math

### What Gets Dispatched
- **PDE solvers** (5-point Laplacian, explicit Euler, Crank-Nicolson)
- **FFT** (1D/2D Cooley-Tukey, Bluestein for prime sizes)
- **Matrix ops** (matmul, LU, Cholesky, QR, SVD approximations)
- **Reduction / scan** (prefix sum, histogram, argmin/argmax)

### CUDAclaw Connection
This is the **primary consumer** of `lau-cudaclaw-bridge`. All operations map to the `MathOp` enum.

```rust
impl GpuDispatch for LauMathDispatch {
    fn dispatch(&self, ctx: &DispatchContext) -> Result<DispatchResult> {
        let math_bridge = MathBridge::new();
        let result = match &self.op {
            MathOp::MatMul { a_shape, b_shape } => {
                // Route to lau-cuda-kernels tiled matmul
                math_bridge.dispatch_op(&self.op, &self.input)
            }
            MathOp::Fft { n } => {
                // Route to lau-cuda-kernels radix-2 FFT PTX
                math_bridge.dispatch_op(&self.op, &self.input)
            }
            MathOp::ElementWise { n, op } => {
                // Persistent kernel lane broadcast for small n;
                // one-shot grid-stride for large n
                math_bridge.dispatch_op(&self.op, &self.input)
            }
            _ => math_bridge.dispatch_op(&self.op, &self.input),
        }?;
        Ok(DispatchResult { success: true, gpu_used: true, .. })
    }
}
```

### GPU Kernels
| Operation | Kernel Type | Launch Config | Shared Memory |
|-----------|-------------|---------------|---------------|
| MatMul (f32) | One-shot tiled | `<<< (N+15)/16, (16,16) >>>` | 2 × 16×16 × 4 B = 2 KB |
| MatMul (f16 TC) | One-shot WMMA | `<<< (N+15)/16, (32,8) >>>` | 2 × 16×16 × 2 B = 1 KB |
| FFT 1D | One-shot radix-2 | `<<< n/2048, 1024 >>>` | 2 × 1024 × 8 B = 16 KB |
| FFT 2D | One-shot row+col | `<<< max(N,M), 256 >>>` | 8 KB |
| Laplacian | One-shot stencil | `<<< (N+31)/32, (32,8) >>>` | 34×10 × 8 B = 2.7 KB |
| Reduction | One-shot warp-reduce | `<<< (N+1023)/1024, 1024 >>>` | 4 KB |
| Prefix Sum | One-shot Brent-Kung | `<<< (N+1023)/1024, 1024 >>>` | 4 KB |

### Memory Layout
- **Matrices / grids:** Unified memory with prefetch to device before kernel, advise `ReadMostly` for RHS matrices
- **Factorizations:** Device-only (LU factors stay on GPU for repeated solves)
- **FFT twiddles:** Device-only constant memory (precomputed at init)

### Expected Speedup
| Operation | CPU (AVX-512) | GPU RTX 4050 | Speedup |
|-----------|---------------|--------------|---------|
| MatMul f32 (1024³) | 420 ms | 18 ms | **23×** |
| MatMul f16 TC (1024³) | — | 8 ms | **~50×** vs f32 CPU |
| FFT 1D (2²⁰) | 65 ms | 3.5 ms | **19×** |
| Laplacian (4096²) | 28 ms | 1.4 ms | **20×** |
| Prefix sum (10⁸) | 18 ms | 0.9 ms | **20×** |

### GpuDispatch Integration
Already fully implemented in `lau-cudaclaw-bridge/src/lib.rs` as `MathDispatch`, `PdeDispatch`, `NnDispatch`, `GraphDispatch`.

---

## 12. Layer 9 — lau-* Physics

### What Gets Dispatched
- **Navier-Stokes** (2D/3D incompressible flow, projection method)
- **Maxwell** (FDTD on Yee grid, 3D electromagnetic)
- **Schrödinger** (split-step Fourier, imaginary-time relaxation)

### CUDAclaw Connection
```rust
impl GpuDispatch for LauPhysicsDispatch {
    fn dispatch(&self, ctx: &DispatchContext) -> Result<DispatchResult> {
        let cmd = Command::new(CommandType::Custom, ctx.next_id())
            .with_data(0x9001, self.pde_type as f64)
            .with_batch_data(self.unified_field_ptr);
        ctx.volatile_dispatcher.submit_volatile(cmd)
    }
}
```

### GPU Kernels

#### Navier-Stokes (2D incompressible)
- **Advection:** Semi-Lagrangian backtracing in shared memory (tile + halo)
- **Diffusion:** Jacobi iteration in shared memory (red-black ordering for convergence)
- **Projection:** Poisson solver via FFT (`cufft` or custom radix-2) or multigrid
- **Type:** One-shot per timestep; host loops over timesteps

#### Maxwell (3D FDTD)
- **E-field update:** Grid-stride over Yee cells, coalesced `Ex/Ey/Ez` writes
- **H-field update:** Same pattern, offset by half-cell
- **PML:** Absorbing boundary in separate kernel (only 6 faces, not full volume)
- **Type:** One-shot per half-timestep

#### Schrödinger (Split-step)
- **Kinetic step:** FFT → multiply by kinetic propagator → inverse FFT
- **Potential step:** Element-wise multiplication (can use persistent kernel lane broadcast)
- **Type:** One-shot per timestep; FFT dominates

### Memory Layout
- **Velocity/pressure fields:** Device-only (entire simulation stays on GPU)
- **E/H fields:** Device-only (3D arrays, too large for frequent CPU sync)
- **Wavefunction:** Device-only (checkpointed to host every N steps)
- **Lookup tables (equation of state, refractive index):** Texture memory / constant cache

### Expected Speedup
| Operation | CPU (OpenMP 24T) | GPU RTX 4050 | Speedup |
|-----------|------------------|--------------|---------|
| NS 2D step (2048²) | 85 ms | 4.5 ms | **19×** |
| NS 3D step (256³) | 420 ms | 28 ms | **15×** |
| Maxwell 3D step (512³) | 650 ms | 35 ms | **19×** |
| Schrödinger split-step (1024³) | 1.2 s | 55 ms | **22×** |

### GpuDispatch Integration
```rust
pub enum PhysicsOp {
    NavierStokes2D { nx: usize, ny: usize, dt: f64, re: f64 },
    NavierStokes3D { nx: usize, ny: usize, nz: usize, dt: f64, re: f64 },
    Maxwell3D { nx: usize, ny: usize, nz: usize, dt: f64, courant: f64 },
    SchrodingerSplitStep { n: usize, dt: f64, potential: UnifiedBuffer<f64> },
}

pub struct LauPhysicsDispatch {
    pub op: PhysicsOp,
    pub fields: UnifiedBuffer<f64>,
    pub scratch: UnifiedBuffer<f64>, // for FFT / multigrid
}
```

---

## 13. Unified Command Queue Schema

To avoid command-type collisions across 9 layers, we use a **layer prefix** in the `data_a` field (high 16 bits) and **sub-op** (low 48 bits):

```
data_a encoding (f64 bit-cast to u64):
  [63:48] = Layer ID (0x01 – 0x09)
  [47:32] = Sub-operation
  [31:0]  = Scalar parameter (count, dimension, batch size)

cmd_type usage:
  NoOp          = heartbeat / keepalive
  Add/Sub/Mul/Div = scalar arithmetic (used by ML feedback DNA mutator)
  MatrixMultiply = lau-math matmul (small matrices via persistent kernel)
  MemoryCopy     = bulk unified memory prefetch / advise
  Custom         = layer-specific payload via batch_data pointer
  SetCellValue   = SmartCRDT cell update (Cocapn, Grand Pattern)
  SpreadsheetEdit = full cell edit with formula (ForgeFlux, Shell)
```

### Priority Streams

Four `CommandQueueHost` instances in unified memory, mapped to `DispatchPriority`:

| Stream | Priority | Layers | Use Case |
|--------|----------|--------|----------|
| `queue_critical` | Critical | Shell/Hermes, Cocapn Fleet | Scheduling, consensus (latency-sensitive) |
| `queue_high` | High | PLATO, lau-Physics | Real-time prediction, simulation timesteps |
| `queue_normal` | Normal | lau-Math, ForgeFlux, Grand Pattern | Batch computation, compression |
| `queue_low` | Low | Spectral, Constraint | Offline eigenvalue, MLIR lowering |

Each stream has its own persistent kernel thread block (4 blocks total, still fits in 20 SMs with massive headroom).

---

## 14. Kernel Variant Selection Matrix

CUDAclaw supports runtime kernel variant selection via `KernelVariant`. The ML feedback loop (`ml_feedback/dna_mutator.rs`) mutates DNA strings that map to variant choices.

| Workload Pattern | Recommended Variant | Rationale |
|------------------|---------------------|-----------|
| High queue depth (>100 cmd/sec) | `WarpAggregatedCas` | Reduces atomic contention on tail |
| Large data (matmul, PDE) | `L1Preferred` | Maximizes L1 hit rate for tiled algorithms |
| Small data, high frequency | `IdleSleep(50)` | Prevents thermal throttling when idle |
| CRDT / graph traversal | `ShmemPreferred` | Shared memory for adjacency / cell caches |
| Memory-bound (FFT, bandwidth) | `SoaLayout` | Structure-of-arrays for coalescing |
| Register-heavy (physics) | `SharedMemory(8192)` | Spills to shared instead of local |
| Tensor Core (WMMA) | `BlockSize(128)` | 4 warps × 32 threads optimal for mma.sync |

### DNA Mutation Example
```rust
// From cudaclaw/src/ml_feedback/dna_mutator.rs
pub fn mutate_kernel_dna(
    base_dna: &str,
    execution_log: &[AgentExecutionRecord],
) -> KernelVariant {
    let success_rate = compute_success_rate(execution_log);
    if success_rate < 0.85 {
        // Stress mutation: increase shared memory, reduce register pressure
        KernelVariant::SharedMemory(16384)
    } else if avg_latency(execution_log) > 5000.0 {
        // Latency mutation: warp-aggregated CAS + L1 preferred
        KernelVariant::WarpAggregatedCas
    } else {
        KernelVariant::Baseline
    }
}
```

---

## 15. Appendix: GpuDispatch Implementations

### 15.1 Trait Definition (from `lau-cudaclaw-bridge`)

```rust
pub trait GpuDispatch: Send + Sync {
    fn label(&self) -> &str;
    fn dispatch(&self, ctx: &DispatchContext) -> Result<DispatchResult>;
    fn uses_gpu(&self) -> bool { false }
    fn estimated_flops(&self) -> u64 { 0 }
}

pub struct DispatchContext {
    pub gpu_available: bool,
    pub device_id: u32,
    pub stream_id: u64,
    pub timeout_ms: u64,
    pub volatile_dispatcher: VolatileDispatcher,
}
```

### 15.2 Layer-Wrap Dispatch Macro

```rust
#[macro_export]
macro_rules! layer_dispatch {
    ($layer:expr, $ctx:expr, $layer_id:expr, $sub_op:expr, $payload:expr) => {{
        let cmd = Command::new(CommandType::Custom, $ctx.next_id())
            .with_data(
                f64::from_bits((($layer_id as u64) << 48) | (($sub_op as u64) << 32)),
                $payload.len() as f64,
            )
            .with_batch_data($payload.as_device_ptr() as u64);
        $ctx.volatile_dispatcher.submit_volatile(cmd)
    }};
}
```

### 15.3 Full Integration Example (lau-Physics)

```rust
// In lau-cudaclaw-bridge/src/lib.rs (proposed extension)

pub struct PhysicsDispatch {
    pub op: PhysicsOp,
    pub fields: UnifiedBuffer<f64>,
    pub scratch: UnifiedBuffer<f64>,
    pub gpu_avail: bool,
}

impl GpuDispatch for PhysicsDispatch {
    fn label(&self) -> &str { "PhysicsDispatch" }

    fn dispatch(&self, ctx: &DispatchContext) -> Result<DispatchResult> {
        let start = Instant::now();
        let field_size = self.fields.len() as u64 * 8;

        // Select kernel variant based on PDE type
        let variant = match &self.op {
            PhysicsOp::NavierStokes3D { .. } => KernelVariant::SharedMemory(8192),
            PhysicsOp::Maxwell3D { .. } => KernelVariant::L1Preferred,
            PhysicsOp::SchrodingerSplitStep { .. } => KernelVariant::SoaLayout,
            _ => KernelVariant::Baseline,
        };

        let cmd = Command::new(CommandType::Custom, ctx.next_id())
            .with_data(0x9001, self.op.discriminant() as f64)
            .with_batch_data(self.fields.as_device_ptr() as u64);

        ctx.volatile_dispatcher.submit_volatile(cmd)?;

        Ok(DispatchResult {
            success: true,
            gpu_used: ctx.gpu_available,
            elapsed_ns: start.elapsed().as_nanos() as u64,
            bytes_transferred: field_size * 2, // read + write
            metadata: vec![
                ("variant".into(), format!("{:?}", variant)),
                ("op".into(), format!("{:?}", self.op)),
            ],
        })
    }

    fn estimated_flops(&self) -> u64 {
        match &self.op {
            PhysicsOp::NavierStokes2D { nx, ny, .. } => (*nx * *ny * 50) as u64,
            PhysicsOp::NavierStokes3D { nx, ny, nz, .. } => (*nx * *ny * *nz * 80) as u64,
            PhysicsOp::Maxwell3D { nx, ny, nz, .. } => (*nx * *ny * *nz * 60) as u64,
            PhysicsOp::SchrodingerSplitStep { n, .. } => (*n * *n * 20) as u64,
        }
    }
}
```

### 15.4 RTX 4050 Tuning Constants

```rust
// Recommended for all kernel launches targeting RTX 4050
pub const RTX4050_SMS: u32 = 20;
pub const RTX4050_WARP_SIZE: u32 = 32;
pub const RTX4050_MAX_THREADS_PER_SM: u32 = 1536;
pub const RTX4050_MAX_REGISTERS_PER_SM: u32 = 65536;
pub const RTX4050_SHARED_MEM_PER_SM: u32 = 102400; // 100 KB (configurable partition)
pub const RTX4050_L2_CACHE_BYTES: u32 = 24 * 1024 * 1024;
pub const RTX4050_MEM_BW_GBPS: f32 = 192.0;

// Block size heuristics
pub const BLOCK_MATMUL: u32 = 256;      // 8 warps, good occupancy
pub const BLOCK_FFT: u32 = 1024;        // 32 warps, max parallelism per butterfly
pub const BLOCK_STENCIL: u32 = 256;     // 8×8 or 32×8 tile
pub const BLOCK_PERSISTENT: u32 = 32;   // 1 warp for command polling
pub const BLOCK_REDUCTION: u32 = 1024;  // 32 warps, tree reduction
```

---

## Document Metadata

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Author** | SuperInstance Architecture Agent |
| **Review Cycle** | Per DNA mutation epoch (auto-regenerated) |
| **Validation** | Compile against `lau-cudaclaw-bridge` v0.1 + `cudaclaw` v0.1 |
| **Next Steps** | (1) Implement `PhysicsDispatch` in bridge, (2) Add layer prefix to `executor.cu`, (3) Tune variants on physical RTX 4050 |
