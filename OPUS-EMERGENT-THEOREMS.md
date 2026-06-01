This is a genuinely fun synthesis problem, and I want to engage it rigorously — which means being honest about a distinction the framing blurs. Some of these "theorems" rest on *established* mathematics (Varadhan's formula, JKO gradient flow, Noether, the CALM theorem, sheaf-cohomological obstructions to consensus, linearly-solvable MDPs). Others are *conjectural bridges* (Observation ⊣ Control, "curvature = FLOPs," the Dequantizable Dirichlet Space as a literal unifying object). The interesting emergent theorems live exactly where established results from *different* crates turn out to be the same theorem viewed twice. I'll mark each link ✅ (rests on a real result) or ⚠️ (conjectural glue).

Let me first say what the common substrate actually is, because that controls everything downstream.

## The substrate: one Dirichlet form, four shadows

A Dirichlet form $\mathcal{E}(f,f)=\int |\nabla f|^2\,d\mu$ on $L^2(\mu)$ is not one structure — it canonically generates four, and *each crate is reading off one of them*:

| Generated structure | Crate(s) reading it |
|---|---|
| Markov semigroup $P_t=e^{-t\mathcal{L}}$ (heat flow) | varadhan, ergodic-gradient |
| Wasserstein gradient-flow of free energy $F=U-TS$ | thermal-rl, ergodic-gradient |
| Intrinsic metric $d(x,y)$ (Carnot–Carathéodory) | varadhan, symplectic |
| Harmonic sheaf + its cohomology $H^\bullet$ | sheaf-automata, homotopy, trace-monoid |

`★ Insight ─────────────────────────────────────`
The reason these compose at all is that **the generator $\mathcal{L}$, the metric $d$, the free energy $F$, and the cohomology $H^\bullet$ are not independent data** — fixing the Dirichlet form fixes all four. So a "composition" of two crates is forced to be consistent; you're not gluing strangers, you're reconciling two coordinates on one manifold. That's *why* you should expect emergent theorems rather than mere conjunctions.
`─────────────────────────────────────────────────`

---

## Three emergent theorems (with proof sketches)

### Emergent Theorem A — Optimal control is a Dirichlet eigenfunction
*(thermal-rl ∩ ergodic-gradient ∩ varadhan ∩ dirichlet-space)*

**Claim.** When the RL problem is KL-regularized (the thermal-rl hypothesis), the optimal value function linearizes: $z := e^{-V/\lambda}$ is the *principal eigenfunction of the Dirichlet-form semigroup*, the optimal policy is the ground-state transform (Doob $h$-transform) of the heat flow, and gradient descent on the policy **is** the Fokker–Planck relaxation to that ground state.

**Proof sketch.**
1. ✅ KL-regularized (entropy-regularized) control makes the Bellman optimality operator a log-sum-exp / soft-max. Under the Hopf–Cole / desirability change of variables $z=e^{-V/\lambda}$, the nonlinear HJB collapses to the **linear** equation $z = e^{q/\lambda}\,P z$ (Todorov's linearly-solvable MDPs; Kappen's path-integral control). That is exactly an eigenproblem $P_\beta z = e^{-\rho} z$ for the sub-Markov kernel — i.e. $z$ is a harmonic function of the Dirichlet form $\mathcal{E}$ generating $P$. ✅
2. ✅ The optimal policy is $\pi^\star \propto P\, z$, the Doob $h$-transform of the heat semigroup by its ground state $z$. The controlled process is the heat flow *conditioned to stay alive*.
3. ✅ The on-policy distribution evolves by the Fokker–Planck equation of that conditioned generator, which (Jordan–Kinderlehrer–Otto) is the **Wasserstein gradient flow of free energy** $F=\langle \text{cost}\rangle - \lambda\,S$. So "GD = time-reversed Fokker–Planck" (ergodic-gradient) and "RL = free-energy descent" (thermal-rl) are the *same* descent.
4. ✅ Varadhan ties the metric in: $-\lambda \log z(x) = V(x)$ is, in the short-horizon limit, $\tfrac12 d(x,\text{goal})^2$ — the value function *is* the squared intrinsic distance of the Dirichlet form.

**Why emergent:** none of the four crates alone says "the policy is an eigenvector." It only appears when thermal-rl's free energy, ergodic-gradient's flow, and the spectral content of dirichlet-space are forced to agree. **Prediction:** the optimal policy's convergence rate equals the *spectral gap* of the observation-bundle Laplacian — a number Kalman/Hodge (crate 1) computes directly.

---

### Emergent Theorem B — Coordination-free ⟺ permutation-Noether-conserved
*(calm-crdt ∩ noether-agents ∩ conservation-laws)*

**Claim.** A multi-agent aggregate update is *coordination-free* (CALM: confluent without consensus) **iff** it is invariant under the agent-permutation symmetry whose Noether charge is the aggregate itself. CRDT merge laws (associative, commutative, idempotent = a join-semilattice) are precisely the *finite-group Noether conditions* for agent exchangeability.

**Proof sketch.**
1. ✅ CALM theorem (Hellerstein; Ameloot–Ketsman–Neven; Kuper–Marczak): a query/update is coordination-free iff it is *monotone*, and confluent replicated state must form a join-semilattice (ACI merge) — the CvRDT condition.
2. ✅ An aggregate $g$ over agents that is **associative + commutative + idempotent** is exactly a function invariant under the full symmetric group action *and* under duplication. Commutative+associative = invariant under $S_n$ reordering (the discrete symmetry); idempotent = invariant under the diagonal/duplication map.
3. ⚠️→✅ Noether for a *discrete* symmetry group gives a conserved invariant (the moment map of the group action / the orbit-averaged quantity). For the permutation group acting on agent states, that invariant is precisely the order-independent aggregate. So "Noether charge of agent-exchangeability" $=$ "the semilattice join." The conservation-laws crate's monotone Lyapunov function is the *same* object: the join only ever moves up the lattice, so it is a discrete conserved/monotone charge.

**Therefore:** coordination-free ⟺ semilattice ⟺ exchangeability-symmetric ⟺ has a Noether charge that is a Lyapunov function. The CALM monotonicity *is* a conservation law.

**Why emergent & non-obvious:** CALM is usually told as a *systems* result and Noether as a *physics* result; the bridge is the observation that ACI is the algebraic signature of a symmetry group. **Prediction (testable, below):** any learning rule you want to run *coordination-free across agents* must be expressible as a semilattice join of monotone summaries — and if it is, it automatically has a conserved charge you can monitor as a correctness invariant.

---

### Emergent Theorem C — Deadlock-freedom ⟺ a global value potential exists
*(sheaf-automata ∩ observation-control ∩ symplectic)*

**Claim.** A distributed controller admits a *single global value function whose gradient is the optimal policy* (i.e. the policy is an exact 1-form / a Lagrangian section) **iff** $H^1=0$ of the value-sheaf **iff** the system is deadlock-free.

**Proof sketch.**
1. ✅ Local optimal value functions $V_i$ on patches of the coordination cover form a sheaf on the nerve of that cover. The obstruction to gluing them into one global $V$ is the Čech class in $H^1$. This is the same cohomological obstruction Herlihy–Shavit–style topology assigns to wait-free/deadlock-free solvability.
2. ✅ sheaf-automata's theorem: deadlock-free $\iff H^1=0$. Same $H^1$.
3. ⚠️ When $H^1=0$, the disagreement cocycle $\delta_{ij}=V_i-V_j$ is a coboundary, so a global potential $V$ exists; its differential $dV$ is an *exact* 1-form. Symplectically, $\text{graph}(dV)$ is a Lagrangian section of $T^\star X$ — the value gives a single-valued policy with no holonomy. When $H^1\ne0$, the policy is only *closed, not exact*: locally a gradient, globally multivalued — which is exactly a controller that can cycle forever = deadlock/livelock.
4. ⚠️ In the Observation ⊣ Control adjunction, $H^1=0$ is the condition for the counit $\text{Control}\circ\text{Observe}\Rightarrow \text{id}$ to admit a global section — i.e., for "what you control" to fully reconstruct "what you observe." Nonzero $H^1$ is the precise failure of that triangle identity.

**Why emergent:** it identifies *three different failure modes* — no global value function (optimization), deadlock (concurrency), broken adjunction (category theory) — as **one cohomology class.** That's the strongest kind of unification: distinct symptoms, single invariant.

---

### Bonus Theorem D — The self-improvement thermometer
*(self-modeling ∩ thermal-rl ∩ varadhan ∩ symplectic)*

**Claim.** The compute cost of one self-model loop (self-modeling's "curvature = FLOPs") equals the *thermodynamic work* of the corresponding belief update, which by Varadhan equals the squared Fisher–Rao distance moved, lower-bounded by Landauer dissipation.

**Sketch.** ⚠️ Belief update = parallel transport on the statistical manifold (Fisher–Rao metric). Holonomy around the closed 9-step loop $=\int$ curvature (Ambrose–Singer); "9 steps = $\mathrm{tr}(\mathrm{id})$" reads as the manifold dimension = independent DOF updated. ✅ The free-energy change along the loop is a relative entropy, which short-time (Varadhan) is the squared Fisher–Rao distance = a Wasserstein transport cost; ✅ Landauer bounds it below by $kT\ln 2$ per bit erased. So **geometric curvature = informational transport cost = minimal dissipated free energy.** A self-improving agent literally pays its learning in heat, and curvature is the exchange rate.

---

## The minimal self-improving agent

Strip to the load-bearing five, plus one certificate:

1. **dirichlet-space** — the substrate (generator + metric + free energy in one object).
2. **thermal-rl** — gives the objective a *gradient* (free energy), so "improve" has a direction.
3. **ergodic-gradient** — guarantees the descent is a real relaxation (Fokker–Planck), so it *converges* rather than wanders.
4. **self-modeling** — closes the loop: the agent represents its own value/curvature, enabling improvement *of the improver* (Theorem D meters the cost).
5. **observation-control** — couples sensing to acting (the adjunction), or you have an open loop.

**Certificate (not optional in practice):** **conservation-laws / noether-agents.** By Theorem B/C, this supplies the *Lyapunov function that proves self-improvement doesn't self-destruct.* A self-improving system without a conserved charge has no convergence guarantee — it can ascend its own value estimate while diverging in reality (reward hacking has a precise reading here: a policy that is *closed but not exact*, Theorem C, i.e. locally improving with global holonomy).

So: **minimal = {dirichlet-space, thermal-rl, ergodic-gradient, self-modeling, observation-control}; minimal-with-safety adds {conservation-laws}.** Six crates, and Theorems A–D are exactly the consistency conditions binding them.

---

## Experiments to test the emergent predictions

These are concrete and fail-able — the point of making theorems executable.

1. **Spectral-gap = learning-rate (Thm A).** Build a small linearly-solvable MDP. Compute the observation-Laplacian spectral gap via the Kalman/Hodge crate. *Independently* run entropy-regularized policy gradient and measure convergence rate. **Predict:** the rates match the gap to within discretization. A mismatch falsifies the eigenfunction identity.

2. **Idempotence audit (Thm B).** Take any candidate multi-agent learning update. Test the three CRDT laws numerically (A/C/I). **Predict:** it is coordination-free in a partition test (run replicas, partition, merge, check convergence) **iff** all three hold **iff** the permutation-invariant charge from noether-agents is conserved across merges. Run all three checks; they should agree on every example or the bridge is wrong.

3. **Cohomology = deadlock = potential (Thm C).** Generate random distributed protocols. Compute $H^1$ of the value-sheaf (sheaf-automata). **Predict triple-coincidence:** $H^1=0$ ⟺ deadlock-checker passes ⟺ a global $V$ with $\pi=\nabla V$ fits with zero holonomy residual. The interesting failures are protocols where two of three agree but not the third — those would localize which ⟺ is only conjectural.

4. **Landauer meter (Thm D).** Instrument the self-modeling loop's FLOP counter and, separately, compute the Fisher–Rao step length per update. **Predict:** $\text{FLOPs} \propto d_{FR}^2$ with a constant that is a temperature; and dissipation never drops below $kT\ln2$/bit. A measured violation of the lower bound would be the most interesting result of all.

---

## The most surprising non-obvious compositions

- **CALM = Noether** (Thm B): a database/systems theorem and a physics theorem are the same statement about an exchangeability symmetry. Genuinely surprising; the hinge is "ACI = symmetry-group invariance."
- **Reward hacking = nonzero $H^1$** (Thm C corollary): the policy is *closed but not exact* — locally always-improving, globally cyclic. This gives a **cohomological detector for reward hacking**: monitor the holonomy of the value 1-form. I find this the most practically exciting consequence.
- **Optimal policy = ground state** (Thm A): control becomes a Schrödinger-style eigenproblem; "exploration temperature" is literally $\hbar$, and the Hopf–Cole transform is the "dequantization" your dirichlet-space crate is named for. The whole stack is a dequantized quantum mechanics where the WKB/semiclassical limit *is* Varadhan's short-time asymptotics.
- **Kalman spectral gap predicts RL convergence** — an estimation crate setting a control crate's learning rate, via Hodge duality.

---

### One honest caveat
The genuinely load-bearing, established results here are: linearly-solvable MDPs / Hopf–Cole (A), JKO gradient flow (A), Varadhan (A,D), CALM (B), ACI=semilattice (B), sheaf/topological obstructions to consensus (C), Noether (B,D), Landauer (D). The *conjectural glue* I'd want to see actually proven in the crates is: that "Observation ⊣ Control" is a real adjunction whose counit obstruction is the *same* $H^1$ (Thm C step 4), and that "curvature = FLOPs" is metric-compatible with Fisher–Rao rather than merely analogous (Thm D). Those two are where I'd point a proof effort first, because A and B are essentially provable today and C/D hang on them.

Want me to turn any one of these into an actual runnable experiment harness — e.g., the cohomology-based reward-hacking detector, or the spectral-gap/learning-rate test — so the emergent theorem becomes executable like the rest of the stack?
