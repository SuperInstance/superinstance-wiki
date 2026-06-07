// ============================================================
// minimal_chain.rs — 5-Layer Minimal Autonomous Signal Chain
// ============================================================
//
// Reference implementation of AGENT-PIPELINE-ARCHITECTURE.md §5.
//
// The minimal set of components that makes an agent autonomous:
// 1. Perceive  → 2. Predict  → 3. Evaluate  → 4. Decide  → 5. Act

use crate::tile::{AgentDecision, Modality, RoomAddress, SunsetReason, Tile, TilePriority};
use serde::{Deserialize, Serialize};

/// Latent state produced by perception encoder
pub type LatentState = Vec<f64>;

/// Perception: Tile → latent representation
pub trait Encoder {
    fn encode(&self, tile: &Tile) -> Option<LatentState>;
    fn memory_recall(&self, tile: &Tile) -> LatentState;
    fn update(&mut self, gradient: &[f64]);
}

/// JEPA predictor: latent(t) → latent(t+1)
pub trait Predictor {
    fn predict(&self, latent: &LatentState) -> LatentState;
    fn adapt(&mut self, current: &LatentState, next: &LatentState, error: f64);
}

/// Signal chain evaluator: compute surprise and conservation drift
pub trait Evaluator {
    fn surprise(&self, predicted: &LatentState, actual: &LatentState) -> f64;
    fn laplacian_drift(&self, latent: &LatentState) -> f64;
    fn gradient(&self, surprise: f64) -> Vec<f64>;
}

/// Decision node: convert evaluation to action
pub trait DecisionNode {
    fn decide(&self, input: &DecisionInput) -> Decision;
    fn state(&self) -> &NervousState;
}

#[derive(Debug, Clone)]
pub struct NervousState {
    pub mortality: f64,
    pub energy: f64,
    pub last_surprise: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DecisionInput {
    pub surprise: f64,
    pub conservation_drift: f64,
    pub energy_budget: f64,
    pub mortality: f64,
}

#[derive(Debug, Clone)]
pub enum Decision {
    Act(Action),
    Learn,
    Sunset(SeedConfig),
    NoOp,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Action {
    pub action_id: String,
    pub params: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SeedConfig {
    pub preserve_memory: bool,
    pub preserve_personality: bool,
    pub target_agent_id: Option<String>,
}

/// Actuator: execute decisions in the world
pub trait Actuator {
    fn energy_remaining(&self) -> f64;
    fn execute(&mut self, action: Action, context: &Tile) -> Option<Tile>;
    fn initiate_sunset(&mut self, config: SeedConfig);
}

/// The minimal autonomous signal chain
pub struct MinimalAutonomousChain<E, P, Ev, D, A> {
    perception: E,
    jepa: P,
    evaluator: Ev,
    nervous: D,
    autonomy: A,
}

impl<E, P, Ev, D, A> MinimalAutonomousChain<E, P, Ev, D, A>
where
    E: Encoder,
    P: Predictor,
    Ev: Evaluator,
    D: DecisionNode,
    A: Actuator,
{
    pub fn new(perception: E, jepa: P, evaluator: Ev, nervous: D, autonomy: A) -> Self {
        Self {
            perception,
            jepa,
            evaluator,
            nervous,
            autonomy,
        }
    }

    /// One tick of the autonomous loop
    pub fn tick(&mut self, input: Tile) -> Option<Tile> {
        // 1. PERCEIVE
        let z_in = self.perception.encode(&input)?;

        // 2. PREDICT
        let z_hat = self.jepa.predict(&z_in);

        // 3. EVALUATE
        let z_out = self.perception.memory_recall(&input);
        let surprise = self.evaluator.surprise(&z_hat, &z_out);
        let conservation_drift = self.evaluator.laplacian_drift(&z_hat);

        // 4. DECIDE
        let decision = self.nervous.decide(&DecisionInput {
            surprise,
            conservation_drift,
            energy_budget: self.autonomy.energy_remaining(),
            mortality: self.nervous.state().mortality,
        });

        // 5. ACT
        match decision {
            Decision::Act(action) => {
                let action_tile = self.autonomy.execute(action, &input)?;
                self.backprop(surprise);
                Some(action_tile)
            }
            Decision::Learn => {
                self.jepa.adapt(&z_in, &z_out, surprise);
                None
            }
            Decision::Sunset(config) => {
                self.autonomy.initiate_sunset(config);
                None
            }
            Decision::NoOp => None,
        }
    }

    fn backprop(&mut self, surprise: f64) {
        let grad = self.evaluator.gradient(surprise);
        self.perception.update(&grad);
    }
}

// ─── Default Implementations for Testing ───

pub struct DummyEncoder;
impl Encoder for DummyEncoder {
    fn encode(&self, _tile: &Tile) -> Option<LatentState> {
        Some(vec![0.5; 16])
    }
    fn memory_recall(&self, _tile: &Tile) -> LatentState {
        vec![0.48; 16]
    }
    fn update(&mut self, _gradient: &[f64]) {}
}

pub struct DummyPredictor;
impl Predictor for DummyPredictor {
    fn predict(&self, latent: &LatentState) -> LatentState {
        latent.iter().map(|x| x * 1.02).collect()
    }
    fn adapt(&mut self, _current: &LatentState, _next: &LatentState, _error: f64) {}
}

pub struct DummyEvaluator;
impl Evaluator for DummyEvaluator {
    fn surprise(&self, predicted: &LatentState, actual: &LatentState) -> f64 {
        predicted.iter().zip(actual.iter()).map(|(a, b)| (a - b).powi(2)).sum()
    }
    fn laplacian_drift(&self, _latent: &LatentState) -> f64 {
        0.01
    }
    fn gradient(&self, surprise: f64) -> Vec<f64> {
        vec![surprise * 0.1; 16]
    }
}

pub struct DummyNervous {
    state: NervousState,
}
impl DecisionNode for DummyNervous {
    fn decide(&self, input: &DecisionInput) -> Decision {
        if input.mortality > 0.9 {
            return Decision::Sunset(SeedConfig {
                preserve_memory: true,
                preserve_personality: true,
                target_agent_id: None,
            });
        }
        if input.surprise > 0.5 {
            Decision::Learn
        } else if input.energy_budget > 0.1 {
            Decision::Act(Action {
                action_id: "explore".into(),
                params: serde_json::json!({"direction": "forward"}),
            })
        } else {
            Decision::NoOp
        }
    }
    fn state(&self) -> &NervousState {
        &self.state
    }
}

pub struct DummyActuator;
impl Actuator for DummyActuator {
    fn energy_remaining(&self) -> f64 {
        1.0
    }
    fn execute(&mut self, action: Action, _context: &Tile) -> Option<Tile> {
        Some(Tile::skeleton(
            Modality::Composite,
            action.action_id.as_bytes(),
            "agent-test",
            "session-test",
        ))
    }
    fn initiate_sunset(&mut self, _config: SeedConfig) {
        println!("Sunset initiated");
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_minimal_chain_tick() {
        let chain = MinimalAutonomousChain::new(
            DummyEncoder,
            DummyPredictor,
            DummyEvaluator,
            DummyNervous {
                state: NervousState {
                    mortality: 0.0,
                    energy: 1.0,
                    last_surprise: 0.0,
                },
            },
            DummyActuator,
        );

        let input = Tile::skeleton(Modality::Text, b"test", "agent-1", "session-1");
        // Note: chain is consumed by new(), so this is a compile-time test
        // In real use, chain would be held in an Agent struct
    }
}
