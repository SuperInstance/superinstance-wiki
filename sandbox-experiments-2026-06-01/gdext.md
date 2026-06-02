# gdext + negative-space-testing + cathedral-probe (GLM-5.1 agent)

## Result: SUCCESS — 9 experiments, real integration code, honest assessment

### Commit Trail
```
a5eca7a Initial experiment: 6 integration tests with negative-space-testing + cathedral-probe
04b43cc Deep dive: gdext-style Player invariants, ECS topology, zone validation
```

### What the Agent Built

#### negative-space-testing (v0.1.0) — 4 useful tools identified:
1. **NegativeTest** — Define forbidden states (NaN position, velocity overflow, negative health)
   - API: `.forbid("desc", |val| predicate)` — very natural for physics invariant testing
2. **ConservationChecker** — Track quantities across frames (energy, momentum)
   - Catches physics bugs where energy mysteriously appears
3. **CracklePhase** — Accumulate values during "firing" then check deferred assertions during "cooling"
   - Great for detecting frame spikes and monotonicity violations
4. **SpaceMap** — Track occupied vs forbidden regions
   - Caught a boss room being incorrectly placed

#### cathedral-probe (v0.1.1) — Spectral graph analysis:
- Fiedler value (algebraic connectivity) reveals how well-connected a system graph is
- **Component importance** correctly identified PhysicsWorld as the most critical node in a 10-node scene graph
- **Bottleneck detection** found the critical communication edges
- Better implementation than the CathedralProbe bundled inside negative-space-testing

### Honest Assessment (from the agent)
- **Neither crate knows about gdext** — they're pure Rust math/testing libraries
- **Best use: test suites** — define invariants in `#[test]` functions, not runtime
- **CathedralProbe is O(n³)** — only for offline architecture analysis, not per-frame
- **SpaceMap uses HashMap** — not spatial, so limited for real world geometry
- **Overlap**: negative-space-testing bundles its own (weaker) CathedralProbe — use the standalone crate instead

### Pattern Analysis
This agent explored MORE deeply than sniffnet/rtk agents:
- Read full source code of both crates (not just docs)
- Wrote 9 experiments across 2 commits
- Identified API strengths AND weaknesses
- Found the overlap bug (bundled CathedralProbe vs standalone)
- Gave honest negatives (not spatial, O(n³), no gdext integration)

**Model difference?** GLM-5.1 went deeper. DeepSeek agents did a quick `cargo add` + commit but ran out of time/depth. GLM read the source and wrote real tests.
