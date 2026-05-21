# Repo Metrics Dashboard

**Generated:** 2026-05-21T09:14:11.904607Z
**Total Repos:** 1664

## Formula

```
base = (relevance_weight * 0.35 + completeness_weight * 0.35 + lifecycle_score * 0.30) * 100
score = min(100, max(0, base + strategic_bonus))
```

### Relevance Weights

| Relevance | Weight |
|-----------|--------|
| Core Fleet | 1.0 |
| Named Vessel | 0.9 |
| Integration Bridge | 0.8 |
| Experimental | 0.7 |
| Chronicled | 0.6 |
| Fork | 0.6 |
| Orphan | 0.5 |

### Completeness Weights

| Completeness | Weight |
|--------------|--------|
| Production | 1.0 |
| Functional | 0.7 |
| Skeleton | 0.4 |
| Scaffold | 0.2 |

### Lifecycle Scores

| Lifecycle | Score |
|-----------|-------|
| Active Dev | 1.0 |
| Maintenance | 0.7 |
| Dormant | 0.4 |
| Abandoned | 0.2 |

### Strategic Bonuses

| Action | Bonus |
|--------|-------|
| KEEP | +10 |
| PRIVATE | +0 |
| ARCHIVE | -20 |
| MONITOR | +0 |
| REVIEW | +0 |

## Tier Distribution

| Tier | Count | % |
|------|-------|---|
| Platinum | 55 | 3.3% |
| Gold | 104 | 6.2% |
| Silver | 1255 | 75.4% |
| Bronze | 250 | 15.0% |
| Rust | 0 | 0.0% |

## Top 25 Repos

| Rank | Repo | Score | Tier | Relevance | Completeness | Lifecycle | Action |
|------|------|-------|------|-----------|--------------|-----------|--------|
| 1 | SuperInstance | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 2 | flux-docs | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 3 | holonomy-consensus | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 4 | flux-verify-api | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 5 | flux-isa | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 6 | pythagorean48-codes | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 7 | cocapn | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 8 | keeper-beacon | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 9 | constraint-theory-core | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 10 | flux-site | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 11 | fleet-router | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 12 | flux-research | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 13 | fleet-health-monitor | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 14 | fleet-calibrator | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 15 | eisenstein | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 16 | flux-vm | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 17 | zeroclaw | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 18 | plato-vessel-core | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 19 | flux-multilingual | 100 | Platinum | Core Fleet | Production | Active Dev | KEEP |
| 20 | oracle1-workspace | 100 | Platinum | Named Vessel | Production | Active Dev | KEEP |
| 21 | plato-training | 100 | Platinum | Named Vessel | Production | Active Dev | KEEP |
| 22 | forgemaster | 100 | Platinum | Named Vessel | Production | Active Dev | KEEP |
| 23 | plato-types | 100 | Platinum | Named Vessel | Production | Active Dev | KEEP |
| 24 | plato-room-phi | 100 | Platinum | Named Vessel | Production | Active Dev | KEEP |
| 25 | plato-experience | 100 | Platinum | Named Vessel | Production | Active Dev | KEEP |

## Bottom 10 Repos

| Rank | Repo | Score | Tier | Relevance | Completeness | Lifecycle | Action |
|------|------|-------|------|-----------|--------------|-----------|--------|
| 1655 | superagent-framework | 34.0 | Bronze | Orphan | Functional | Dormant | ARCHIVE |
| 1656 | Sandbox-Lifecycle-Manager | 34.0 | Bronze | Orphan | Functional | Dormant | ARCHIVE |
| 1657 | SuperInstance-SDK1 | 34.0 | Bronze | Orphan | Functional | Dormant | ARCHIVE |
| 1658 | educationgamecocapn | 34.0 | Bronze | Orphan | Functional | Dormant | ARCHIVE |
| 1659 | ws-fabric | 34.0 | Bronze | Orphan | Functional | Dormant | ARCHIVE |
| 1660 | Ghost-tiles | 34.0 | Bronze | Orphan | Functional | Dormant | ARCHIVE |
| 1661 | test-runner-vessel | 34.0 | Bronze | Orphan | Functional | Dormant | ARCHIVE |
| 1662 | doc-writer-vessel | 34.0 | Bronze | Orphan | Functional | Dormant | ARCHIVE |
| 1663 | comms-engineer-vessel | 34.0 | Bronze | Orphan | Functional | Dormant | ARCHIVE |
| 1664 | flux-agent-a0fa81 | 34.0 | Bronze | Orphan | Functional | Dormant | ARCHIVE |

## Sample Breakdowns

### SuperInstance

- **Score:** 100
- **Tier:** Platinum
- **Relevance:** Core Fleet (weight 1.0)
- **Completeness:** Production (weight 1.0)
- **Lifecycle:** Active Dev (score 1.0)
- **Action:** KEEP (bonus +10)
- **Base:** 100.0

### flux-docs

- **Score:** 100
- **Tier:** Platinum
- **Relevance:** Core Fleet (weight 1.0)
- **Completeness:** Production (weight 1.0)
- **Lifecycle:** Active Dev (score 1.0)
- **Action:** KEEP (bonus +10)
- **Base:** 100.0

### holonomy-consensus

- **Score:** 100
- **Tier:** Platinum
- **Relevance:** Core Fleet (weight 1.0)
- **Completeness:** Production (weight 1.0)
- **Lifecycle:** Active Dev (score 1.0)
- **Action:** KEEP (bonus +10)
- **Base:** 100.0

### flux-verify-api

- **Score:** 100
- **Tier:** Platinum
- **Relevance:** Core Fleet (weight 1.0)
- **Completeness:** Production (weight 1.0)
- **Lifecycle:** Active Dev (score 1.0)
- **Action:** KEEP (bonus +10)
- **Base:** 100.0

### flux-isa

- **Score:** 100
- **Tier:** Platinum
- **Relevance:** Core Fleet (weight 1.0)
- **Completeness:** Production (weight 1.0)
- **Lifecycle:** Active Dev (score 1.0)
- **Action:** KEEP (bonus +10)
- **Base:** 100.0

---
*Generated by scripts/repo_metrics.py*