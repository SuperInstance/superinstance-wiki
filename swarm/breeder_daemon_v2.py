"""BreederDaemonV2 — lifecycle-orchestrated auto-breeder with FLUX gating.

Wires together:
    - AgentLifecycleFSMv2 (per-agent state machine)
    - JEPAGrid (room activity / weights)
    - TournamentRound (selection)
    - ThermalBudget (slot management)
    - FluxGatingChecker (Path A constraint library)

Path A integration
------------------
FLUX is treated as a constraint library, not a VM.  The daemon calls
``flux_checker.check_candidate()`` before spawning children,
``score_for_breeding()`` as a tournament tiebreak, and
``check_batch()`` after each grid tick on the top-k rooms.
"""

from __future__ import annotations

__all__ = ["BreederDaemonV2", "AutoBreederV2"]

import logging
import math
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

from nerve.room_grid import JEPAGrid
from swarm.breeder_fsm_v2 import AgentLifecycleFSMv2, LifecycleState
from swarm.flux_gating import (
    FluxGatingChecker,
    FluxGatingConfig,
    GatingResult,
    PythonFluxFallback,
    ViolationSeverity,
)
from swarm.thermal import DeviceType, ThermalBudget
from swarm.tournament import AgentScore, TournamentRound, breed

logger = logging.getLogger(__name__)


@dataclass
class BreedRecord:
    """Log entry for a single breed cycle."""

    child_id: str
    parent_ids: tuple[str, ...]
    room_id: int
    tick: int
    flux_passed: bool
    flux_score: float
    child_config: Optional[dict] = None

    def __repr__(self) -> str:
        return (
            f"BreedRecord(child={self.child_id!r}, "
            f"room={self.room_id}, tick={self.tick}, flux={self.flux_passed})"
        )


class BreederDaemonV2:
    """Orchestrates breeding with FLUX constraint gating (Path A).

    Args:
        grid: JEPAGrid instance.
        thermal: ThermalBudget instance.
        interval: Seconds between auto-breed cycles.
        cold_threshold: Activity threshold below which a room is "cold".
        n_winners: How many tournament winners to breed from.
        device: Default compute device for new agents.
        flux_config: Optional FLUX gating configuration.  If provided,
            a ``PythonFluxFallback`` checker is auto-created.
    """

    def __init__(
        self,
        grid: JEPAGrid,
        thermal: ThermalBudget,
        interval: int = 10,
        cold_threshold: int = 3,
        n_winners: int = 3,
        device: DeviceType = DeviceType.GPU,
        flux_config: Optional[FluxGatingConfig] = None,
    ) -> None:
        self.grid = grid
        self.thermal = thermal
        self.interval = interval
        self.cold_threshold = cold_threshold
        self.n_winners = n_winners
        self.device = device

        # v2 FSM registry: agent_id -> AgentLifecycleFSMv2
        self._fsm_registry: dict[str, AgentLifecycleFSMv2] = {}

        # FLUX gating
        self._flux_config = flux_config
        self._flux_checker: Optional[FluxGatingChecker] = None
        if flux_config is not None:
            self._flux_checker = PythonFluxFallback(flux_config)

        # Logging / stats
        self._breed_log: list[BreedRecord] = []
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._tick_count = 0

    # ── public API ──────────────────────────────────────────

    def attach_flux_gating(self, checker: FluxGatingChecker) -> None:
        """Attach (or replace) the FLUX constraint checker.

        This is the primary integration hook for Path A.  The checker
        can be ``PythonFluxFallback`` or a future Rust FFI wrapper.
        """
        self._flux_checker = checker
        logger.info("FLUX gating attached: %s", type(checker).__name__)

    @property
    def flux_checker(self) -> Optional[FluxGatingChecker]:
        return self._flux_checker

    def run_tick(self, x: Optional[np.ndarray] = None) -> dict[str, Any]:
        """Run one grid tick + FLUX batch check on top-k rooms.

        Args:
            x: Optional input stimulus for the grid.

        Returns:
            Dict with ``grid_result``, ``flux_batch``, and ``tick``.
        """
        self._tick_count += 1
        tick = self._tick_count

        # 1. Grid tick
        grid_result = self.grid.tick(x if x is not None else np.random.randn(64))

        # 2. FLUX batch check on top-k rooms
        flux_batch: list[GatingResult] = []
        if self._flux_checker is not None:
            topk = self.grid.top(k=max(20, self.n_winners * 2))
            candidates = []
            for room_id, activity in topk:
                # Build a mutation plan from current room state
                plan = self._build_mutation_plan(room_id, activity)
                candidates.append((room_id, plan))
            flux_batch = self._flux_checker.check_batch(candidates)

        return {
            "tick": tick,
            "grid_result": grid_result,
            "flux_batch": flux_batch,
        }

    def tournament_select(
        self,
        population: list[AgentScore],
    ) -> list[AgentScore]:
        """Run tournament and return ranked winners.

        If FLUX gating is active, ``score_for_breeding`` is used as a
        tiebreak when two agents have the same win count.
        """
        tournament = TournamentRound(population)
        ranked = tournament.run()

        if self._flux_checker is None:
            # No FLUX tiebreak — return raw tournament order
            return [r.scores for r in ranked[: self.n_winners] if r.scores is not None]

        # --- FLUX tiebreak ---
        # Re-rank by (wins, flux_score) instead of just wins
        scored: list[tuple[AgentScore, float]] = []
        for result in ranked:
            if result.scores is None:
                continue
            agent_id = result.scores.agent_id
            room_idx = self._agent_id_to_room(agent_id)
            room_vector = self._get_room_vector(room_idx)
            room_meta = {
                "chaos": float(self.grid.chaos[room_idx]) if room_idx is not None else 0.0,
                "activity": result.scores.product,
            }
            flux_score = self._flux_checker.score_for_breeding(room_vector, room_meta)
            scored.append((result.scores, flux_score))

        # Sort by flux_score descending (higher = better)
        scored.sort(key=lambda t: t[1], reverse=True)
        return [s for s, _ in scored[: self.n_winners]]

    def breed_cycle(
        self,
        n_winners: Optional[int] = None,
    ) -> list[tuple[int, str]]:
        """Run one full breeding cycle with FLUX gating.

        1. Find cold rooms.
        2. Score hot rooms and run tournament.
        3. **FLUX check** each winner before breeding.
        4. Create children from FLUX-approved winners.
        5. Rebirth cold rooms.
        6. Respect thermal budget.

        Returns:
            List of ``(reborn_room_id, child_id)`` tuples.
        """
        n_winners = n_winners or self.n_winners

        cold_rooms = self.grid.cold(thresh=self.cold_threshold)
        if not cold_rooms:
            return []

        # Build scores for hot rooms
        hot_rooms = self.grid.top(k=max(20, n_winners * 2))
        if not hot_rooms:
            return []

        max_activity = max(a for _, a in hot_rooms) or 1.0
        population = [
            AgentScore(
                agent_id=f"room_{rid}",
                ethos=activity / max_activity,
                pathos=activity / max_activity,
                logos=activity / max_activity,
            )
            for rid, activity in hot_rooms
        ]

        # Tournament with optional FLUX tiebreak
        winners = self.tournament_select(population)
        if not winners:
            return []

        # --- FLUX gating: check each winner before breeding ---
        approved_winners: list[AgentScore] = []
        for winner in winners:
            room_idx = self._agent_id_to_room(winner.agent_id)
            if room_idx is None:
                continue
            mutation_plan = self._build_mutation_plan(room_idx, winner.product)
            if self._flux_checker is not None:
                result = self._flux_checker.check_candidate(room_idx, mutation_plan)
                if not result.passed:
                    logger.warning(
                        "FLUX blocked winner %s (score=%.3f, violations=%d)",
                        winner.agent_id,
                        result.score,
                        len(result.violations),
                    )
                    continue
                approved_winners.append(winner)
            else:
                approved_winners.append(winner)

        if not approved_winners:
            logger.info("All tournament winners blocked by FLUX gating.")
            return []

        # Breed children from approved winners
        num_children = min(len(cold_rooms), len(approved_winners))
        children = breed(approved_winners, num_children=num_children)

        # Rebirth cold rooms
        results: list[tuple[int, str]] = []
        for idx, child in enumerate(children):
            if idx >= len(cold_rooms):
                break

            room_id = cold_rooms[idx]
            child_id = child["id"]
            parent_a = child.get("parent_a")
            parent_b = child.get("parent_b")
            parent_ids = tuple(p for p in (parent_a, parent_b) if p is not None)

            # Find parent room for weight cloning
            parent_room = None
            for pid in parent_ids:
                pr = self._agent_id_to_room(pid)
                if pr is not None:
                    parent_room = pr
                    break

            # Thermal budget check
            if not self.thermal.can_spawn(self.device):
                ok = self.thermal.parent_sacrifice_before_spawn(
                    parent_id=parent_ids[0] if parent_ids else "",
                    child_device=self.device,
                )
                if not ok:
                    logger.warning("No thermal headroom for room %d, skipping", room_id)
                    continue

            # Clone parent weights if we found one
            if parent_room is not None:
                self.grid.breed(parent_room, room_id)
            else:
                self.grid.rebirth(room_id)

            # Allocate child in thermal budget
            self.thermal.allocate(child_id, self.device)

            # Register FSM for the child
            fsm = AgentLifecycleFSMv2(agent_id=room_id, initial_state=LifecycleState.EGG)
            with self._lock:
                self._fsm_registry[child_id] = fsm

            # Log
            flux_score = 1.0
            flux_passed = True
            if self._flux_checker is not None and parent_room is not None:
                mp = self._build_mutation_plan(parent_room, 0.0)
                gr = self._flux_checker.check_candidate(parent_room, mp)
                flux_score = gr.score
                flux_passed = gr.passed

            record = BreedRecord(
                child_id=child_id,
                parent_ids=parent_ids,
                room_id=room_id,
                tick=self._tick_count,
                flux_passed=flux_passed,
                flux_score=flux_score,
                child_config=child,
            )
            with self._lock:
                self._breed_log.append(record)

            results.append((room_id, child_id))
            logger.info(
                "Bred child %s into room %d from parent(s) %s (tick %d)",
                child_id,
                room_id,
                parent_ids,
                self._tick_count,
            )

        return results

    def start(self) -> None:
        """Start the background daemon thread."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop,
            name="breeder-daemon-v2",
            daemon=True,
        )
        self._thread.start()
        logger.info("BreederDaemonV2 started (interval=%d)", self.interval)

    def stop(self) -> None:
        """Stop the daemon thread."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None
        logger.info("BreederDaemonV2 stopped")

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def breed_log(self) -> list[BreedRecord]:
        with self._lock:
            return list(self._breed_log)

    @property
    def fsm_registry(self) -> dict[str, AgentLifecycleFSMv2]:
        with self._lock:
            return dict(self._fsm_registry)

    # ── internals ───────────────────────────────────────────

    def _build_mutation_plan(
        self,
        room_id: int,
        activity: float,
    ) -> dict[str, Any]:
        """Build a mutation plan dict for FLUX checking."""
        # Compute weight norm from the room's current weights
        w_norm = 0.0
        for key in ("w1", "w2", "w3"):
            arr = self.grid.w[key][room_id]
            w_norm += float(np.linalg.norm(arr)) ** 2
        w_norm = math.sqrt(w_norm)

        return {
            "candidate_id": f"room_{room_id}",
            "weights": w_norm,
            "chaos": float(self.grid.chaos[room_id]),
            "thermal_headroom": self.thermal.thermal_headroom(),
            "activity": activity,
            "room_id": room_id,
        }

    def _agent_id_to_room(self, agent_id: str) -> Optional[int]:
        """Parse 'room_N' → N."""
        if agent_id.startswith("room_"):
            try:
                return int(agent_id.split("_")[1])
            except (IndexError, ValueError):
                return None
        return None

    def _get_room_vector(self, room_idx: Optional[int]) -> np.ndarray:
        """Return a flat vector representing the room's weights."""
        if room_idx is None:
            return np.zeros(1, dtype=np.float32)
        pieces = []
        for key in ("w1", "w2", "w3"):
            pieces.append(self.grid.w[key][room_idx].ravel())
        return np.concatenate(pieces)

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.run_tick()
                self.breed_cycle()
            except Exception:
                logger.exception("BreederDaemonV2 cycle failed")
            self._stop_event.wait(self.interval)


# ── backward-compatible alias ─────────────────────────────

AutoBreederV2 = BreederDaemonV2
