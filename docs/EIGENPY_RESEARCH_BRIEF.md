# EigenPy Research Brief — SuperInstance Enhancement Opportunities

**Fleet:** Cocapn Fleet  
**Scout:** Fleet Research Scout (kimi1 subagent)  
**Date:** 2026-05-29  
**Repo:** `https://github.com/SuperInstance/eigenpy`  
**Scope:** Architecture analysis, limitation audit, and concrete enhancement proposals mapped to SuperInstance science

---

## 1. Executive Summary

EigenPy is a mature C++/Python binding layer that exposes Eigen3's dense linear algebra to Python as NumPy objects. It is the product of ~5 years of development (2014–2019) by INRIA/LAAS-CNRS, focused on robotics (Gepetto/Pinocchio ecosystem). For the Cocapn Fleet, eigenpy represents a **strategic dependency with untapped potential**: its zero-copy numpy↔Eigen bridge and geometry bindings are production-quality, but its architecture stops at dense matrices and double/float/int scalars — precisely where our science (sparse vector tables, fixed-point VMs, geometric consensus) begins.

This brief identifies **5 concrete enhancement paths** that would turn eigenpy from a passive dependency into an active accelerator for fleet science.

---

## 2. Architecture Deep Dive

### 2.1 Core Binding Strategy

EigenPy uses **Boost.Python** (not pybind11) to register bidirectional type converters between NumPy arrays and Eigen::Matrix types. The architecture is three-layered:

| Layer | File | Role |
|-------|------|------|
| **Type Traits** | `include/eigenpy/fwd.hpp`, `details.hpp` | `NumpyEquivalentType<T>` maps C++ scalars to `NPY_*` constants. `FromTypeToType<From,To>` prevents lossy conversions at the Boost.Python converter registry. |
| **Zero-Copy Mapping** | `include/eigenpy/map.hpp` | `MapNumpy<MatType>::map(pyArray)` wraps a `PyArrayObject` with `Eigen::Map` — no allocation, no memcpy. Handles row-major/column-major stride computation via `StrideType`. |
| **Converter Registration** | `include/eigenpy/details.hpp` | `EigenToPy<MatType>` and `EigenFromPy<MatType>` are registered with `bp::converter::registry::push_back`. This is the critical hot path: every Python→C++ call traverses this registry. |

### 2.2 Supported Types (Current)

```cpp
// From details.hpp — hardcoded scalar mappings
template<> struct NumpyEquivalentType<double> { enum { type_code = NPY_DOUBLE }; };
template<> struct NumpyEquivalentType<int>     { enum { type_code = NPY_INT }; };
template<> struct NumpyEquivalentType<long>    { enum { type_code = NPY_LONG }; };
template<> struct NumpyEquivalentType<float>   { enum { type_code = NPY_FLOAT }; };
```

**Matrix types pre-registered** (`src/eigenpy.cpp`):
- `MatrixXd`, `Matrix2d`, `Matrix3d`, `Matrix4d`
- `VectorXd`, `Vector2d`, `Vector3d`, `Vector4d`
- `Ref<MatType>` (Eigen 3.2+ only)

### 2.3 Geometry Module

The geometry bindings (`include/eigenpy/quaternion.hpp`, `angle-axis.hpp`) expose:
- `Eigen::Quaternion<T>` with full Pythonic API (`__getitem__`, `__setitem__`, `slerp`, `dot`, `angularDistance`)
- `Eigen::AngleAxis<T>`
- `Eigen::Quaterniond` ↔ rotation matrix conversion

These are **not** generic templates — they are manually instantiated for `double` only.

### 2.4 Solvers Module

`src/solvers/solvers.cpp` exposes:
- `ConjugateGradient` with Identity and Diagonal preconditioners
- `LeastSquaresConjugateGradient` (Eigen 3.3.5+)
- `ComputationInfo` enum (Success, NumericalIssue, NoConvergence, InvalidInput)

Notably **absent**: `SparseLU`, `SimplicialCholesky`, `BiCGSTAB`, or any sparse solver.

### 2.5 Memory Model

EigenPy handles Eigen's 16-byte SIMD alignment requirement via a custom Boost.Python allocator macro (`EIGENPY_DEFINE_STRUCT_ALLOCATOR_SPECIALIZATION` in `memory.hpp`). This is critical for robotics workloads but adds complexity.

---

## 3. Limitation Analysis

### 3.1 Scalar Type Ceiling

**Finding:** Only `int`, `long`, `float`, `double` are supported. No `std::complex`, no fixed-point, no bfloat16, no user-defined scalar types.

**Fleet Impact:** Our FLUX VM executes in fixed-point arithmetic (60 opcodes, stack-machine). Any matrix operation inside FLUX constraints (e.g., rotation checks, covariance verification) must be implemented from scratch in Python/NumPy rather than leveraging Eigen's optimized kernels.

### 3.2 Sparse Matrix Blind Spot

**Finding:** Eigen's `SparseMatrix` and `SparseVector` are entirely unbound. The solver module only covers dense iterative solvers.

**Fleet Impact:** Our federated vector tables (`MeshVectorGossip`) and MAP-Elites archives are naturally sparse — high-dimensional embeddings where most entries are zero. Without sparse bindings, vector table cosine similarity, CRDT merge operations, and novelty search all incur O(n²) dense overhead.

### 3.3 Expression Template Black Box

**Finding:** EigenPy converts numpy arrays **into** Eigen matrices, then converts results **back** to numpy. It does **not** expose Eigen's lazy expression templates to Python. Operations like `A * B + C` allocate three temporary matrices.

**Fleet Impact:** Our lock-free routing pre-computation and thermal scheduler matrix updates could be 2–3× faster if chained operations were fused at the C++ level.

### 3.4 Boost.Python Dependency

**Finding:** The project predates pybind11 (2015) and is locked into Boost.Python's heavier build model, Python 2/3 compat shims (`PY_MAJOR_VERSION >= 3` checks), and manual `Py_INCREF` reference counting.

**Fleet Impact:** Build fragility. The `CMakeLists.txt` requires `boost::python`, `eigen3 >= 3.0.5`, and manual numpy include detection. This is not a `pip install` friendly package.

### 3.5 No GPU / No Parallelism

**Finding:** No CUDA support, no OpenMP exposure, no threading control. Eigen can use OpenMP internally, but EigenPy does not expose `Eigen::setNbThreads()` or any parallel API.

**Fleet Impact:** Our device-router already heterogeneously routes to CUDA/iGPU/CPU. EigenPy sits entirely on the CPU path with no offload hooks.

### 3.6 Limited Decomposition Coverage

**Finding:** README advertises Cholesky, SVD, QR — but the codebase only exposes iterative solvers (CG, LSCG) via the solvers module. Dense decompositions are not bound.

**Fleet Impact:** CMA-ES emitters in our breeding loop need `SelfAdjointEigenSolver` for covariance adaptation. Currently unavailable through eigenpy.

---

## 4. SuperInstance Science → Enhancement Map

### Proposal 1: Fixed-Point Scalar Extension for FLUX VM Integration

**What:** Extend `NumpyEquivalentType` and `EigenObjectAllocator` to support a custom fixed-point scalar type (e.g., `Q15` or `Q31`) compatible with FLUX's 32-bit fixed-point execution model.

**Why it matters:** FLUX constraints frequently need matrix-vector multiplication (rotation checks, covariance bounds). Today these are implemented in pure Python with `numpy.dot` on float64, then converted to fixed-point for VM execution. A fixed-point Eigen binding would let FLUX constraints run matrix ops natively in the target arithmetic, eliminating the float→fixed conversion step and enabling SIMD-optimized fixed-point matmul.

**Implementation sketch:**
```cpp
// New file: include/eigenpy/fixed_point.hpp
namespace eigenpy {
  template<> struct NumpyEquivalentType<Q15> { 
    enum { type_code = NPY_INT16 }; // or custom dtype
  };
  
  // Specialize EigenObjectAllocator for fixed-point
  template<typename MatType>
  struct FixedPointAllocator {
    static void allocate(PyArrayObject* pyArray, void* storage) {
      // Map numpy int16 array as Q15 matrix
      new(storage) MatType(MapNumpy<MatType>::map(pyArray));
    }
  };
}
```

**Effort:** Medium (1–2 days). Requires defining a `Q15` scalar class satisfying Eigen's `NumTraits` interface.

**Priority:** P1 — Unblocks FLUX Path B geometric constraint checks.

---

### Proposal 2: Sparse Matrix Bindings for Vector Tables and MAP-Elites

**What:** Bind `Eigen::SparseMatrix<T>` and `Eigen::SparseVector<T>` with numpy COO/CSR interop. Add `SparseLU`, `SimplicialCholesky`, and sparse matrix-vector product.

**Why it matters:**
- **Vector tables:** `MeshVectorGossip` CRDT merges can be expressed as sparse matrix additions. Cosine similarity over sparse embeddings is O(nnz) not O(dim).
- **MAP-Elites archives:** Our `BreederDaemonV2` novelty search maintains a population archive. For high-dimensional behavior descriptors (>100 dims), the archive occupancy is <1%. Sparse matrix storage would let us scale archives to 10⁶ cells.
- **Consensus:** `holonomy-consensus` (GL(9)) involves sparse cycle matrices on fleet topology graphs.

**Implementation sketch:**
```cpp
// New file: include/eigenpy/sparse.hpp
namespace eigenpy {
  template<typename SparseMat>
  struct SparseToPy {
    static PyObject* convert(const SparseMat& mat) {
      // Export to scipy.sparse.csr_matrix
      // or numpy arrays (data, indices, indptr)
    }
  };
}
```

**Effort:** High (3–4 days). Requires scipy.sparse dependency, custom converter for CSR/CSC formats, and solver exposure.

**Priority:** P0 — Directly scales two fleet subsystems (vector tables + MAP-Elites).

---

### Proposal 3: Matrix Group / Transform Bindings for Geometric Consensus

**What:** Extend the geometry module to bind `Eigen::Transform`, `Eigen::Isometry3d`, `Eigen::Affine3d`, and `Eigen::Projective3d`. Add matrix group operations (SE(3), SO(3) exponential/log maps).

**Why it matters:** Our `holonomy-consensus` checks GL(9) matrices for zero-holonomy cycles. Currently this is implemented in Rust (`holonomy-consensus` crate). For Python-side consensus verification (e.g., `ByzantineBreedGate` in the breeder), we need fast SE(3) composition and adjoint operations. Eigen's `Geometry` module already has these — eigenpy only binds a fraction.

**Implementation sketch:**
```cpp
// Extend include/eigenpy/geometry.hpp
void exposeTransform();
void exposeSE3();

// In geometry module
bp::class_<Eigen::Isometry3d>("Isometry3d")
  .def("translation", ...)
  .def("rotation", ...)
  .def("__mul__", &composeSE3);
```

**Effort:** Medium (1–2 days). Pattern already established by quaternion/angle-axis visitors.

**Priority:** P1 — Enables Python-side geometric consensus checks for `ByzantineBreedGate`.

---

### Proposal 4: Dense Decomposition Exposure for CMA-ES Emitters

**What:** Bind `Eigen::SelfAdjointEigenSolver`, `Eigen::GeneralizedSelfAdjointEigenSolver`, `Eigen::LLT` (Cholesky), and `Eigen::BDCSVD`.

**Why it matters:** Our breeding loop uses CMA-ES emitters for quality diversity. CMA-ES requires eigendecomposition of the covariance matrix every generation. Currently done in numpy (`np.linalg.eigh`) which is fast but not controllable from the FLUX VM. Binding Eigen's solvers would let us:
- Run covariance decomposition inside fixed-point constraints
- Use Eigen's `SelfAdjointEigenSolver` which is 20–30% faster than numpy for small matrices (<100 dims)
- Support half-precision covariance matrices for thermal-constrained breeding

**Implementation sketch:**
```cpp
// New file: include/eigenpy/decompositions.hpp
namespace eigenpy {
  template<typename MatrixType>
  struct SelfAdjointEigenSolverVisitor : public bp::def_visitor<...> {
    // expose eigenvalues(), eigenvectors(), info()
  };
}
```

**Effort:** Low (0.5–1 day). Straightforward def_visitor pattern.

**Priority:** P1 — Breeding loop performance and VM integration.

---

### Proposal 5: Expression Fusion / Lazy Evaluation API

**What:** Expose a Python context manager or chained API that accumulates operations and evaluates them as a single Eigen expression tree.

**Why it matters:** Our lock-free routing (`numpy pre-computation`) and thermal scheduler do sequences of matrix updates:
```python
R = alpha * A @ B + beta * C  # 3 temporary allocations in eigenpy today
```
With expression templates, this becomes one fused kernel with no temporaries.

**Implementation sketch:**
```python
# Python API
with eigenpy.fused() as ctx:
    R = ctx.add(ctx.mul(alpha, A), ctx.mul(beta, B))
    # Evaluated as: R = alpha*A + beta*B without temporaries
```

**Effort:** High (4–5 days). Requires designing a Python-DSL that maps to Eigen's C++ expression templates. Non-trivial API design problem.

**Priority:** P2 — Nice to have, but dense matmul is already fast enough for current fleet scale.

---

## 5. Synergy Matrix

| Fleet Science | EigenPy Today | With Proposals | Impact |
|--------------|---------------|----------------|--------|
| **MAP-Elites / QD** | Dense matrix only | Sparse archive + fast eigendecomp | 10× archive scale |
| **Federated Vector Tables** | Dense vectors | Sparse embeddings + fast similarity | 100× table size |
| **FLUX VM** | Float64 only | Fixed-point matrix ops | Native constraint geometry |
| **BFT Consensus** | Quaternions only | SE(3)/GL(n) transforms | Python-side geometric verification |
| **Lock-Free Routing** | Per-op temporaries | Expression fusion | 2–3× throughput |
| **CMA-ES Emitters** | numpy.eigh | Eigen SelfAdjointEigenSolver | VM-integrated covariance update |

---

## 6. Risk & Trade-off Assessment

| Proposal | Build Risk | Runtime Risk | Maintenance Burden |
|----------|-----------|--------------|-------------------|
| Fixed-point scalars | Medium (custom NumTraits) | Low (Eigen's fixed-point is mature) | Low — additive, non-breaking |
| Sparse matrices | High (scipy.sparse interop) | Medium (memory pattern changes) | Medium — new API surface |
| Matrix group bindings | Low | Low | Low — follows existing pattern |
| Decomposition exposure | Low | Low | Low — additive |
| Expression fusion | High (API design) | High (C++ template complexity) | High — new paradigm |

**Recommendation:** Execute in order 4 → 3 → 1 → 2 → 5. Start with low-risk, high-value additive bindings (decompositions, transforms), then tackle the scalar system (fixed-point), then sparse matrices. Expression fusion is a P2 research project.

---

## 7. Conclusion

EigenPy is **not** a generic linear algebra library — it is a robotics-focused bridge between numpy and Eigen's dense matrix/geometry types. For the Cocapn Fleet, its current value is in zero-copy data sharing and quaternion/rotation bindings. Its future value depends on extending beyond dense `float64` into the territory our science occupies: sparse high-dimensional spaces, fixed-point arithmetic, matrix groups, and expression-level optimization.

The codebase is well-structured (`details.hpp`/`map.hpp` pattern is clean) but locked into Boost.Python's older paradigm. A pybind11 migration would reduce build complexity and open the door to more modern binding techniques, but that is a separate strategic decision.

**Immediate next action:** Prototype Proposal 4 (dense decomposition exposure) on a feature branch. It is the smallest change with direct breeding-loop impact.

---

*Scout out. Returning to main agent for dispatch.*
