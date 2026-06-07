# Sandbox Experiment Summary

## 5 experiments launched, 3 produced data, 2 rate-limited

### Results Table

| Repo | Agent Model | Crates Tried | Result |
|------|------------|--------------|--------|
| sniffnet | DeepSeek | conservation-checker | Added to Cargo.toml, planned bandwidth tracking |
| rtk | DeepSeek | conservation-checker | Added to Cargo.toml, planned token budget CLI |
| gdext | GLM-5.1 | negative-space-testing + cathedral-probe | 9 experiments, real tests, honest assessment |
| trippy | GLM-5.1 | — | Rate limited |
| arroyo | GLM-5.1 | — | Rate limited |

### Key Finding 1: conservation-checker is the universal entry point
Both successful DeepSeek agents independently chose conservation-checker first.
Neither chose cathedral-probe or crackle-runtime.

Why: 'Budget tracking' maps to the most universal developer pain point.
'Things that should not decrease' is intuitive without reading docs.

### Key Finding 2: Deeper exploration picks up the other crates
The GLM-5.1 gdext agent explored deeper and found value in BOTH
negative-space-testing and cathedral-probe. It wrote 9 real experiments.
More time = more crate adoption.

### Key Finding 3: There's an overlap bug
negative-space-testing bundles its own CathedralProbe which is weaker
than the standalone cathedral-probe crate. Agents get confused by this.
Need to either: remove the bundled version, or clearly document the difference.

### Key Finding 4: GLM-5.1 goes deeper than DeepSeek for this task
DeepSeek: quick action (cargo add + commit message) but shallow.
GLM-5.1: reads source, writes tests, gives honest negatives.
For sandbox experiments, GLM is the better choice.

