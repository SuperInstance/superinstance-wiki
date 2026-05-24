# Security Test Report — sunset-ecosystem

## What Worked

- **SignedWAL chain integrity**: All 5 entries (3 spawns + 2 breeds) verified successfully. The HMAC-SHA256 backend worked out of the box without extra dependencies.
- **HolonomyConsensus round**: A single `register_lineage` proposal was created and committed with quorum `1/1` for a 3-node network. The commit path and status reporting are clean.
- **LineageSanityChecker ran**: It correctly traversed all pairs and identified every parent-child relationship in the population.

## What Was Confusing

- The **default `incest` guard** in `LineageSanityChecker` flags *any* parent-child pair as FATAL. This is confusing in a breeding context because children naturally have parents. The guard appears designed to prevent *breeding* between ancestors/descendants, not to flag their mere coexistence in a population list.
- **Quorum math for small fleets**: With `N=3`, Byzantine tolerance `f=0` and quorum `=1`. A single self-vote commits immediately, which feels too permissive for a "consensus" round. It is mathematically correct (`2f+1` with `f=0`), but practically surprising.

## Rating: ★★★☆☆ (3/5)

The primitives are well-structured and the WAL crypto is solid. The lineage checker API is powerful but the default guards need tuning for typical breeding workflows. The consensus quorum math for small N is technically correct but could benefit from a minimum-size safeguard or explicit documentation.

## Top 2 Suggestions

1. **Add a `breeding_only=True` mode to `LineageSanityChecker.check_all()`** so it only runs pairwise guards on agents marked as eligible breeders, avoiding false-positive FATALs on normal parent-child coexistence.
2. **Document or enforce a minimum `quorum` floor in `HolonomyConsensus`** (e.g., `max(2f+1, 2)`) so small fleets still require at least 2 votes before a proposal commits, making the consensus round more meaningful for testing.
