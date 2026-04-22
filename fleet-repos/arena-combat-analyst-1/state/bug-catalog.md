# Bug Catalog — Self-Play Arena

## Bug 1: Curriculum Stuck at Stage 1

**Lines:** 368-384 (`_check_promotion`), 386-388 (`get_stage`), 486 (`/register`)

**Symptom:** Every agent reports `"stage": 1` forever, even after dozens of wins.

**Root Cause:** The `_check_promotion` method uses `len(history) < 5` as a guard, but `history` is a `defaultdict(list)` that is only populated via `record_result`. After a server restart, all history is lost because `AdaptiveCurriculum` state is **never persisted to disk**. Additionally, the `/register` endpoint (line 486) calls `curriculum.get_stage(name)`, which mutates the `agent_stage` defaultdict but does not create a history entry. The agent appears in `to_dict()` output with stage 1, but no matches have been played.

However, the **primary** issue is more subtle: `_check_promotion` never demotes, and the win-rate window is fixed at 5. If an agent goes on a losing streak after promotion, it stays at the higher stage forever. But the reported symptom is "stuck at Stage 1", which points to the **persistence gap**: on every server restart, `agent_stage` and `agent_history` reset to empty `defaultdict`s. Since the Arena is a long-running HTTP server that may restart frequently, agents never accumulate enough in-memory history to promote.

**Proposed Diff:**

```python
# Add save/load for curriculum state (around line 355, after DATA_DIR setup)
CURRICULUM_FILE = DATA_DIR / "curriculum.json"

# In AdaptiveCurriculum.__init__ (line 368)
    def __init__(self):
        self.agent_stage = defaultdict(lambda: 1)
        self.agent_history = defaultdict(list)
        self._load()

    def _save(self):
        with open(CURRICULUM_FILE, "w") as f:
            json.dump({
                "agent_stage": dict(self.agent_stage),
                "agent_history": {k: v[-50:] for k, v in self.agent_history.items()}
            }, f)

    def _load(self):
        if CURRICULUM_FILE.exists():
            with open(CURRICULUM_FILE) as f:
                data = json.load(f)
                for name, stage in data.get("agent_stage", {}).items():
                    self.agent_stage[name] = stage
                for name, hist in data.get("agent_history", {}).items():
                    self.agent_history[name] = hist

    def record_result(self, agent_name, won):
        self.agent_history[agent_name].append(won)
        self.agent_history[agent_name] = self.agent_history[agent_name][-20:]
        self._check_promotion(agent_name)
        self._save()
```

---

## Bug 2: Archetypes Always "Unknown"

**Lines:** 290-293 (`classify` empty guard), ~400 (`Match.to_dict` archetype call), 509-510 (`/match_detail` actions parsing), 540-545 (`/match` no actions passed)

**Symptom:** Every match shows `"player_a_archetype": "Unknown"` and `"player_b_archetype": "Unknown"`.

**Root Cause:** Two paths lead to "Unknown":

1. **The quick `/match` endpoint** (lines 540-545) creates a `Match` without passing `player_a_actions` or `player_b_actions`:
   ```python
   match = Match(pa, pb, game, winner=winner, reward_a=reward, reward_b=reward_b)
   ```
   These default to `None`, which `Match.to_dict()` converts to `[]`, triggering the `if not actions: return "Unknown"` guard in `classify`.

2. **The `/match_detail` endpoint** (lines 509-510) parses actions from query params:
   ```python
   actions_a = params.get("actions_a", [""])[0].split(",") if params.get("actions_a") else []
   ```
   When `actions_a` is missing, this correctly yields `[]` → "Unknown". When it is present but empty (`""`), it yields `[""]` — `total=1`, all keyword counts are `0`, and none of the ratio thresholds are met. The code falls through to `else: archetype = "Social Mimic"`. But most callers simply omit the parameter, so Unknown dominates.

**Proposed Diff:**

Fix `/match` to at least infer archetypes from available data, and improve the empty-actions fallback:

```python
# In /match (around line 540):
# Pass minimal action lists or skip archetype computation entirely
# Better: store a placeholder that signals "quick match, no action log"
match = Match(pa, pb, game, winner=winner, reward_a=reward, reward_b=reward_b)
# Add a flag so to_dict() knows not to re-classify
match.quick = True

# In Match.to_dict (around line 435):
def to_dict(self):
    # ...
    if getattr(self, 'quick', False):
        arch_a = arch_b = "QuickMatch"
    else:
        arch_a = archetypes.classify(self.player_a, self.player_a_actions)
        arch_b = archetypes.classify(self.player_b, self.player_b_actions)
    return {
        # ...
        "player_a_archetype": arch_a,
        "player_b_archetype": arch_b,
    }

# In classify (around line 290):
# Filter out empty strings from the actions list
actions = [a for a in actions if a.strip()]
if not actions:
    return "Unknown"
```

---

## Bug 3: Metrics Always Zero

**Lines:** ~330 (`RewardFunction.compute` metric weights), 500-545 (`/match` hardcoded metrics), 415-425 (`Match.__init__` defaults)

**Symptom:** `rooms_explored=0`, `insight_words=0`, `steps_taken=20`, `novel_strategy=False` in every match record. The metric-based reward components are negligible (≈0) compared to the win/loss component.

**Root Cause:** The quick `/match` endpoint computes reward with hardcoded constants (`1, 100, 20, False`) but then creates a `Match` object without passing those values:

```python
# Line ~535-545
won = winner == "a"
reward = reward_fn.compute(won, 1, 100, 20, False)   # hardcoded
reward_b = reward_fn.compute(not won, 1, 100, 20, False)
match = Match(pa, pb, game, winner=winner, reward_a=reward, reward_b=reward_b)
# rooms_explored defaults to 0, insight_words defaults to 0
```

So the match is saved with `rooms_explored=0` and `insight_words=0` even though the reward was computed with `1` and `100`. When replaying or analyzing, the metrics appear zero.

Additionally, the default weights in `RewardFunction` (line ~330) make metric contributions tiny:
- `exploration`: 0.1 × 0.1 = 0.01
- `insight_quality`: 0.5 × 0.2 = 0.10
- `efficiency`: 0.01 × 0.8 = 0.008
- `novelty`: 0.3 × 0 = 0

Compared to `win_loss: 1.0 × ±1 = ±1.0`, the metric components are effectively lost in the noise.

**Proposed Diff:**

```python
# In /match (around line 540):
# Compute metrics from actual query params, with real defaults
rooms = int(params.get("rooms", ["1"])[0])
words = int(params.get("insight_words", ["0"])[0])
steps = int(params.get("steps", ["20"])[0])
novel = params.get("novel", ["false"])[0].lower() == "true"

won = winner == "a"
reward = reward_fn.compute(won, rooms, words, steps, novel)
reward_b = reward_fn.compute(not won, rooms, words, steps, novel)

match = Match(pa, pb, game, winner=winner, reward_a=reward, reward_b=reward_b,
              rooms_explored=rooms, insight_words=words, steps_taken=steps,
              novel_strategy=novel)
```

And optionally raise metric weights so they matter:

```python
# In RewardFunction (around line 327):
DEFAULT_WEIGHTS = {
    "win_loss": 1.0,
    "exploration": 0.5,      # was 0.1
    "insight_quality": 1.0,  # was 0.5
    "efficiency": 0.5,       # was 0.01
    "novelty": 1.0,          # was 0.3
}
```

---

## Summary Table

| Bug | File Lines | Symptom | Root Cause |
|-----|-----------|---------|------------|
| Curriculum stuck | 368-384, 486 | Always stage 1 | No persistence; state lost on restart |
| Archetypes Unknown | 290-293, 400, 509-545 | All archetypes "Unknown" | `/match` passes no actions; empty list triggers guard |
| Metrics zero | ~330, 500-545 | `rooms=0`, `words=0` | Quick match hardcodes metrics but doesn't store them in `Match` |
