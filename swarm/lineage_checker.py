"""LineageSanityChecker — validates agent genealogy and genetic health.

Checks performed
----------------
1. **Incest detection** — parent-child mating (or any direct ancestor
   breeding with a descendant) is flagged.
2. **Generation gaps** — verifies that generational distance between
   breeding pairs is within bounds (e.g. no siblings breeding, no
   great-great-grandparent pairs).
3. **Mutation rate bounds** — per-agent mutation rate must sit within
   a configurable ``[min, max]`` window.
4. **Genetic diversity collapse** — flags when the effective population
   size drops below a threshold or when heterozygosity collapses.

Data model
----------
Each agent carries a ``LineageRecord`` with its genealogy.  The checker
ingests a population (a list of records) and emits ``LineageViolation``
objects describing every problem found.
"""

from __future__ import annotations

__all__ = [
    "LineageRecord",
    "MutationProfile",
    "LineageViolation",
    "ViolationSeverity",
    "LineageSanityChecker",
    "IncestGuard",
    "GenerationGapGuard",
    "MutationRateGuard",
    "DiversityGuard",
]

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Optional


class ViolationSeverity(Enum):
    """Severity of a lineage violation."""

    INFO = auto()      # Cosmetic / advisory
    WARNING = auto()   # Suspicious but not fatal
    ERROR = auto()     # Breeds unhealthy offspring
    FATAL = auto()     # Must abort — system integrity at risk


@dataclass(frozen=True)
class LineageRecord:
    """Genealogy snapshot for a single agent.

    Args:
        agent_id: Unique identifier.
        generation: Non-negative generation number (0 = founder).
        parent_ids: IDs of direct parents (normally 0, 1, or 2).
        children_ids: IDs of direct children (computed or stored).
        mutation_profile: Per-agent mutation metadata.
        metadata: Free-form extra data (e.g. breed timestamp, room id).
    """

    agent_id: int
    generation: int = 0
    parent_ids: tuple[int, ...] = ()
    children_ids: tuple[int, ...] = ()
    mutation_profile: MutationProfile = field(
        default_factory=lambda: MutationProfile()
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_founder(self) -> bool:
        return len(self.parent_ids) == 0


@dataclass(frozen=True)
class MutationProfile:
    """Per-agent mutation metadata.

    Args:
        rate: Observed mutation rate in ``[0.0, 1.0]`` (or ``None`` if
            unknown).
        count: Absolute number of mutations applied.
        spectrum: Optional dict mapping mutation class → count.
    """

    rate: Optional[float] = None
    count: int = 0
    spectrum: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class LineageViolation:
    """A single reported lineage problem.

    Args:
        kind: Human-readable violation category.
        severity: How bad it is.
        agent_ids: IDs of the agents involved.
        message: Human-readable description.
        detail: Arbitrary structured data for debugging.
    """

    kind: str
    severity: ViolationSeverity
    agent_ids: tuple[int, ...]
    message: str
    detail: dict[str, Any] = field(default_factory=dict)


# ── Guard callables (used by the checker) ──────────────────────────

IncestGuard = Callable[[
    LineageRecord, LineageRecord, dict[int, LineageRecord]
], Optional[LineageViolation]]

GenerationGapGuard = Callable[[
    LineageRecord, LineageRecord, dict[int, LineageRecord]
], Optional[LineageViolation]]

MutationRateGuard = Callable[[LineageRecord], Optional[LineageViolation]]

DiversityGuard = Callable[[
    list[LineageRecord], dict[int, LineageRecord]
], list[LineageViolation]]


# ── Default guards ─────────────────────────────────────────────────

def _default_incest_guard(
    a: LineageRecord,
    b: LineageRecord,
    population: dict[int, LineageRecord],
) -> Optional[LineageViolation]:
    """Flag if *a* and *b* share a direct ancestor/descendant relationship."""

    def _is_ancestor(descendant: LineageRecord, ancestor_id: int) -> bool:
        """DFS up the family tree.  Cycles are silently broken."""
        visited: set[int] = set()
        stack = list(descendant.parent_ids)
        while stack:
            pid = stack.pop()
            if pid == ancestor_id:
                return True
            if pid in visited:
                continue
            visited.add(pid)
            parent = population.get(pid)
            if parent is not None:
                stack.extend(parent.parent_ids)
        return False

    # Direct parent-child
    if a.agent_id in b.parent_ids or b.agent_id in a.parent_ids:
        return LineageViolation(
            kind="incest:parent_child",
            severity=ViolationSeverity.FATAL,
            agent_ids=(a.agent_id, b.agent_id),
            message=f"Agent {a.agent_id} and Agent {b.agent_id} are parent and child.",
            detail={"relationship": "parent-child"},
        )

    # Any ancestor relationship
    if _is_ancestor(a, b.agent_id):
        return LineageViolation(
            kind="incest:ancestor_descendant",
            severity=ViolationSeverity.FATAL,
            agent_ids=(a.agent_id, b.agent_id),
            message=(
                f"Agent {b.agent_id} is an ancestor of Agent {a.agent_id}."
            ),
            detail={"relationship": "ancestor-descendant", "direction": f"{b.agent_id}→{a.agent_id}"},
        )

    if _is_ancestor(b, a.agent_id):
        return LineageViolation(
            kind="incest:ancestor_descendant",
            severity=ViolationSeverity.FATAL,
            agent_ids=(a.agent_id, b.agent_id),
            message=(
                f"Agent {a.agent_id} is an ancestor of Agent {b.agent_id}."
            ),
            detail={"relationship": "ancestor-descendant", "direction": f"{a.agent_id}→{b.agent_id}"},
        )

    return None


def _default_generation_gap_guard(
    a: LineageRecord,
    b: LineageRecord,
    population: dict[int, LineageRecord],
    *,
    max_gap: int = 1,
) -> Optional[LineageViolation]:
    """Flag if the generational distance between *a* and *b* exceeds *max_gap*.

    A gap of 0 means same generation (siblings / cousins).  A gap of 1
    allows parent-child but that is already caught by the incest guard.
    The default ``max_gap=1`` therefore allows siblings and cousins but
    blocks grandparent-grandchild or wider.
    """
    gap = abs(a.generation - b.generation)
    if gap > max_gap:
        return LineageViolation(
            kind="generation_gap:excessive",
            severity=ViolationSeverity.ERROR,
            agent_ids=(a.agent_id, b.agent_id),
            message=(
                f"Generation gap between Agent {a.agent_id} (gen {a.generation}) "
                f"and Agent {b.agent_id} (gen {b.generation}) is {gap}, "
                f"max allowed is {max_gap}."
            ),
            detail={"gap": gap, "max_gap": max_gap},
        )
    return None


def _default_mutation_rate_guard(
    agent: LineageRecord,
    *,
    min_rate: float = 0.0,
    max_rate: float = 1.0,
) -> Optional[LineageViolation]:
    """Flag if an agent's mutation rate sits outside ``[min_rate, max_rate]``."""
    rate = agent.mutation_profile.rate
    if rate is None:
        return None  # unknown = unchecked

    if rate < min_rate or rate > max_rate:
        return LineageViolation(
            kind="mutation_rate:out_of_bounds",
            severity=ViolationSeverity.ERROR,
            agent_ids=(agent.agent_id,),
            message=(
                f"Agent {agent.agent_id} mutation rate {rate:.4f} is outside "
                f"bounds [{min_rate:.4f}, {max_rate:.4f}]."
            ),
            detail={"rate": rate, "min_rate": min_rate, "max_rate": max_rate},
        )
    return None


def _default_diversity_guard(
    population: list[LineageRecord],
    pop_dict: dict[int, LineageRecord],
    *,
    min_unique_founders: int = 3,
    min_heterozygosity: float = 0.05,
) -> list[LineageViolation]:
    """Flag population-level diversity collapse.

    Checks:
    1. Number of unique founder lineages ≥ *min_unique_founders*.
    2. Heterozygosity proxy (pairwise generation variance) ≥ *min_heterozygosity*.
    """
    violations: list[LineageViolation] = []

    # --- founder diversity ---
    founders = set()
    for rec in population:
        if rec.is_founder():
            founders.add(rec.agent_id)
        else:
            # Walk up to find the ultimate founders
            visited: set[int] = set()
            stack = list(rec.parent_ids)
            while stack:
                pid = stack.pop()
                if pid in visited:
                    continue
                visited.add(pid)
                parent = pop_dict.get(pid)
                if parent is None:
                    founders.add(pid)  # external / unknown founder
                elif parent.is_founder():
                    founders.add(pid)
                else:
                    stack.extend(parent.parent_ids)

    if len(founders) < min_unique_founders:
        violations.append(
            LineageViolation(
                kind="diversity:founder_collapse",
                severity=ViolationSeverity.FATAL,
                agent_ids=tuple(r.agent_id for r in population),
                message=(
                    f"Only {len(founders)} unique founder lineages detected "
                    f"(min {min_unique_founders})."
                ),
                detail={
                    "founder_count": len(founders),
                    "min_unique_founders": min_unique_founders,
                    "founders": sorted(founders),
                },
            )
        )

    # --- heterozygosity proxy ---
    # Use coefficient of variation of generation numbers as a simple proxy.
    if len(population) >= 2:
        gens = [r.generation for r in population]
        mean_g = sum(gens) / len(gens)
        if mean_g > 0:
            variance = sum((g - mean_g) ** 2 for g in gens) / len(gens)
            std = math.sqrt(variance)
            cv = std / mean_g
            if cv < min_heterozygosity:
                violations.append(
                    LineageViolation(
                        kind="diversity:low_heterozygosity",
                        severity=ViolationSeverity.WARNING,
                        agent_ids=tuple(r.agent_id for r in population),
                        message=(
                            f"Generation CV {cv:.4f} below threshold "
                            f"{min_heterozygosity:.4f} — population may be inbred."
                        ),
                        detail={
                            "cv": cv,
                            "min_heterozygosity": min_heterozygosity,
                            "mean_generation": mean_g,
                            "std_generation": std,
                        },
                    )
                )

    return violations


class LineageSanityChecker:
    """Validates a population of agents for genetic sanity.

    The checker is configurable: each guard can be replaced or extended.
    By default all four checks are enabled with conservative thresholds.

    Args:
        max_generation_gap: Maximum allowed generational distance between
            breeding partners (default 1 — allows siblings/cousins only).
        mutation_min: Lower bound for acceptable mutation rate (default 0.0).
        mutation_max: Upper bound for acceptable mutation rate (default 1.0).
        min_unique_founders: Minimum number of distinct founder lineages
            required to avoid diversity-collapse (default 3).
        min_heterozygosity: Minimum generation CV before a diversity warning
            is raised (default 0.05).
    """

    def __init__(
        self,
        *,
        max_generation_gap: int = 1,
        mutation_min: float = 0.0,
        mutation_max: float = 1.0,
        min_unique_founders: int = 3,
        min_heterozygosity: float = 0.05,
    ) -> None:
        self.max_generation_gap = max_generation_gap
        self.mutation_min = mutation_min
        self.mutation_max = mutation_max
        self.min_unique_founders = min_unique_founders
        self.min_heterozygosity = min_heterozygosity

        # Individual agent guards
        self.mutation_guards: list[MutationRateGuard] = [
            lambda agent: _default_mutation_rate_guard(
                agent,
                min_rate=self.mutation_min,
                max_rate=self.mutation_max,
            )
        ]

        # Pairwise guards
        self.pair_guards: list[tuple[str, IncestGuard | GenerationGapGuard]] = [
            ("incest", _default_incest_guard),
            (
                "generation_gap",
                lambda a, b, pop: _default_generation_gap_guard(
                    a, b, pop, max_gap=self.max_generation_gap
                ),
            ),
        ]

        # Population-level guards
        self.population_guards: list[DiversityGuard] = [
            lambda pop, pop_dict: _default_diversity_guard(
                pop,
                pop_dict,
                min_unique_founders=self.min_unique_founders,
                min_heterozygosity=self.min_heterozygosity,
            )
        ]

    # ── public API ──────────────────────────────────────────────────

    def check_pair(
        self,
        a: LineageRecord,
        b: LineageRecord,
        population: Optional[dict[int, LineageRecord]] = None,
    ) -> list[LineageViolation]:
        """Run all pairwise guards on the mating pair *(a, b)*.

        Returns a list of every violation found (empty list = clean).
        """
        pop = population or {}
        violations: list[LineageViolation] = []
        for _name, guard in self.pair_guards:
            v = guard(a, b, pop)
            if v is not None:
                violations.append(v)
        return violations

    def check_agent(
        self,
        agent: LineageRecord,
    ) -> list[LineageViolation]:
        """Run all individual-agent guards.

        Currently only mutation-rate guards.
        """
        violations: list[LineageViolation] = []
        for guard in self.mutation_guards:
            v = guard(agent)
            if v is not None:
                violations.append(v)
        return violations

    def check_population(
        self,
        population: list[LineageRecord],
    ) -> list[LineageViolation]:
        """Run all population-level guards.

        Returns a list of every violation found.
        """
        pop_dict = {r.agent_id: r for r in population}
        violations: list[LineageViolation] = []
        for guard in self.population_guards:
            violations.extend(guard(population, pop_dict))
        return violations

    def check_all(
        self,
        population: list[LineageRecord],
    ) -> list[LineageViolation]:
        """Run **all** guards (pairwise + individual + population).

        Pairwise checks are run for every unordered pair of agents that
        are both in ``SURVIVE`` or ``BREED`` state (or simply every pair
        if no state information is available).  This is O(n²) — use
        :meth:`check_population` for large fleets if you only need
        population-level stats.
        """
        pop_dict = {r.agent_id: r for r in population}
        violations: list[LineageViolation] = []

        # Individual
        for rec in population:
            violations.extend(self.check_agent(rec))

        # Pairwise — every unordered pair
        n = len(population)
        for i in range(n):
            for j in range(i + 1, n):
                violations.extend(
                    self.check_pair(population[i], population[j], pop_dict)
                )

        # Population-level
        violations.extend(self.check_population(population))

        return violations

    def is_healthy(
        self,
        population: list[LineageRecord],
    ) -> bool:
        """True iff no FATAL or ERROR violations are found."""
        violations = self.check_all(population)
        for v in violations:
            if v.severity in (ViolationSeverity.FATAL, ViolationSeverity.ERROR):
                return False
        return True

    def summary(
        self,
        population: list[LineageRecord],
    ) -> dict[str, Any]:
        """Human-readable summary dict.

        Returns::

            {
                "population_size": int,
                "violations": list[LineageViolation],
                "counts_by_severity": dict[str, int],
                "counts_by_kind": dict[str, int],
                "healthy": bool,
            }
        """
        violations = self.check_all(population)
        counts_by_severity: dict[str, int] = {}
        counts_by_kind: dict[str, int] = {}
        for v in violations:
            sev = v.severity.name
            counts_by_severity[sev] = counts_by_severity.get(sev, 0) + 1
            counts_by_kind[v.kind] = counts_by_kind.get(v.kind, 0) + 1

        return {
            "population_size": len(population),
            "violations": violations,
            "counts_by_severity": counts_by_severity,
            "counts_by_kind": counts_by_kind,
            "healthy": self.is_healthy(population),
        }

    def __repr__(self) -> str:
        return (
            f"LineageSanityChecker("
            f"max_generation_gap={self.max_generation_gap}, "
            f"mutation_bounds=[{self.mutation_min}, {self.mutation_max}], "
            f"min_founders={self.min_unique_founders}, "
            f"min_het={self.min_heterozygosity})"
        )
