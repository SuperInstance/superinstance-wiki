# Jordan's Python DS Diary — SuperInstance Math Review

**Date:** 2026-06-01  
**Who:** Jordan, data scientist (scikit-learn, scipy, numpy daily driver)  
**Task:** Evaluate SuperInstance Python packages for real-world adoption

---

## TL;DR

These are beautifully crafted mathematical libraries with excellent test coverage and zero dependencies. They're *academically impressive* but **not production-ready for a data science team** — no numpy integration, pure-Python performance bottlenecks, and significant feature gaps vs scipy/sklearn. Think of them as well-written textbooks you can `import`, not tools you'd ship to prod.

---

## Package-by-Package Review

### 1. superinstance-math (94 tests ✅)

**The Python front door.** Covers information geometry, optimal transport, persistent homology, spectral methods, and group theory.

| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| API Pythonicity | 7 | Clean ABCs, dataclass-like feel, good `__init__.py` with `__all__`. Naming is clear (`kl_divergence`, `wasserstein_1d`, `sinkhorn`). Feels like a well-structured academic library. |
| Documentation | 8 | Every module has docstrings. Every function has Args/Returns. Examples in docstrings. The best-documented of the five. |
| Performance | 3 | **Critical issue**: Everything is pure Python lists. No numpy arrays. The Sinkhorn algorithm uses `list[list[float]]` for matrices. `O(n²)` pairwise distances via Python loops. `top_k_eigenvalues` uses power iteration in pure Python. This will be 100-1000x slower than scipy/numpy equivalents. |
| Integration | 2 | Zero numpy. Zero pandas. No `__array__` protocol. No `.fit()` / `.transform()` sklearn API. Can't pass DataFrames or ndarrays. |
| Real-world Usefulness | 5 | The *math* is right and interesting. Information geometry (Fisher-Rao, natural gradients, alpha-connections) is genuinely useful and underrepresented in Python. Optimal transport is hot right now (POT library exists but this is simpler). Persistent homology (giotto-tda, ripser) has better alternatives. |

**Code Quality Notes:**
- `NormalManifold.fisher_rao_distance` — the closed-form is correct ✓
- `sinkhorn` uses log-domain stabilization — good numerical hygiene ✓
- `_mod2_rank` for Betti numbers — correct Z/2 Gaussian elimination ✓
- `chentsov_theorem()` returns a *string* instead of computing anything — feels like a stub
- `cross_entropy` uses numerical integration with `for i in range(n)` — will crawl on real data
- No `__repr__` on most classes, `StatisticalManifold` ABC has no `__eq__`

### 2. kintsugi-math (84 tests ✅)

**Fault tolerance as aesthetic philosophy.** Error trace analysis, data fragment reassembly, imperfection metrics, fault injection, error propagation graphs.

| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| API Pythonicity | 8 | Most Pythonic of the bunch. Uses `dataclass`, `defaultdict`, `deque`, `field`. `CrackGraph` with BFS downstream/upstream is genuinely useful. |
| Documentation | 8 | Excellent docstrings with examples. Every function has a clear purpose. The "golden seam" metaphor actually maps well to the code. |
| Performance | 6 | Mostly operates on dicts and lists — fine for its use case (error analysis isn't usually on hot paths). `CrackGraph.downstream()` BFS is clean O(V+E). |
| Integration | 4 | Works with standard Python types (dicts, lists, exceptions). Could actually be used alongside any framework. No numpy dependency but doesn't need one. |
| Real-world Usefulness | 7 | **Most practical package.** `CrackGraph` for error propagation mapping, `inject_faults` for chaos testing, `FragmentCollection` for partial data recovery — these solve real problems. I'd actually use `build_crack_graph` and `find_golden_joints` for production error analysis. |

**Code Quality Notes:**
- `severity_score` using MRO depth is clever but fragile — custom exceptions will score inconsistently
- `golden_ratio_recovery` comparing recovery ratio to φ is ... fun but not scientifically grounded
- `WabiSabiReport` aesthetic scoring is subjective (completeness * 0.7 + uniformity * 0.3) but documented as such
- `reassemble` with gap_filler callback is a nice pattern
- `shortest_crack_path` returns None for unreachable — correct, would prefer empty list but fine

### 3. quipu-math (51 tests ✅)

**Incan quipu knot encoding.** Number encoding/decoding, cord trees, weave/unweave operations, checksums, SVG visualization.

| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| API Pythonicity | 7 | Clean dataclass-based models. `CordTree.serialize()`/`.deserialize()` JSON is practical. `to_svg()` is a nice touch. |
| Documentation | 8 | Great cultural context + technical documentation. Clear encoding conventions explained. |
| Performance | 6 | Fine for what it does (small integers encoded as knots). Not a bottleneck concern. |
| Integration | 5 | JSON serialization makes it interoperable. SVG output could embed in Jupyter. But the domain is very niche. |
| Real-world Usefulness | 3 | It's a **fascinating art/math project**, not a production tool. Quipu encoding is historically interesting but I can't imagine a use case at work. Maybe educational? |

**Code Quality Notes:**
- `KnotType` enum has `single = 1`, `figure_eight = 1`, `long = 0` — the duplicate values for single and figure_eight is intentional (both represent digit 1) but could confuse users
- `weave` uses `v1 * 10000 + v2` for combining — hard limit of 9999 per value, not documented as a constraint
- `unweave` relies on color string format `"woven:color1+color2"` — fragile parsing
- `is_associative` checks values match, which is correct for the encoding

### 4. symmetry-math (45 tests ✅)

**Group theory done properly.** Abstract `Group` ABC with concrete S_n, C_n, D_n. 2D transforms as affine matrices. Wallpaper group classification. Crystallographic point groups.

| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| API Pythonicity | 9 | **Best API design.** Proper abstract base class with `elements`, `operation`, `identity`, `inverse`. `is_abelian()`, `powers()`, `order_of()`, `subgroups()` are all correctly derived. Feels like what you'd design in a textbook. |
| Documentation | 7 | Good module docstrings. Point group crystallography is well-documented. Could use more examples in the group theory module. |
| Performance | 3 | `SymmetricGroup` generates ALL permutations eagerly. `S_10` = 3.6M elements × 10-tuples = ~360MB. `subgroups()` brute-forces subsets — exponential. This is a toy for n ≤ 8. |
| Integration | 2 | No numpy. Transform matrices are tuples of tuples. Can't compose with scipy's `SpatialRotation` or any 3D library. |
| Real-world Usefulness | 4 | Crystallographic point groups and wallpaper classification are niche but real (materials science, crystallography). The group theory ABC is pedagogically excellent but not competitive with sympy's `PermutationGroup` or sage. |

**Code Quality Notes:**
- `Transform` as `Tuple[Tuple[float,...],...]` instead of numpy arrays is a deliberate choice but limits composability
- `_SubgroupView` delegation pattern is clean
- `classify_pattern` admits it's simplified (can't distinguish p4m from p4g)
- `_has_glide_reflection` returns `False` hardcoded — **this is a stub**
- `systematic_absences` rules are simplified pedagogically — correct for teaching, not for actual diffraction analysis

### 5. griot-math (TypeScript, not Python)

**West African griot oral tradition as data structures.** Story genealogies, memory decay, call-and-response protocols.

| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| API Pythonicity | N/A | **It's TypeScript**, not Python. Can't use it in a Python project without a bridge. |
| Documentation | 7 | Well-commented TypeScript with JSDoc-style annotations. |
| Performance | 6 | Map-based lookups, DFS for genealogy. Fine for story counts < 10K. |
| Integration | N/A | TypeScript/Node.js ecosystem, not Python. |
| Real-world Usefulness | 3 | The memory decay model (exponential forgetting with reinforcement) maps to Ebbinghaus curve concepts. Interesting for knowledge management systems, but there are better implementations in Python (e.g., Anki-style spaced repetition libraries). |

**Note:** This shouldn't be listed as a Python package on PyPI if it's TypeScript.

---

## Adoption Blockers

1. **Zero numpy integration** — Every data scientist works in numpy. These libraries operate on `list[list[float]]`. Converting DataFrames to lists and back is a non-starter for real workflows.

2. **Pure Python performance** — The Sinkhorn, eigenvalue, and distance computations will be orders of magnitude slower than scipy. For a team that processes millions of rows, this is disqualifying.

3. **No sklearn-compatible API** — No `.fit()`, `.transform()`, `.fit_transform()`. Can't use in sklearn Pipelines. Can't use `GridSearchCV`. Can't cross-validate.

4. **No sparse matrix support** — Graph Laplacian on a dense adjacency matrix? For any real graph (>10K nodes), this explodes.

5. **Missing critical features** — No multivariate distributions. No GPU support. No batch operations. No C extensions.

6. **Alpha status (0.1.0)** — No backward compatibility guarantees. No changelog. No contribution guide.

## Feature Gaps vs scipy/sklearn

| Feature | scipy | superinstance-math |
|---------|-------|--------------------|
| Wasserstein distance | `scipy.stats.wasserstein_distance` — 1D, fast C | `wasserstein_1d` — pure Python, slow |
| Optimal transport | POT library (C backend) | `sinkhorn` — pure Python, small matrices only |
| Spectral methods | `scipy.sparse.linalg.eigsh` — sparse, ARPACK | `top_k_eigenvalues` — dense, power iteration |
| Group theory | `sympy.combinatorics` — comprehensive | Basic C_n, D_n, S_n only |
| KL divergence | `scipy.special.kl_div` — vectorized | Scalar-only, Monte Carlo integration |
| Persistent homology | `giotto-tda` / `ripser` — optimized C++ | Toy VR complex, dim ≤ 2 |

## What Would Make Me Recommend This

1. **Accept numpy arrays as input** — Add `np.ndarray` support alongside lists. Even just accepting arrays and converting internally would help.

2. **Add a `scipy` backend** — Let me `pip install superinstance-math[scipy]` and get 100x speedups by delegating to `scipy.linalg`, `scipy.spatial.distance`, etc.

3. **sklearn-compatible estimators** — `SpectralEmbedding` should subclass `sklearn.base.BaseEstimator` and implement `.fit()`.

4. **Vectorized operations** — `kl_divergence` should accept arrays of samples, not loop in Python.

5. **Real-world examples** — Jupyter notebooks showing "here's a dataset, here's how you use our library to analyze it."

6. **Benchmark against scipy** — Show me the accuracy and speed tradeoffs. If you're slower, tell me what I gain.

## Specific Code Quality Issues

1. **`superinstance-math/spectral.py`** — `top_k_eigenvalues` is not reliable. Power iteration finds *largest* eigenvalues; the code tries to find smallest but the implementation is confused (updates `v` with `w` each iteration but `lam` is the Rayleigh quotient of the previous `v`). The eigenvalues are approximate at best.

2. **`superinstance-math/persistent_homology.py`** — VR complex limited to dim 2. Betti number computation uses Euler characteristic shortcut that can give wrong results for complexes with dim > 2 simplices.

3. **`superinstance-math/information_geometry.py`** — `chentsov_theorem()` returns a string. It should be a docstring or a raised `NotImplementedError` for the general computation, not a function that returns prose.

4. **`kintsugi-math/golden_repair.py`** — `severity_score` uses MRO depth which gives inconsistent results for custom exceptions (depth varies with inheritance chain length).

5. **`symmetry-math/wallpaper.py`** — `_has_glide_reflection` returns hardcoded `False`. Wallpaper classification is incomplete.

6. **All packages** — No `py.typed` marker. No `TYPE_CHECKING` imports for optional numpy. No `__slots__` on frequently-instantiated classes.

7. **All packages** — No CI configuration visible. No GitHub Actions, no tox.ini, no Makefile.

---

## Final Ratings Summary

| Package | API | Docs | Perf | Integration | Usefulness | Overall |
|---------|:---:|:----:|:----:|:-----------:|:----------:|:-------:|
| superinstance-math | 7 | 8 | 3 | 2 | 5 | **5.0** |
| kintsugi-math | 8 | 8 | 6 | 4 | 7 | **6.6** |
| quipu-math | 7 | 8 | 6 | 5 | 3 | **5.8** |
| symmetry-math | 9 | 7 | 3 | 2 | 4 | **5.0** |
| griot-math | N/A | 7 | 6 | N/A | 3 | **N/A** |

## Bottom Line

**kintsugi-math** is the only package I'd actually use at work — its error propagation analysis and fault injection tools solve real problems and don't need numpy. The rest are beautiful mathematical art projects that need significant engineering work before they're competitive with scipy/sklearn. The math is correct, the code is clean, the tests are thorough — but they're solving problems that already have faster, more integrated solutions in the Python ecosystem.

If the team adds numpy/scipy backends and sklearn-compatible APIs, I'd reconsider. The information geometry module in superinstance-math fills a genuine gap in the Python ecosystem — it just needs to be fast enough to use on real data.

---

*"I wanted to love these. The math is beautiful, the code is clean, the cultural inspiration is genuine. But at work, I need speed, numpy, and sklearn compatibility. Right now these are museum pieces — elegant, correct, and impractical."* — Jordan
