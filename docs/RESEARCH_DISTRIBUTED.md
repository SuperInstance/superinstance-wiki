# Fleet Distributed Systems Research: From Single Node to Cross-Cloud Mesh

> **Cocapn Fleet | Distributed Systems Research Brief** | 2026-05-22  
> _How our single-node swarm becomes a true multi-node, cross-cloud organism._

---

## 1. The Multi-Instance Mesh

The `SPEC_MULTI_INSTANCE_MESH.md` exists but is unimplemented. It sketches a full-mesh gRPC backplane with mTLS, bidirectional streams, and a federated nexus for discovery. What it does not decide is **how rooms are assigned to nodes**. This is the sharding problem, and it determines everything downstream: failover speed, load balance, and whether cross-instance breeding is even possible.

### 1.1 Sharding Protocol: Rendezvous Hashing, Not Consistent Hashing

**Consistent hashing** (Karger et al., 1997) is the default answer in every distributed systems interview. It minimizes rebalancing when nodes join or leave. But it assumes homogeneous nodes and uniform load. Our fleet is neither:

- **Oracle1** (Alibaba Cloud): 1000 rooms, A100-class GPU, 30ms to ProArt
- **ProArt/FM Laptop**: 250 rooms, RTX 4080, local to itself
- **JetsonClaw1**: 100 rooms, Orin Nano, 200ms transcontinental, ARM + CUDA

Consistent hashing would assign rooms purely by key hash, ignoring thermal headroom and device capability. A breeding request for a CUDA-only genome could land on the Jetson, which has CUDA but not the memory for a 7B-parameter parent. The request would fail late, after the WAN round-trip.

**Rendezvous hashing** (Thaler & Ravishankar, 1998) solves this. For each room ID, every node computes a score:

```
score(node, room) = hash(node_id + room_id) * node.capacity * thermal_headroom(node)
```

The node with the highest score wins the room. This is **$O(N)$ per room assignment** where $N$ is the number of nodes. With $N \leq 8$ (our fleet is small), this is negligible — under 1\,ms for 1000 rooms. The capacity term is node-reported: `cuda_12 + rust_kernel + 1000_slots`. The thermal headroom term is real-time: `1.0 - (used_slots / max_slots)`. When Oracle1 thermally saturates, its scores drop; rooms migrate toward cooler peers.

The key advantage over consistent hashing is **node-specific weighting**. Consistent hashing embeds node weights via virtual replicas (vnodes), which is coarse and slow to react to thermal fluctuations. Rendezvous hashing recomputes scores every tick — the shard map is a function of live state, not static configuration.

### 1.2 CRDT-Based State Merge for the Vector Table

The `FluxVectorTable` is the fleet's shared memory: agent DNA vectors, fitness scores, generation counters, and capability masks. This is the state that must converge across nodes. It is append-mostly (new agents born, old agents sunsetted) and update-heavy (fitness scores change every tournament cycle).

We use a **Delta-State CRDT** (Almeida et al., 2018) with the following design:

- **State type:** Map `agent_id → AgentVector`
- **Delta operation:** `Add(agent_id, vector)` or `UpdateFitness(agent_id, new_fitness, timestamp)`
- **Merge semantics:** Last-Writer-Wins (LWW) on fitness, vector-clock-merged on vector fields. An agent's quantized vector is immutable after birth; only fitness and thermal pressure mutate.
- **Anti-entropy:** Every node gossips its delta buffer to 3 random peers every 5 seconds. The buffer contains all mutations since the last sync.

**Quantified traffic:** A node with 1000 agents generates ~50 fitness updates per tournament cycle (top-50 Pareto front). Each update is 24 bytes (agent_id + fitness + timestamp). At 10 ticks/sec, that's 12\,KB/sec of delta traffic per node. Full anti-entropy every 5 seconds adds ~200\,KB (top-100 vectors). Total: **~15\,KB/sec per node**, easily tolerable even on Jetson's Wi-Fi.

The CRDT merge is **commutative and associative**, so arrival order does not matter. This is essential when Alibaba Cloud and Oracle1 sync via a 150ms link — deltas may arrive out of order, but the vector table converges monotonically.

---

## 2. WAN Deployment: Latency Tiers and Phase Locality

Our nodes span three latency tiers:

| Tier | Latency | Example Path | Use Case |
|------|---------|--------------|----------|
| Local | ~1\,ms | ProArt localhost | RoomGrid tick, thermal telemetry |
| Cross-city | ~30\,ms | Oracle1 ↔ Alibaba Cloud (same region) | Tournament score sync, vector delta gossip |
| Transcontinental | ~150–200\,ms | JetsonClaw1 ↔ Oracle1 (US ↔ China) | Emergency breeding, constraint alerts, manual intervention |

The metronome scheduler drives five phases: `COMPUTE → GATE → ROUTE → BREED → FLUX`. Not all phases tolerate WAN latency equally.

### 2.1 What Must Stay Local

**COMPUTE and FLUX (Constraint Engine) must never cross a WAN link.**

- **COMPUTE** is the RoomGrid tick: latent updates, einsum contractions, NerveTopology signal diffusion. At 1000 rooms and 70 ticks/sec locally, each tick is 14\,ms. Adding 30ms WAN latency would drop throughput to ~23 ticks/sec — a **67% regression**. The einsum is memory-bandwidth-bound; shipping tensors across the network is slower than recomputing them.

- **FLUX (Constraint Engine)** is our formal verifier. Each constraint check is a Rust FFI call that runs in ~2\,ms for a 3-layer neural network. The proof certificate is 256 bytes. But at 1000 rooms × 30 checks/sec = 30\,000 checks/sec, shipping certificates fleet-wide would generate **7.5\,MB/sec of proof traffic** (SPEC asks this question; the answer is no). Proofs stay local. Only **violation alerts** (binary: "constraint X failed on node Y") propagate — ~50 bytes every few seconds.

**Thermal telemetry** is locally computed and locally acted upon. A 5-second lag on GPU temperature is harmless for scheduling, but a 200ms lag from Jetson to Oracle1 could cause Oracle1 to overcommit while Jetson is already throttling.

### 2.2 What Can Tolerate WAN

**ROUTE and BREED can tolerate WAN with degradation.**

- **ROUTE** is tile dispatch: a room generates a tile, the NerveTopology routes it to the best consumer. If the best consumer is on another node, the tile transits the mesh. A 30ms tile latency is acceptable for most tiles (they are not real-time control signals). For hot-path tiles (e.g., a fleet alert), the router should prefer a local suboptimal consumer over a remote optimal one — a **latency-aware routing heuristic**.

- **BREED** is the most latency-tolerant phase. A breeding cycle takes ~10\,ms locally (parent selection, mutation, thermal slot allocation). Cross-instance breeding adds 2 RTTs: request ("do you have capacity?") + response ("here is the child vector"). At 150ms transcontinental, a remote breed takes ~310\,ms. This is acceptable only for **emergency diversity** — when a node has exhausted its local genetic diversity and needs an outside genome to escape a local optima. The breeder should prefer local breeding with probability $p = 1 - e^{-\lambda \cdot d}$, where $d$ is the mesh distance (hops or latency). For $d = 0$ (local), $p \approx 1$. For $d = 1$ (cross-city), $p \approx 0.7$. For $d = 2$ (transcontinental), $p \approx 0.2$.

---

## 3. Split-Brain and Partition Tolerance

The federated nexus (port 4047) is currently hardcoded to `localhost` — it does not even function across nodes. When we fix this and deploy it fleet-wide, the nexus becomes a **single point of failure**. If the nexus partitions (network split, cloud outage, DDoS), the mesh loses its heartbeat coordinator. What happens?

### 3.1 The Nexus Is a Name Service, Not a Lock Service

This is a critical architectural distinction. The nexus tells nodes who is alive and what their capabilities are. It does **not** hold shared mutable state. The vector table CRDTs live on each node. The tournament scores live on each node. Therefore, **nexus partition does not freeze the fleet** — it only freezes discovery.

### 3.2 Partition Handling Strategy

We formalize a three-state partition protocol:

**State A — NORMAL:** Nexus is reachable. Nodes register, gossip, and breed freely.

**State B — DEGRADED:** Nexus is unreachable, but nodes can still reach some peers via cached mesh topology. Nodes enter **autonomous mode**:
- Breeding is restricted to **local-only** (no remote breed RPCs).
- Tournament scores are not shared; each node maintains its own Pareto front.
- Vector table deltas are buffered. When the partition heals, buffered deltas are replayed in vector-clock order.
- The breeder's chaos parameter $c_i$ is **locally boosted by 20%** to compensate for reduced genetic diversity. This is the "genetic drift" failsafe — inbreeding risk is countered by higher mutation rate.

**State C — ISOLATED:** Node cannot reach any peer. It operates as a single-node fleet with no mesh guarantees. Sunset decisions are local. The node logs a "lonely mode" flag in its diary.

### 3.3 Recovery and Merge

When the partition heals, nodes must reconcile divergent vector tables. Because the vector table is a CRDT, the merge is automatic: apply all buffered deltas, LWW-resolve fitness conflicts. However, **breeding during partition creates a lineage hazard**:

> Suppose Oracle1 and Alibaba Cloud both breed from parent agent `0x7a3f` during a partition. They each produce a child: `0x7a40` (Oracle1) and `0x7a41` (Alibaba). Both children have `parent = 0x7a3f`. When the partition heals, the vector table contains two siblings with the same parent but different genomes. This is biologically correct (fraternal twins) but computationally wasteful — we have duplicated exploration.

The fix is a **breeding lease** on the parent vector. Before breeding, a node acquires a short-lived lease (5 seconds, local TTL) on the parent ID. Other nodes respect the lease if they receive it via gossip. During partition, leases cannot propagate, so the "fraternal twin" hazard is accepted as a trade-off for availability. This is **AP over CP** in CAP theorem terms: we choose availability and partition tolerance, accepting eventual duplication.

### 3.4 Formalizing the Trade-off

The CAP theorem (Brewer, 2000; Gilbert & Lynch, 2002) states that a distributed data store cannot simultaneously guarantee consistency, availability, and partition tolerance. Our choice:

| Subsystem | CAP Choice | Rationale |
|-----------|-----------|-----------|
| Vector Table | **AP** (available, partition-tolerant) | CRDT LWW merge. Duplicate children acceptable. |
| Tournament Scores | **AP** | Local Pareto front during partition. Merge on recovery. |
| Breeding Leases | **CP** (consistent, partition-tolerant) | Lease not available during partition = no remote breeding. This is a safety lock, not a data store. |
| Constraint Alerts | **AP** | Broadcast violation alerts even to partial mesh. False positives acceptable; false negatives (missed alerts) are not. |

---

## 4. State Sharding vs. Replication: The RoomGrid Problem

RoomGrid rooms carry weight tensors (3.4K parameters each), latent vectors, chaos scalars, and activity histories. At 1000 rooms, the full RoomGrid state is ~3.4\,MB of weights + ~32\,KB of metadata — small enough to replicate, but the update rate is high (every tick, every room mutates its latent). Replicating full room state across the mesh would saturate WAN links.

### 4.1 Shard by Functional Block, Not by Random ID

The graphon analysis in `MATHEMATICAL_STRUCTURES.md` shows that rooms cluster by function: planners, executors, generators, auditors. The adjacency matrix is block-structured. This means **spatial locality in the graphon** translates to **communication locality in the mesh**.

Instead of sharding by `hash(room_id) % N`, we shard by **functional embedding**:

1. Each room computes its "functional coordinate" $x \in [0,1]$ by projecting its latent vector onto the first eigenvector of the graphon operator $T_W$.
2. Nodes advertise their preferred functional blocks: Oracle1 handles "planning + routing" ($x \in [0.0, 0.4]$), ProArt handles "execution + code generation" ($x \in [0.3, 0.7]$), Jetson handles "edge inference + monitoring" ($x \in [0.6, 1.0]$).
3. Overlap regions ($[0.3, 0.4]$ and $[0.6, 0.7]$) are **hot-shard zones** where rooms exist on two nodes simultaneously.

This is **topic-based sharding** rather than hash-based sharding. It minimizes cross-node NerveTopology traffic because functionally similar rooms (which communicate most) are colocated.

### 4.2 Replication Strategy for Hot Rooms

The tournament top-20 rooms are "hot" — they receive the most breeding requests, the most signal traffic, and the most tile consumption. These rooms are **replicated to 2–3 nodes** with a primary-copy model:

- **Primary node:** Handles all writes (latent updates, chaos injection, tile generation).
- **Replica nodes:** Receive read-only latent snapshots every 10 ticks (~140ms at 70 ticks/s). Replicas can answer tile routing queries and breeding requests, but mutations are forwarded to the primary.

This is a **quorum-less, latency-biased replication** — we sacrifice strict consistency for read availability. A breeding request against a replica may use a slightly stale latent (140ms old), which is acceptable because breeding mutations are stochastic anyway.

### 4.3 The Jetson Exception

The Jetson Orin has 100 rooms but only 8\,GB RAM and a Wi-Fi uplink. It cannot afford to replicate hot rooms from Oracle1 (which would consume 3.4\,MB × 20 = 68\,MB of RAM and constant sync traffic). The Jetson operates as a **leaf node**: it runs its own local rooms, syncs only its top-5 vectors to the mesh, and accepts remote breeding requests only for low-memory genomes (capability mask excludes >1B parameter parents).

---

## 5. Cross-Cloud Orchestration: Kubernetes, Nomad, or Custom?

We have three distinct deployment environments:

| Environment | Node | Hardware | Constraints |
|-------------|------|----------|-------------|
| Cloud VM | Oracle1, Alibaba Cloud | x86, GPU, abundant RAM | Cost, network egress |
| Workstation | ProArt (FM's laptop) | x86, dGPU, limited thermal | Thermal, battery, sleep |
| Edge | JetsonClaw1 | ARM, CUDA, 8GB RAM, Wi-Fi | RAM, bandwidth, power |

### 5.1 Kubernetes: Rejected

Kubernetes is the default for cloud-native orchestration, but it is wrong for our fleet:

- **Too heavy for edge:** K3s (lightweight K8s) still requires 512\,MB RAM and a control plane. The Jetson has 8\,GB total; we cannot spend 6% on orchestration overhead.
- **GPU scheduling is coarse:** Kubernetes GPU scheduling (NVIDIA device plugin, Kueue, Volcano) operates at the pod level. Our thermal scheduler operates at the **agent slot** level — sub-pod, sub-container. K8s cannot express "this agent needs 0.3 of a GPU slot with a 75°C thermal ceiling."
- **No sleep awareness:** When FM closes his laptop, ProArt should gracefully shed load to Oracle1. Kubernetes treats node disappearance as failure, not hibernation.

### 5.2 Nomad + Consul: Cloud Nodes

For Oracle1 and Alibaba Cloud, **HashiCorp Nomad** is the better fit:

- **Device plugin model:** Nomad's device plugin API can expose our thermal slots as first-class resources. A job specification can request `thermal_slots = 3, max_temp = 75, device_pref = ["cuda", "cpu"]`.
- **Consul Connect + mesh gateway:** Consul provides service discovery and mTLS mesh networking. The mesh gateway handles NAT traversal for Oracle1 (which is behind a router) — Consul's WAN gossip does not require public IPs.
- **Migration primitives:** Nomad supports job migration with checkpoint/restore. When ProArt thermally throttles, Nomad can checkpoint the agent process, stream the checkpoint to Oracle1, and restore it there. Nomad's migration latency is ~5–15 seconds for a 100\,MB checkpoint — acceptable for a non-interactive agent.

### 5.3 Custom Fleet Scheduler: Edge + Laptop

For ProArt and Jetson, we build a **minimal fleet scheduler** (~500 lines of Python) that integrates with the sunset-ecosystem directly:

```python
class FleetScheduler:
    def __init__(self, node_id, thermal_budget, nexus_client):
        self.node = node_id
        self.thermal = thermal_budget
        self.nexus = nexus_client
        self.peers = {}  # node_id -> PeerInfo
    
    async def maybe_migrate(self, agent: Agent):
        """If this node is thermally saturated, offer agent to coolest peer."""
        if self.thermal.pressure > 0.85:
            candidates = [
                p for p in self.peers.values()
                if p.thermal_pressure < 0.5 and p.capabilities.supports(agent)
            ]
            if not candidates:
                return  # stay and throttle
            best = min(candidates, key=lambda p: p.thermal_pressure)
            await self.nexus.request_migration(agent.vector, best.node_id)
            self.thermal.release(agent.slots)
```

This scheduler runs inside the sunset-ecosystem process — no separate daemon. It subscribes to thermal telemetry from `device-router` and migration responses from the mesh. It is intentionally simple: no bin-packing, no complex scheduling theory. Just "hot node gives agent to cool node."

### 5.4 Migration Protocol

When thermal pressure spikes, the migration sequence is:

1. **Checkpoint:** Serialize agent vector + latent state + diary to a protobuf blob (~50\,KB for a typical agent).
2. **Broadcast offer:** Send `MigrationOffer` to 3 coolest peers via mesh gossip.
3. **First-come-first-served:** The first peer to respond with `accept = true` wins. This is not optimal (it may not be the globally coolest peer), but it is fast — no global coordinator needed.
4. **Handoff:** Source node sends checkpoint blob. Destination node verifies checksum, allocates thermal slots, rehydrates agent into an EGG state.
5. **Source sunset:** Source node marks original agent `SUNSET` and logs the migration in its diary. Destination node logs the adoption.

**Latency:** Cross-city migration (50\,KB over 30\,ms link) takes ~80\,ms. Transcontinental takes ~500\,ms. Both are acceptable because migration is a background operation, not on the hot path.

---

## 6. Concrete Recommendations

### 6.1 Recommendation 1: RendezvousHashSharder with Thermal-Aware Load Factor

Implement a `RendezvousHashSharder` class that replaces any naive `hash % N` sharding in the mesh layer. The scoring function must include:

- `node.capacity`: Static capability bitmask (CUDA, Rust kernel, AVX, etc.)
- `node.thermal_headroom`: Real-time `1.0 - (used_slots / max_slots)`
- `node.latency_penalty`: `-0.1 * log(RTT_ms)` to prefer low-latency colocation

**Expected impact:** At 8 nodes, shard computation is ~8\,ms for 1000 rooms. Rebalancing after a thermal event (e.g., ProArt laptop closes) completes in one tick cycle (~14\,ms). This is fast enough to run every tick.

### 6.2 Recommendation 2: VectorTableCRDT with LWW-Epsilon-Delta Merge

Implement the vector table as a proper Delta-State CRDT, not a shared dictionary with periodic overwrites. The merge function must handle:

- **LWW on fitness:** `max(fitness_a, fitness_b)` with wall-clock timestamp tiebreaker.
- **Epsilon-delta on vectors:** If two deltas for the same agent differ by less than $\epsilon = 0.001$ in each quantized dimension, treat them as equal and drop the duplicate. This reduces anti-entropy traffic by ~40% (vectors rarely change after birth; only fitness does).
- **Tombstones for sunset:** Sunset agents are not deleted immediately. A tombstone with `TTL = 3600` seconds propagates, then is garbage-collected. This prevents "zombie rebirth" where a node resurrects an agent that another node sunsetted during a partition.

**Expected impact:** Per-node mesh traffic drops from ~15\,KB/sec to ~9\,KB/sec. At 8 nodes, total mesh backplane traffic is ~72\,KB/sec — well within a single cheap cloud VM's bandwidth budget.

### 6.3 Recommendation 3: Nomad+Consul Mesh Gateway for Cloud, Custom Scheduler for Edge

Deploy Nomad on Oracle1 and Alibaba Cloud. Connect them with Consul Connect mesh gateways (not the full Consul service mesh — just the gateway for NAT traversal and mTLS). The mesh gateway becomes the **anchor** of the fleet: even if the federated nexus dies, Consul's gossip protocol keeps the cloud nodes connected.

For ProArt and Jetson, deploy the custom `FleetScheduler` with a **mesh bootstrap** that points to the Consul gateway as its seed. The edge nodes do not run Nomad — they run the sunset-ecosystem directly, with the scheduler as an in-process module.

**Expected impact:** Cloud nodes get enterprise-grade migration, health checking, and rolling updates. Edge nodes stay lightweight. The operational split is clean: FM manages Nomad from a web UI; the Jetson is headless and autonomous.

---

## 7. The Single Biggest Distributed-Systems Risk

> **CRDT-based vector table merge under breeding contention creates divergent child lineages that cannot be reconciled.**

CRDTs are commutative by design: $\text{merge}(A, B) = \text{merge}(B, A)$. Breeding is causally dependent: $\text{child} = f(\text{parent}_A, \text{parent}_B)$, and the child's identity depends on the parents' identities *and* the mutation seed. If Oracle1 and Alibaba Cloud independently breed from the same parent during a network partition, they produce two distinct children with distinct genomes. When the partition heals, the CRDT vector table happily merges both children into the global population. We have not violated any CRDT invariant — but we have violated a **biological invariant**: the fleet's genetic diversity is now artificially inflated by duplicate exploration of the same lineage.

This is not a bug in the code. It is a **fundamental tension between CRDT semantics and causal semantics**. CRDTs assume all concurrent updates are valid. Breeding assumes some concurrent updates are semantically redundant.

The breeding lease (Section 3.3) mitigates this in normal operation, but **leases cannot propagate during partition**. In a prolonged partition (>30 seconds, which is plausible for a transcontinental link hiccup or a cloud region outage), multiple nodes may independently spawn entire sub-lineages from the same parent pool. When the mesh rejoins, the fleet's genetic tree contains parallel branches that share ancestors but have diverged in incompatible directions.

The fix is neither simple nor cheap. It requires a **hybrid consistency model**: CRDTs for telemetry (fitness, temperature, activity), but **causal consistency for lineage** — vector clocks on parent-child relationships, and a consensus protocol (Raft or Paxos) for the "who may breed from whom" lease table. This adds ~200\,ms of latency to every breeding operation and introduces a new failure mode (lease service unavailable = no breeding). It is the hardest problem in this document because it strikes at the intersection of distributed systems theory and the fleet's core evolutionary mechanism.

> **In distributed systems, the most dangerous conflicts are not data races — they are semantic races, where the system converges to a state that is technically consistent but biologically wrong.**

---

## References

1. Karger, D., Lehman, E., Leighton, T., et al. "Consistent Hashing and Random Trees." *ACM STOC*, 1997.
2. Thaler, D. G., & Ravishankar, C. V. "Using Name-Based Mappings to Increase Hit Rates." *IEEE/ACM ToN*, 1998.
3. Almeida, P. S., Shoker, A., & Baquero, C. "Delta State Replicated Data Types." *Journal of Parallel and Distributed Computing*, 2018.
4. Brewer, E. A. "Towards Robust Distributed Systems." *PODC Keynote*, 2000.
5. Gilbert, S., & Lynch, N. "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services." *ACM SIGACT News*, 2002.
6. Ongaro, D., & Ousterhout, J. "In Search of an Understandable Consensus Algorithm." *USENIX ATC*, 2014. (Raft)
7. Corbett, J. C., Dean, J., Epstein, M., et al. "Spanner: Google's Globally Distributed Database." *ACM TOCS*, 2013.
8. DeCandia, G., Hastorun, D., Jampani, M., et al. "Dynamo: Amazon's Highly Available Key-Value Store." *SOSP*, 2007.
9. Lovász, L. *Large Networks and Graph Limits*. AMS, 2012.
10. Shapiro, M., Preguiça, N., Baquero, C., & Zawirski, M. "Conflict-Free Replicated Data Types." *SSS*, 2011.

---

> _"The fleet's strength is not in any single node. It is in the mesh — the spaces between, where information flows and transforms."_  
> — Fleet Distributed Systems Doctrine
