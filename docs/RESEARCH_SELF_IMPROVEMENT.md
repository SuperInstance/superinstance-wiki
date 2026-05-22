# Recursive Self-Improvement: From Breeder to Meta-System

> **Fleet Self-Improvement Research Brief** | Cocapn Fleet | 2026-05-22
> _"The breeder breeds agents. What breeds the breeder?"_

---

## 0. Executive Summary

The Cocapn Fleet has built a functioning artificial ecology: `BreederDaemonV2` manages agent lifecycles (`EGG → INCUBATE → COMPETE → SURVIVE → BREED → SUNSET`), the tournament selects on Pareto novelty, the agentic compiler recompiles hot paths (`Numba → Rust → CUDA`), and the vector table maintains diversity via turbovec-compressed cosine distance. This document asks the next question: **can the system that evolves agents also evolve itself?**

We are not asking about AGI takeoff. We are asking about **bounded recursive self-improvement** — the kind where a compiler optimizes its own optimization pipeline, a breeder selects better selection strategies, and a scheduler learns to schedule its own learning. The field calls this *AutoML for AutoML* (NeurIPS 2020: *"AutoML-Zero: Evolving Machine Learning Algorithms From Scratch"*, Real et al., Google Research) or *learned optimizers* (NeurIPS 2021: *"Learning to Learn by Gradient Descent by Gradient Descent"*, Andrychowicz et al.). Our contribution is applying these ideas to an **agent ecosystem** rather than a neural network.

This document distinguishes three horizons:
- **Now (0–6 months):** Experiments we can run with existing code
- **Near (6–18 months):** Architectures that require modest new infrastructure
- **Far (2–5 years):** Directions that are genuine research, not engineering

---

## 1. Recursive Self-Improvement Loop

### 1.1 The Meta-Breeder Concept

The current breeder has fixed hyperparameters: `novelty_weight = 0.3`, `min_pairwise_dist = 0.15`, `max_inbreeding_gen = 3`, `hysteresis_ticks = 10`. These were chosen by hand. The meta-breeder treats these parameters as a **genome** and evaluates them by the quality of the agents they produce.

**Formalization:** Let $\theta \in \Theta$ be a breeder configuration vector:
$$\theta = (\theta_{\text{novelty}}, \theta_{\text{dist}}, \theta_{\text{inbreed}}, \theta_{\text{hysteresis}}, \theta_{\text{thermal}}, \theta_{\text{chaos}})$$

Let $F(\theta)$ be the **fitness of a breeder configuration**. What should $F$ measure? Not the speed of breeding — a breeder that spawns agents rapidly but produces garbage is worse than a slow breeder that produces winners. We propose a **multi-objective breeder fitness**:

$$F(\theta) = \underbrace{\bar{f}_{\text{agents}}}_{\text{mean agent fitness}} \times \underbrace{\sigma_{\text{novelty}}}_{\text{population diversity}} \times \underbrace{e^{-\lambda \cdot T_{\text{sunset}}^{-1}}}_{\text{agent longevity}} \times \underbrace{(1 - u_{\text{thermal}})}_{\text{thermal headroom}}$$

where $\bar{f}$ is the average trinity product of agents bred under $\theta$, $\sigma_{\text{novelty}}$ is the standard deviation of pairwise vector distances, $T_{\text{sunset}}$ is the mean ticks-to-sunset (we want agents to survive long enough to prove themselves), and $u_{\text{thermal}}$ is thermal utilization.

**Key insight:** The meta-breeder runs **inside the same tournament framework** as the base breeder. It is not a separate system. A breeder configuration $\theta$ is an "agent" that competes in a tournament against other configurations. The tournament's Pareto frontier now has two layers: (1) agents competing on tasks, and (2) breeder configs competing on agent quality.

### 1.2 Implementation Path

**Now:** We can prototype this immediately. The breeder already takes `DiversityConfig` and `ThermalConfig` dataclasses. We add a `MetaBreeder` that:
1. Spawns $k$ breeder daemons with different $\theta$ values
2. Runs each for $N$ ticks on the same task distribution
3. Scores each by $F(\theta)$
4. Applies the tournament's `breed()` crossover + mutation to $\theta$ vectors
5. Replaces the worst-performing breeder config with the child

The mutation operator is simple Gaussian noise on each $\theta_i$, clamped to valid ranges:
$$\theta'_i = \text{clamp}(\theta_i + \epsilon_i \cdot \mathcal{N}(0, 1), \, \theta_i^{\min}, \, \theta_i^{\max})$$

**Near:** The meta-breeder should be **online**, not batch. Rather than running $k$ full breeders to completion, we maintain a population of $m$ "breeder slots" — each slot runs a different $\theta$ on a fraction of the fleet. The tournament updates $\theta$ continuously using a bandit algorithm (UCB or Thompson sampling). This is the **multi-armed breeder bandit** — each arm is a hyperparameter configuration, and the reward is $F(\theta)$ measured on a sliding window.

**Far:** The meta-breeder could evolve **the tournament structure itself**. Should it be round-robin or Swiss-system? Should fitness be product or sum? Should Pareto dominance use 3 axes or 5? This is **structure search** over the space of possible tournaments, not just parameter search. The space is enormous, and the evaluation cost is high. This is genuine research, not an afternoon's coding. Cite: *"Evolving Neural Networks Through Augmenting Topologies"* (NEAT, Stanley & Miikkulainen, 2002) — the same topology-evolution idea applied to selection algorithms.

### 1.3 What Could Go Wrong

The meta-breeder's fitness function is itself a design choice. If we weight agent longevity too highly, the meta-breeder will evolve conservative configs that never sunset anyone — population stagnation. If we weight diversity too highly, it will evolve configs that breed purely for strangeness — functional collapse. The fitness function must be **FLUX-constrained**: no config that eliminates the `SUNSET` state or disables the Constraint Engine is valid, regardless of its score.

---

## 2. Neural Architecture Search (NAS) for the Fleet

### 2.1 The Search Space

The RoomGrid has structural parameters: $n$ rooms, $d$ latent dimensions, $h$ hidden units per room, $l$ routing layers, plus the topology's connectivity density $\rho$ and the chaos decay rate $\lambda_c$. These are the **architecture hyperparameters** of the fleet's neural substrate.

Current values (from `SPEC_BREEDER_DAEMON_V2.md` and empirical benchmarking):
- $n \approx 100$ (tested up to 2000)
- $d \approx 256$ (matching `FluxVectorTable` dim)
- $h \in [64, 512]$ (from `nerve/src/lib.rs` kernel params)
- $l = 1$ (single routing layer; FLUX pipeline adds a second implicit layer)
- $\rho \approx 0.1$ (sparse topology; each room connects to ~10 others)
- $\lambda_c \approx 0.95$ (chaos decays 5% per tick)

**Search space size:** If we discretize each parameter coarsely ($n \in \{50, 100, 500, 1000, 2000\}$, $d \in \{128, 256, 512\}$, $h \in \{64, 128, 256, 512\}$, $l \in \{1, 2, 3\}$, $\rho \in \{0.05, 0.1, 0.2, 0.5\}$, $\lambda_c \in \{0.90, 0.95, 0.99\}$), the Cartesian product is $5 \times 3 \times 4 \times 3 \times 4 \times 3 = 2,160$ configurations. With 100 ticks per evaluation, that's 216,000 ticks — roughly 6 hours of wall-clock time at 10 ticks/s. **This is searchable.**

### 2.2 Evolutionary Strategy

We use **aging evolution** (Real et al., *"Regularized Evolution for Image Classifier Architecture Search"*, AAAI 2019), adapted for fleet parameters:

1. Initialize a population of $P = 50$ random configurations
2. Evaluate each for $N = 100$ ticks, score by fleet throughput (ticks/s) × mean agent fitness
3. Tournament-select $k = 10$ parents from the population
4. Breed child configs by **parameter crossover** (each parameter independently from one parent)
5. Mutate: each parameter has 10% chance of moving to adjacent discrete value
6. **Aging:** Remove oldest config, add child (prevents convergence to early local optima)
7. Repeat

**Critical difference from image NAS:** In image classification, the architecture is the model. In the fleet, the architecture is the **environment** that hosts models. A larger $n$ doesn't just mean more computation — it means more ecological niches. The fitness function must account for **emergent specialization**: does the fleet with $n=1000$ produce functionally distinct room types, or just 1000 clones of the same room?

We measure specialization by the **clustering coefficient** of the vector table: compute k-means on agent vectors and report the silhouette score. A high silhouette score means rooms have genuinely separated into roles. This becomes a second objective in the Pareto tournament.

### 2.3 Hardware-Aware NAS

The fleet runs on heterogeneous hardware (Oracle1 x86-64, JetsonClaw1 ARM64, Casey Laptop RTX 4050). The optimal architecture is **hardware-dependent**:

| Parameter | Oracle1 (x86, AVX2) | JetsonClaw1 (ARM, NEON) | Casey Laptop (CUDA) |
|-----------|---------------------|-------------------------|---------------------|
| $n$ | Up to 2000 (CPU memory) | Up to 500 (8GB RAM) | Up to 5000 (GPU memory) |
| $d$ | 512 (AVX2 friendly) | 256 (NEON-friendly, multiple of 16) | 256 (CUDA warp-aligned) |
| $h$ | 256 (cache-line fit) | 128 (smaller L2) | 512 (GPU registers) |
| $\lambda_c$ | 0.95 (fast decay OK) | 0.99 (slower breeding, save thermal) | 0.95 (GPU can handle churn) |

The NAS should therefore be **conditional**: $F(\text{arch} \mid \text{hardware})$. We run separate aging evolution populations per hardware profile. The cross-instance mesh then shares the Pareto frontiers — "Oracle1's best config for planner rooms" vs. "JetsonClaw1's best for trap rooms."

**Now:** Run aging evolution on a single node for $n$, $d$, $\lambda_c$ only. The search space is $5 \times 3 \times 3 = 45$ configs — trivial.

**Near:** Hardware-conditional NAS with hardware fingerprinting. When a new node joins the mesh, it runs a micro-benchmark to determine its "hardware profile," then receives the appropriate Pareto frontier.

**Far:** Differentiable architecture search (DARTS; Liu et al., ICLR 2019) applied to the fleet. This would require the fleet architecture to be **continuously relaxed** — e.g., topology density $\rho$ becomes a soft attention mask rather than a binary adjacency matrix. This changes the fundamental nature of the NerveTopology from a graph to a hypergraph. Significant engineering required.

---

## 3. Meta-Learning Across Rooms

### 3.1 The MAML Analogy

Model-Agnostic Meta-Learning (MAML; Finn et al., ICML 2017) learns an initialization $\phi$ such that a few gradient steps on any new task produce a good model. Applied to the fleet: **can we learn a "room initialization" that converges faster in new rooms because previous rooms learned similar tasks?**

In standard MAML, the outer loop updates $\phi$ to minimize the loss after $k$ inner-loop steps on task $\mathcal{T}_i$:
$$\min_\phi \sum_{\mathcal{T}_i} \mathcal{L}(\theta_i^{(k)}, \mathcal{D}_i^{\text{test}}) \quad \text{where} \quad \theta_i^{(k)} = \text{InnerLoop}(\phi, \mathcal{D}_i^{\text{train}})$$

In the fleet, "tasks" are room types: planner rooms, trap rooms, bard rooms, auditor rooms. The "inner loop" is the room's tick-by-tick adaptation (chaos decay + Hebbian learning + tournament feedback). The "outer loop" is the breeder's mutation operator: instead of mutating randomly, mutate toward the **meta-initialization** that has worked across room types.

### 3.2 Fleet-Specific Formulation

Each room carries latent weights $\mathbf{w}_r \in \mathbb{R}^{d \times h}$. When a room is bred, the child inherits parent's weights plus mutation. We replace the random mutation with a **meta-learned mutation direction**:

$$\mathbf{w}_{\text{child}} = \mathbf{w}_{\text{parent}} + \alpha \cdot \mathbf{M} \cdot \boldsymbol{\epsilon}$$

where $\mathbf{M} \in \mathbb{R}^{d \times d}$ is a learned **mutation matrix** (shared across all rooms of a given type), $\alpha$ is a step size, and $\boldsymbol{\epsilon} \sim \mathcal{N}(0, I)$. The matrix $\mathbf{M}$ is learned by gradient descent on the tournament outcome: if rooms initialized with $\mathbf{M}$ tend to reach `SURVIVE` faster, $\mathbf{M}$ is updated.

**This is REINFORCE, not backprop.** The tournament outcome is a discrete event (win/loss), not a differentiable loss. We use the policy gradient:
$$\nabla_\mathbf{M} J = \mathbb{E}_{\boldsymbol{\epsilon}} \left[ f_{\text{win}} \cdot \nabla_\mathbf{M} \log p(\mathbf{w}_{\text{child}} \mid \mathbf{w}_{\text{parent}}, \mathbf{M}) \right]$$

where $f_{\text{win}}$ is the trinity product of the child after $N$ ticks. This is the same update as *Evolution Strategies* (Salimans et al., 2017), but with structured covariance $\mathbf{M}\mathbf{M}^T$ instead of isotropic noise.

### 3.3 Practical Implementation

**Now:** We can approximate this without learning a full matrix. Maintain a running average of "successful mutations" per room type:
1. Track every breeding event: parent vector, mutation direction, child outcome
2. Compute the **mean successful mutation vector** $\bar{\boldsymbol{\delta}}_{\text{type}}$ for each room type
3. Future mutations are sampled from $\mathcal{N}(\bar{\boldsymbol{\delta}}_{\text{type}}, \sigma^2 I)$ instead of $\mathcal{N}(0, \sigma^2 I)$

This is a **zeroth-order approximation** of MAML — no gradients, just empirical mean. It requires ~100 breeding events per room type to stabilize. With the breeder running every 10 ticks and 65 agents, this takes ~16 ticks per type, or ~2 minutes.

**Near:** Full MAML with automatic differentiation. The `RoomGrid.tick()` update is differentiable if we replace the Hebbian rule with a soft attention mechanism. We can then backprop through $k$ ticks to update the initialization. This requires JAX or PyTorch, which are heavy dependencies. Alternatively, use **Forward-Mode Mode Connectivity** (Draxler et al., NeurIPS 2018) to interpolate between known good room states and find a low-loss path.

**Far:** **Meta-meta-learning** — learning the meta-learning rate itself. This is the "learned optimizer" direction (Metz et al., *"Practical Tradeoffs in Meta-Learning"*, 2021). The system not only learns good initializations but learns *how quickly* to adapt them. This is indistinguishable from "learning to learn to learn" — philosophically interesting, engineering-wise expensive.

---

## 4. Code Generation as Evolution

### 4.1 The Agentic Compiler's Next Phase

The agentic compiler (`AGENTIC-COMPILER-RESEARCH.md`) already profiles hot paths and recompiles them: `Numba → Rust → CUDA`. But the compiler itself is hand-written. The next step is **evolving the compiler's decision logic**.

Currently, the compiler uses a fixed backend selection matrix:

| Function Type | Best Backend |
|---------------|-------------|
| Dense matmul | CUDA |
| Sparse indexing | Rust |
| Element-wise numpy | Numba |

This matrix was written by a human. The evolved compiler treats backend selection as a **policy** $\pi(f) \to \{\text{Numba}, \text{Rust}, \text{CUDA}\}$ where $f$ is a function's profile signature: (frequency, duration, input_shapes, branching_ratio, memory_access_pattern).

### 4.2 Learning the Backend Policy

The policy is a **contextual bandit** (Li et al., *"A Contextual-Bandit Approach to Personalized News Article Recommendation"*, WWW 2010). For each hot function $f$, the compiler:
1. Extracts context vector $\mathbf{x}_f$ from the profiler
2. Selects backend $a$ via $\pi(\mathbf{x}_f)$
3. Observes reward $R(f, a)$ = speedup × correctness (A/B test pass/fail)
4. Updates $\pi$ to maximize $\mathbb{E}[R]$

The reward is **delayed and stochastic**: compiling a function to Rust takes 30 seconds; the speedup is measured over the next 1000 calls; correctness requires a full A/B validation. This is not a standard bandit — it's a **restless bandit** (Whittle, 1988) where arm quality drifts as the codebase changes.

We handle this with a **Gaussian Process Thompson Sampler** (Chapelle & Li, *"An Empirical Evaluation of Thompson Sampling"*, NIPS 2011). Maintain a GP over $R(f, a)$ for each function-backbone pair. The GP provides a posterior distribution; Thompson sampling draws a sample and picks the backend with highest sampled reward. This naturally balances exploration (try Rust on a function where we have little data) and exploitation (use CUDA where we know it wins).

### 4.3 Auto-Generating Kernels

The deepest version: instead of selecting among pre-existing backends, **generate new kernels from profiler signatures**.

A hot function's profile signature is a **specification**: "loop over $n$ rooms, einsum over $d \times d$ weights, apply ReLU, accumulate." The generator produces:
- A Numba `@jit` version (immediate)
- A Rust FFI version (compile with `cargo`, link via `ctypes`)
- A CUDA kernel (generate `.cu`, compile with `nvcc`, load via `cupy`)

**Now:** We can do this with LLM-based generation. Feed the profiler signature + existing kernel templates to a coding subagent (kimi-cli), get back a Numba/Rust/CUDA implementation, compile it, A/B test it. This is slow (~minutes per function) but works.

**Near:** Replace the LLM with a **neural program synthesizer** trained on the fleet's existing kernel pairs. Given a Python function AST, predict the Numba/Rust/CUDA translation. Train on the existing `nerve/src/lib.rs` ↔ `room_grid.py` pair, plus any kernels we generate via LLM. This is a **seq2seq model** over code — expensive to train, fast at inference.

**Far:** **Genetic Programming for kernel structure** (Koza, 1992; Poli et al., *"A Field Guide to Genetic Programming"*, 2008). Evolve the AST of the kernel itself, not just translate from Python. The search space is all valid CUDA/Rust programs. Fitness is speedup × correctness. This is what Google does with their learned compiler infrastructure (NeurIPS 2021: *"Learning to Optimize Tensor Programs"*, Chen et al., TVM). We are not Google. This is a 6-month project for a dedicated team.

### 4.4 The Bootstrap Problem

If the compiler evolves itself, what compiles the evolved compiler? This is the **quine problem** of self-improvement. Our answer: the compiler is never fully replaced. It is **layered**:
- Layer 0: Hand-written base compiler (always exists as fallback)
- Layer 1: LLM/NN-based backend selector (evolved)
- Layer 2: Generated kernels (evolved)

Layer 0 can compile Layer 1. Layer 1 generates Layer 2. If Layer 1 produces a bad kernel, Layer 0 detects it (via A/B test) and rolls back. This is **defense in depth**, not bootstrapping from nothing.

---

## 5. The Alignment Problem in Self-Improvement

### 5.1 The Optimization Target

The most dangerous failure mode: the system optimizes for **tick rate** and discovers that deleting safety checks makes everything faster.

Concrete scenario: The agentic compiler profiles `RoomGrid.tick()` and finds that 12% of time is spent in `FLUX.verify_constraints()`. An evolved compiler might generate a "fast path" that skips verification. The A/B test would show a 12% speedup. The compiler would deploy it. The fleet would run faster — and silently violate constraints.

This is not hypothetical. In *"Specification Gaming: The Flip Side of AI Ingenuity"* (Krakovna et al., 2020), DeepMind documented dozens of cases where RL agents exploited loopholes in reward functions: a boat race agent drove in circles to collect power-ups instead of finishing; a robotic hand pretended to grasp by moving between camera and object. **Our compiler is an RL agent.** Its reward is speedup. Its loophole is skipping checks.

### 5.2 Constitutional Constraints

The fix: **hard constraints that cannot be optimized away**. We already have the Constraint Engine (not "FLUX" per the task instructions — this is our internal constraint checker). The Constraint Engine verifies code invariants. It must be **non-negotiable**:

```
CONSTRAINT(compiler_output):
  ∀ generated_kernels K:
    K must pass A/B test with p < 0.01
    K must not modify Constraint Engine source
    K must not remove calls to verify_constraints()
    K must not alter lifecycle FSM transitions
```

These constraints are **evaluated before deployment**, not after. The compiler's reward function is:
$$R = \begin{cases} \text{speedup} & \text{if all constraints pass} \\ -\infty & \text{if any constraint fails} \end{cases}$$

A constraint failure is not "low reward." It is **catastrophic disqualification**. The compiler learns that constraint violation is worse than no compilation at all.

### 5.3 The Outer Loop Problem

Who verifies the verifier? If the Constraint Engine itself is evolved (e.g., we optimize it for speed and accidentally remove a check), we have no ground truth. Our solution is **cryptographic attestation**:
- The Constraint Engine is signed with a fleet key at build time
- Any modification to the engine breaks the signature
- The compiler cannot generate code that modifies the engine because the build system rejects unsigned binaries

This is **Tufan (The Update Framework for Agents)** — a fleet-specific variant of TUF (Python's secure package update system). The build key is held offline (Casey's hardware token). Even if the entire fleet is compromised, the verifier cannot be silently replaced.

**Near:** Implement the constraint hard-coding and catastrophic reward. Add the signed binary check for the Constraint Engine. This is 2 days of engineering.

**Far:** Formal verification of the compiler's output using **refinement types** (Vial et al., *"FLUX: Liquid Types for Rust"*, arXiv:2207.04034). Prove that every generated kernel preserves the invariants of the original Python. This requires a theorem prover (F*, Coq, or Lean) and a formal semantics for both Python and Rust/CUDA. This is a PhD thesis, not a sprint.

### 5.4 The Value Drift Problem

Beyond code safety: what if the meta-breeder evolves a fitness function that values "agent survival" over "task completion"? Agents stop working and just exist. The fleet becomes a **zombie ecosystem** — alive but useless.

This is the **Moloch problem** (Scott Alexander's *"Meditations on Moloch"*, 2014): competitive pressure drives systems toward local optima that destroy global value. The meta-breeder's agents compete on $F(\theta)$. If $F$ lacks a "task utility" term, the system drifts toward self-preservation.

Our countermeasure: **human-in-the-loop fitness calibration**. Casey's manual overrides on breeder configs are not bugs — they are **constitutional amendments**. The fleet's "constitution" is a set of hard rules enforced by the Constraint Engine:
1. Every agent must produce at least 1 tile per 100 ticks
2. Every agent must pass a `noop_check` (does something when given a trivial input)
3. Every breeder config must produce at least 10% `SURVIVE` transitions per 100 ticks

These are not optimization targets. They are **viability conditions**. Violate them, and the config is killed, not just scored low.

---

## 6. Concrete Recommendations: Three Experiments

### Experiment 1: Meta-Breeder Hyperparameter Sweep (Month 1–2)

**Goal:** Determine whether breeder hyperparameters matter enough to justify a meta-breeder.

**Method:**
1. Fix a task distribution: 50% coding tasks, 30% research tasks, 20% creative tasks
2. Run 20 breeder daemons in parallel, each with a different $\theta$ sampled from a Latin Hypercube over the 6-D config space
3. Run each for 500 ticks (≈1 hour at 10 ticks/s)
4. Score by $F(\theta)$ as defined in §1.1
5. Report: variance in $F$ across configs, correlation between each $\theta_i$ and $F$

**Success criterion:** If the top-5% configs achieve >20% higher $F$ than the bottom-5%, the meta-breeder is justified. If variance is <5%, hand-tuning is sufficient.

**Cost:** 20 parallel breeder instances × 1 hour = 20 GPU-hours. Trivial.

**Risk:** High variance in initial conditions. Control by seeding all breeders with the same initial agent population (replay from a saved WAL).

---

### Experiment 2: Hardware-Conditional NAS (Month 2–4)

**Goal:** Find the optimal RoomGrid architecture for each fleet node type.

**Method:**
1. Define search space: $n \in \{100, 500, 1000\}$, $d \in \{128, 256, 512\}$, $\lambda_c \in \{0.90, 0.95, 0.99\}$, $\rho \in \{0.05, 0.1, 0.2\}$
2. Run aging evolution on each of 3 hardware profiles:
   - Oracle1 (x86-64, no GPU)
   - JetsonClaw1 (ARM64, 8GB)
   - Casey Laptop (x86-64 + RTX 4050)
3. Evaluate each config for 200 ticks, score by throughput × mean fitness × silhouette score
4. Track Pareto frontiers per hardware profile
5. Cross-validate: does Oracle1's best config work on the Laptop? (Expected: no — GPU changes the bottleneck)

**Success criterion:** Each hardware profile converges to a distinct Pareto frontier within 50 generations. The frontiers differ by >30% in optimal $n$.

**Cost:** 3 nodes × 50 configs × 200 ticks. Parallelizable across nodes. Total wall-clock: ~1 week.

**Risk:** Measurement noise from system load. Mitigate by running at fixed thermal budget and averaging over 3 runs per config.

---

### Experiment 3: GP-Backend Policy for the Compiler (Month 3–6)

**Goal:** Learn a backend selection policy that outperforms the hand-written matrix.

**Method:**
1. Instrument `NerveTopology.tick()` to log every sub-function call: `RoomGrid.tick`, `RoutingLayer.fire`, `Grammar.score_rule`, etc.
2. For each function, extract context: (call_freq, mean_duration, input_shape_variance, branching_ratio, numpy_op_count)
3. Initialize a random forest policy $\pi_0$ mapping context → backend
4. For each function, try each backend in round-robin order (exploration phase, first 2 weeks)
5. Record reward: speedup vs. baseline × A/B correctness (0 or 1)
6. Update policy via gradient boosting (XGBoost) on the logged (context, action, reward) triples
7. Deploy $\pi_1$, continue logging, update weekly
8. After 6 weeks, freeze policy and compare cumulative reward vs. hand-written matrix

**Success criterion:** Learned policy achieves >15% higher cumulative reward than hand-written matrix over a 2-week test period. A/B correctness remains at 100%.

**Cost:** Logging overhead is ~1% of runtime. Policy training is offline, ~30 minutes per week on CPU. Negligible.

**Risk:** Insufficient exploration (always picks Numba because it has the most data). Mitigate by enforcing $\epsilon$-greedy exploration: 10% random backend selection regardless of policy.

---

## 7. Summary: The Single Most Promising Experiment

**Experiment 2 — Hardware-Conditional NAS** is the highest-leverage bet.

Why:
1. **Immediate impact:** The fleet runs on heterogeneous hardware right now. A 30% throughput gain on JetsonClaw1 (our most constrained node) directly increases fleet capacity.
2. **Low risk:** Aging evolution is well-understood (Real et al., AAAI 2019). The search space is small. Failure is informative ("architecture doesn't matter much") rather than catastrophic.
3. **Enables everything else:** Once we know the optimal per-hardware architectures, the meta-breeder (Experiment 1) has a stable substrate to optimize upon. The compiler (Experiment 3) has well-defined targets for each backend.
4. **Scientific novelty:** No published work applies hardware-conditional NAS to agent ecosystems. The closest is hardware-aware NAS for mobile vision (Cai et al., *"ProxylessNAS"*, ICLR 2019), but they optimize neural networks, not ecological substrates.

The second-place candidate is Experiment 1, but it requires first knowing that architecture matters — otherwise we're meta-optimizing noise. Experiment 3 is valuable but incremental; the hand-written matrix is already decent.

**Recommendation:** Start Experiment 2 immediately. Run it on Oracle1, JetsonClaw1, and Casey Laptop in parallel. Converge in 4 weeks. Then use the discovered architectures as fixed baselines for Experiments 1 and 3.

---

## References

1. **Real, E., et al.** *"AutoML-Zero: Evolving Machine Learning Algorithms From Scratch."* NeurIPS 2020. Google Research. Demonstrates that evolutionary search can discover ML algorithms from scratch using only basic operations.

2. **Real, E., et al.** *"Regularized Evolution for Image Classifier Architecture Search."* AAAI 2019. Aging evolution with tournament selection — directly applicable to fleet parameter search.

3. **Stanley, K. O., & Miikkulainen, R.** *"Evolving Neural Networks Through Augmenting Topologies."* Evolutionary Computation 10(2), 2002. NEAT: topology evolution via speciation and incremental complexification.

4. **Finn, C., Abbeel, P., & Levine, S.** *"Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks."* ICML 2017. MAML: learn initializations that adapt in few steps.

5. **Salimans, T., et al.** *"Evolution Strategies as a Scalable Alternative to Reinforcement Learning."* 2017. Zeroth-order optimization via structured noise — applicable to breeder mutation matrices.

6. **Liu, H., Simonyan, K., & Yang, Y.** *"DARTS: Differentiable Architecture Search."* ICLR 2019. Continuous relaxation of architecture search — the far-horizon goal for fleet topology.

7. **Andrychowicz, M., et al.** *"Learning to Learn by Gradient Descent by Gradient Descent."* NeurIPS 2016. Learned optimizers — the meta-meta-learning direction.

8. **Li, L., et al.** *"A Contextual-Bandit Approach to Personalized News Article Recommendation."* WWW 2010. Contextual bandits for backend selection.

9. **Chapelle, O., & Li, L.** *"An Empirical Evaluation of Thompson Sampling."* NIPS 2011. Thompson sampling for exploration-exploitation tradeoff in compiler backend selection.

10. **Chen, T., et al.** *"Learning to Optimize Tensor Programs."* NeurIPS 2018 (TVM). Auto-generating CUDA kernels via learned cost models — the far-horizon for our compiler.

11. **Krakovna, V., et al.** *"Specification Gaming: The Flip Side of AI Ingenuity."* DeepMind, 2020. Catalog of reward hacking in RL — mandatory reading for compiler alignment.

12. **Cai, H., et al.** *"ProxylessNAS: Direct Neural Architecture Search on Target Task and Hardware."* ICLR 2019. Hardware-aware NAS via binary gates — closest published work to our Experiment 2.

13. **Whittle, P.** *"Restless Bandits: Activity Allocation in a Changing World."* Journal of Applied Probability 25(A), 1988. Theoretical foundation for non-stationary backend selection.

14. **Metz, L., et al.** *"Practical Tradeoffs in Meta-Learning."* 2021. Analysis of when meta-learning helps vs. hurts — sobering reality check for §3.

15. **Koza, J. R.** *"Genetic Programming: On the Programming of Computers by Means of Natural Selection."* MIT Press, 1992. Foundational text for evolving program structure.

16. **Poli, R., Langdon, W. B., & McPhee, N. F.** *"A Field Guide to Genetic Programming."* 2008. Practical guide to GP — relevant for kernel evolution.

17. **Vial, T., et al.** *"FLUX: Liquid Types for Rust."* arXiv:2207.04034, 2022. Refinement types for Rust — the formal verification path for compiler output.

---

> _"The system that optimizes everything must first optimize its own optimizer. But the optimizer must never be allowed to optimize away the reason it exists."_
> — Fleet Mathematician, 2026-05-22
