#!/usr/bin/env python3
"""Tests for swarm.lineage_checker — agent genealogy sanity validation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from swarm.lineage_checker import (
    LineageRecord,
    MutationProfile,
    LineageViolation,
    ViolationSeverity,
    LineageSanityChecker,
    _default_incest_guard,
    _default_generation_gap_guard,
    _default_mutation_rate_guard,
    _default_diversity_guard,
)


# ── 1. Incest Detection ────────────────────────────────────────────

def test_parent_child_is_incest() -> None:
    parent = LineageRecord(agent_id=1, generation=0)
    child = LineageRecord(agent_id=2, generation=1, parent_ids=(1,))
    pop = {1: parent, 2: child}
    v = _default_incest_guard(parent, child, pop)
    assert v is not None
    assert v.severity == ViolationSeverity.FATAL
    assert "parent_child" in v.kind


def test_child_parent_is_incest() -> None:
    parent = LineageRecord(agent_id=1, generation=0)
    child = LineageRecord(agent_id=2, generation=1, parent_ids=(1,))
    pop = {1: parent, 2: child}
    v = _default_incest_guard(child, parent, pop)
    assert v is not None
    assert "parent_child" in v.kind


def test_grandparent_grandchild_is_incest() -> None:
    grandparent = LineageRecord(agent_id=1, generation=0)
    parent = LineageRecord(agent_id=2, generation=1, parent_ids=(1,))
    grandchild = LineageRecord(agent_id=3, generation=2, parent_ids=(2,))
    pop = {1: grandparent, 2: parent, 3: grandchild}
    v = _default_incest_guard(grandparent, grandchild, pop)
    assert v is not None
    assert "ancestor_descendant" in v.kind


def test_unrelated_pair_is_clean() -> None:
    a = LineageRecord(agent_id=1, generation=0)
    b = LineageRecord(agent_id=2, generation=0)
    pop = {1: a, 2: b}
    assert _default_incest_guard(a, b, pop) is None


def test_cousins_are_clean() -> None:
    grandparent = LineageRecord(agent_id=1, generation=0)
    parent_a = LineageRecord(agent_id=2, generation=1, parent_ids=(1,))
    parent_b = LineageRecord(agent_id=3, generation=1, parent_ids=(1,))
    cousin_a = LineageRecord(agent_id=4, generation=2, parent_ids=(2,))
    cousin_b = LineageRecord(agent_id=5, generation=2, parent_ids=(3,))
    pop = {1: grandparent, 2: parent_a, 3: parent_b, 4: cousin_a, 5: cousin_b}
    assert _default_incest_guard(cousin_a, cousin_b, pop) is None


def test_missing_parent_in_population_still_walks() -> None:
    # Parent 99 is not in pop — guard should treat as external founder
    child = LineageRecord(agent_id=2, generation=1, parent_ids=(99,))
    pop = {2: child}
    v = _default_incest_guard(child, LineageRecord(agent_id=99), pop)
    # 99 isn't a parent of 99, and 99 isn't a parent of 2 in pop
    # Actually 99 is parent of 2, so child=2, potential mate=99
    # 99 is in parent_ids of 2 → parent-child!
    assert v is not None
    assert "parent_child" in v.kind


# ── 2. Generation Gap ────────────────────────────────────────────────

def test_same_generation_ok() -> None:
    a = LineageRecord(agent_id=1, generation=2)
    b = LineageRecord(agent_id=2, generation=2)
    assert _default_generation_gap_guard(a, b, {}, max_gap=1) is None


def test_gap_of_one_ok() -> None:
    a = LineageRecord(agent_id=1, generation=1)
    b = LineageRecord(agent_id=2, generation=2)
    assert _default_generation_gap_guard(a, b, {}, max_gap=1) is None


def test_gap_of_two_blocked() -> None:
    a = LineageRecord(agent_id=1, generation=0)
    b = LineageRecord(agent_id=2, generation=2)
    v = _default_generation_gap_guard(a, b, {}, max_gap=1)
    assert v is not None
    assert v.severity == ViolationSeverity.ERROR
    assert v.detail["gap"] == 2


def test_gap_guard_respects_custom_max() -> None:
    a = LineageRecord(agent_id=1, generation=0)
    b = LineageRecord(agent_id=2, generation=3)
    # gap=3, max_gap=5 → ok
    assert _default_generation_gap_guard(a, b, {}, max_gap=5) is None
    # gap=3, max_gap=2 → blocked
    v = _default_generation_gap_guard(a, b, {}, max_gap=2)
    assert v is not None


# ── 3. Mutation Rate ───────────────────────────────────────────────

def test_mutation_within_bounds_is_clean() -> None:
    agent = LineageRecord(
        agent_id=1,
        mutation_profile=MutationProfile(rate=0.15),
    )
    assert _default_mutation_rate_guard(agent, min_rate=0.0, max_rate=1.0) is None


def test_mutation_too_high() -> None:
    agent = LineageRecord(
        agent_id=1,
        mutation_profile=MutationProfile(rate=1.05),
    )
    v = _default_mutation_rate_guard(agent, min_rate=0.0, max_rate=1.0)
    assert v is not None
    assert v.severity == ViolationSeverity.ERROR
    assert v.detail["rate"] == 1.05


def test_mutation_too_low() -> None:
    agent = LineageRecord(
        agent_id=1,
        mutation_profile=MutationProfile(rate=-0.01),
    )
    v = _default_mutation_rate_guard(agent, min_rate=0.0, max_rate=1.0)
    assert v is not None


def test_mutation_none_is_unchecked() -> None:
    agent = LineageRecord(
        agent_id=1,
        mutation_profile=MutationProfile(rate=None),
    )
    assert _default_mutation_rate_guard(agent) is None


def test_mutation_exact_boundary() -> None:
    agent = LineageRecord(
        agent_id=1,
        mutation_profile=MutationProfile(rate=1.0),
    )
    assert _default_mutation_rate_guard(agent, min_rate=0.0, max_rate=1.0) is None


# ── 4. Diversity Collapse ──────────────────────────────────────────

def test_founder_collapse_with_one_founder() -> None:
    founder = LineageRecord(agent_id=1, generation=0)
    child = LineageRecord(agent_id=2, generation=1, parent_ids=(1,))
    pop = [founder, child]
    pop_dict = {r.agent_id: r for r in pop}
    violations = _default_diversity_guard(pop, pop_dict, min_unique_founders=3)
    kinds = [v.kind for v in violations]
    assert "diversity:founder_collapse" in kinds
    founder_v = next(v for v in violations if "founder_collapse" in v.kind)
    assert founder_v.severity == ViolationSeverity.FATAL


def test_founder_collapse_avoided_with_many_founders() -> None:
    pop = [
        LineageRecord(agent_id=1, generation=0),
        LineageRecord(agent_id=2, generation=0),
        LineageRecord(agent_id=3, generation=0),
        LineageRecord(agent_id=4, generation=1, parent_ids=(1, 2)),
        LineageRecord(agent_id=5, generation=1, parent_ids=(2, 3)),
    ]
    pop_dict = {r.agent_id: r for r in pop}
    violations = _default_diversity_guard(pop, pop_dict, min_unique_founders=3)
    founder_violations = [v for v in violations if "founder_collapse" in v.kind]
    assert len(founder_violations) == 0


def test_low_heterozygosity_warning() -> None:
    # All same generation → CV = 0 → triggers warning
    pop = [
        LineageRecord(agent_id=i, generation=5) for i in range(1, 5)
    ]
    pop_dict = {r.agent_id: r for r in pop}
    violations = _default_diversity_guard(
        pop, pop_dict, min_unique_founders=1, min_heterozygosity=0.01
    )
    kinds = [v.kind for v in violations]
    assert "diversity:low_heterozygosity" in kinds
    het_v = next(v for v in violations if "low_heterozygosity" in v.kind)
    assert het_v.severity == ViolationSeverity.WARNING


def test_diversity_healthy_population() -> None:
    pop = [
        LineageRecord(agent_id=1, generation=0),
        LineageRecord(agent_id=2, generation=0),
        LineageRecord(agent_id=3, generation=0),
        LineageRecord(agent_id=4, generation=1, parent_ids=(1,)),
        LineageRecord(agent_id=5, generation=2, parent_ids=(4,)),
        LineageRecord(agent_id=6, generation=3, parent_ids=(5,)),
    ]
    pop_dict = {r.agent_id: r for r in pop}
    violations = _default_diversity_guard(
        pop, pop_dict, min_unique_founders=3, min_heterozygosity=0.01
    )
    # Should have no founder collapse (3 founders) and CV should be high
    assert len(violations) == 0


# ── 5. LineageSanityChecker Integration ────────────────────────────

def test_checker_check_pair_finds_both_violations() -> None:
    grandparent = LineageRecord(agent_id=1, generation=0)
    parent = LineageRecord(agent_id=2, generation=1, parent_ids=(1,))
    grandchild = LineageRecord(agent_id=3, generation=2, parent_ids=(2,))
    pop = {1: grandparent, 2: parent, 3: grandchild}
    checker = LineageSanityChecker()
    violations = checker.check_pair(grandparent, grandchild, pop)
    kinds = {v.kind for v in violations}
    assert "incest:ancestor_descendant" in kinds
    assert "generation_gap:excessive" in kinds


def test_checker_check_agent_mutation() -> None:
    agent = LineageRecord(
        agent_id=1,
        mutation_profile=MutationProfile(rate=1.5),
    )
    checker = LineageSanityChecker(mutation_max=1.0)
    violations = checker.check_agent(agent)
    assert len(violations) == 1
    assert violations[0].kind == "mutation_rate:out_of_bounds"


def test_checker_check_population_diversity() -> None:
    pop = [
        LineageRecord(agent_id=1, generation=0),
        LineageRecord(agent_id=2, generation=1, parent_ids=(1,)),
    ]
    checker = LineageSanityChecker(min_unique_founders=3)
    violations = checker.check_population(pop)
    assert any("founder_collapse" in v.kind for v in violations)


def test_checker_check_all_comprehensive() -> None:
    # A small inbred population with multiple problems
    founder = LineageRecord(agent_id=1, generation=0)
    child = LineageRecord(
        agent_id=2,
        generation=1,
        parent_ids=(1,),
        mutation_profile=MutationProfile(rate=-0.05),
    )
    grandchild = LineageRecord(
        agent_id=3,
        generation=2,
        parent_ids=(2,),
        mutation_profile=MutationProfile(rate=1.5),
    )
    # Add same-gen clones to force low heterozygosity
    clone_a = LineageRecord(agent_id=4, generation=5, parent_ids=(3,))
    clone_b = LineageRecord(agent_id=5, generation=5, parent_ids=(3,))
    clone_c = LineageRecord(agent_id=6, generation=5, parent_ids=(3,))
    pop = [founder, child, grandchild, clone_a, clone_b, clone_c]

    checker = LineageSanityChecker(min_unique_founders=3, min_heterozygosity=0.80)
    violations = checker.check_all(pop)

    kinds = [v.kind for v in violations]
    # Pairwise incest
    assert any("incest" in k for k in kinds)
    # Generation gap
    assert any("generation_gap" in k for k in kinds)
    # Mutation out of bounds (child rate=-0.05, grandchild rate=1.5)
    assert kinds.count("mutation_rate:out_of_bounds") == 2
    # Founder collapse — only 1 founder lineage (agent 1)
    assert any("founder_collapse" in k for k in kinds)
    # Low heterozygosity — many agents at gen 5
    assert any("low_heterozygosity" in k for k in kinds)


def test_is_healthy_returns_false_on_fatal() -> None:
    parent = LineageRecord(agent_id=1, generation=0)
    child = LineageRecord(agent_id=2, generation=1, parent_ids=(1,))
    pop = [parent, child]
    checker = LineageSanityChecker()
    assert checker.is_healthy(pop) is False


def test_is_healthy_returns_true_for_clean_pop() -> None:
    # All same generation — no parent-child pairs, so no incest flags
    pop = [
        LineageRecord(agent_id=1, generation=2),
        LineageRecord(agent_id=2, generation=2),
        LineageRecord(agent_id=3, generation=2),
        LineageRecord(agent_id=4, generation=2),
        LineageRecord(agent_id=5, generation=2),
    ]
    checker = LineageSanityChecker(min_unique_founders=3)
    assert checker.is_healthy(pop) is True


def test_summary_structure() -> None:
    # Same-gen population — no parent-child pairs to trigger incest flags
    pop = [
        LineageRecord(agent_id=1, generation=2),
        LineageRecord(agent_id=2, generation=2),
        LineageRecord(agent_id=3, generation=2),
    ]
    checker = LineageSanityChecker(min_unique_founders=3)
    summary = checker.summary(pop)
    assert summary["population_size"] == 3
    assert isinstance(summary["violations"], list)
    assert isinstance(summary["counts_by_severity"], dict)
    assert isinstance(summary["counts_by_kind"], dict)
    assert summary["healthy"] is True


def test_checker_repr() -> None:
    checker = LineageSanityChecker(max_generation_gap=2, mutation_max=0.5)
    r = repr(checker)
    assert "max_generation_gap=2" in r
    assert "mutation_bounds=[0.0, 0.5]" in r


# ── 6. Edge Cases ─────────────────────────────────────────────────

def test_empty_population_is_healthy() -> None:
    checker = LineageSanityChecker(min_unique_founders=0)
    assert checker.is_healthy([]) is True
    assert len(checker.check_all([])) == 0


def test_single_agent_no_pairs() -> None:
    pop = [LineageRecord(agent_id=1, generation=0)]
    checker = LineageSanityChecker(min_unique_founders=1)
    violations = checker.check_all(pop)
    assert len(violations) == 0


def test_circular_parent_reference_handled() -> None:
    # Pathological: agent is its own parent (should not infinite loop)
    agent = LineageRecord(agent_id=1, generation=1, parent_ids=(1,))
    pop = {1: agent}
    v = _default_incest_guard(agent, agent, pop)
    assert v is not None  # parent-child with self


def test_checker_custom_guards() -> None:
    checker = LineageSanityChecker()
    # Add a custom guard that always flags odd IDs
    def odd_guard(a: LineageRecord, b: LineageRecord, pop: dict[int, LineageRecord]) -> Optional[LineageViolation]:
        if a.agent_id % 2 == 1 and b.agent_id % 2 == 1:
            return LineageViolation(
                kind="custom:both_odd",
                severity=ViolationSeverity.WARNING,
                agent_ids=(a.agent_id, b.agent_id),
                message="Both agents have odd IDs",
            )
        return None

    checker.pair_guards.append(("custom_odd", odd_guard))
    pop = [
        LineageRecord(agent_id=1, generation=0),
        LineageRecord(agent_id=3, generation=0),
    ]
    violations = checker.check_pair(pop[0], pop[1])
    assert any(v.kind == "custom:both_odd" for v in violations)


# ── Standalone runner ──────────────────────────────────────────────

def run_all_standalone() -> bool:
    """Run every test function manually (no pytest)."""
    import traceback

    tests = [
        test_parent_child_is_incest,
        test_child_parent_is_incest,
        test_grandparent_grandchild_is_incest,
        test_unrelated_pair_is_clean,
        test_cousins_are_clean,
        test_missing_parent_in_population_still_walks,
        test_same_generation_ok,
        test_gap_of_one_ok,
        test_gap_of_two_blocked,
        test_gap_guard_respects_custom_max,
        test_mutation_within_bounds_is_clean,
        test_mutation_too_high,
        test_mutation_too_low,
        test_mutation_none_is_unchecked,
        test_mutation_exact_boundary,
        test_founder_collapse_with_one_founder,
        test_founder_collapse_avoided_with_many_founders,
        test_low_heterozygosity_warning,
        test_diversity_healthy_population,
        test_checker_check_pair_finds_both_violations,
        test_checker_check_agent_mutation,
        test_checker_check_population_diversity,
        test_checker_check_all_comprehensive,
        test_is_healthy_returns_false_on_fatal,
        test_is_healthy_returns_true_for_clean_pop,
        test_summary_structure,
        test_checker_repr,
        test_empty_population_is_healthy,
        test_single_agent_no_pairs,
        test_circular_parent_reference_handled,
        test_checker_custom_guards,
    ]

    passed = 0
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"  ✅ {fn.__name__}")
            passed += 1
        except Exception as exc:
            print(f"  ❌ {fn.__name__}: {exc}")
            traceback.print_exc()
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    ok = run_all_standalone()
    sys.exit(0 if ok else 1)
