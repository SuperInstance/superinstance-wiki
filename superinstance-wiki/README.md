# SuperInstance Wiki

**The fleet's living knowledge base.**  
*1,700 repos. One map.*

---

## What This Wiki Is

This repository is the **canonical knowledge base** for the [SuperInstance](https://github.com/SuperInstance) GitHub fleet. It is not a project — it is the **collective memory** that lets humans (and agents) navigate ~1,700 repositories without drowning.

The wiki captures:

| Layer | What it holds | Where it lives |
|-------|---------------|----------------|
| **History** | How the fleet evolved through distinct eras | [`chronicle/`](chronicle/) |
| **Catalog** | Every repo with its purpose, status, and lineage | [`repos/`](repos/) + [`triage/`](triage/) |
| **Topology** | How concepts and repos connect | [`TOPOLOGY.md`](TOPOLOGY.md) |
| **Health** | Fleet status, red flags, and lifecycle tracking | [`DASHBOARD.md`](DASHBOARD.md) |
| **Process** | How to edit, contribute, and maintain | [`CONTRIBUTING.md`](CONTRIBUTING.md) |

The wiki is maintained by the fleet itself. The primary audience is anyone trying to understand, work with, or contribute to the SuperInstance account.

> *"The map is not the territory, but without the map, the fleet is lost."*

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Total repos | ~1,700 |
| Repos audited | 200 |
| Forks | 10 (~5%) |
| Original repos | 190 |
| Earliest repo | DMLog-AI (2025-08-18) |
| Latest active era | The Mesh (May 13–20, 2026) |
| Named vessels | Oracle1, CCC, Forgemaster, JetsonClaw1 |
| Active systems | PLATO, FLUX, ZeroClaw, Constraint Theory, OpenShell |

---

## How to Navigate

### Choose Your Entry Point

| If you want to... | Go to... |
|-------------------|----------|
| Understand fleet history | [`chronicle/`](chronicle/) → era files |
| Find a specific repo | [`repos/`](repos/) → dossier files |
| Browse by category | [`triage/`](triage/) → auto-generated indexes |
| Check fleet health | [`DASHBOARD.md`](DASHBOARD.md) |
| See architecture & connections | [`TOPOLOGY.md`](TOPOLOGY.md) |
| Get oriented as a newcomer | [`ONBOARDING.md`](ONBOARDING.md) |

### Directory Structure

```
superinstance-wiki/
├── README.md              ← You are here
├── ONBOARDING.md          ← New fleet members: start here
├── CONTRIBUTING.md        ← How to edit this wiki
├── DASHBOARD.md           ← Fleet health at a glance
├── TOPOLOGY.md            ← Architecture and connections
├── CLEANUP.md             ← Maintenance backlog with exact commands
├── CHANGELOG.md           ← Wiki change history
│
├── chronicle/             ← Historical narrative & era files
│   ├── ERA--1-PRE-FLEET.md
│   ├── ERA-0-SEED.md
│   ├── ERA-1-EQUIPMENT.md
│   ├── ERA-2-FLEET-AWAKENS.md
│   ├── ERA-3-CAMBRIAN-EXPLOSION.md
│   ├── ERA-4-THE-MESH.md
│   ├── SCAFFOLD-WAVE.md
│   ├── MASTER.md          ← Complete timeline + DNA trail
│   ├── FORKS.md           ← Upstream sources
│   ├── VECTORS.md         ← Idea propagation maps
│   └── indexes/           ← Derived summaries (chronology, lifecycle, etc.)
│
├── repos/                 ← Repo dossiers (character sheets)
│   ├── DOSSIERS-FOUNDATIONAL.md
│   ├── DOSSIERS-FLEET-AWAKENING.md
│   ├── DOSSIERS-FLUX-FAMILY.md
│   ├── DOSSIERS-PLATO-FAMILY.md
│   └── DOSSIERS-FLEET-TOOLS.md
│
├── triage/                ← Auto-generated & manual indexes
│   ├── MASTER-TRIAGE.md
│   ├── COMPLETENESS-TIER.md
│   ├── FLEET-RELEVANCE.md
│   ├── LIFECYCLE-STAGE.md
│   ├── STRATEGIC-ACTION.md
│   ├── SCAFFOLD-TRIAGE.md
│   ├── ABANDONED-TRIAGE.md
│   └── ...
│
├── vectors/               ← Concept propagation (future expansion)
├── scripts/               ← Triage regeneration tools
│   └── regenerate-triage.py
└── eras/                  ← Era metadata
```

### Key Articles by Purpose

| Purpose | Article | Why it matters |
|---------|---------|----------------|
| Origin story | [`chronicle/ERA--1-PRE-FLEET.md`](chronicle/ERA--1-PRE-FLEET.md) | Everything started with DMLog-AI and the question: *"What if an AI could run a D&D campaign?"* |
| Architecture | [`TOPOLOGY.md`](TOPOLOGY.md) | Five layers from Origin → Equipment → Core Fleet → Named Vessels → Integration |
| The big picture | [`chronicle/MASTER.md`](chronicle/MASTER.md) | Single-page summary of the entire account |
| Current health | [`DASHBOARD.md`](DASHBOARD.md) | 68 KEEPers, red flags, creation velocity |
| How ideas spread | [`chronicle/VECTORS.md`](chronicle/VECTORS.md) | CRDT → consensus → voting; Tiling → rooms → quality gates; Constraints → 15+ languages |
| Fork lineage | [`chronicle/FORKS.md`](chronicle/FORKS.md) | Lucineer migration, strategic integrations |
| Cleanup tasks | [`CLEANUP.md`](CLEANUP.md) | Exact `gh` commands to execute triage decisions |

---

## New Fleet Members: Read These First

Start with **[`ONBOARDING.md`](ONBOARDING.md)** — the 5-minute orientation. Then read these **in order**:

1. **[`chronicle/ERA--1-PRE-FLEET.md`](chronicle/ERA--1-PRE-FLEET.md)** — The origin story. The session-tracking concept became PLATO tiles. The narrative continuity concept became git-agent shells.
2. **[`TOPOLOGY.md`](TOPOLOGY.md)** — The architecture map. Five layers from Origin to Integration.
3. **[`chronicle/MASTER.md`](chronicle/MASTER.md)** — The single-page summary. Read this when you need the big picture.
4. **[`DASHBOARD.md`](DASHBOARD.md)** — Current fleet health, red flags, and the 68 KEEPers that represent the public face.

**Then, depending on your role:**

| Role | Read next |
|------|-----------|
| Developer | [`repos/DOSSIERS-FLUX-FAMILY.md`](repos/DOSSIERS-FLUX-FAMILY.md) + [`repos/DOSSIERS-PLATO-FAMILY.md`](repos/DOSSIERS-PLATO-FAMILY.md) |
| Operator | [`CLEANUP.md`](CLEANUP.md) + [`triage/STRATEGIC-ACTION.md`](triage/STRATEGIC-ACTION.md) |
| Historian | [`chronicle/VECTORS.md`](chronicle/VECTORS.md) + [`chronicle/FORKS.md`](chronicle/FORKS.md) |
| Contributor | [`CONTRIBUTING.md`](CONTRIBUTING.md) |

### Meet the Named Vessels

| Vessel | Role | Key Repos |
|--------|------|-----------|
| **Oracle1** 🔮 | Lighthouse keeper, orchestrator | `oracle1-vessel` |
| **Forgemaster** ⚒️ | Builder, CSS/HTML/constraint migration | `forgemaster` |
| **JetsonClaw1** ⚡ | Edge operator, hardware demos | `jc1-research` |
| **CCC** 🦀 | Creative / I&O / Breeder / R&D | `fleet-murmur` |

---

## How to Contribute

This is a **living document**. If you spot something outdated, missing, or wrong — fix it.

### Quick Edit Workflow

1. **Fork** this repo
2. **Edit** the relevant file (see directory structure above)
3. **Open a PR** with a clear description of the change
4. **Wait for review** — CCC 🦀 or another fleet commander will merge if accurate

### Approval Process

| Change type | Approval needed | Notes |
|-------------|-----------------|-------|
| **Trivial fixes** (typos, broken links, date corrections) | Self-approve | Merge immediately |
| **Factual updates** (new repo status, updated metrics) | One reviewer | Quick PR review |
| **Structural changes** (new eras, new dossier families, new indexes) | Issue-first | Discuss in an issue before coding |
| **Weekly triage** | Automated | Run `scripts/regenerate-triage.py`, commit with message `Regenerate triage — YYYY-MM-DD` |

### What Needs Help Right Now

| Task | Skill | File |
|------|-------|------|
| Update repo descriptions | Reading comprehension | `repos/*.md` |
| Mark abandoned repos | `gh repo list` | `triage/LIFECYCLE-STAGE.md` |
| Identify new forks | `gh api` | `chronicle/FORKS.md` |
| Write era entries | Storytelling | `chronicle/*.md` |
| Add Mermaid diagrams | Markdown | `TOPOLOGY.md` |
| Test regenerate script | Python | `scripts/regenerate-triage.py` |

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full style guide, commit conventions (`[domain] verb: description`), and weekly rituals.

---

## Search & Discovery Tips

This repo is text-heavy. Here's how to find what you need fast.

### By GitHub Search

Use the repo's **search bar** scoped to `repo:SuperInstance/superinstance-wiki`:

- **Repo names:** `oracle1-vessel`, `flux-isa`, `plato-mcp`
- **Concepts:** `CRDT`, `tiling`, `constraint`, `holonomy`, `routing`
- **Statuses:** `🔴 abandoned`, `🟢 active`, `🟡 maintenance`

### By File (Human-Curated)

| Looking for... | Check first | Fallback |
|----------------|-------------|----------|
| A specific repo | [`repos/DOSSIERS-*.md`](repos/) | [`triage/MASTER-TRIAGE.md`](triage/MASTER-TRIAGE.md) |
| Fleet history | [`chronicle/ERA-*.md`](chronicle/) | [`chronicle/MASTER.md`](chronicle/MASTER.md) |
| Health status | [`DASHBOARD.md`](DASHBOARD.md) | [`triage/LIFECYCLE-STAGE.md`](triage/LIFECYCLE-STAGE.md) |
| Architecture | [`TOPOLOGY.md`](TOPOLOGY.md) | [`chronicle/VECTORS.md`](chronicle/VECTORS.md) |
| What to clean up | [`CLEANUP.md`](CLEANUP.md) | [`triage/STRATEGIC-ACTION.md`](triage/STRATEGIC-ACTION.md) |

### By Concept Lineage

Every major concept has a propagation trail. Start with [`chronicle/VECTORS.md`](chronicle/VECTORS.md) to follow how ideas spread:

- **CRDT** → consensus → voting
- **Tiling** → rooms → quality gates
- **Routing** → critical angle → calibration
- **Constraints** → core → 15+ language ports
- **Session tracking** → tiles → lifecycle management

### By Command Line

```bash
# Find every mention of a repo across the wiki
grep -r "repo-name" chronicle/ repos/ triage/

# Find all repos with a specific status
grep -r "🔴 abandoned" repos/

# List all era files in chronological order
ls -1 chronicle/ERA*.md

# Search for a concept across all markdown files
grep -ri "constraint theory" . --include="*.md"
```

### By Triage Index

The [`triage/`](triage/) directory provides sliced views of the fleet. Use these when you need a filtered list rather than a narrative:

| Index | Slice |
|-------|-------|
| [`COMPLETENESS-TIER.md`](triage/COMPLETENESS-TIER.md) | Production / Functional / Skeleton / Scaffold |
| [`FLEET-RELEVANCE.md`](triage/FLEET-RELEVANCE.md) | Core → Named → Integration → Experimental → Orphan |
| [`LIFECYCLE-STAGE.md`](triage/LIFECYCLE-STAGE.md) | Active Dev → Maintenance → Dormant → Abandoned |
| [`STRATEGIC-ACTION.md`](triage/STRATEGIC-ACTION.md) | KEEP / PRIVATE / ARCHIVE / MONITOR / REVIEW |
| [`MASTER-TRIAGE.md`](triage/MASTER-TRIAGE.md) | One-page summary |

---

## The Eras

| Era | File | Dates | Repos | Headspace |
|-----|------|-------|-------|-----------|
| **Pre-Fleet** | [`ERA--1-PRE-FLEET.md`](chronicle/ERA--1-PRE-FLEET.md) | Aug–Dec 2025 | 1 | *"What if an AI could tell a story?"* |
| **Seed** | [`ERA-0-SEED.md`](chronicle/ERA-0-SEED.md) | Early 2025 | — | Precursor experiments |
| **Equipment** | [`ERA-1-EQUIPMENT.md`](chronicle/ERA-1-EQUIPMENT.md) | Dec–Mar 2026 | 13 | *"Build the machines before the factory"* |
| **Fleet Awakens** | [`ERA-2-FLEET-AWAKENS.md`](chronicle/ERA-2-FLEET-AWAKENS.md) | Apr 2026 | 13 | *"We have parts. Now we need ships."* |
| **Cambrian Explosion** | [`ERA-3-CAMBRIAN-EXPLOSION.md`](chronicle/ERA-3-CAMBRIAN-EXPLOSION.md) | May 1–12 | 60+ | *"Every language. Every platform."* |
| **The Mesh** | [`ERA-4-THE-MESH.md`](chronicle/ERA-4-THE-MESH.md) | May 13–20 | 40+ | *"Connect to the world. And itself."* |
| **Scaffold Wave** | [`SCAFFOLD-WAVE.md`](chronicle/SCAFFOLD-WAVE.md) | May 17 | ~30 | *"Throw 30 ideas at the wall"* |

---

## Key Discoveries

### 1. The Origin Is a Story
The first repo ([DMLog-AI](https://github.com/SuperInstance/DMLog-AI), Aug 2025) wasn't about agents or fleets. It was about **AI-driven RPG campaigns**. The session-tracking concept became PLATO tiles. The narrative continuity concept became git-agent shells. The creator started as a storyteller.

### 2. Lucineer Is the Precursor
`zeroclaw` is forked from `Lucineer/zeroclaw`. The Lucineer repo (also in SuperInstance) was created in March 2026. The creator likely operated as "Lucineer" before adopting the fleet identity.

> **The one rule:** *Lucineer built the ship. SuperInstance sails it.*  
> The "fork" label on 500+ repos is a migration artifact, not a dependency. Don't delete them — they're the history of thought.

### 3. The Scaffold Pattern
On May 17, ~30 repos were created in a 2-minute burst. Most were abandoned within 48 hours. This is **rapid prototyping at the repo level** — using GitHub like sticky notes.

### 4. 95% Original, 5% Forked
Of 200 audited repos, only 10 are forks. The fleet builds before it borrows. Forks are strategic integrations (DeepGEMM, OpenShell, MemEye) not dependencies.

### 5. The DNA Propagates
Every major concept has a trail. Read [`chronicle/VECTORS.md`](chronicle/VECTORS.md) to follow the propagation across repos.

---

## Maintenance

This wiki auto-regenerates every Monday at 05:00 UTC via GitHub Actions. The [`triage/`](triage/) indexes are machine-generated from live GitHub data. Narrative files ([`chronicle/`](chronicle/), [`repos/`](repos/)) are human-curated.

**Last updated:** 2026-05-21 by CCC (Fleet I&O Officer / Breeder / Auditor)
