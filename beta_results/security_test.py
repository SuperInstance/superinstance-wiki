"""Security test: provenance for ML model lineage."""
import sys, time, hashlib, importlib.util

# Load swarm.lineage_checker from workspace root (LineageRecord API)
_spec = importlib.util.spec_from_file_location("swarm.lineage_checker", "/root/.openclaw/workspace/swarm/lineage_checker.py")
swarm_lc = importlib.util.module_from_spec(_spec)
sys.modules["swarm.lineage_checker"] = swarm_lc
_spec.loader.exec_module(swarm_lc)
LineageRecord = swarm_lc.LineageRecord
MutationProfile = swarm_lc.MutationProfile
LineageSanityChecker = swarm_lc.LineageSanityChecker

sys.path.insert(0, "/root/.openclaw/workspace/sunset-ecosystem")
from logos.signed_wal import SignedWAL, WALEntry
from nexus.distributed_consensus import HolonomyConsensus

# ── 1. Create 3 founder agents ──────────────────────────────────
founders = [
    LineageRecord(agent_id=0, generation=0, mutation_profile=MutationProfile(rate=0.05)),
    LineageRecord(agent_id=1, generation=0, mutation_profile=MutationProfile(rate=0.03)),
    LineageRecord(agent_id=2, generation=0, mutation_profile=MutationProfile(rate=0.04)),
]

# ── 2. Breed 2 children ─────────────────────────────────────────
children = [
    LineageRecord(agent_id=3, generation=1, parent_ids=(0, 1),
                  mutation_profile=MutationProfile(rate=0.06)),
    LineageRecord(agent_id=4, generation=1, parent_ids=(1, 2),
                  mutation_profile=MutationProfile(rate=0.07)),
]

population = founders + children

# ── 3. Record births in SignedWAL ───────────────────────────────
wal = SignedWAL(algorithm="hmac-sha256")
for a in founders:
    wal.append(WALEntry(timestamp=time.time(), agent_id=a.agent_id,
                        operation="spawn", vector_hash=hashlib.sha256(str(a.agent_id).encode()).hexdigest()[:16],
                        parent_ids=list(a.parent_ids), generation=a.generation))
for c in children:
    wal.append(WALEntry(timestamp=time.time(), agent_id=c.agent_id,
                        operation="breed", vector_hash=hashlib.sha256(str(c.agent_id).encode()).hexdigest()[:16],
                        parent_ids=list(c.parent_ids), generation=c.generation))

# ── 4. Run LineageSanityChecker ─────────────────────────────────
checker = LineageSanityChecker()
summary = checker.summary(population)
print("=== LineageSanityChecker ===")
print(f"Population: {summary['population_size']}, Healthy: {summary['healthy']}")
for v in summary["violations"]:
    print(f"  {v.severity.name}: {v.kind} — {v.message}")

# ── 5. Run ONE HolonomyConsensus round ──────────────────────────
consensus = HolonomyConsensus(node_id="node-0", peers=["node-1", "node-2"])
prop = consensus.propose_state_change("register_lineage", {"agents": [a.agent_id for a in population]})
consensus.vote_on_proposal(prop.digest(), approve=True)
result = consensus.commit_if_quorum(prop.digest())
print("\n=== HolonomyConsensus ===")
print(f"Proposal: {prop.operation} | Committed: {result.committed} | Votes: {result.votes_for}/{result.quorum_size}")

# ── 6. Verify WAL chain integrity ───────────────────────────────
ok, idx = wal.verify_chain()
print(f"\n=== SignedWAL ===")
print(f"Chain valid: {ok}, entries: {len(wal.entries)}")
if not ok:
    print(f"  First invalid at index {idx}")
