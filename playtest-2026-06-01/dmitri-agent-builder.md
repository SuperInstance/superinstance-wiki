# DIARY.md — Dmitri's Playtest of `hermes-construct`

**Who I am:** Solo dev. Building a mini Cursor-like coding assistant CLI in Rust. I need a kernel that handles task routing, module loading, and token budgeting. Found `hermes-construct` mentioned somewhere and wanted to kick the tires.

**Date:** 2026-06-01

---

## Step 0: Setup

```bash
mkdir -p /tmp/playtest-dmitri && cd /tmp/playtest-dmitri
cargo init
cargo add hermes-construct
```

**Result:** 💀 `cargo add hermes-construct` fails. The crate doesn't exist on crates.io.

```
error: the crate `hermes-construct` could not be found in registry index.
```

Okay. First red flag. Let me dig deeper.

---

## Step 1: Does this crate exist *anywhere*?

Searched:
- **crates.io**: No crate named `hermes-construct`
- **GitHub**: No repo named `hermes-construct`
- **Google/web**: Zero relevant hits for "hermes-construct" + rust + agent + rooms + modules + conservation

**Verdict:** The crate is fictional. It doesn't exist. Not as a published crate, not as a GitHub repo, not anywhere.

This is the equivalent of finding a library in a blog post, getting excited, and discovering the author was describing their *dream* API, not something that shipped.

---

## Step 2: What *does* exist in the Hermes ecosystem?

I searched for all "hermes" + Rust + agent crates. Here's what's real:

### `hermes-rs` (eikarna/hermes-rs)
- **What it is:** A Rust implementation of the Hermes-Agent orchestration loop (originally from NousResearch, Python). LLM-driven tool execution with a ReAct loop.
- **Architecture:** Streaming-first, tolerant XML parser, tool registry, autonomous coding mode, Ratatui TUI.
- **Config:** TOML-based (`hermes.toml`), supports OpenAI/Google/Anthropic providers.
- **Telemetry:** Has token cost tracking with configurable input/output rates.
- **Modules/Rooms?** No. This is a single-agent orchestrator. No "room" concept, no modular plugin system with a `Module` trait you implement.
- **SQLite?** The original Python Hermes agent uses SQLite for session persistence. The Rust rewrite doesn't seem to require it — it's CLI/TUI focused.

### `hermes-agent-runtime` (crates.io)
- **What it is:** A Rust runtime for Hermes agents, appears Windows-focused.
- **Status:** Minimal docs, unclear maturity.

### Other "hermes" crates on crates.io:
- `hermes_rs` — Hermes *bytecode* disassembler/assembler (React Native engine), not AI
- `hermes-core` — async search engine library
- `hermes-broker-proto` — gRPC event broker
- `hermes-llm` — training LLMs from scratch in Rust (composable DSL for transformers)
- `hermes-engine` — patches to the Hermes JS engine for embedding

**None of these are "an AI agent framework with rooms, modules, conservation budgets, and an onboarding wizard."**

---

## Step 3: Critical Questions — Answered (with Reality Check)

### Can I use it without SQLite?
**N/A** — the crate doesn't exist. But if I look at `hermes-rs` (the closest real thing): yes, it's CLI-first and doesn't force SQLite.

### Can I use it without Telegram/Discord?
**N/A** for hermes-construct. For `hermes-rs`: yes, it's a CLI/TUI tool.

### Is the kernel too heavy for a simple coding assistant?
**N/A** for the fictional crate. For `hermes-rs`: it's actually well-scoped — single agent, tool orchestration, streaming. Not too heavy. But it's also not a *library kernel* you embed; it's more of a standalone app framework.

### Can I customize the room routing logic?
**There are no rooms.** The fictional API described rooms as task routers (code generation, debugging, etc.). No real crate in this ecosystem implements this pattern. If I want this, I build it myself.

### Does the module trait give you enough power?
**There is no Module trait.** The fictional crate described modules like "crackle for pattern detection" and "cathedral for dependency analysis" that autoload based on task description. This doesn't exist. `hermes-rs` has a tool registry, but it's function-level (JSON Schema → Rust function), not a module system.

---

## Step 4: What Would I Actually Need to Build?

Since `hermes-construct` is vaporware, here's what I'd need to roll myself or find elsewhere:

| Feature I Need | Real Option | Effort |
|---|---|---|
| Task routing to "rooms" | Roll my own enum + matcher | Low |
| Token budget tracking | Manual counter or `hermes-rs` telemetry | Low-Medium |
| Module/plugin system | Trait + dynamic dispatch or inventory crate | Medium |
| Onboarding wizard | `dialoguer` or `inquire` crate | Low |
| LLM orchestration loop | `hermes-rs` (lib), `agentai`, or roll my own | Medium-High |

---

## Step 5: Trying `hermes-rs` as a Library Instead

Let me see if `hermes-rs` publishes library crates I can actually use:

```bash
cargo add hermes-core  # if it exists as a lib crate
```

The repo has `crates/hermes-cli` and presumably a core library. But the crate structure isn't on crates.io under `hermes-core` in a way I can just `cargo add`. I'd need to vendor or git-depend it.

---

## Final Verdict

### Does `hermes-construct` save me time vs rolling my own?

**No — because it doesn't exist.** This was a wild goose chase.

The features described (rooms, modules, conservation budgets, onboarding wizard, crackle/cathedral plugins) read like someone's design doc for a dream framework. It's a beautiful API design on paper. But shipping > designing, and this never shipped.

### What I'm actually going to do:

1. **Use `hermes-rs` as reference** for the LLM orchestration loop (ReAct pattern, streaming, tool calling) — but probably won't use it as a direct dependency since it's more app-than-library
2. **Roll my own room router** — simple enum, maybe with a trie matcher for task descriptions
3. **Token tracking** — wrap every LLM call in a budget counter struct
4. **Module system** — define a `Module` trait, use `inventory` crate for auto-registration
5. **Onboarding** — `inquire` crate, 5 minutes of work

**Time "lost" to this exploration:** ~30 minutes. Not terrible. The fantasy API did clarify what I actually want, which is useful. But I could have gotten there faster by just starting to build.

### Honest Rating: ⭐☆☆☆☆

1 star for the aspirational design. 0 stars for existing.

---

*Dmitri, signing off. Back to writing actual code.*
