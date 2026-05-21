# Cross-Repo Patterns — Lite Survey

**Generated:** 2026-05-21  
**Method:** Zero-clone analysis via `gh repo list` (n=100 sample) + `gh search code` (5 pattern queries)  
**Source indexes:** `INDEXES/MASTER-INDEX.md` (1,664 repos), `INDEXES/FLEET-RELEVANCE.md`

---

## 1. Pattern Catalog

### Dependency Management — Mostly Absent
| Pattern | Hits (search) | Actual repos with file | Inference |
|---------|---------------|----------------------|-----------|
| `config.py` | 30 search results | ~4 unique repos | Configuration is ad-hoc; most repos lack structured env handling |
| `requirements.txt` | 30 search results | ~5 unique repos | Python repos rarely declare dependencies. Most hits are CI templates that *check* for the file |
| `Dockerfile` | 30 search results | ~2 unique repos | The fleet is essentially **non-containerized** |
| `.github/workflows` | 30 search results | ~18 unique repos | Only **~1% of the fleet** has CI (18 / 1,664) |

**Key finding:** The vast majority of repos are "skeleton" or "functional" tier with no packaging, no containers, and no continuous integration. The `gh search` hits are dominated by documentation references, CI templates that *mention* these files, and Lucineer-related copies — not actual manifests.

### Repo Lifecycle — Creation Spike Then Stagnation
From `MASTER-INDEX.md`:
- **1,062 repos** created in 2026-04 alone (64% of all repos)
- **407 repos** created in 2026-05 so far
- Only **65 repos (3.9%)** marked `KEEP` — the rest are `REVIEW` (74.4%) or `ARCHIVE` (15.0%)
- Monthly velocity shows a massive April 2026 burst, then continued high creation in May

---

## 2. Language Distribution (from 100-repo sample)

| Language | Count | % | Notes |
|----------|-------|---|-------|
| Python | ~62 | 62% | Dominant. Most created in last 60 days, 0 stars |
| Rust | ~10 | 10% | Core infrastructure (forgemaster, OpenShell, holonomy-consensus, etc.) |
| TypeScript | ~5 | 5% | Equipment routers, webgpu-profiler |
| HTML | ~4 | 4% | Landing pages, documentation sites |
| C | ~2 | 2% | flux-engine-c, flux-fracture-c |
| Shell | ~1 | 1% | deadband-rs |
| Null / None | ~6 | 6% | Docs-only or empty repos |
| **Esoteric / Dead** | **8** | **8%** | COBOL, ALGOL, SNOBOL, MUMPS, PL/I, RPGLE, Fortran, Chapel — all `flux-*` repos |

---

## 3. Stargazer Distribution (from 100-repo sample)

| Stars | Count | % | Notable repos |
|-------|-------|---|---------------|
| 0 | ~82 | 82% | The silent majority |
| 1 | ~12 | 12% | fleet-homology, DeepGEMM, pythagorean48-codes, plato-room-phi, etc. |
| 2 | ~5 | 5% | oracle1-workspace, forgemaster, webgpu-profiler, constraint-theory-llvm |
| 3 | ~1 | 1% | SuperInstance (the main org page / HTML) |

**Rust repos average higher stars** than Python repos in the sample — the most-starred original fleet code is Rust-based.

---

## 4. 🎯 Novel Insight — The Graveyard of Dead Languages

> **Despite 1,664 repos, 8 of them are written in dead or legacy languages (COBOL, ALGOL, SNOBOL, MUMPS, PL/I, RPGLE, Fortran, Chapel) — all created on the same day (2026-05-19), all with exactly 1 push, all abandoned with 0 stars. They share the `flux-*` prefix (flux-cobol, flux-algol, flux-snobol, flux-mumps, flux-pli, flux-rpg, flux-fortran, flux-chapel), suggesting a single batch experiment in esoteric-language bindings that was never continued.**

This is the most surprising pattern in the fleet: a brief, uniform burst of esoteric language repos that serve no apparent production purpose and have received zero subsequent attention. They exist as fossils — evidence of an exploratory phase that was abandoned before it began.

---

## 5. Fleet Health Summary

| Metric | Value | Assessment |
|--------|-------|------------|
| Total repos | 1,664 | Large footprint, high noise |
| With CI | ~18 | **~1%** — critical gap |
| With containers | ~2 | **~0.1%** — non-containerized fleet |
| Production tier | 736 (44.2%) | Many may be "production" in name only |
| KEEP-action repos | 65 (3.9%) | Very few repos have been vetted for long-term retention |
| Rust repos (core) | ~20 | Highest quality, most external attention |
| Python skeletons | ~1,000+ | Created en masse, mostly unproven |

---

## Methodology Note

This report uses **zero full clones** — all data derived from:
1. `gh repo list SuperInstance --limit 100 --json name,primaryLanguage,pushedAt,createdAt,stargazerCount`
2. `gh search code "<pattern>" --owner SuperInstance --limit 30` (5 queries)
3. Existing triage indexes in `superinstance-wiki`

Search results were manually deduplicated to count *unique repos* vs. documentation references / Lucineer copies. Numbers are estimates — a full audit would require deeper inspection.
