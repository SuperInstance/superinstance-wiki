// ============================================================
// tile.rs — Universal Tile Schema for SuperInstance Pipeline
// ============================================================
//
// This is the reference implementation of the Tile format described in
// AGENT-PIPELINE-ARCHITECTURE.md §1.
//
// Dependencies:
//   serde = { version = "1", features = ["derive"] }
//   uuid = { version = "1", features = ["v4", "serde"] }
//   blake3 = "1"

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
    Audio,
    Code,
    Data,
    Image,
    Text,
    Sensor,
    Composite,
}

impl std::fmt::Display for Modality {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Modality::Audio => write!(f, "audio"),
            Modality::Code => write!(f, "code"),
            Modality::Data => write!(f, "data"),
            Modality::Image => write!(f, "image"),
            Modality::Text => write!(f, "text"),
            Modality::Sensor => write!(f, "sensor"),
            Modality::Composite => write!(f, "composite"),
        }
    }
}

/// Routing address within the PLATO room topology
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct RoomAddress {
    pub domain: String,
    pub room_id: String,
    pub slot: u16,
}

/// Conservation spectral signature — ensures Laplacian coherence
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ConservationSignature {
    pub laplacian_norm: f64,
    pub lambda_max: f64,
    pub spectral_gap: f64,
    pub content_hash: [u8; 32],
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, PartialOrd)]
pub enum TilePriority {
    Background = 0,
    Normal = 1,
    Urgent = 2,
    Critical = 3,
}

/// The Tile: universal data particle of the SuperInstance pipeline
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Tile {
    pub tile_id: uuid::Uuid,
    pub version: TileVersion,
    pub modality: Modality,
    pub created_at: u64,

    pub source_address: RoomAddress,
    pub target_address: RoomAddress,
    pub return_address: Option<RoomAddress>,

    pub payload: Vec<u8>,
    pub payload_type: String,
    pub shape: Vec<usize>,

    pub tags: Vec<String>,
    pub confidence: f32,
    pub priority: TilePriority,
    pub ttl_ms: u32,

    pub parents: Vec<uuid::Uuid>,
    pub source_hash: [u8; 32],
    pub lineage: Vec<String>,

    pub conservation: ConservationSignature,

    pub agent_id: String,
    pub session_id: String,
    pub epoch: u64,
}

impl Tile {
    /// Create a skeleton tile from raw bytes before transformation
    pub fn skeleton(
        modality: Modality,
        raw: &[u8],
        agent_id: &str,
        session_id: &str,
    ) -> Self {
        Self {
            tile_id: uuid::Uuid::new_v4(),
            version: TileVersion::CURRENT,
            modality,
            created_at: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos() as u64,
            source_address: RoomAddress {
                domain: "harbor".into(),
                room_id: "input-gate".into(),
                slot: 0,
            },
            target_address: RoomAddress {
                domain: "forge".into(),
                room_id: format!("{}-transformer", modality),
                slot: 0,
            },
            return_address: None,
            payload: raw.to_vec(),
            payload_type: format!("application/vnd.superinstance.raw+{}", modality),
            shape: vec![raw.len()],
            tags: vec!["raw".into()],
            confidence: 1.0,
            priority: TilePriority::Normal,
            ttl_ms: 30_000,
            parents: vec![],
            source_hash: blake3::hash(raw).into(),
            lineage: vec!["forge-detect".into()],
            conservation: ConservationSignature {
                laplacian_norm: 0.0,
                lambda_max: 10.0,
                spectral_gap: 0.0,
                content_hash: [0; 32],
            },
            agent_id: agent_id.into(),
            session_id: session_id.into(),
            epoch: 0,
        }
    }

    /// Compute content hash and update conservation signature
    pub fn seal(&mut self) {
        let hash = blake3::hash(&self.payload);
        self.conservation.content_hash = hash.into();
    }

    /// Check if this tile has exceeded its TTL
    pub fn is_expired(&self) -> bool {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos() as u64;
        (now - self.created_at) > (self.ttl_ms as u64 * 1_000_000)
    }

    /// Create a child tile inheriting provenance from this tile
    pub fn child(&self, modality: Modality, payload: Vec<u8>, payload_type: &str) -> Self {
        let mut child = Self::skeleton(modality, &payload, &self.agent_id, &self.session_id);
        child.parents = vec![self.tile_id];
        child.epoch = self.epoch + 1;
        child.payload = payload;
        child.payload_type = payload_type.into();
        child.source_address = self.target_address.clone();
        child.lineage = self.lineage.clone();
        child
    }
}

/// Output from any PLATO room
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RoomOutput {
    pub input_tile_id: uuid::Uuid,
    pub output_tiles: Vec<Tile>,
    pub state_delta: Vec<u8>,
    pub decision: Option<AgentDecision>,
    pub conservation_drift: f64,
}

/// Minimal decision atom emitted by the nervous system
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AgentDecision {
    Act {
        action_id: String,
        params: serde_json::Value,
    },
    Learn {
        target_room: RoomAddress,
        objective: String,
    },
    Communicate {
        target_agent: String,
        message_tile: Tile,
    },
    Sunset {
        reason: SunsetReason,
        seed_agent: Option<String>,
    },
    NoOp {
        confidence: f32,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SunsetReason {
    ContextSaturation,
    TaskCompletion,
    ErrorAccumulation,
    FleetRebalance,
    GenerationalHandoff,
}

/// Tile batch for vectorized room entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TileBatch {
    pub tiles: Vec<Tile>,
    pub batch_id: uuid::Uuid,
    pub target_domain: String,
    pub conservation_aggregate: f64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_skeleton_tile() {
        let raw = b"hello world";
        let tile = Tile::skeleton(Modality::Text, raw, "agent-1", "session-42");
        assert_eq!(tile.modality, Modality::Text);
        assert_eq!(tile.payload, raw.to_vec());
        assert!(tile.parents.is_empty());
    }

    #[test]
    fn test_child_tile() {
        let parent = Tile::skeleton(Modality::Text, b"parent", "agent-1", "session-42");
        let child = parent.child(Modality::Composite, b"child".to_vec(), "test/child");
        assert_eq!(child.parents, vec![parent.tile_id]);
        assert_eq!(child.epoch, parent.epoch + 1);
    }

    #[test]
    fn test_ttl_expiration() {
        let mut tile = Tile::skeleton(Modality::Sensor, b"x", "a", "s");
        tile.created_at = 0; // Force old timestamp
        tile.ttl_ms = 1;     // 1ms TTL
        assert!(tile.is_expired());
    }
}
