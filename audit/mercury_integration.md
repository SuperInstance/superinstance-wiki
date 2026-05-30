# Mercury Integration Plan

## What Mercury Is

Mercury is a modern logic/functional programming language in the SuperInstance OpenConstruct ecosystem. It supports:
- **Declarative programming** — relations and constraints as first-class citizens
- **Higher-order functions** — functions as data
- **Type inference** — statically typed with inference
- **Pattern matching** — algebraic data types
- **Constraint propagation/unification** — built-in constraint solving
- **OpenConstruct ABI** — compiles to ecosystem-compatible targets

Used for constraint specification in the `conservation-spectral` pipeline.

## Integration with Sunset-Ecosystem

### 1. Breeding Constraint Specification

Mercury's declarative constraints can specify breeding rules:
- Genetic compatibility (dominant/recessive trait inheritance)
- Inbreeding limits (pedigree depth checks)
- Diversity thresholds (minimum Hamming distance between parents)
- FLUX constraint propagation (hard/soft breeding rules)

**Integration point:** `swarm/breeder.py` — add `MercuryConstraintEngine` class that loads `.m` constraint files and evaluates candidate pairs against them.

```python
# swarm/mercury_constraints.py
class MercuryConstraintEngine:
    def __init__(self, rules_file: str) -> None: ...
    def check_pair(self, parent_a: Agent, parent_b: Agent) -> bool: ...
    def violation_reason(self) -> str: ...
```

### 2. Pedigree & Lineage Rule Engine

Mercury's relational model is ideal for genealogical queries:
- "Find all descendants carrying recessive trait X"
- "Check if agents share common ancestor within N generations"
- "Compute inbreeding coefficient"

**Integration point:** `swarm/lineage.py` — add `MercuryPedigreeQuery` class for complex lineage rules.

```python
# swarm/mercury_pedigree.py
class MercuryPedigreeQuery:
    def __init__(self, lineage_db: LineageDB) -> None: ...
    def common_ancestor_depth(self, a: str, b: str, max_depth: int) -> int: ...
    def descendants_with_trait(self, ancestor: str, trait: str) -> list[str]: ...
```

### 3. Consensus Logic

Mercury's logic unification can replace imperative vote-counting in our BFT consensus:
- Declare consensus rules as Horn clauses
- Unify quorum certificates declaratively
- Backtrack on Byzantine fault detection

**Integration point:** `swarm/fleet_bft_qd.py` — add `MercuryConsensusRules` for declarative PBFT phase transitions.

```python
# swarm/mercury_consensus.py
class MercuryConsensusRules:
    def check_quorum(self, msgs: list[ConsensusMessage], f: int) -> bool: ...
    def valid_view_change(self, view: int, certificates: list[ViewChangeCert]) -> bool: ...
```

## Action Items

1. **Find Mercury compiler** — `mmc` (Mercury compiler) or OpenConstruct build toolchain
2. **Test constraint propagation** — Write a `.m` file encoding `HDCDiversityScorer` logic
3. **Benchmark** — Compare Mercury constraint solving vs Python imperative for 1000+ agent evaluations
4. **FFI Bridge** — If Mercury compiles to C, use `ctypes` or `cffi` to call from Python

## Files to Create

- `swarm/mercury_constraints.py` — Breeding constraint wrapper
- `swarm/mercury_pedigree.py` — Lineage query wrapper  
- `swarm/mercury_consensus.py` — BFT logic wrapper
- `rules/breeding.m` — Sample breeding constraint rules
- `tests/test_mercury_integration.py` — Integration tests (xfail until compiler available)

## Open Questions

- Is Mercury compiler (`mmc`) available in this environment?
- Does SuperInstance provide pre-built `libmercury.so`?
- Can we use `mercury-stdlib` Python bindings if they exist?
