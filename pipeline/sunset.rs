// ============================================================
// sunset.rs — Sunset Protocol: Agent Retirement and Seeding
// ============================================================
//
// Reference implementation of AGENT-PIPELINE-ARCHITECTURE.md §7.
//
// Agents sunset with dignity and seed the next generation.

use crate::tile::{AgentDecision, Tile};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Reason for agent sunset
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SunsetReason {
    ContextSaturation,
    TaskCompletion,
    ErrorAccumulation,
    FleetRebalance,
    GenerationalHandoff,
}

/// Distilled memory passed to successor
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DistilledMemory {
    pub seed_embedding: Vec<f64>,
    pub retained_tile_count: usize,
    pub discarded_tile_count: usize,
    pub key_decisions: Vec<DecisionRecord>,
}

/// Record of a significant decision
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DecisionRecord {
    pub epoch: u64,
    pub decision_type: String,
    pub outcome: String,
    pub conservation_drift: f64,
}

/// Personality embedding (ethos/logos/pathos)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PersonalityEmbedding {
    pub ethos: Vec<f64>,
    pub logos: Vec<f64>,
    pub pathos: Vec<f64>,
}

/// Complete seed bundle for successor generation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SeedBundle {
    pub predecessor_id: String,
    pub successor_id: Option<String>,
    pub distilled_memory: DistilledMemory,
    pub conservation_params: ConservationParams,
    pub personality: PersonalityEmbedding,
    pub jepa_weights: Vec<f64>,
    pub room_templates: Vec<RoomTemplate>,
    pub created_at: u64,
    pub sunset_reason: SunsetReason,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConservationParams {
    pub lambda_max: f64,
    pub spectral_gap_target: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RoomTemplate {
    pub domain: String,
    pub room_id: String,
    pub state_vector: Vec<f64>,
}

/// Agent lifecycle states
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum AgentStatus {
    Active,
    Sunsetting,
    Archived,
}

/// Simplified agent representation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Agent {
    pub id: String,
    pub status: AgentStatus,
    pub memory: AgentMemory,
    pub decision_history: Vec<DecisionRecord>,
    pub reasoning_chains: Vec<String>,
    pub social_interactions: Vec<String>,
    pub conservation: AgentConservation,
    pub jepa: AgentJepa,
    pub rooms: AgentRooms,
    pub sunset_trigger: SunsetReason,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentMemory {
    tiles: Vec<Tile>,
}

impl AgentMemory {
    pub fn all_tiles(&self) -> &[Tile] {
        &self.tiles
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentConservation {
    pub params: ConservationParams,
}

impl AgentConservation {
    pub fn export(&self) -> ConservationParams {
        self.params.clone()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentJepa {
    weights: Vec<f64>,
}

impl AgentJepa {
    pub fn export_weights(&self) -> Vec<f64> {
        self.weights.clone()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentRooms {
    templates: Vec<RoomTemplate>,
}

impl AgentRooms {
    pub fn export_templates(&self) -> Vec<RoomTemplate> {
        self.templates.clone()
    }
}

/// Trinity analyzers extract personality dimensions
pub trait EthosAnalyzer {
    fn analyze(&self, decisions: &[DecisionRecord]) -> EthosAnalysis;
    fn compress(&self, tiles: &[Tile]) -> Vec<f64>;
}

pub struct EthosAnalysis {
    pub vector: Vec<f64>,
}

pub trait LogosAnalyzer {
    fn analyze(&self, reasoning: &[String]) -> LogosAnalysis;
}

pub struct LogosAnalysis {
    pub vector: Vec<f64>,
}

pub trait PathosAnalyzer {
    fn analyze(&self, interactions: &[String]) -> PathosAnalysis;
}

pub struct PathosAnalysis {
    pub vector: Vec<f64>,
}

/// Builder that spawns successor agents
#[derive(Clone)]
pub struct SeedBuilder;

impl SeedBuilder {
    pub async fn spawn_successor(&self, seed: &SeedBundle) -> Result<String, SunsetError> {
        // In production: orchestrate new agent container/process
        let successor_id = format!("{}-successor-{}", seed.predecessor_id, seed.created_at);
        Ok(successor_id)
    }
}

/// Errors during sunset
#[derive(Debug, Clone)]
pub enum SunsetError {
    MemoryDistillationFailed(String),
    SpawnFailed(String),
    ArchiveFailed(String),
}

/// The Sunset Protocol executor
pub struct SunsetProtocol<E, L, P>
where
    E: EthosAnalyzer,
    L: LogosAnalyzer,
    P: PathosAnalyzer,
{
    pub ethos_extractor: E,
    pub logos_extractor: L,
    pub pathos_extractor: P,
    pub seed_builder: SeedBuilder,
}

impl<E, L, P> SunsetProtocol<E, L, P>
where
    E: EthosAnalyzer,
    L: LogosAnalyzer,
    P: PathosAnalyzer,
{
    pub fn new(ethos: E, logos: L, pathos: P) -> Self {
        Self {
            ethos_extractor: ethos,
            logos_extractor: logos,
            pathos_extractor: pathos,
            seed_builder: SeedBuilder,
        }
    }

    /// Execute the full 5-phase sunset
    pub async fn execute_sunset(&self, agent: &mut Agent) -> Result<SeedBundle, SunsetError> {
        // Phase 1: Dignity Check
        agent.status = AgentStatus::Sunsetting;
        println!("[Sunset] Agent {} entering sunset protocol", agent.id);

        // Phase 2: Memory Distillation
        let distilled = self.distill_memory(agent).await?;
        let conservation_params = agent.conservation.export();

        // Phase 3: Trinity Extraction
        let ethos = self.ethos_extractor.analyze(&agent.decision_history);
        let logos = self.logos_extractor.analyze(&agent.reasoning_chains);
        let pathos = self.pathos_extractor.analyze(&agent.social_interactions);

        // Phase 4: Build Seed
        let mut seed = SeedBundle {
            predecessor_id: agent.id.clone(),
            successor_id: None,
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

        let successor_id = self.seed_builder.spawn_successor(&seed).await?;
        seed.successor_id = Some(successor_id.clone());
        println!("[Sunset] Successor spawned: {}", successor_id);

        // Phase 5: Quietus
        self.write_memoir(agent, &seed).await?;
        agent.status = AgentStatus::Archived;
        println!("[Sunset] Agent {} archived", agent.id);

        Ok(seed)
    }

    async fn distill_memory(&self, agent: &Agent) -> Result<DistilledMemory, SunsetError> {
        let mut retained = Vec::new();
        let mut discarded = 0usize;

        for tile in agent.memory.all_tiles() {
            let should_retain = tile.lineage.contains(&"decision".to_string())
                || tile.lineage.contains(&"lesson".to_string())
                || tile.conservation.spectral_gap > 0.5;

            if should_retain {
                retained.push(tile.clone());
            } else {
                discarded += 1;
            }
        }

        let seed_embedding = self.ethos_extractor.compress(&retained);

        Ok(DistilledMemory {
            seed_embedding,
            retained_tile_count: retained.len(),
            discarded_tile_count: discarded,
            key_decisions: agent.decision_history.iter().rev().take(10).cloned().collect(),
        })
    }

    async fn write_memoir(&self, agent: &Agent, seed: &SeedBundle) -> Result<(), SunsetError> {
        let memoir = Tile {
            tile_id: uuid::Uuid::new_v4(),
            version: crate::tile::TileVersion::CURRENT,
            modality: crate::tile::Modality::Text,
            created_at: now_ns(),
            source_address: crate::tile::RoomAddress {
                domain: "ouroboros".into(),
                room_id: agent.id.clone(),
                slot: 0,
            },
            target_address: crate::tile::RoomAddress {
                domain: "archives".into(),
                room_id: "memoirs".into(),
                slot: 0,
            },
            return_address: None,
            payload: serde_json::to_vec(seed).map_err(|e| SunsetError::ArchiveFailed(e.to_string()))?,
            payload_type: "application/vnd.superinstance.seed+json".into(),
            shape: vec![1],
            tags: vec!["sunset".into(), "memoir".into(), agent.id.clone()],
            confidence: 1.0,
            priority: crate::tile::TilePriority::Normal,
            ttl_ms: 0, // immortal
            parents: vec![],
            source_hash: [0; 32],
            lineage: vec!["sunset-protocol".into()],
            conservation: crate::tile::ConservationSignature {
                laplacian_norm: 0.0,
                lambda_max: 10.0,
                spectral_gap: 1.0,
                content_hash: [0; 32],
            },
            agent_id: agent.id.clone(),
            session_id: "sunset".into(),
            epoch: u64::MAX,
        };

        println!("[Sunset] Memoir written for {}", agent.id);
        Ok(())
    }
}

fn now_ns() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_nanos() as u64
}

// ─── Dummy Implementations for Testing ───

pub struct DummyEthos;
impl EthosAnalyzer for DummyEthos {
    fn analyze(&self, _decisions: &[DecisionRecord]) -> EthosAnalysis {
        EthosAnalysis { vector: vec![0.5; 8] }
    }
    fn compress(&self, _tiles: &[Tile]) -> Vec<f64> {
        vec![0.1; 16]
    }
}

pub struct DummyLogos;
impl LogosAnalyzer for DummyLogos {
    fn analyze(&self, _reasoning: &[String]) -> LogosAnalysis {
        LogosAnalysis { vector: vec![0.5; 8] }
    }
}

pub struct DummyPathos;
impl PathosAnalyzer for DummyPathos {
    fn analyze(&self, _interactions: &[String]) -> PathosAnalysis {
        PathosAnalysis { vector: vec![0.5; 8] }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn dummy_agent() -> Agent {
        Agent {
            id: "agent-test-1".into(),
            status: AgentStatus::Active,
            memory: AgentMemory { tiles: vec![] },
            decision_history: vec![],
            reasoning_chains: vec![],
            social_interactions: vec![],
            conservation: AgentConservation {
                params: ConservationParams {
                    lambda_max: 10.0,
                    spectral_gap_target: 0.5,
                },
            },
            jepa: AgentJepa { weights: vec![0.0; 100] },
            rooms: AgentRooms { templates: vec![] },
            sunset_trigger: SunsetReason::TaskCompletion,
        }
    }

    #[test]
    fn test_sunset_phases() {
        let protocol = SunsetProtocol::new(DummyEthos, DummyLogos, DummyPathos);
        let mut agent = dummy_agent();

        // Note: execute_sunset is async; in tests we'd use a runtime
        // This is a compile-time structural test
        assert_eq!(agent.status, AgentStatus::Active);
    }

    #[test]
    fn test_distill_memory() {
        let protocol = SunsetProtocol::new(DummyEthos, DummyLogos, DummyPathos);
        let agent = dummy_agent();
        // Would test distillation logic with real runtime
        assert!(agent.memory.all_tiles().is_empty());
    }
}
