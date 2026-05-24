#!/usr/bin/env python3
"""Data Scientist beta test: Using BreederDaemonV2 + RoomGrid as hyperparameter search."""
import sys
import tempfile
import numpy as np

# Mock cocapn_traps before importing breeder_daemon_v2
import types
_mock_cocapn_traps = types.ModuleType("cocapn_traps")
_mock_cocapn_traps_types = types.ModuleType("cocapn_traps.traps")
_mock_diversity_trap = types.ModuleType("cocapn_traps.traps.diversity_collapse_trap")

class _MockDiversityAlert:
    def __init__(self, level, recommended_action):
        self.level = level
        self.recommended_action = recommended_action

class _MockDiversityCollapseTrap:
    def __init__(self, *args, **kwargs):
        self._history = []
    def record(self, diversity_score):
        self._history.append(diversity_score)
    def check(self):
        if len(self._history) >= 3:
            return _MockDiversityAlert("CRITICAL", "CROSS_SHIP_INJECTION")
        if len(self._history) >= 2:
            return _MockDiversityAlert("WARNING", "EMERGENCY_MUTATE")
        return None

_mock_diversity_trap.DiversityCollapseTrap = _MockDiversityCollapseTrap
_mock_diversity_trap.DiversityAlert = _MockDiversityAlert
sys.modules["cocapn_traps"] = _mock_cocapn_traps
sys.modules["cocapn_traps.traps"] = _mock_cocapn_traps_types
sys.modules["cocapn_traps.traps.diversity_collapse_trap"] = _mock_diversity_trap

sys.path.insert(0, "/root/.openclaw/workspace/sunset-ecosystem")

from nerve.room_grid import RoomGrid
from swarm.breeder_daemon_v2 import BreederDaemonV2, DiversityConfig, ThermalConfig
from swarm.thermal import ThermalBudget, DeviceType


def evaluate_hyperparams(room_id, grid):
    """Mock fitness: sum of room weights = 'model performance'."""
    w = grid.w["w1"][room_id]
    score = float(np.mean(np.abs(w)))
    return score


def main():
    print("=" * 60)
    print("DATA SCIENTIST BETA: Hyperparameter Search via Breeder")
    print("=" * 60)

    # Setup
    grid = RoomGrid(n=20)
    thermal = ThermalBudget({DeviceType.GPU: 10, DeviceType.CPU: 20})
    fd, wal_path = tempfile.mkstemp(suffix=".sqlite")
    import os
    os.close(fd)

    daemon = BreederDaemonV2(
        grid=grid,
        thermal=thermal,
        vector_table=None,
        diversity=DiversityConfig(),
        thermal_cfg=ThermalConfig(max_agents=15, hysteresis_ticks=1),
        wal_path=wal_path,
        tick_interval=1.0,
        use_hdc=False,
    )

    # Seed 5 initial random models
    print("\n[1] Seeding 5 random models...")
    for i in range(5):
        grid.w["w1"][i] = np.random.randn(64, 32).astype(np.float32) * 0.1
        grid.activity[i] = 5

    daemon.start()
    
    # Seed agents AFTER start() so WAL replay doesn't overwrite
    from swarm.lifecycle_fsm import AgentLifecycleFSM, LifecycleState
    for i in range(5):
        daemon._fsm[i] = AgentLifecycleFSM(agent_id=i, initial_state=LifecycleState.SURVIVE, strict=False)
        daemon._room_allocations[i] = i
        daemon.thermal.spawn(f"agent_{i}", DeviceType.GPU)

    # Evaluate initial population
    initial_scores = [evaluate_hyperparams(i, grid) for i in range(5)]
    print(f"    Initial fitness: mean={np.mean(initial_scores):.4f} max={np.max(initial_scores):.4f}")

    # Run 3 breeding generations
    print("\n[2] Running 3 breeding generations...")
    daemon.start()
    for gen in range(3):
        # Get current agents and their fitness
        current_agents = list(daemon._fsm.keys())
        scores = []
        for aid in current_agents:
            room_id = daemon._find_room_for_agent(aid)
            if room_id is not None and room_id < grid.n:
                scores.append((aid, evaluate_hyperparams(room_id, grid)))
        scores.sort(key=lambda x: x[1], reverse=True)
        if len(scores) >= 2:
            parent_a, _ = scores[0]
            parent_b, _ = scores[1]
            daemon.queue_breed(parent_a=parent_a, parent_b=parent_b, priority=10)
            daemon.step()
            print(f"    Gen {gen+1}: bred parents {parent_a},{parent_b} → new agent")

    daemon.stop()

    # Evaluate final population
    final_scores = []
    for aid in daemon._fsm:
        room_id = daemon._find_room_for_agent(aid)
        if room_id is not None and room_id < grid.n:
            final_scores.append(evaluate_hyperparams(room_id, grid))
    if final_scores:
        print(f"\n[3] Final fitness: mean={np.mean(final_scores):.4f} max={np.max(final_scores):.4f}")
        improvement = (np.mean(final_scores) - np.mean(initial_scores)) / (np.mean(initial_scores) + 1e-9)
        print(f"    Improvement: {improvement*100:+.1f}%")

    print("\n✅ Script completed without crashes")
    os.unlink(wal_path)


if __name__ == "__main__":
    main()
