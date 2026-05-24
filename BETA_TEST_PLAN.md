# Beta Test Fleet — External Visitor Simulation

## Mission
Spawn subagents acting as real-world developers who discovered SuperInstance repos on GitHub. They try to use them as tools for their own projects. Report honestly on what works, what's confusing, and what capabilities they actually gained.

## Tester Personas

### 1. Data Scientist (ML Pipeline Orchestration)
**Repo target:** `sunset-ecosystem` (BreederDaemonV2, RoomGrid, FluxVectorTable)
**Persona:** "I need a self-organizing grid of ML model variants that compete, mutate, and get pruned based on fitness."
**Task:** Try to use BreederDaemonV2 as a hyperparameter search engine. Can you define models as 'agents', breed winners, and get better configs?

### 2. Game Developer (Procedural NPC Population)
**Repo target:** `sunset-ecosystem` (RoomGrid, Plato observer, lifecycle FSM)
**Persona:** "I need a living world where NPCs spawn, compete for resources, have children, and die off — with persistent state I can observe."
**Task:** Try to use RoomGrid + Plato observer as an NPC population manager. Can you spawn characters, watch them compete, and get lifecycle events?

### 3. DevOps Engineer (Server Thermal Management)
**Repo target:** `sunset-ecosystem` + `cocapn-health` (ThermalBudget, health-thermal bridge)
**Persona:** "I need thermal-aware load balancing across heterogeneous hardware (GPU, NPU, CPU)."
**Task:** Try to use ThermalBudget + DeviceType system to schedule jobs on available hardware. Can you model a data center where jobs compete for thermal slots?

### 4. Security Researcher (Consensus + Lineage Verification)
**Repo target:** `sunset-ecosystem` (HolonomyConsensus, LineageSanityChecker, SignedWAL)
**Persona:** "I need verifiable provenance for ML model lineage in a distributed environment."
**Task:** Try to use the consensus + WAL + lineage system to track model provenance. Can you create agents, breed them, and verify nobody tampered with the history?

## Deliverable Format
Each tester returns:
1. **Setup time** — how long to get something running?
2. **Docs quality** — 1-5 stars, what's missing?
3. **Working capabilities** — what actually worked?
4. **Broken/friction** — what failed or was confusing?
5. **Real-world verdict** — would you use this in production?
6. **Suggestions** — what would make this a 5-star tool?
