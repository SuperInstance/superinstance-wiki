# 🎮 Developer Diary: Exploring SuperInstance's Luau Packages

**Author:** Alex (Roblox game dev, 3 years Luau experience)  
**Date:** June 1, 2026  
**Context:** Never heard of SuperInstance before today. Stumbled onto these packages while looking for tools for my next game. Here's my honest take after reading every line of source code.

---

## Day 1: First Impressions

Okay so I found this org called SuperInstance on GitHub with 11 Luau packages. At first glance it looks like someone built an entire game engine in pure Luau — spatial indexing, biome generation, quest systems, crafting, even group theory. That's either incredibly ambitious or completely insane. Let me dig in.

The first thing I notice: **every single package is v0.1.0.** That's a yellow flag. These are all first releases. But the READMEs are genuinely good — detailed API references, code examples, even install instructions for Wally/Rojo/manual. That's more than most Roblox open source packages offer.

Let me go through them one by one.

---

## 1. luau-spatial — ⭐⭐⭐⭐⭐ (My Favorite)

**API Design: 9/10** — This feels like it was written by someone who actually builds Roblox games. `QuadTree.new(bounds)`, `grid:queryRadius(pos, radius)` — it's clean, idiomatic, and doesn't fight the language. The `Vec2` type is simple but correct.

**Documentation: 9/10** — Best README of the bunch. Full API reference table, performance comparison, use cases, install instructions. I could genuinely use this without asking anyone anything.

**Test Coverage: 8/10** — 40+ tests across Vec2, BoundingBox, QuadTree, GridHash, and SpatialHash. Good edge cases (boundary queries, empty trees, duplicate positions, tiny cell sizes). Missing: no performance/stress tests, no concurrent access tests.

**Roblox Integration: 8/10** — Pure math, no Roblox API dependencies. This is actually a strength — it works anywhere. The README correctly calls out that `workspace:GetPartBoundsInRadius` only works with BaseParts, while this works with ANY data.

**Missing Features:**
- No 3D version (only 2D/Vec2). Most Roblox games need 3D spatial queries.
- No entity update/move operation — you have to remove + re-insert, which is clunky.
- No `__tostring` on QuadTree/GridHash for debugging.
- No serialization support.

**Bugs/Issues I Found:**
- `SpatialHash.remove()` matches by position AND radius, but if you pass slightly different radius than what you inserted with, it silently fails. Should use the `entries` map (keyed by `data`) for removal instead.
- `SpatialHash.queryPotentialCollisions()` uses `tostring()` on data for dedup keys — this will collide if data is a table (gives "table 0x..."). Should use the `entries` map instead.
- `GridHash.remove()` uses exact Vec2 equality — floating point positions will break this.

**What would make me adopt it:** A 3D Octree + Vec3, and a `move(oldPos, newPos, data)` method.

---

## 2. luau-biome — ⭐⭐⭐⭐

**API Design: 8/10** — The `BiomeGenerator.new(seed):generate(w, h)` API is clean. The Whittaker diagram approach for biome selection is clever. `WorldMap:biomeAt(x, y)` is intuitive.

**Documentation: 8/10** — Good README with a biome reference table showing temperature/moisture/elevation ranges AND mathematical themes (which is... unusual but cool for an educational game).

**Test Coverage: 9/10** — 30+ tests covering Xoshiro determinism, all 10 biomes, same-seed-same-map, bounds checking, property validation. This is one of the better-tested packages.

**Roblox Integration: 7/10** — Pure Luau again, but the `--!strict` type annotations are nice. The noise generation uses pre-computed grids, which is memory-efficient. However, for large worlds, the full grid approach won't scale — a 1024×1024 map stores 3 full number grids.

**Missing Features:**
- No streaming/chunked generation — you have to generate the entire world upfront.
- No interpolation between biome cells (would cause hard edges in terrain).
- No way to regenerate a single cell or region.
- The noise grid is fixed at `256/scale + 2` which means maps larger than ~256 will have wrapping artifacts.

**Bugs/Issues:**
- `Xoshiro` implementation is a 32-bit approximation of xoshiro256**, not a true 256-bit PRNG. The state space is much smaller than claimed. Fine for games, but don't use it for anything security-related.
- `BiomeGenerator:generate()` — the noise layers use `tempSeed`, `moistSeed`, `elevSeed` from `self._rng:nextInt(1, 1000000)`. This means two BiomeGenerators with the same seed will produce the same world, but the internal noise layer seeds have only 1M possible values each, reducing effective seed space.
- `selectBiome()` — The biome selection logic is a cascade of if/else, not a true Whittaker diagram lookup. This means some biome combinations are unreachable depending on temperature/moisture/elevation overlaps. For example, `CrystalCaves` requires `elevation < 0.2 AND temp > 5 AND temp < 20 AND moisture >= 0.3 AND moisture < 0.65`, which is very narrow and might rarely appear.

**What would make me adopt it:** Chunk-based generation and a proper Perlin/Simplex noise implementation instead of value noise.

---

## 3. luau-quest — ⭐⭐⭐

**API Design: 7/10** — The `Quest.new()` + `QuestTracker` pattern works, but it feels verbose. Having to match event types to objective types manually is error-prone. The objective factories (`.BuildStructure`, `.ExploreBiome`) are nice though.

**Documentation: 7/10** — Good examples, decent API reference. But the objective types table doesn't show all the parameters each type accepts. Had to read the source to figure out `ConservationChallenge` takes `{targetError, topology}`.

**Test Coverage: 4/10** — **NO TEST FILE EXISTS.** The README mentions tests but there's no `tests/` directory. Wait, correction — there IS a `tests/run-tests.luau` but I didn't see explicit test cases in it. Let me re-check... Actually there are no tests in the test runner for quest specifically. The quest module is tested implicitly through the demo.

Actually wait, I re-read — there IS a test file but it has no tests specific to quest edge cases like: what happens when you start a quest without registering it? What about completing a quest twice? What about `ObjectiveTypes.ObserveRoom` with 0 minReadings? These are untested.

**Roblox Integration: 5/10** — The event-driven approach (`tracker:onEvent(event)`) is the right pattern for Roblox, but there's no integration with RemoteEvents, no data persistence, and no way to sync quest state between server and client.

**Missing Features:**
- No save/load (quests lost on server restart).
- No RemoteEvent integration for client UI updates.
- No quest chains or branching quests.
- `ObjectiveTypes.CollaborateWith` is defined in the enum but has no factory function — it'll error if used.
- No `TeachAgent` factory function either (wait, it IS there, but `CollaborateWith` is missing).
- No quest abandonment/cancellation.
- No time-based objectives.
- No way to display quest progress to the player.

**Bugs/Issues:**
- `ObjectiveTypes` uses `setmetatable(ObjectiveTypes, ObjectiveTypes)` — this means calling `ObjectiveTypes.NonExistentType()` will return `nil` instead of erroring. Silent failures in production.
- `QuestTracker:getStatus()` returns `{progress = (done, total)}` — that's a tuple syntax inside a table, which is NOT valid Luau. This will cause a runtime error. Should be `{progress = {done, total}}`.
- `ExploreBiome` uses `obj.visitedBiomes = {}` but checks `obj.visitedBiomes[event.biome]` — the table is never populated, so this should work, but it's using the event's biome field as a key directly, meaning string matching matters a lot.

**What would make me adopt it:** Data persistence, client sync, and fixing the `getStatus` bug.

---

## 4. luau-scheduler — ⭐⭐⭐⭐

**API Design: 9/10** — This is genuinely well-designed. `scheduleOnce`, `scheduleRecurring`, `cancel`, `tick` — it's simple, predictable, and the priority system makes sense. The `RunService.Heartbeat:Connect(function() sched:tick() end)` pattern is exactly how I'd use it.

**Documentation: 8/10** — Clear API reference, good examples. The priority table and task state table are helpful.

**Test Coverage: 9/10** — 25 tests covering one-shot, recurring, priority ordering (all 5 levels), cancellation, edge cases (empty scheduler, zero/negative delay), query methods. This is thorough.

**Roblox Integration: 9/10** — Designed for `RunService.Heartbeat`. The tick-based approach (not time-based) is correct for deterministic game logic. The `realm = "server"` in wally.toml is honest — this should only run server-side.

**Missing Features:**
- No way to get a task by name (only by ID).
- No task groups/tags for bulk operations.
- No way to pause/resume individual tasks.
- No error handling in task callbacks — a failing callback will crash the entire scheduler tick.
- No maximum tasks limit (could OOM with runaway scheduling).

**Bugs/Issues:**
- `Scheduler:tick()` collects due tasks into a list, sorts, then executes. If a recurring task schedules a NEW task during its callback, that new task won't be checked until the next tick. This is probably fine but should be documented.
- Completed tasks accumulate in `self.tasks` forever — no garbage collection. For a long-running server, this is a memory leak. Should add a `purge()` method or auto-clean completed tasks.
- The `typeof(task)` annotation in the sort comparison won't actually work in strict Luau — it should use an explicit type.

**What would make me adopt it:** Task names for lookup, error isolation in callbacks, and auto-cleanup of completed tasks.

---

## 5. luau-conservation — ⭐⭐⭐

**API Design: 6/10** — This is niche. Really niche. The functions are clear enough (`massConserved`, `energyConserved`, `noetherCheck`) but they're very specific to educational games about physics. For a regular game dev, this is confusing — what's a "conservation law" and why do I care?

**Documentation: 7/10** — The README explains Noether's theorem, which is cool, but the API feels academic. The `symmetryToQuantity` mapping table is nice.

**Test Coverage: 5/10** — Tests exist but are thin. No edge case testing for: zero inputs, negative energies, empty transform chains, unknown symmetry names.

**Roblox Integration: 4/10** — Pure math with no Roblox integration. This is really a math library pretending to be a game tool.

**Missing Features:**
- No visualization or debugging tools.
- No integration with actual Roblox physics (AssemblyLinearVelocity, etc.).
- `findViolation` only works on flat number arrays — no nested structures.
- No angular momentum conservation despite claiming it in the symmetry table.

**Bugs/Issues:**
- `energyConserved()` uses a hardcoded 5% tolerance (`math.abs(ratio - 1.0) <= 0.05`) — this should be configurable.
- `flowConserved()` has inconsistent tolerance handling: `if inSum == 0 then return outSum <= tolerance` uses absolute tolerance, but the normal case uses `tolerance * math.abs(inSum)` which is relative tolerance. These are fundamentally different error models.
- `findViolation()` checks `if sumBefore ~= 0` but doesn't handle the case where sumBefore is very close to zero (floating point issues).

**What would make me adopt it:** Honestly, I wouldn't. This is for educational games only. But if I were building one, I'd want Roblox physics integration and configurable tolerances.

---

## 6. luau-recipe — ⭐⭐⭐⭐

**API Design: 9/10** — The chainable builder pattern is excellent: `Recipe.new("sword"):input("iron", 3):output("sword", 1):biomeRequired("tundra")`. This feels like a modern Luau API. The `RecipeBook` with `craft()`, `whatCanCraft()`, `recipesUsing()` covers the main use cases.

**Documentation: 8/10** — Great examples, clear API. The biome/skill gate examples are well-chosen.

**Test Coverage: 9/10** — 25+ tests including chain recipes, multi-output, combined biome+skill gates, inventory deduction edge cases, exact material usage. This is thorough.

**Roblox Integration: 7/10** — The inventory is a plain `{ [string]: number }` table, which is fine but doesn't map to Roblox's inventory systems. You'd need an adapter layer.

**Missing Features:**
- No recipe categories or tags.
- No recipe discovery/unlocking system (you know all recipes from the start).
- No probability/random outputs (e.g., 10% chance of rare drop).
- No recipe level/mastery system (crafting 100 swords could unlock a better version).
- The `Ingredient` module exists but `Recipe` uses plain `{name, count}` tables internally — `Ingredient` is never used.

**Bugs/Issues:**
- `RecipeBook:craft()` modifies the `inventory` table IN PLACE. This is documented behavior but it's a footgun — if crafting fails partway through (shouldn't happen with current code, but still), the inventory is in an inconsistent state. Would be safer to return a new inventory or use a transaction pattern.
- `RecipeBook:register()` asserts `recipe ~= nil and type(recipe.name) == "function"` — good, but doesn't validate that `:getInputs()` and `:getOutputs()` exist.

**What would make me adopt it:** Recipe discovery, probability outputs, and actually using the `Ingredient` type consistently.

---

## 7. luau-genealogy — ⭐⭐⭐⭐

**API Design: 8/10** — This is a unique package. Entity lineage tracking with multi-parent spawning, LCA, evolutionary distance, cousin detection. It's well-structured and the method names are clear.

**Documentation: 7/10** — Good API reference, decent examples. Could use more "why would I use this" explanation. The README shows the API but not the game design patterns it enables.

**Test Coverage: 9/10** — 27 tests! That's the most of any package. Covers roots, children, multi-parent, deep lineage, LCA edge cases (unrelated roots, self, parent-child, cousins), evolutionary distance, and error cases (empty parent list).

**Roblox Integration: 6/10** — Pure data structure, no Roblox ties. Fine for what it is.

**Missing Features:**
- No entity deletion.
- No way to rename entities.
- No serialization/deserialization.
- No visualization (family tree renderer).
- `lineage()` only follows the first parent — in a multi-parent tree, you lose information.

**Bugs/Issues:**
- `areCousins()` checks if `ancestorsA[b]` exists, but `_ancestorSet()` returns IDs, not names, and `a`/`b` ARE IDs, so this is correct. However, it also checks `ancestorsB[a]` — this calls `_ancestorSet(b)` which rebuilds the ancestor set. This is O(n) per call. For repeated cousin checks, this should be cached.
- `evolutionaryDistance()` uses a stack-based DFS that searches upward. For deep trees, this is inefficient compared to memoizing depths.
- No protection against circular references (if you manually corrupt the parent pointers).

**What would make me adopt it:** Entity deletion, serialization, and caching for repeated queries.

---

## 8. luau-math — ⭐⭐⭐

**API Design: 7/10** — Three modules: Symmetry (group theory), Rhythm (music math), Sequence (Fibonacci, Pascal). The APIs are clean but... who is this for? The symmetry group module is mathematically correct but I can't imagine using `DihedralGroup:compose()` in a Roblox game.

**Documentation: 7/10** — Full API reference. Could use more practical examples of how to use symmetry groups in a game context.

**Test Coverage: 6/10** — Tests exist but I didn't see them testing edge cases like: CyclicGroup with n=1, negative inputs, Fibonacci with large n (integer overflow), Pascal with n=0.

**Roblox Integration: 5/10** — The rhythm module has the most game potential (syncing music to gameplay), but there's no actual audio playback integration. It's all math with no `Sound` or `SoundGroup` usage.

**Missing Features:**
- No matrix/vector math (which is what Roblox devs actually need).
- No quaternion support.
- No easing functions.
- No random distribution utilities.
- No noise functions (Perlin/Simplex).
- The Sequence module is very basic — Luau already has `math.sqrt`, so Golden.ratio() is just a thin wrapper.

**Bugs/Issues:**
- `Fibonacci.nth(n)` with large n will silently overflow Lua's number type (doubles max out around fib(1474)). No error or warning.
- `Golden.fibonacciSpiral()` uses `goldenAngle = 2 * math.pi / (phi * phi)` — this is actually the golden angle expressed as `2π / φ²`, which equals `2π(1 - 1/φ)` ≈ 2.3999... radians. The formula is technically correct but non-standard; most implementations use `2π(2 - φ)`.
- `DihedralGroup:compose()` — the formula for `s*r^a * s*r^b` gives `r^(b-a)`, which is correct for the standard presentation of D_n.
- `Groove.swingFactor()` — at `swingPercent = 100`, `upFraction = 0`, which means the upbeat duration is 0ms. This would cause a division by zero or infinite tempo if used to schedule notes.

**What would make me adopt it:** Matrices, vectors, easing functions, and Perlin noise. The group theory stuff is cool but not something I'd reach for.

---

## 9. luau-git-world — ⭐⭐⭐

**API Design: 7/10** — Teaching git through Roblox gameplay is a creative idea. The API maps git concepts to game actions: `saveEntity` = add, `commit` = commit, `createBranch` = branch. It works.

**Documentation: 7/10** — The game-mechanics-to-git-concepts table in the README is excellent. Makes the purpose immediately clear.

**Test Coverage: 7/10** — 14 test groups covering world creation, entities, commits, branches, fork, merge, snapshots. Decent coverage.

**Roblox Integration: 5/10** — It's a pure data structure with no actual git integration or persistence. The "merge" is basically a no-op — it just creates a commit message saying "Merged X into Y" without actually combining entity states from different branches.

**Missing Features:**
- **Merge is fake.** `merge()` just commits a message but doesn't actually combine entities from both branches. This is the biggest gap — a game teaching git should at least handle basic merge semantics.
- No conflict detection or resolution.
- No diff between commits.
- No revert/reset.
- No cherry-pick.
- Entities are shared globally across branches — `checkout()` just changes `currentBranch` but doesn't swap entity state. So entities saved on one branch are visible on all branches, which completely breaks the branch isolation concept.

**Bugs/Issues:**
- **Critical:** Branches share the same entity store. If you save an entity on branch A, switch to branch B, the entity is still there. This fundamentally breaks the git metaphor.
- `fork()` copies entities but doesn't create the branch specified in the `newBranch` parameter (it's accepted but ignored).
- `commitHistory` is a flat array across all branches. `branches` stores per-branch commit messages but NOT entity snapshots. So the actual state history is in `commitHistory` but the branch-level tracking is incomplete.
- No way to load a previous commit's state (no `git checkout <commit>`).

**What would make me adopt it:** Fix branch isolation (each branch gets its own entity snapshot), implement real merge, add diff support.

---

## 10. luau-audio — ⭐⭐⭐⭐

**API Design: 8/10** — Clean, focused module. `midiToFreq`, `majorScale`, `transpose`, `velocityToDb` — these are exactly the functions you need for music in games. No bloat.

**Documentation: 7/10** — Short but clear. The API table is complete. Could use more examples of how to use this with Roblox's `Sound` objects.

**Test Coverage: 7/10** — 15 tests covering frequency conversion, note names, intervals, scales, transpose, invert, velocity/dB conversion. Missing: negative MIDI notes, extreme values, chromatic/blues scales.

**Roblox Integration: 5/10** — Pure math again. No `Sound` object integration, no `SoundGroup` volume control, no playback scheduling. You'd have to build that layer yourself.

**Missing Features:**
- No chord generation (major, minor, 7th, etc.).
- No key detection.
- No time signature or bar tracking.
- No integration with `Sound.PlaybackSpeed` for pitch control.
- No blues, harmonic minor, melodic minor scales.
- No microtonal support.

**Bugs/Issues:**
- `midiToName()` — For negative MIDI notes, the octave calculation `math.floor(midi / 12) - 1` gives incorrect results. MIDI -1 would give "B-1" instead of the standard "C-1".
- `dbToVelocity()` — Uses `math.floor(math.clamp(v, 0, 127) + 0.5)` which rounds. This means `dbToVelocity(velocityToDb(x))` may not round-trip exactly for all values.

**What would make me adopt it:** Chord generation, `Sound` object integration, and more scale types.

---

## 11. luau-demo — ⭐⭐

**API Design: 4/10** — This is barely a demo. Nearly every line of the actual integration code is commented out. It's a skeleton that shows the *pattern* but doesn't actually wire anything together.

**Documentation: 5/10** — The game loop architecture diagram is nice, but the demo itself is non-functional.

**Test Coverage: 3/10** — Tests exist but test the stub implementation, not the integration.

**Roblox Integration: 2/10** — It literally doesn't do anything. Every real call is commented out with `-- self.scheduler:tick()` etc. The "demo" is just a simulation.

**Missing Features:**
- Everything. This should be a working game that demonstrates all 10 packages. Currently it's a README with code comments.

**What would make me adopt it:** Make it actually work. Wire up all the packages. Even a simple 5-minute gameplay loop would be worth 100× more than this stub.

---

## 📊 Score Card

| Package | API | Docs | Tests | Roblox | Overall |
|---------|-----|------|-------|--------|---------|
| luau-spatial | 9 | 9 | 8 | 8 | ⭐⭐⭐⭐⭐ |
| luau-scheduler | 9 | 8 | 9 | 9 | ⭐⭐⭐⭐ |
| luau-recipe | 9 | 8 | 9 | 7 | ⭐⭐⭐⭐ |
| luau-biome | 8 | 8 | 9 | 7 | ⭐⭐⭐⭐ |
| luau-genealogy | 8 | 7 | 9 | 6 | ⭐⭐⭐⭐ |
| luau-audio | 8 | 7 | 7 | 5 | ⭐⭐⭐⭐ |
| luau-quest | 7 | 7 | 4 | 5 | ⭐⭐⭐ |
| luau-conservation | 6 | 7 | 5 | 4 | ⭐⭐⭐ |
| luau-math | 7 | 7 | 6 | 5 | ⭐⭐⭐ |
| luau-git-world | 7 | 7 | 7 | 5 | ⭐⭐⭐ |
| luau-demo | 4 | 5 | 3 | 2 | ⭐⭐ |

---

## 🏆 Top 3 I'd Actually Use

### 1. luau-spatial
This is production-ready for 2D games. The QuadTree implementation is solid, the API is intuitive, and the performance characteristics are well-documented. I'd use this for projectile systems, proximity triggers, and minimap culling in a top-down game. **Would use today.**

### 2. luau-scheduler
Simple, well-tested, integrates cleanly with `RunService.Heartbeat`. The priority system is exactly what you need for game loops where AI shouldn't block physics. I'd use this as the backbone of any server-side game loop. **Would use today.**

### 3. luau-recipe
The chainable API is a joy to use. If I were building any kind of crafting system (which is like 60% of Roblox games), I'd reach for this immediately. The biome/skill gates are a bonus that saves me from writing boilerplate. **Would use today.**

---

## 🚧 Biggest Gaps Blocking Adoption

1. **No 3D spatial support** — Roblox is a 3D engine. The spatial package only does 2D. This is the #1 blocker for most games.

2. **No data persistence** — None of the packages have save/load. Quest progress, world state, inventory — all lost on server restart. For a production game, this is a dealbreaker.

3. **No client-server sync** — Quest tracker, inventory, recipe book — all server-only with no RemoteEvent integration. In Roblox, the server owns state but the client needs to display it.

4. **luau-demo is non-functional** — For someone evaluating these packages, the demo should be a working game that sells you on the ecosystem. Currently it's comments.

5. **luau-math lacks game-math essentials** — No matrices, no vectors (beyond Vec2), no easing, no noise. The group theory stuff is cool but most devs need `lerp`, `smoothstep`, and `PerlinNoise`.

---

## 🐛 Bugs & Issues (Ranked by Severity)

### Critical (Will cause incorrect behavior)
1. **luau-git-world:** Branches share entity state — completely breaks the git metaphor (P0)
2. **luau-quest:** `getStatus()` uses tuple syntax inside a table — runtime error (P0)
3. **luau-git-world:** `merge()` doesn't actually merge anything — just logs a message (P1)

### High (Will cause unexpected behavior)
4. **luau-spatial:** `SpatialHash.remove()` fails silently if radius doesn't match exactly (P1)
5. **luau-spatial:** `SpatialHash.queryPotentialCollisions()` uses `tostring()` for dedup — unreliable with table data (P1)
6. **luau-scheduler:** Completed tasks leak memory (never cleaned up) (P2)
7. **luau-math:** `Groove.swingFactor(120, 100)` produces 0ms upbeat — division by zero (P2)

### Medium (Edge cases / usability)
8. **luau-conservation:** `energyConserved()` hardcoded 5% tolerance (P3)
9. **luau-conservation:** `flowConserved()` mixes relative and absolute tolerance (P3)
10. **luau-audio:** `midiToName()` incorrect for negative MIDI values (P3)
11. **luau-quest:** `CollaborateWith` objective type defined but has no factory (P3)
12. **luau-recipe:** `Ingredient` module exists but is never used by `Recipe` (P3)

---

## 📋 Feature Requests (Ranked by Impact)

1. **3D spatial (Octree + Vec3)** — The single most impactful addition. Most Roblox games are 3D.
2. **Data persistence layer** — Save/load for quest state, world state, inventory. JSON serialization at minimum.
3. **Client-server sync patterns** — RemoteEvent wrappers for quest progress, inventory updates.
4. **Entity move/update in spatial** — `QuadTree:move(oldPos, newPos, data)` instead of remove+insert.
5. **Real merge in luau-git-world** — Actually combine entity states from branches with conflict detection.
6. **Branch isolation in luau-git-world** — Each branch should have its own entity snapshot.
7. **Matrix/Vector3/Easing in luau-math** — Game-math essentials that every Roblox dev needs.
8. **Task name lookup in scheduler** — `getByName(name)` for debugging and cancellation by name.
9. **Error isolation in scheduler callbacks** — Wrap callbacks in pcall so one failing task doesn't crash the loop.
10. **Working demo** — Actually wire up all 10 packages into a playable game loop.
11. **Recipe discovery/unlocking** — Hidden recipes that unlock based on conditions.
12. **Probability outputs in recipes** — `output("rare_gem", 1, chance = 0.1)` for RNG crafting.

---

## Final Thoughts

These packages have **real potential**. The top 3 (spatial, scheduler, recipe) are genuinely useful today. The educational vision (teaching math and git through gameplay) is ambitious and well-executed at the API level.

But the ecosystem feels like it was designed top-down by a mathematician rather than bottom-up by a game developer. luau-conservation and luau-math's symmetry groups are academically interesting but solve problems most Roblox devs don't have. Meanwhile, the problems every Roblox dev DOES have — 3D math, persistence, networking — are missing.

The good news: the code quality is consistently high. Type annotations, proper metatables, clean exports, consistent MIT licensing. Whoever wrote this knows Luau well.

The bad news: it's v0.1.0 across the board and it shows. The demo doesn't work, the git-world package has a fundamental design flaw (shared entity state across branches), and there's no story for persistence or networking.

**My verdict:** Use spatial, scheduler, and recipe in your next game. Watch the rest. When they add 3D support, persistence, and fix the git-world isolation bug, this could be a serious ecosystem.

---

*This diary was written after reading every source file, every test, and every README across all 11 repositories. No code was executed — all analysis is from reading the source. Take my bug reports with a grain of salt until you verify them.*
