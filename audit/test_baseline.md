# Sunset Ecosystem Test Run — May 30, 2026

**Command:** `pytest tests/ -x --tb=short`
**Result:** 3169 passed, 15 skipped, 2 xfailed, 1 failed, 15 warnings in 272.07s

## Failure
- `tests/test_hdc_novelty.py::test_speedup_vs_cosine`
  - Expected ≥5× speedup with AVX-512
  - Got 0.87× (HDC 8.98 ms vs cosine 7.79 ms)
  - Hardware-specific: this machine lacks AVX-512

## Warnings
- PytestUnknownMarkWarning: `benchmark` mark not registered (4×)
- PytestCollectionWarning: classes with `__init__` cannot be collected as tests (3 files)
- NumbaWarning: compilation falling back to object mode (1×)
- RuntimeWarning: Mean of empty slice / divide by zero (3×)

## Notes
- 6704 tests collected total
- Only ~3200 ran before `-x` stopped on first failure
- The AVX-512 failure is environment-specific, not a code bug
- Running without `-x` would show full results
- 2 xfailed tests are expected (known issues)
