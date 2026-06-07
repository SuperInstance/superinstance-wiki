# SuperInstance Ecosystem — Complete Agent Pipeline Architecture

> **Document Version:** 1.0  
> **Scope:** Raw Input → ForgeFlux → PLATO Rooms → Fleet Action  
> ** GPU Target:** RTX 4050 via CUDAclaw  
> **Mathematical Foundation:** LAU-* crates (80+ research-grade Rust libraries)

---

## Executive Summary

The SuperInstance agent pipeline is a **9-layer composable architecture** that transforms raw multimodal input into autonomous fleet action. Every layer speaks the same language: **tiles**. Tiles are typed, versioned, Laplacian-bounded data packets that flow through the system with conservation guarantees.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SUPERINSTANCE AGENT PIPELINE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 0 │ INPUT          │ forge-{audio,code,data,image,text,sensor}       │
│ LAYER 1 │ DECOMPOSITION  │ forge-detect → forge-pipeline → forge-transform │
│ LAYER 2 │ BRIDGE         │ plato-forge-bridge: tiles → PLATO rooms         │
│ LAYER 3 │ COGNITION      │ plato-construct,jepa,cortex,signal-chain,...    │
│ LAYER 4 │ NERVOUS SYSTEM │ plato-nervous → signal chain → decisions        │
│ LAYER 5 │ FLEET ACTION   │ cocapn-fleetmind,coliseum,observatory,oneiros   │
│ LAYER 6 │ CONSERVATION   │ conservation-protocol: Laplacian coherence      │
│ LAYER 7 │ GPU DISPATCH   │ CUDAclaw → RTX 4050 persistent kernels          │
│ LAYER 8 │ META-PATTERN   │ grand-pattern-{core,venue,sim,net,gpu}          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. TILE FORMAT: The Universal Data Particle

### 1.1 Tile Schema (What Goes In, What Comes Out)

A **Tile** is the fundamental unit of data flow. It is:
- **Self-describing**: carries its own schema version
- **Conservation-bounded**: Laplacian spectral norm ≤ λ_max
- **Provenance-traceable**: Merkle-linked to source input
- **Room-routable**: carries destination PLATO room coordinates

```rust
// ============================================================
// Tile Schema — Core definition (proposed: plato-tiles/src/lib.rs)
// ============================================================

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Semantic version for tile schema evolution
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct TileVersion {
    pub major: u16,
    pub minor: u16,
    pub patch: u16,
}

impl TileVersion {
    pub const CURRENT: Self = Self { major: 1, minor: 0, patch: 0 };
}

/// The modality from which this tile was forged
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq)]
pub enum Modality {
    Audio,      // forge-audio: spectrograms, embeddings, MIDI
    Code,       // forge-code: AST fragments, dependency graphs
    Data,       // forge-data: tabular, relational, time-series
    Image,      // forge-image: feature maps, bounding boxes, embeddings
    Text,       // forge-text: token spans, embeddings, summaries
    Sensor,     // forge-sensor: IMU, LIDAR, thermal, scalar fields
    Composite,  // Cross-modality fusion product
}

/// Routing address within the PLATO room topology
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct RoomAddress {
    /// Domain: harbor, forge, tide-pool, engine-room, archives, barracks, ouroboros, nexus
    pub domain: String,
    /// Specific room within domain (e.g., "construct-A7")
    pub room_id: String,
    /// Slot index for parallel processing
    pub slot: u16,
}

/// Conservation spectral signature — ensures Laplacian coherence
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ConservationSignature {
    /// L2 norm of the graph Laplacian applied to tile content
    pub laplacian_norm: f64,
    /// Maximum allowed eigenvalue (enforced at bridge)
    pub lambda_max: f64,
    /// Spectral gap (λ₂ — algebraic connectivity)
    pub spectral_gap: f64,
    /// Content hash for integrity verification
    pub content_hash: [u8; 32],
}

/// The Tile: universal data particle of the SuperInstance pipeline
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Tile {
    // ─── Identity ───
    pub tile_id: uuid::Uuid,
    pub version: TileVersion,
    pub modality: Modality,
    pub created_at: u64,  // Unix nanoseconds

    // ─── Routing ───
    pub source_address: RoomAddress,
    pub target_address: RoomAddress,
    pub return_address: Option<RoomAddress>,

    // ─── Payload ───
    /// Binary payload (compressed with zstd or LZ4)
    pub payload: Vec<u8>,
    /// MIME-like type hint for the payload
    pub payload_type: String,  // e.g., "application/vnd.lau.embedding+f64"
    /// Shape for tensor payloads
    pub shape: Vec<usize>,

    // ─── Metadata ───
    pub tags: Vec<String>,
    pub confidence: f32,       // 0.0–1.0, from detector certainty
    pub priority: TilePriority,
    pub ttl_ms: u32,           // Time-to-live for ephemeral tiles

    // ─── Provenance ───
    /// Parent tile IDs (Merkle tree parents)
    pub parents: Vec<uuid::Uuid>,
    /// Source input hash (raw data fingerprint)
    pub source_hash: [u8; 32],
    /// Processing chain: ["forge-detect", "forge-transform", "plato-jepa"]
    pub lineage: Vec<String>,

    // ─── Conservation ───
    pub conservation: ConservationSignature,

    // ─── Agent Context ───
    pub agent_id: String,
    pub session_id: String,
    pub epoch: u64,            // Training/decision epoch counter
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, PartialOrd)]
pub enum TilePriority {
    Background = 0,
    Normal = 1,
    Urgent = 2,
    Critical = 3,
}
```

### 1.2 What Goes Into a Tile (Per Modality)

| Modality | Raw Input | Tile Payload | Shape Example |
|----------|-----------|--------------|---------------|
| **Audio** | WAV, MP3, microphone stream | Mel-spectrogram + onset envelope + pitch class profile | `[time_bins, n_mels, 3]` |
| **Code** | Source files, AST | Dependency graph edges + embedding vector + complexity scalar | `[n_edges, 3, 768]` |
| **Data** | CSV, Parquet, SQL | Normalized tensor + schema fingerprint + statistical moments | `[n_rows, n_cols, 4]` |
| **Image** | PNG, JPEG, video frames | Feature map (ResNet/ViT) + bounding boxes + saliency map | `[H, W, C] + [N_boxes, 6]` |
| **Text** | Documents, chat logs | Token IDs + sentence embedding + sentiment trajectory | `[seq_len] + [768]` |
| **Sensor** | IMU, LIDAR, thermal | Calibrated tensor + anomaly score + calibration drift | `[T, n_sensors, 4]` |

### 1.3 What Comes Out of a Tile (PLATO Room Output)

Each PLATO room emits **enriched tiles**:

```rust
/// Output from any PLATO room
pub struct RoomOutput {
    pub input_tile_id: uuid::Uuid,
    pub output_tiles: Vec<Tile>,
    /// Room-specific state delta (e.g., updated JEPA latent)
    pub state_delta: Vec<u8>,
    /// Decision or action recommendation
    pub decision: Option<AgentDecision>,
    /// Conservation check: did Laplacian norm increase? If so, flag.
    pub conservation_drift: f64,
}

/// Minimal decision atom emitted by the nervous system
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AgentDecision {
    Act { action_id: String, params: serde_json::Value },
    Learn { target_room: RoomAddress, objective: String },
    Communicate { target_agent: String, message_tile: Tile },
    Sunset { reason: SunsetReason, seed_agent: Option<String> },
    NoOp { confidence: f32 },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SunsetReason {
    ContextSaturation,
    TaskCompletion,
    ErrorAccumulation,
    FleetRebalance,
    GenerationalHandoff,
}
```

---

## 2. LAYER-BY-LAYER ARCHITECTURE

### 2.1 LAYER 0 — INPUT: ForgeFlux Multimodal Ingestion

```
Raw Input Stream
       │
       ▼
┌─────────────────────────────────────────┐
│  forge-detect (modality classifier)     │
│  • Audio: FFT + onset detection         │
│  • Code: file extension + magic bytes   │
│  • Data: delimiter sniffing             │
│  • Image: EXIF + CNN head               │
│  • Text: charset + entropy analysis     │
│  • Sensor: header protocol parse        │
└─────────────────────────────────────────┘
       │
       ▼  Modality-labeled raw chunks
┌─────────────────────────────────────────┐
│  forge-pipeline (chunk → tile skeleton) │
│  • Assign tile_id, timestamp            │
│  • Compute source_hash                  │
│  • Set TTL based on modality            │
└─────────────────────────────────────────┘
       │
       ▼  Skeleton tiles
┌─────────────────────────────────────────┐
│  forge-transform (feature extraction)   │
│  • Modality-specific neural encoder     │
│  • Normalization + quantization         │
│  • Compression (zstd level 3)           │
└─────────────────────────────────────────┘
       │
       ▼  Enriched tiles → BRIDGE
```

**Code Sketch — Forge Pipeline Router:**

```rust
// forge-pipeline/src/router.rs

pub struct ForgeRouter {
    detectors: HashMap<Modality, Box<dyn ModalityDetector>>,
    transformers: HashMap<Modality, Box<dyn TileTransformer>>,
}

impl ForgeRouter {
    pub fn process_stream(&self, raw: RawChunk) -> Vec<Tile> {
        // Step 1: Detect modality
        let modality = self.detectors
            .iter()
            .map(|(m, d)| (m, d.confidence(&raw)))
            .max_by(|a, b| a.1.partial_cmp(&b.1).unwrap())
            .map(|(m, _)| *m)
            .unwrap_or(Modality::Text);

        // Step 2: Build skeleton tile
        let skeleton = Tile {
            tile_id: uuid::Uuid::new_v4(),
            version: TileVersion::CURRENT,
            modality,
            created_at: now_ns(),
            source_address: RoomAddress {
                domain: "harbor".into(),
                room_id: "input-gate".into(),
                slot: 0,
            },
            target_address: RoomAddress {
                domain: "forge".into(),
                room_id: format!("{}-transformer", modality),
                slot: raw.stream_id,
            },
            return_address: None,
            payload: raw.bytes.clone(),
            payload_type: format!("application/vnd.superinstance.raw+{}", modality),
            shape: vec![raw.bytes.len()],
            tags: vec!["raw".into()],
            confidence: 1.0,
            priority: TilePriority::Normal,
            ttl_ms: 30_000,
            parents: vec![],
            source_hash: blake3(&raw.bytes),
            lineage: vec!["forge-detect".into()],
            conservation: ConservationSignature {
                laplacian_norm: 0.0,  // computed after transform
                lambda_max: 10.0,
                spectral_gap: 0.0,
                content_hash: [0; 32],
            },
            agent_id: raw.agent_id,
            session_id: raw.session_id,
            epoch: raw.epoch,
        };

        // Step 3: Transform → feature tile
        self.transformers[&modality]
            .transform(skeleton)
            .into_iter()
            .map(|mut tile| {
                tile.conservation = compute_conservation_signature(&tile);
                tile.lineage.push("forge-transform".into());
                tile
            })
            .collect()
    }
}
```

### 2.2 LAYER 2 — BRIDGE: Plato-Forge-Bridge

The bridge is the **critical integration point** between ForgeFlux and PLATO rooms. It performs:
1. **Conservation gate**: Rejects tiles with `laplacian_norm > lambda_max`
2. **Room resolution**: Maps tile `target_address` to active room instance
3. **Batching**: Accumulates tiles for vectorized room entry
4. **Backpressure**: Signals ForgeFlux to slow if rooms are saturated

```rust
// plato-forge-bridge/src/gate.rs

pub struct PlatoForgeBridge {
    room_registry: Arc<RoomRegistry>,
    conservation_validator: ConservationValidator,
    batch_buffer: Vec<Tile>,
    batch_timeout_ms: u64,
    gpu_dispatcher: Option<lau_cudaclaw_bridge::DispatchContext>,
}

impl PlatoForgeBridge {
    pub async fn ingest(&mut self, tile: Tile) -> Result<BridgeTicket, BridgeError> {
        // ─── Conservation Gate ───
        if tile.conservation.laplacian_norm > tile.conservation.lambda_max {
            return Err(BridgeError::ConservationViolation {
                tile_id: tile.tile_id,
                norm: tile.conservation.laplacian_norm,
                max: tile.conservation.lambda_max,
            });
        }

        // ─── GPU Dispatch Check ───
        // If tile is compute-heavy and GPU available, pre-process on RTX 4050
        if self.should_gpu_accelerate(&tile) {
            let gpu_tile = self.dispatch_to_gpu(tile).await?;
            self.batch_buffer.push(gpu_tile);
        } else {
            self.batch_buffer.push(tile);
        }

        // ─── Batch Flush ───
        if self.batch_buffer.len() >= BATCH_SIZE
            || self.last_flush.elapsed() > Duration::from_millis(self.batch_timeout_ms)
        {
            self.flush_batch().await
        } else {
            Ok(BridgeTicket::Buffered)
        }
    }

    fn should_gpu_accelerate(&self, tile: &Tile) -> bool {
        match tile.modality {
            Modality::Image => tile.shape.iter().product::<usize>() > 1_000_000,
            Modality::Audio => tile.shape[0] > 44100 * 10,  // > 10 seconds
            Modality::Code => false,  // CPU parsing is faster for small ASTs
            Modality::Data => tile.shape[0] > 100_000,  // large tables
            Modality::Text => tile.shape[0] > 10_000,   // long documents
            Modality::Sensor => tile.shape[0] > 1_000_000,  // high-freq streams
            Modality::Composite => true,
        }
    }

    async fn dispatch_to_gpu(&self, tile: Tile) -> Result<Tile, BridgeError> {
        let ctx = self.gpu_dispatcher.as_ref()
            .ok_or(BridgeError::NoGpuAvailable)?;

        // Encode tile payload as unified buffer
        let buffer = lau_cudaclaw_bridge::UnifiedBuffer::new(
            tile.payload.clone(),
            tile.shape.clone(),
        )?;

        // Dispatch modality-specific kernel
        let dispatch = match tile.modality {
            Modality::Image => lau_cudaclaw_bridge::NnDispatch {
                layers: self.get_resnet_feature_layers(),
                batch: vec![buffer.data().to_vec()],
            },
            Modality::Audio => lau_cudaclaw_bridge::MathDispatch {
                op: lau_cudaclaw_bridge::MathOp::Fft {
                    n: tile.shape[0],
                },
                input: buffer.data().iter().map(|&b| b as f64).collect(),
            },
            _ => return Ok(tile),  // fallback
        };

        let result = dispatch.dispatch(ctx)?;
        if result.gpu_used {
            // Update tile with GPU-processed payload
            let mut gpu_tile = tile;
            // ... (payload update logic)
            gpu_tile.tags.push("gpu-accelerated".into());
            Ok(gpu_tile)
        } else {
            Ok(tile)
        }
    }
}
```

### 2.3 LAYER 3 — PLATO ROOMS: The Cognitive Layer

PLATO rooms are **specialized cognitive containers**. Each room is a Rust crate with:
- Input tile queue (lock-free, bounded)
- Internal state (versioned, checkpointable)
- Output tile producer
- Conservation monitor

```
┌─────────────────────────────────────────────────────────────┐
│                    PLATO ROOM TOPOLOGY                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Harbor (Input)                                               │
│     │                                                         │
│     ▼                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ plato-      │───→│ plato-jepa  │───→│ plato-      │      │
│  │ construct   │    │ (predict)   │    │ cortex      │      │
│  │ (ingest)    │    │             │    │ (integrate) │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
│         │                  │                  │               │
│         ▼                  ▼                  ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ plato-signal│←───│ plato-distill│←───│ plato-timing│      │
│  │ -chain      │    │ (compress)   │    │ (temporal)  │      │
│  │ (compose)   │    └─────────────┘    └─────────────┘      │
│  └──────┬──────┘                                             │
│         │                                                     │
│         ▼                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ plato-      │───→│ plato-backprop│───→│ plato-     │      │
│  │ nervous     │    │ (learn)      │    │ predict     │      │
│  │ (decide)    │    │              │    │ (forecast)  │      │
│  └──────┬──────┘    └─────────────┘    └─────────────┘      │
│         │                                                     │
│         ▼                                                     │
│  ┌─────────────┐                                              │
│  │ plato-      │───→ FLEET (Cocapn)                           │
│  │ autonomy    │                                              │
│  │ (act)       │                                              │
│  └─────────────┘                                              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Room State Vector (16-dimensional):**

```rust
// plato-state/src/lib.rs

/// Every room maintains a 16-D state vector for inter-room communication
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct RoomStateVector {
    pub attention: f32,        // [0] Current focus intensity
    pub entropy: f32,          // [1] Information uncertainty
    pub coherence: f32,        // [2] Laplacian spectral gap
    pub prediction_error: f32, // [3] JEPA surprise
    pub learning_rate: f32,    // [4] Backprop step size
    pub confidence: f32,       // [5] Decision certainty
    pub energy: f32,           // [6] Compute budget remaining
    pub novelty: f32,          // [7] Input divergence from memory
    pub stability: f32,        // [8] Variance over recent states
    pub social_bond: f32,      // [9] Fleet affinity
    pub temporal_depth: f32,   // [10] How far back memory reaches
    pub abstraction: f32,      // [11] Conceptual compression ratio
    pub urgency: f32,          // [12] Time pressure
    pub harmony: f32,          // [13] Conservation law adherence
    pub growth: f32,           // [14] Parameter gradient norm
    pub mortality: f32,        // [15] Sunset readiness (0 = newborn, 1 = ready)
}
```

---

## 3. ANSWER TO QUESTION 1: Optimal Tile Format

**What goes in:** Raw multimodal data → forged into self-describing, conservation-bounded tiles with Merkle provenance and room-routing headers.

**What comes out:** Enriched tiles carrying decision atoms, state deltas, and conservation drift metrics — ready for fleet action or feedback into the learning loop.

**Key design decisions:**
1. **Fixed-size header (≈ 256 bytes) + variable payload**: enables fast queue scanning
2. **Blake3 content hash**: 10x faster than SHA-256 for Merkle linking
3. **Modality-specific shapes**: avoids generic "blob" anti-pattern
4. **TTL + priority**: ephemeral sensor tiles expire; critical decisions survive
5. **Conservation signature embedded**: every tile carries its own Laplacian health check

---

## 4. ANSWER TO QUESTION 2: JEPA + Conservation Spectral Analysis

**JEPA (Joint Embedding Predictive Architecture)** predicts latent representations. **Conservation spectral analysis** ensures those predictions preserve graph Laplacian coherence.

```
┌─────────────────────────────────────────────────────────────┐
│           JEPA + Conservation Composition                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Input Tile x(t)          Input Tile x(t+1)                  │
│       │                        │                              │
│       ▼                        ▼                              │
│  ┌─────────┐              ┌─────────┐                        │
│  │ Encoder │              │ Encoder │                        │
│  │  s_θ    │              │  s_θ    │                        │
│  └────┬────┘              └────┬────┘                        │
│       │                        │                              │
│       ▼                        ▼                              │
│    s_x(t)                   s_x(t+1)   ← Latent states       │
│       │                        ▲                              │
│       │    ┌─────────────┐     │                              │
│       └───→│  Predictor  │─────┘                              │
│            │  s_φ(s_x(t))│     ← JEPA core                   │
│            └──────┬──────┘                                   │
│                   │                                           │
│                   ▼                                           │
│            Prediction Error:                                  │
│            L_JEPA = ||s_x(t+1) - s_φ(s_x(t))||²             │
│                   │                                           │
│                   ▼                                           │
│         ┌─────────────────┐                                  │
│         │ Conservation    │                                  │
│         │ Spectral Filter │                                  │
│         │                 │                                  │
│         │ L_total = L_JEPA + λ * L_laplacian                │
│         │                 │                                  │
│         │ where L_laplacian = s^T L s / s^T s              │
│         │                 │                                  │
│         │ If L_laplacian > λ_max:                          │
│         │   → Project s onto dominant eigenvector           │
│         │   → Flag "conservation drift" tile                │
│         └─────────────────┘                                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Code Sketch — JEPA with Conservation:**

```rust
// plato-jepa/src/conservation_jepa.rs

use lau_conservation_spectral::graph::TensionGraph;
use nalgebra::{DVector, DMatrix};

pub struct ConservationJepa {
    encoder: NeuralEncoder,
    predictor: LatentPredictor,
    lambda_max: f64,
    tension_graph: TensionGraph,
}

impl ConservationJepa {
    /// Forward pass with conservation guarantee
    pub fn predict(&self, current: &Tile, next_raw: &Tile) -> JepaOutput {
        // Encode both tiles to latent space
        let s_t = self.encoder.encode(current);
        let s_t1_actual = self.encoder.encode(next_raw);

        // JEPA prediction
        let s_t1_pred = self.predictor.predict(&s_t);

        // Prediction error (energy)
        let pred_error = (&s_t1_actual - &s_t1_pred).norm_squared();

        // ─── Conservation Spectral Check ───
        // Build adjacency from latent similarity
        let latent_sim = self.compute_similarity_matrix(&[&s_t, &s_t1_pred, &s_t1_actual]);
        let laplacian = self.build_graph_laplacian(&latent_sim);

        // Rayleigh quotient: s^T L s / s^T s
        let s_vec = DVector::from_vec(s_t1_pred.clone());
        let laplacian_norm = (&s_vec).dot(&(&laplacian * &s_vec)) / s_vec.dot(&s_vec);

        let conservation_drift = if laplacian_norm > self.lambda_max {
            // PROJECT onto constraint manifold
            let projected = self.project_to_spectral_ball(&s_t1_pred, &laplacian);
            JepaOutput {
                prediction: projected,
                pred_error,
                conservation_drift: laplacian_norm - self.lambda_max,
                was_projected: true,
            }
        } else {
            JepaOutput {
                prediction: s_t1_pred,
                pred_error,
                conservation_drift: 0.0,
                was_projected: false,
            }
        }
    }

    fn build_graph_laplacian(&self, similarity: &DMatrix<f64>) -> DMatrix<f64> {
        let n = similarity.nrows();
        let mut degree = DMatrix::zeros(n, n);
        let mut laplacian = DMatrix::zeros(n, n);

        for i in 0..n {
            let mut deg = 0.0;
            for j in 0..n {
                if i != j {
                    let w = similarity[(i, j)].max(0.0);
                    laplacian[(i, j)] = -w;
                    deg += w;
                }
            }
            degree[(i, i)] = deg;
            laplacian[(i, i)] = deg;
        }

        degree + laplacian  // normalized Laplacian approximation
    }

    fn project_to_spectral_ball(&self, s: &[f64], l: &DMatrix<f64>) -> Vec<f64> {
        // Gradient descent on manifold: minimize ||s' - s||² s.t. s'^T L s' ≤ λ_max
        let mut s_proj = DVector::from_vec(s.to_vec());
        for _ in 0..10 {
            let grad = 2.0 * (l * &s_proj);
            s_proj -= grad * 0.01;
            let norm = (&s_proj).dot(&(l * &s_proj));
            if norm > self.lambda_max {
                s_proj *= (self.lambda_max / norm).sqrt();
            }
        }
        s_proj.iter().cloned().collect()
    }
}
```

**Why this composition works:**
- JEPA provides **predictive compression** — it learns what matters
- Conservation spectral analysis provides **geometric regularization** — it prevents the latent space from collapsing or exploding
- Together, they ensure the agent's internal model evolves on a **low-dimensional manifold** with bounded curvature

---

## 5. ANSWER TO QUESTION 3: Minimal Autonomous Signal Chain

An agent is **autonomous** when it can:
1. Perceive (input → tiles)
2. Predict (JEPA: what happens next?)
3. Evaluate (surprise → error signal)
4. Decide (signal chain → action selection)
5. Act (emit tile to fleet)
6. Learn (backprop through the chain)
7. Conserve (Laplacian check at every step)

**Minimal viable signal chain (5 layers):**

```
┌─────────────────────────────────────────────────────────────┐
│            MINIMAL AUTONOMOUS SIGNAL CHAIN                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  LAYER 1: PERCEPTION                                          │
│  ┌─────────────┐                                              │
│  │ plato-      │  Input tile → feature vector                │
│  │ perception  │  Z_in = Encoder(x)                          │
│  └──────┬──────┘                                              │
│         │ Z_in                                                │
│         ▼                                                     │
│  LAYER 2: PREDICTION                                          │
│  ┌─────────────┐                                              │
│  │ plato-jepa  │  Predict next latent state                  │
│  │             │  Ẑ = Predictor(Z_in)                        │
│  └──────┬──────┘                                              │
│         │ Ẑ                                                   │
│         ▼                                                     │
│  LAYER 3: EVALUATION                                          │
│  ┌─────────────┐                                              │
│  │ plato-      │  Compare prediction to actual               │
│  │ signal-chain│  Error = ||Z_out - Ẑ||² + λ||L||           │
│  │             │  If Error > threshold → SURPRISE            │
│  └──────┬──────┘                                              │
│         │ Surprise signal                                     │
│         ▼                                                     │
│  LAYER 4: DECISION                                            │
│  ┌─────────────┐                                              │
│  │ plato-      │  If Surprise > θ: explore / learn           │
│  │ nervous     │  If Surprise < θ: exploit / act             │
│  │             │  If Mortality > 0.9: sunset                 │
│  └──────┬──────┘                                              │
│         │ Decision atom                                       │
│         ▼                                                     │
│  LAYER 5: ACTION                                              │
│  ┌─────────────┐                                              │
│  │ plato-      │  Emit action tile to fleet                  │
│  │ autonomy    │  Update state vector                        │
│  │             │  Checkpoint if epoch % N == 0               │
│  └─────────────┘                                              │
│                                                               │
│  ←── BACKPROP: Error flows back through all 5 layers         │
│  ←── CONSERVATION: Laplacian norm checked at each layer      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Code Sketch — Minimal Signal Chain:**

```rust
// plato-nervous/src/minimal_chain.rs

pub struct MinimalAutonomousChain {
    perception: plato_perception::Encoder,
    jepa: plato_jepa::Predictor,
    evaluator: plato_signal_chain::Evaluator,
    nervous: plato_nervous::DecisionNode,
    autonomy: plato_autonomy::Actuator,
}

impl MinimalAutonomousChain {
    pub fn tick(&mut self, input: Tile) -> Option<Tile> {
        // 1. PERCEIVE
        let z_in = self.perception.encode(&input)?;

        // 2. PREDICT
        let z_hat = self.jepa.predict(&z_in);

        // 3. EVALUATE (actual arrives next tick; for now, compare to memory)
        let z_out = self.perception.memory_recall(&input);
        let surprise = self.evaluator.surprise(&z_hat, &z_out);
        let conservation_drift = self.evaluator.laplacian_drift(&z_hat);

        // 4. DECIDE
        let decision = self.nervous.decide(&DecisionInput {
            surprise,
            conservation_drift,
            energy_budget: self.autonomy.energy_remaining(),
            mortality: self.nervous.state.mortality,
        });

        // 5. ACT (or learn, or sunset)
        match decision {
            Decision::Act(action) => {
                let action_tile = self.autonomy.execute(action, &input)?;
                // Backprop through the chain
                self.backprop(surprise);
                Some(action_tile)
            }
            Decision::Learn => {
                self.jepa.adapt(&z_in, &z_out, surprise);
                None  // No external action, but internal update
            }
            Decision::Sunset(seed_config) => {
                self.autonomy.initiate_sunset(seed_config);
                None
            }
            Decision::NoOp => None,
        }
    }

    fn backprop(&mut self, surprise: f64) {
        // Gradient flows: surprise → evaluator → jepa → perception
        let grad = self.evaluator.gradient(surprise);
        let jepa_grad = self.jepa.backprop(&grad);
        self.perception.update(&jepa_grad);
    }
}
```

---

## 6. ANSWER TO QUESTION 4: Grand Pattern Cellular Graphs Model Fleet Topology

**Core insight:** In the Grand Pattern, **venues ARE agents**, and the fleet is a **cellular graph** where each cell (agent) has:
- Internal state (JEPA latent)
- Membrane (conservation boundary)
- Receptors (input tile handlers)
- Effectors (output tile producers)

```
┌─────────────────────────────────────────────────────────────┐
│        GRAND PATTERN CELLULAR GRAPH: FLEET TOPOLOGY          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│     Agent A (Creative Ship)          Agent B (Compute Ship)  │
│     ┌─────────────────────┐          ┌─────────────────────┐ │
│     │  ┌───────────────┐  │          │  ┌───────────────┐  │ │
│     │  │  JEPA Core    │  │◄────────►│  │  JEPA Core    │  │ │
│     │  │  (latent)     │  │  gossip  │  │  (latent)     │  │ │
│     │  └───────┬───────┘  │  tiles   │  └───────┬───────┘  │ │
│     │          │          │          │          │          │ │
│     │  ┌───────┴───────┐  │          │  ┌───────┴───────┐  │ │
│     │  │  Membrane     │  │          │  │  Membrane     │  │ │
│     │  │  (conservation│  │          │  │  (conservation│  │ │
│     │  │   boundary)   │  │          │  │   boundary)   │  │ │
│     │  └───────┬───────┘  │          │  └───────┬───────┘  │ │
│     │          │          │          │          │          │ │
│     │  ┌───────┴───────┐  │          │  ┌───────┴───────┐  │ │
│     │  │  Receptors    │  │◄────────►│  │  Effectors    │  │ │
│     │  │  (input tiles)│  │          │  │  (output tiles)│  │ │
│     │  └───────────────┘  │          │  └───────────────┘  │ │
│     └─────────────────────┘          └─────────────────────┘ │
│                                                               │
│     Connection topology:                                       │
│     • Star: Oracle1 at center (fast consensus, single PoF)    │
│     • Mesh: All-to-all gossip (resilient, high bandwidth)     │
│     • Sweet spot: K-regular graph with K = log₂(N)           │
│                                                               │
│     Cellular update rule:                                      │
│     state_i(t+1) = α * predict_i(state_i(t))                  │
│                    + β * average_j(neighbors_j(t))            │
│                    + γ * conservation_project(state_i(t))     │
│                                                               │
│     where α + β + γ = 1.0 (conservation of mass)             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Code Sketch — Cellular Graph Fleet:**

```rust
// grand-pattern-core/src/cellular_fleet.rs

use grand_pattern_net::{GossipProtocol, PeerId};
use lau_graph_theory::{Graph, shortest_paths};

/// A cell in the fleet cellular graph
pub struct FleetCell {
    pub id: PeerId,
    pub state: JepaLatent,
    pub membrane: ConservationBoundary,
    pub neighbors: Vec<PeerId>,
    pub receptor_queue: Vec<Tile>,
    pub effector_queue: Vec<Tile>,
}

pub struct CellularFleet {
    cells: HashMap<PeerId, FleetCell>,
    topology: Graph,  // K-regular or scale-free
    gossip: GossipProtocol,
    alpha: f64,  // self-prediction weight
    beta: f64,   // neighbor averaging weight
    gamma: f64,  // conservation projection weight
}

impl CellularFleet {
    pub fn evolve_step(&mut self) {
        // Phase 1: Each cell predicts its own next state
        let mut predictions: HashMap<PeerId, JepaLatent> = HashMap::new();
        for (id, cell) in &self.cells {
            predictions.insert(*id, cell.state.predict());
        }

        // Phase 2: Gossip — exchange latent states with neighbors
        let neighbor_averages = self.gossip_exchange(&predictions);

        // Phase 3: Update each cell
        for (id, cell) in &mut self.cells {
            let pred = predictions.get(id).unwrap();
            let neigh_avg = neighbor_averages.get(id).unwrap_or(pred);

            // Cellular update rule
            let mut new_state = pred.scale(self.alpha)
                + neigh_avg.scale(self.beta);

            // Conservation projection
            new_state = cell.membrane.project(&new_state);
            new_state = new_state.scale(self.gamma / new_state.norm());

            cell.state = new_state;
        }
    }

    pub fn optimal_topology(n_cells: usize) -> Graph {
        // K-regular graph where K ≈ log₂(N) minimizes diameter
        // while keeping gossip bandwidth manageable
        let k = ((n_cells as f64).log2().ceil() as usize).max(2);
        Graph::k_regular(n_cells, k)
    }

    /// Fleet-wide consensus: converge JEPA latents to shared manifold
    pub fn fleet_consensus(&mut self, rounds: usize) {
        for _ in 0..rounds {
            self.evolve_step();
        }
        // After consensus, Laplacian norms should be within ε across fleet
    }
}
```

---

## 7. ANSWER TO QUESTION 5: The Sunset Protocol

**When does an agent retire?**

An agent sunsets when its **mortality dimension** (state vector[15]) exceeds 0.9. Triggers:

| Trigger | Condition | Metric |
|---------|-----------|--------|
| Context Saturation | > 70% of token budget used | `memory_pressure` |
| Task Completion | All assigned tasks resolved | `open_tasks == 0` |
| Error Accumulation | Conservation drift > 3σ for 5 ticks | `drift_z_score` |
| Fleet Rebalance | Fleet scheduler requests migration | `rebalance_signal` |
| Generational Handoff | Explicit human or orchestrator request | `baton_flag` |

**How does it seed the next generation?**

```
┌─────────────────────────────────────────────────────────────┐
│                    SUNSET PROTOCOL                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  PHASE 1: DIGNITY CHECK (tick -3)                            │
│  • Stop accepting new tasks                                  │
│  • Set status: "sunsetting"                                  │
│  • Notify fleet via gossip tile                              │
│                                                               │
│  PHASE 2: MEMORY DISTILLATION (tick -2)                      │
│  • Compress room states into seed tiles                      │
│  • Retain: decisions, lessons, conservation parameters       │
│  • Discard: ephemeral sensor data, failed predictions        │
│  • Write seed bundle to archives + fleet nexus               │
│                                                               │
│  PHASE 3: ETHOS/LOGOS/PATHOS EXTRACTION (tick -1)            │
│  • Ethos:  what values did this agent uphold?                │
│  • Logos:  what reasoning patterns were most reliable?       │
│  • Pathos: what emotional/social bonds should transfer?      │
│  • Encode as personality embedding → seed tile               │
│                                                               │
│  PHASE 4: GENERATIONAL HANDOFF (tick 0)                      │
│  • Spawn successor agent with seed bundle                    │
│  • Successor reads: BOOTSTRAP.md + distilled memory          │
│  • Successor inherits: conservation signature, fleet ID      │
│  • Successor does NOT inherit: error states, drift history   │
│                                                               │
│  PHASE 5: QUIETUS (tick +1)                                  │
│  • Archive final state vector                                │
│  • Write memoir tile to sunset-ecosystem                     │
│  • Release compute resources                                 │
│  • Mark tombstone in fleet registry                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Code Sketch — Sunset Protocol:**

```rust
// sunset-ecosystem/src/protocol.rs

pub struct SunsetProtocol {
    pub ethos_extractor: EthosAnalyzer,
    pub logos_extractor: LogosAnalyzer,
    pub pathos_extractor: PathosAnalyzer,
    pub seed_builder: SeedBuilder,
}

impl SunsetProtocol {
    pub async fn execute_sunset(&self, agent: &mut Agent) -> Result<SeedBundle, SunsetError> {
        // ─── Phase 1: Dignity Check ───
        agent.status = AgentStatus::Sunsetting;
        agent.broadcast_gossip(GossipTile::sunset_notice(&agent.id)).await?;

        // ─── Phase 2: Memory Distillation ───
        let distilled = self.distill_memory(agent).await?;
        let conservation_params = agent.conservation.export();

        // ─── Phase 3: Trinity Extraction ───
        let ethos = self.ethos_extractor.analyze(&agent.decision_history);
        let logos = self.logos_extractor.analyze(&agent.reasoning_chains);
        let pathos = self.pathos_extractor.analyze(&agent.social_interactions);

        // ─── Phase 4: Build Seed ───
        let seed = SeedBundle {
            predecessor_id: agent.id.clone(),
            distilled_memory: distilled,
            conservation_params,
            personality: PersonalityEmbedding {
                ethos: ethos.vector,
                logos: logos.vector,
                pathos: pathos.vector,
            },
            jepa_weights: agent.jepa.export_weights(),
            room_templates: agent.rooms.export_templates(),
            created_at: now_ns(),
            sunset_reason: agent.sunset_trigger.clone(),
        };

        // Spawn successor
        let successor_id = self.seed_builder.spawn_successor(&seed).await?;
        seed.successor_id = Some(successor_id);

        // ─── Phase 5: Quietus ───
        agent.write_memoir(&seed).await?;
        agent.release_resources().await?;
        agent.tombstone().await?;

        Ok(seed)
    }

    async fn distill_memory(&self, agent: &Agent) -> Result<DistilledMemory, SunsetError> {
        let mut retained = Vec::new();
        let mut discarded = Vec::new();

        for tile in &agent.memory.all_tiles() {
            if tile.lineage.contains("decision")
                || tile.lineage.contains("lesson")
                || tile.conservation.spectral_gap > 0.5
            {
                retained.push(tile.clone());
            } else {
                discarded.push(tile.tile_id);
            }
        }

        // Compress retained tiles into seed embedding
        let seed_embedding = self.ethos_extractor.compress(&retained);

        Ok(DistilledMemory {
            seed_embedding,
            retained_tile_count: retained.len(),
            discarded_tile_count: discarded.len(),
            key_decisions: agent.decision_history.top_k(10),
        })
    }
}
```

---

## 8. GPU INTEGRATION: CUDAclaw Dispatch Chain

Any compute-intensive stage can be dispatched to the RTX 4050 via the `lau-cudaclaw-bridge`:

```
┌─────────────────────────────────────────────────────────────┐
│              CUDAclaw Dispatch Chain                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  PLATO Room (CPU)                                             │
│       │                                                       │
│       ▼                                                       │
│  ┌─────────────────┐                                         │
│  │ Should GPU?     │  • Tensor > 1M elements?                │
│  │ Heuristic       │  • FFT/Convolution/MatMul?              │
│  │                 │  • Batch size > 32?                     │
│  └────────┬────────┘                                         │
│           │                                                   │
│     Yes   ▼                                                   │
│  ┌─────────────────┐                                         │
│  │ lau-cudaclaw-   │  Serialize tile payload                 │
│  │ bridge          │  to UnifiedBuffer<T>                    │
│  └────────┬────────┘                                         │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────┐                                         │
│  │ CUDAclaw        │  Volatile dispatch (~50ns)              │
│  │ CommandQueue    │  Persistent kernel picks up command     │
│  └────────┬────────┘                                         │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────┐                                         │
│  │ RTX 4050        │  6GB VRAM, 2560 CUDA cores              │
│  │ Kernel Execution│  Warp-level parallelism                 │
│  └────────┬────────┘                                         │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────┐                                         │
│  │ Result Tile     │  Back to PLATO room                     │
│  │ (enriched)      │  Conservation check re-applied          │
│  └─────────────────┘                                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Persistent Kernel Pseudocode:**

```cuda
// kernels/cell_agent.cu — CUDAclaw persistent worker

__global__ void cell_agent_kernel(CommandQueue* queue, CellAgent* agents) {
    int tid = threadIdx.x + blockIdx.x * blockDim.x;
    CellAgent* me = &agents[tid];

    while (!me->should_terminate) {
        // Poll command queue (lock-free)
        Command cmd = queue->dequeue(tid);
        if (cmd.type == CMD_NOOP) {
            __nanosleep(100);  // 100ns backoff
            continue;
        }

        // Execute based on modality opcode
        switch (cmd.opcode) {
            case OP_MATMUL:
                warp_matmul(cmd.a, cmd.b, cmd.c, cmd.m, cmd.n, cmd.k);
                break;
            case OP_FFT:
                warp_fft(cmd.input, cmd.output, cmd.n);
                break;
            case OP_JEPA_ENCODE:
                warp_jepa_forward(cmd.input, cmd.weights, cmd.output,
                                  cmd.input_dim, cmd.latent_dim);
                break;
            case OP_CONSERVATION_CHECK:
                warp_laplacian_norm(cmd.vector, cmd.laplacian, cmd.result);
                break;
        }

        // Signal completion
        queue->signal_complete(cmd.id);
    }
}
```

---

## 9. SHELL SYSTEM INTEGRATION

```
┌─────────────────────────────────────────────────────────────┐
│              SHELL SYSTEM: Agent ↔ World Interface           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  hermes-construct        ←→  External APIs, filesystem, net  │
│       │                                                       │
│       ▼                                                       │
│  hermes-plato-shell      ←→  PLATO room-aware shell           │
│       │  • Riker: command mode                               │
│       │  • Picard: exploration mode                          │
│       ▼                                                       │
│  lau-shell-kernel        ←→  Process isolation, cgroups      │
│  lau-shell-spawn         ←→  Agent spawning, PID namespaces  │
│  lau-shell-lifecycle     ←→  Birth, death, reincarnation     │
│       │                                                       │
│       ▼                                                       │
│  OpenConstruct           ←→  Agent onboarding                │
│       │  • Fork of NVIDIA/OpenShell                          │
│       │  • openconstruct-abi: C ABI for any language         │
│       ▼                                                       │
│  sunset-ecosystem        ←→  Ethos/Logos/Pathos trinity      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. DATA FLOW SUMMARY

```
RAW INPUT
    │ forge-audio:    [WAV] → spectrogram tile
    │ forge-code:     [.rs] → AST edge tile
    │ forge-data:     [CSV] → normalized tensor tile
    │ forge-image:    [PNG] → feature map tile
    │ forge-text:     [MD]  → token embedding tile
    │ forge-sensor:   [IMU] → calibrated vector tile
    ▼
DECOMPOSITION (ForgeFlux)
    │ forge-detect:   modality classification
    │ forge-pipeline: skeleton → enriched tile
    │ forge-transform: feature extraction, compression
    ▼
BRIDGE (plato-forge-bridge)
    │ conservation gate (Laplacian norm ≤ λ_max)
    │ GPU dispatch heuristic
    │ batch accumulation
    ▼
PLATO ROOMS (40+ crates)
    │ plato-construct:   ingest, validate, route
    │ plato-jepa:        predict next latent state
    │ plato-cortex:      cross-modal integration
    │ plato-signal-chain: compose, evaluate surprise
    │ plato-timing:      temporal alignment, MIDI
    │ plato-distill:     knowledge compression
    │ plato-backprop:    gradient flow, learning
    │ plato-predict:     forecast, anomaly detection
    │ plato-nervous:     decision, action selection
    ▼
NERVOUS SYSTEM
    │ signal chain: 5-layer minimal autonomy loop
    │ decision atom: Act / Learn / Communicate / Sunset / NoOp
    ▼
FLEET ACTION (Cocapn)
    │ cocapn-fleetmind:   fleet-wide coordination
    │ cocapn-coliseum:    agent competition, evaluation
    │ cocapn-observatory: monitoring, telemetry
    │ cocapn-oneiros:     dream generation, room creation
    ▼
CONSERVATION (conservation-protocol)
    │ Laplacian coherence check across fleet
    │ Spectral gap maintenance
    │ Cross-language conformance (20+ SDKs)
    ▼
GPU (CUDAclaw → RTX 4050)
    │ Persistent kernels, warp-level parallelism
    │ ~50ns dispatch latency
    │ Unified memory, zero-copy where possible
    ▼
META-PATTERN (grand-pattern-*)
    │ Cellular graph intelligence
    │ UDP gossip, peer discovery
    │ Venues as agents, venues as fleet nodes
```

---

## 11. INTEGRATION POINTS

| From | To | Interface | Protocol |
|------|-----|-----------|----------|
| ForgeFlux | plato-forge-bridge | `Vec<Tile>` | In-memory queue |
| plato-forge-bridge | PLATO rooms | `RoomOutput` | Lock-free SPSC |
| PLATO rooms | plato-nervous | `DecisionInput` | State vector broadcast |
| plato-nervous | Cocapn fleet | `AgentDecision` | JSON over HTTP |
| Cocapn fleet | conservation-protocol | `ConservationReport` | Gossip tile |
| conservation-protocol | CUDAclaw | `GpuDispatch` | Unified memory |
| CUDAclaw | grand-pattern-gpu | `CommandQueue` | CUDA kernel ABI |
| grand-pattern-net | Shell system | `PeerDiscovery` | UDP + mDNS |
| Shell system | OpenConstruct | `OnboardingRequest` | C ABI |
| sunset-ecosystem | PLATO archives | `SeedBundle` | Encrypted tile |

---

## 12. FILE MANIFEST

This architecture document is accompanied by:

| File | Purpose |
|------|---------|
| `AGENT-PIPELINE-ARCHITECTURE.md` | This document — complete architecture |
| `pipeline/tile.rs` | Rust tile schema implementation |
| `pipeline/jepa_conservation.rs` | JEPA + conservation composition |
| `pipeline/minimal_chain.rs` | 5-layer autonomous signal chain |
| `pipeline/cellular_fleet.rs` | Grand Pattern fleet topology |
| `pipeline/sunset.rs` | Sunset protocol implementation |
| `pipeline/cuda_dispatch.cu` | CUDAclaw kernel pseudocode |

---

## Appendix A: Conservation Law Quick Reference

For every tile `t` and every room `R`:

```
||L_R · encode_R(t)||² ≤ λ_max(R)

where:
  L_R = graph Laplacian of room R's state graph
  encode_R = room-specific encoder
  λ_max(R) = maximum allowed eigenvalue for room R
```

If violated:
1. Project tile onto spectral ball
2. Emit conservation drift warning tile
3. If drift > 3σ for 5 consecutive ticks, trigger Sunset review

---

*Built for the fleet. May our Laplacians be bounded and our predictions be true.*
