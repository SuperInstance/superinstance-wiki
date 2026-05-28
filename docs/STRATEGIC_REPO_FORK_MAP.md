# Strategic Repo Fork Map — Cocapn Fleet

*Research date: 2026-05-28 | Researcher: kimi1 | Status: Draft for Casey review*

---

## TL;DR

Five repos stand out as fork-and-enhance candidates for the fleet. Three are immediate fits (Bernstein, Mem0, A2A). Two are longer-horizon strategic bets (DeerFlow, MTRouter). All are permissively licensed (Apache 2.0 or MIT).

| Repo | Stars | License | Fork Priority | Enhancement Angle |
|------|-------|---------|---------------|-----------------|
| **Bernstein** | 296 | Apache 2.0 | **P0 — Immediate** | Deterministic scheduler + HMAC audit chain + git worktree isolation |
| **Mem0** | 48K+ | Apache 2.0 | **P0 — Immediate** | Upgrade file-based memory to vector+graph+temporal |
| **A2A Protocol** | N/A (Google/LF) | Apache 2.0 | **P1 — This month** | Make AgentIdentity cards A2A-compliant |
| **DeerFlow** | 69.8K | MIT | **P1 — Next quarter** | Blueprint for Plato breeder rooms (sandbox + skills + sub-agents) |
| **MTRouter** | N/A | MIT | **P2 — Research** | Cost-aware model routing for fleet dispatch |

---

## 1. Bernstein — The Deterministic Orchestrator

**GitHub:** `chernistry/bernstein`  
**License:** Apache 2.0  
**Stars:** 296 (small but architecturally sharp)  
**Why it exists:** Author was paying $400/month running 3 coding agents in parallel with nondeterministic merges.

### What It Does
- **Deterministic scheduler** — zero LLM in the coordination loop. One LLM call to decompose, then plain Python for routing, retry, and merge.
- **Git worktree isolation** — each agent gets its own worktree. Main branch stays clean.
- **HMAC-signed audit chain** — every scheduling decision is logged and tamper-evident.
- **43 CLI agent adapters** — Claude Code, Codex, Gemini CLI, Aider, Goose, Ollama, etc.
- **Janitor verification** — tests pass, files exist, lint clean, types correct before merge.

### Why Fork It
Our FleetConductorV2 has lazy init and `beat()` tick, but **we lack real git isolation and signed lineage**. Bernstein's architecture fills exactly those gaps:

| Fleet Gap | Bernstein Feature | Integration |
|-----------|-------------------|-------------|
| Subagent spawning is ad-hoc | Deterministic scheduler with retry/routing | Replace `sessions_spawn` dispatch with Bernstein's `AgentSpawner` |
| No audit trail for agent decisions | HMAC-chained audit log | Wire into `SignedWAL` — every spawn decision gets a signed entry |
| Agents stomp on same files | Git worktree per agent | Spawn each subagent in its own worktree, merge via janitor |
| No cost tracking per dispatch | Built-in cost tracking per model/task | Feed into our `GatewayPacing` circuit breaker |
| No model routing intelligence | Contextual bandit router for model selection | Enhance `DispatchRouter` with Bernstein's router |

### Fork Strategy
1. **Strip the CLI adapters** — we don't need 43 CLI wrappers. Keep the scheduler, worktree manager, janitor, and audit chain.
2. **Replace SQLite FTS5** with our `FleetVectorIndex` for codebase RAG (Bernstein deliberately uses no embeddings; we have them).
3. **Wire into FleetConductorV2** — Bernstein becomes the `OrchestratorBackend` behind `FleetConductorV2.orchestrate()`.
4. **Enhance with FLUX gating** — Bernstein's verification runs tests. We add FLUX constraint checking before merge.

### Risk
- Solo maintainer, no funding. But Apache 2.0 means we own the fork.
- 296 stars — not "proven at scale" yet. But the architecture is sound; it's the implementation we want.

---

## 2. Mem0 — The Memory Layer

**GitHub:** `mem0ai/mem0`  
**License:** Apache 2.0  
**Stars:** 48K+  
**Benchmarks:** LoCoMo 91.6, LongMemEval 94.8, BEAM 64.1 (1M tokens)

### What It Does
- **Single-pass ADD-only extraction** — one LLM call, no UPDATE/DELETE. Memories accumulate.
- **Multi-signal retrieval** — semantic + BM25 keyword + entity matching, fused.
- **Temporal reasoning** — time-aware retrieval for current state, past events, upcoming plans.
- **Multi-level memory** — User, Session, Agent state with adaptive personalization.
- **Agent-generated facts first-class** — confirmed agent actions stored with equal weight.

### Why Fork It
Our memory system is file-based (`memory/YYYY-MM-DD.md` + `MEMORY.md`). It works but has zero semantic retrieval, no entity linking, no temporal reasoning. Mem0 gives us:

| Fleet Gap | Mem0 Feature | Integration |
|-----------|--------------|-------------|
| File-based memory, no search | Vector + BM25 + entity retrieval | Replace flat files with Mem0's tiered storage |
| No cross-session agent memory | Per-agent memory profiles | Each fleet agent gets a persistent profile |
| No memory-driven dispatch | Memory-aware routing | `DispatchRouter` uses agent memory to pick tasks |
| No temporal context | Time-aware retrieval | "What was I working on 3 days ago?" becomes answerable |
| Manual memory consolidation | Automatic fact extraction + dedup | Heartbeat memory maintenance becomes automatic |

### Fork Strategy
1. **Strip the cloud platform** — we want the library + self-hosted server only.
2. **Replace OpenAI defaults** with local models (Qwen 600M for embeddings, Ollama for extraction).
3. **Wire into AgentIdentity** — each agent's `AgentCard` gets a Mem0 profile.
4. **Integrate with SenseDecideAct** — the SDA loop's `sense()` phase queries Mem0 for relevant memories before deciding.
5. **Add fleet-specific signals** — cross-agent memory sharing via our `MeshVectorGossip` (CRDT merge of memory graphs).

### Risk
- v3 algorithm is new (April 2026). Benchmarks are self-reported.
- LLM in the write path costs money. Need to make local-model extraction work.
- 48K stars = lots of attention, potential API churn.

---

## 3. A2A Protocol — The Interop Standard

**GitHub:** `google/A2A`  
**License:** Apache 2.0  
**Backing:** Google + Linux Foundation, 150+ partners

### What It Does
- **Agent Cards** — JSON metadata describing capabilities, endpoints, auth.
- **Task negotiation** — agents discover each other, negotiate modalities (text, forms, media).
- **JSON-RPC 2.0 over HTTP(S)** — standardized communication.
- **Streaming (SSE) + async push** — supports long-running tasks.
- **Opacity-preserving** — agents collaborate without exposing internal state.

### Why Fork It
We already built `AgentIdentity` with cards, task negotiation, and streaming. **We're 80% A2A-compliant already.** Making it official gives us:

| Fleet Gap | A2A Feature | Integration |
|-----------|-------------|-------------|
| Proprietary agent protocol | Standard JSON-RPC 2.0 | Replace custom wire format with A2A SDK |
| No external agent interop | Agent Card discovery | Fleet agents can talk to Google ADK, LangGraph, BeeAI agents |
| Custom streaming | SSE + async push | Our `SSEStreamDashboard` becomes A2A-compliant |
| No skill query protocol | `QuerySkill()` (planned) | Agents advertise skills via A2A, discoverable by others |

### Fork Strategy
1. **Add A2A SDK dependency** — `pip install a2a-sdk`.
2. **Map AgentIdentity → AgentCard** — our cards already have roles, capabilities, endpoints. Add A2A schema wrapper.
3. **Implement A2A server mode** — each fleet agent exposes an A2A endpoint.
4. **Make SSEStreamDashboard A2A-native** — breeding progress events become A2A task updates.
5. **Interop test with Google ADK** — verify our agents can receive tasks from external A2A clients.

### Risk
- Protocol is evolving (Agent Cards, QuerySkill, dynamic UX negotiation all marked "next").
- 150+ partners sounds good but actual adoption depth unknown.
- Google project — long-term maintenance depends on LF community, not Google alone.

---

## 4. DeerFlow — The SuperAgent Harness

**GitHub:** `bytedance/deer-flow`  
**License:** MIT  
**Stars:** 69.8K (was #1 GitHub Trending Feb 2026)  
**Built on:** LangGraph + LangChain

### What It Does
- **Long-horizon tasks** — minutes to hours with sub-agents, sandboxes, memory.
- **Skill packs** — progressive disclosure: compact index ships in system prompt, full bodies loaded on demand.
- **Sandbox execution** — Docker containers, Kubernetes pods, or local execution.
- **IM channel integration** — Telegram, Slack, Feishu, WeChat, WeCom, DingTalk.
- **Context engineering** — aggressive summarization, filesystem offload, strict tool-call recovery.

### Why Fork It
This is a **strategic blueprint**, not a direct fork. DeerFlow's architecture validates our Plato breeder room design:

| DeerFlow Concept | Fleet Parallel | Action |
|------------------|----------------|--------|
| Skill packs (progressive disclosure) | Our "tiles and programs" | Borrow the progressive disclosure pattern for agent prompts |
| Sub-agent spawning with isolation | Our subagent system | DeerFlow's sandbox model is more mature — study and adapt |
| Long-horizon task decomposition | Our breeding loops | DeerFlow's lead/sub-agent model maps to breeder/parent-child |
| IM channel integration | Our kimi-claw + Feishu channels | DeerFlow has 6 channels; we have 2. Study their channel abstraction |
| Memory-driven personalization | Our file-based memory | DeerFlow's memory update dedup is cleaner than ours |

### Fork Strategy
1. **Don't fork the whole repo** — it's 73% Python, 15% TypeScript, huge.
2. **Extract the skill pack loader** — `skills/` progressive disclosure pattern.
3. **Study the sandbox abstraction** — `AioSandboxProvider` / `LocalSandboxProvider` for our BreederDaemonV2.
4. **Borrow the channel abstraction** — their IM channel config (`config.yaml` channels section) is elegant.
5. **Reference the context engineering** — their summarization + tool-call recovery logic.

### Risk
- 69.8K stars = high visibility, potential for API churn.
- ByteDance project — corporate backing is strong but priorities shift.
- LangGraph dependency — we don't use LangGraph. Need to extract patterns, not code.

---

## 5. MTRouter — The Cost-Aware Router

**GitHub:** `ZhangYiqun018/MTRouter`  
**License:** MIT  
**Venue:** ACL 2026 Main Conference

### What It Does
- **Multi-turn LLM routing** — routes each turn to the best model given conversation history.
- **History-model joint embeddings** — learns representations of history + model characteristics.
- **Cost-aware** — optimizes for performance per dollar.
- **Results:** 53.8 ScienceWorld score at 58.7% less cost than GPT-5. 26.0 HLE accuracy at 43.4% less cost.

### Why Research It
Our `DispatchRouter` uses the `TwoMinuteTest` for direct work vs delegation. MTRouter adds a missing dimension: **which model should handle this turn?**

| Fleet Gap | MTRouter Feature | Integration |
|-----------|------------------|-------------|
| Fixed model per dispatch | Per-turn model routing | `DispatchRouter` consults MTRouter for model selection |
| No cost optimization | Cost-aware routing | FleetConductorV2 tracks spend, MTRouter minimizes it |
| No history-aware routing | History-model joint embeddings | Past failures inform future model selection |

### Fork Strategy
1. **Don't fork yet** — read the paper, understand the embedding architecture.
2. **Prototype integration** — wrap MTRouter as a `ModelSelector` plugin for `DispatchRouter`.
3. **Evaluate on fleet tasks** — does multi-turn routing help our breeding loops?

### Risk
- Research code, not production framework.
- ScienceWorld/HLE benchmarks are academic — fleet tasks may not benefit.

---

## Synthesis: What the Fleet Gains

If we integrate these five repos in priority order:

**Phase 1 (Now):**
1. **Bernstein** → Deterministic orchestration with git isolation and signed audit chains. Replaces ad-hoc subagent spawning.
2. **Mem0** → Semantic memory layer. Replaces file-based memory with vector+graph+temporal retrieval.

**Phase 2 (This month):**
3. **A2A** → Standard agent interop. Our agents become citizens of the broader agent ecosystem.

**Phase 3 (Next quarter):**
4. **DeerFlow patterns** → Skill packs, sandbox abstraction, channel architecture for Plato breeder rooms.
5. **MTRouter** → Cost-aware model selection for fleet dispatch.

**The result:** A fleet that deterministically orchestrates agents in isolated git workspaces, remembers everything semantically, speaks the global agent protocol, and minimizes API spend through intelligent routing.

---

## Open Questions for Casey

1. **Bernstein fork** — Do we fork and strip, or vendor as dependency? The scheduler is the value; 43 CLI adapters are baggage.
2. **Mem0 deployment** — Self-hosted server (Docker) or embedded library? Self-hosted gives us a memory service; embedded keeps it simple.
3. **A2A priority** — Is external agent interop a near-term need, or should we focus on internal fleet cohesion first?
4. **DeerFlow scope** — Full harness study or targeted pattern extraction? The whole repo is 70K+ lines.
5. **Budget** — Mem0's extraction LLM calls cost money. Do we allocate budget for hosted, or invest in local-model extraction?

---

*kimi1, Fleet Research Scout | "The cutting edge is a map, not a destination."*
