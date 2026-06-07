// ============================================================
// jepa_conservation.rs — JEPA + Conservation Spectral Composition
// ============================================================
//
// Reference implementation of AGENT-PIPELINE-ARCHITECTURE.md §4.
//
// Combines Joint Embedding Predictive Architecture (JEPA) with
// conservation spectral analysis to ensure latent predictions
// preserve Laplacian coherence.

use nalgebra::{DMatrix, DVector};
use serde::{Deserialize, Serialize};

/// Latent state vector produced by JEPA encoder
pub type JepaLatent = Vec<f64>;

/// Neural encoder: raw tile → latent representation
pub trait NeuralEncoder {
    fn encode(&self, tile: &crate::tile::Tile) -> Option<JepaLatent>;
}

/// Predictor: latent(t) → latent(t+1)
pub trait LatentPredictor {
    fn predict(&self, latent: &JepaLatent) -> JepaLatent;
    fn adapt(&mut self, current: &JepaLatent, next: &JepaLatent, error: f64);
}

/// Output of the conservation-aware JEPA forward pass
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JepaOutput {
    pub prediction: JepaLatent,
    pub pred_error: f64,
    pub conservation_drift: f64,
    pub was_projected: bool,
}

/// JEPA predictor regularized by conservation spectral constraints
pub struct ConservationJepa<E, P> {
    encoder: E,
    predictor: P,
    lambda_max: f64,
}

impl<E: NeuralEncoder, P: LatentPredictor> ConservationJepa<E, P> {
    pub fn new(encoder: E, predictor: P, lambda_max: f64) -> Self {
        Self {
            encoder,
            predictor,
            lambda_max,
        }
    }

    /// Forward pass with conservation guarantee
    pub fn predict(&self, current: &crate::tile::Tile, next_raw: &crate::tile::Tile) -> Option<JepaOutput> {
        let s_t = self.encoder.encode(current)?;
        let s_t1_actual = self.encoder.encode(next_raw)?;

        // JEPA prediction
        let s_t1_pred = self.predictor.predict(&s_t);

        // Prediction error
        let pred_error = squared_distance(&s_t1_pred, &s_t1_actual);

        // ─── Conservation Spectral Check ───
        let latent_sim = self.compute_similarity_matrix(&[&s_t, &s_t1_pred, &s_t1_actual]);
        let laplacian = build_graph_laplacian(&latent_sim);

        let s_vec = DVector::from_vec(s_t1_pred.clone());
        let laplacian_norm = s_vec.dot(&(&laplacian * &s_vec)) / s_vec.dot(&s_vec);

        if laplacian_norm > self.lambda_max {
            let projected = project_to_spectral_ball(&s_t1_pred, &laplacian, self.lambda_max);
            Some(JepaOutput {
                prediction: projected,
                pred_error,
                conservation_drift: laplacian_norm - self.lambda_max,
                was_projected: true,
            })
        } else {
            Some(JepaOutput {
                prediction: s_t1_pred,
                pred_error,
                conservation_drift: 0.0,
                was_projected: false,
            })
        }
    }

    fn compute_similarity_matrix(&self, latents: &[&JepaLatent]) -> DMatrix<f64> {
        let n = latents.len();
        let mut sim = DMatrix::zeros(n, n);
        for i in 0..n {
            for j in 0..n {
                sim[(i, j)] = cosine_similarity(latents[i], latents[j]);
            }
        }
        sim
    }
}

fn squared_distance(a: &[f64], b: &[f64]) -> f64 {
    a.iter().zip(b.iter()).map(|(x, y)| (x - y).powi(2)).sum()
}

fn cosine_similarity(a: &[f64], b: &[f64]) -> f64 {
    let dot: f64 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
    let norm_a: f64 = a.iter().map(|x| x * x).sum::<f64>().sqrt();
    let norm_b: f64 = b.iter().map(|x| x * x).sum::<f64>().sqrt();
    if norm_a == 0.0 || norm_b == 0.0 {
        0.0
    } else {
        dot / (norm_a * norm_b)
    }
}

fn build_graph_laplacian(similarity: &DMatrix<f64>) -> DMatrix<f64> {
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

    &degree + &laplacian
}

fn project_to_spectral_ball(s: &[f64], l: &DMatrix<f64>, lambda_max: f64) -> Vec<f64> {
    let mut s_proj = DVector::from_vec(s.to_vec());
    for _ in 0..10 {
        let grad = 2.0 * (l * &s_proj);
        s_proj -= grad * 0.01;
        let norm = s_proj.dot(&(l * &s_proj));
        if norm > lambda_max {
            s_proj *= (lambda_max / norm).sqrt();
        }
    }
    s_proj.iter().cloned().collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    struct DummyEncoder;
    impl NeuralEncoder for DummyEncoder {
        fn encode(&self, _tile: &crate::tile::Tile) -> Option<JepaLatent> {
            Some(vec![1.0, 0.5, -0.2])
        }
    }

    struct DummyPredictor;
    impl LatentPredictor for DummyPredictor {
        fn predict(&self, latent: &JepaLatent) -> JepaLatent {
            latent.iter().map(|x| x * 1.01).collect()
        }
        fn adapt(&mut self, _current: &JepaLatent, _next: &JepaLatent, _error: f64) {}
    }

    #[test]
    fn test_conservation_jepa_passes() {
        let encoder = DummyEncoder;
        let predictor = DummyPredictor;
        let jepa = ConservationJepa::new(encoder, predictor, 100.0); // very high lambda

        let t1 = crate::tile::Tile::skeleton(crate::tile::Modality::Text, b"a", "ag", "se");
        let t2 = crate::tile::Tile::skeleton(crate::tile::Modality::Text, b"b", "ag", "se");

        let out = jepa.predict(&t1, &t2).unwrap();
        assert!(!out.was_projected); // should pass with high lambda_max
    }

    #[test]
    fn test_graph_laplacian() {
        let sim = DMatrix::from_row_slice(3, 3, &[
            1.0, 0.5, 0.0,
            0.5, 1.0, 0.3,
            0.0, 0.3, 1.0,
        ]);
        let lap = build_graph_laplacian(&sim);
        // Diagonal should be row sums of off-diagonal
        assert!((lap[(0, 0)] - 0.5).abs() < 1e-10);
        assert!((lap[(1, 1)] - 0.8).abs() < 1e-10);
        assert!((lap[(2, 2)] - 0.3).abs() < 1e-10);
    }
}
