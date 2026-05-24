#!/usr/bin/env python3
"""Game Dev beta test: Using RoomGrid + Plato observer as NPC population manager."""
import sys
import numpy as np
import types

# ── Mock plato_core ──
_mock_plato = types.ModuleType("plato_core")
_mock_plato_types = types.ModuleType("plato_core.types")

class _MockLamportClock:
    def __init__(self, node_id=0):
        self._tick = 0; self.node_id = node_id
    def tick(self):
        self._tick += 1
        return self._tick

class _MockTileLifecycle:
    ACTIVE = "active"
    SUPERSEDED = "superseded"

class _MockTileType:
    METRICS = "metrics"
    EVALUATION = "evaluation"

class _MockLifecycleEvent:
    pass

def _mock_content_hash(data):
    import hashlib
    return hashlib.sha256(str(data).encode()).hexdigest()[:16]

class _MockTrainingTile:
    def __init__(self, tile_id, room, tile_type, state, lamport, name, description, content_hash, base_model, source_room, parent_tile=""):
        self.tile_id = tile_id; self.room = room; self.tile_type = tile_type; self.state = state
        self.lamport = lamport; self.name = name; self.description = description
        self.content_hash = content_hash; self.base_model = base_model; self.source_room = source_room
        self.parent_tile = parent_tile; self._payload = {}
    def set_payload(self, payload):
        self._payload = payload

class _MockPlatoBridge:
    def __init__(self, room):
        self.room = room; self._tiles = []; self._clock = _MockLamportClock()
    def submit(self, tile):
        self._tiles.append(tile)
        return tile.tile_id
    def get_tile(self, tile_id):
        for t in self._tiles:
            if t.tile_id == tile_id: return t
        return None
    def all_tiles(self):
        return self._tiles

_mock_plato_types.LamportClock = _MockLamportClock
_mock_plato_types.TrainingTile = _MockTrainingTile
_mock_plato_types.TileType = _MockTileType
_mock_plato_types.TileLifecycle = _MockTileLifecycle
_mock_plato_types.LifecycleEvent = _MockLifecycleEvent
_mock_plato_types.content_hash = _mock_content_hash
_mock_plato.types = _mock_plato_types

sys.modules["plato_core"] = _mock_plato
sys.modules["plato_core.types"] = _mock_plato_types

sys.path.insert(0, "/root/.openclaw/workspace/sunset-ecosystem")

from nerve.room_grid import RoomGrid
from sunset.plato_bridge import PlatoBridge
from sunset.roomgrid_plato_observer import RoomGridPlatoObserver


def main():
    print("=" * 60)
    print("GAME DEV BETA: NPC Population Manager")
    print("=" * 60)

    grid = RoomGrid(n=50)
    bridge = PlatoBridge(room="npc-world")
    obs = RoomGridPlatoObserver(bridge=bridge)
    grid.attach_plato_observer(obs)

    print("\n[1] Spawning 50 NPCs (rooms) with random personalities...")
    for i in range(50):
        grid.w["w1"][i] = np.random.randn(64, 32).astype(np.float32) * 0.1
        grid.activity[i] = np.random.randint(1, 10)

    print("\n[2] Running 10 game ticks (NPCs competing for resources)...")
    for tick in range(10):
        signal = np.random.randn(64).astype(np.float32)
        grid.tick(signal)

    stats = grid.stats
    print(f"\n[3] Population stats after 10 ticks:")
    print(f"    Active NPCs: {stats['active']}/{stats['rooms']} ({stats['pct']})")
    print(f"    Diversity: {stats.get('diversity', 'N/A')}")

    tiles = bridge.all_tiles()
    print(f"\n[4] Observer tiles written: {len(tiles)}")
    diversity_tiles = [t for t in tiles if "diversity" in t.tile_id]
    occupancy_tiles = [t for t in tiles if "occupancy" in t.tile_id]
    print(f"    Diversity tiles: {len(diversity_tiles)}")
    print(f"    Occupancy tiles: {len(occupancy_tiles)}")

    print("\n✅ Script completed without crashes")
    print("    NPCs spawned, competed, and left records in Plato observer.")


if __name__ == "__main__":
    main()
