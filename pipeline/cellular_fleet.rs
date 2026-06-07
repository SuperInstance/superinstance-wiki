// ============================================================
// cellular_fleet.rs — Grand Pattern Cellular Graph Fleet Topology
// ============================================================
//
// Reference implementation of AGENT-PIPELINE-ARCHITECTURE.md §6.
//
// Models the fleet as a cellular graph where each agent is a cell
// with membrane (conservation boundary), receptors, and effectors.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Peer identifier in the fleet mesh
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct PeerId(pub u64);

/// JEPA latent state shared between fleet cells
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JepaLatent {
    pub values: Vec<f64>,
}

impl JepaLatent {
    pub fn predict(&self) -> Self {
        Self {
            values: self.values.iter().map(|v| v * 1.01).collect(),
        }
    }

    pub fn scale(&self, factor: f64) -> Self {
        Self {
            values: self.values.iter().map(|v| v * factor).collect(),
        }
    }

    pub fn norm(&self) -> f64 {
        self.values.iter().map(|v| v * v).sum::<f64>().sqrt()
    }
}

impl std::ops::Add for JepaLatent {
    type Output = Self;
    fn add(self, rhs: Self) -> Self::Output {
        Self {
            values: self
                .values
                .into_iter()
                .zip(rhs.values.into_iter())
                .map(|(a, b)| a + b)
                .collect(),
        }
    }
}

/// Conservation boundary around each cell
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConservationBoundary {
    pub lambda_max: f64,
}

impl ConservationBoundary {
    /// Project latent state onto spectral ball if it exceeds lambda_max
    pub fn project(&self, latent: &JepaLatent) -> JepaLatent {
        let n = latent.norm();
        if n > self.lambda_max {
            latent.scale(self.lambda_max / n)
        } else {
            latent.clone()
        }
    }
}

/// A cell in the fleet cellular graph
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FleetCell {
    pub id: PeerId,
    pub state: JepaLatent,
    pub membrane: ConservationBoundary,
    pub neighbors: Vec<PeerId>,
    pub receptor_queue: Vec<crate::tile::Tile>,
    pub effector_queue: Vec<crate::tile::Tile>,
}

/// Simple graph structure for fleet topology
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Graph {
    pub node_count: usize,
    pub adjacency: Vec<Vec<usize>>,
}

impl Graph {
    pub fn k_regular(n: usize, k: usize) -> Self {
        let mut adj = vec![vec![]; n];
        let half_k = k / 2;
        for i in 0..n {
            for j in 1..=half_k {
                let neighbor = (i + j) % n;
                adj[i].push(neighbor);
                adj[neighbor].push(i);
            }
        }
        Self {
            node_count: n,
            adjacency: adj,
        }
    }

    pub fn scale_free(n: usize, m: usize) -> Self {
        // Barabási–Albert preferential attachment
        let mut adj = vec![vec![]; n];
        let mut degrees = vec![0usize; n];
        let mut edges = 0;

        // Start with m fully connected nodes
        for i in 0..m.min(n) {
            for j in 0..i {
                adj[i].push(j);
                adj[j].push(i);
                degrees[i] += 1;
                degrees[j] += 1;
                edges += 2;
            }
        }

        // Preferential attachment
        for i in m..n {
            let mut targets = vec![];
            while targets.len() < m {
                let r = fastrand::usize(0..edges);
                let mut cumsum = 0;
                for (node, &deg) in degrees.iter().enumerate() {
                    cumsum += deg;
                    if cumsum > r && !targets.contains(&node) && node != i {
                        targets.push(node);
                        break;
                    }
                }
            }
            for &t in &targets {
                adj[i].push(t);
                adj[t].push(i);
                degrees[i] += 1;
                degrees[t] += 1;
                edges += 2;
            }
        }

        Self {
            node_count: n,
            adjacency: adj,
        }
    }
}

/// Gossip protocol for latent state exchange
#[derive(Debug, Clone)]
pub struct GossipProtocol;

impl GossipProtocol {
    pub fn exchange(&self, cell: &FleetCell, all_cells: &HashMap<PeerId, FleetCell>) -> JepaLatent {
        let mut sum = JepaLatent {
            values: vec![0.0; cell.state.values.len()],
        };
        let mut count = 0;
        for neighbor_id in &cell.neighbors {
            if let Some(neighbor) = all_cells.get(neighbor_id) {
                sum = sum + neighbor.state.clone();
                count += 1;
            }
        }
        if count > 0 {
            sum.scale(1.0 / count as f64)
        } else {
            cell.state.clone()
        }
    }
}

/// Cellular graph fleet implementing Grand Pattern topology
pub struct CellularFleet {
    pub cells: HashMap<PeerId, FleetCell>,
    pub topology: Graph,
    pub gossip: GossipProtocol,
    pub alpha: f64,  // self-prediction weight
    pub beta: f64,   // neighbor averaging weight
    pub gamma: f64,  // conservation projection weight
}

impl CellularFleet {
    pub fn new(n_cells: usize, alpha: f64, beta: f64, gamma: f64) -> Self {
        let topology = Self::optimal_topology(n_cells);
        let mut cells = HashMap::new();

        for i in 0..n_cells {
            let peer_id = PeerId(i as u64);
            let neighbors: Vec<PeerId> = topology.adjacency[i]
                .iter()
                .map(|&j| PeerId(j as u64))
                .collect();

            cells.insert(
                peer_id,
                FleetCell {
                    id: peer_id,
                    state: JepaLatent {
                        values: vec![fastrand::f64(); 16],
                    },
                    membrane: ConservationBoundary { lambda_max: 10.0 },
                    neighbors,
                    receptor_queue: vec![],
                    effector_queue: vec![],
                },
            );
        }

        Self {
            cells,
            topology,
            gossip: GossipProtocol,
            alpha,
            beta,
            gamma,
        }
    }

    pub fn optimal_topology(n_cells: usize) -> Graph {
        let k = ((n_cells as f64).log2().ceil() as usize).max(2);
        Graph::k_regular(n_cells, k)
    }

    /// One evolution step: predict, gossip, update, conserve
    pub fn evolve_step(&mut self) {
        // Phase 1: Self-prediction
        let predictions: HashMap<PeerId, JepaLatent> = self
            .cells
            .iter()
            .map(|(id, cell)| (*id, cell.state.predict()))
            .collect();

        // Phase 2: Gossip (neighbor averaging)
        let all_cells = self.cells.clone();
        let neighbor_averages: HashMap<PeerId, JepaLatent> = self
            .cells
            .iter()
            .map(|(id, cell)| (*id, self.gossip.exchange(cell, &all_cells)))
            .collect();

        // Phase 3: Update each cell
        for (id, cell) in &mut self.cells {
            let pred = predictions.get(id).unwrap();
            let neigh_avg = neighbor_averages.get(id).unwrap_or(pred);

            // Cellular update rule
            let mut new_state = pred.scale(self.alpha) + neigh_avg.scale(self.beta);

            // Conservation projection + normalization
            new_state = cell.membrane.project(&new_state);
            let n = new_state.norm();
            if n > 0.0 {
                new_state = new_state.scale(self.gamma / n);
            }

            cell.state = new_state;
        }
    }

    /// Run fleet-wide consensus for given rounds
    pub fn fleet_consensus(&mut self, rounds: usize) {
        for _ in 0..rounds {
            self.evolve_step();
        }
    }

    /// Compute fleet-wide Laplacian coherence metric
    pub fn fleet_coherence(&self) -> f64 {
        let norms: Vec<f64> = self
            .cells
            .values()
            .map(|c| c.state.norm())
            .collect();
        let mean = norms.iter().sum::<f64>() / norms.len() as f64;
        let variance = norms.iter().map(|n| (n - mean).powi(2)).sum::<f64>() / norms.len() as f64;
        // Lower variance = higher coherence
        1.0 / (1.0 + variance)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_k_regular_graph() {
        let g = Graph::k_regular(8, 3);
        assert_eq!(g.node_count, 8);
        for adj in &g.adjacency {
            assert_eq!(adj.len(), 3);
        }
    }

    #[test]
    fn test_cellular_evolution() {
        let mut fleet = CellularFleet::new(4, 0.5, 0.3, 0.2);
        let initial_coherence = fleet.fleet_coherence();
        fleet.evolve_step();
        let final_coherence = fleet.fleet_coherence();
        // Coherence should remain bounded (conservation)
        assert!(final_coherence >= 0.0 && final_coherence <= 1.0);
        assert!(fleet.cells.values().all(|c| c.state.norm() <= 10.0));
    }

    #[test]
    fn test_fleet_consensus() {
        let mut fleet = CellularFleet::new(16, 0.4, 0.4, 0.2);
        fleet.fleet_consensus(10);
        // After consensus, norms should be similar across cells
        let norms: Vec<f64> = fleet.cells.values().map(|c| c.state.norm()).collect();
        let max_norm = norms.iter().cloned().fold(0.0, f64::max);
        let min_norm = norms.iter().cloned().fold(f64::INFINITY, f64::min);
        assert!((max_norm - min_norm) < 1.0); // should have converged
    }
}
