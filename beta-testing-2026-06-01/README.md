# Beta Testing — June 1, 2026

5 initial testers + 3 re-testers evaluated hermes-construct and the standalone crate ecosystem.

## Round 1: Initial Testing

| Tester | Background | Diary | Key Finding | Score |
|--------|-----------|-------|-------------|-------|
| Riley | Senior Rust dev | [diary](riley-rust-dev.md) | No lib.rs — can't embed | 3/10 first impression, 6/10 code |
| Samira | DevOps/SRE | [diary](samira-devops.md) | No Prometheus, crates don't interop | 5-7/10 |
| Jordan | Non-tech founder | — | Not for non-devs, trust score 3/10 | 3/10 |
| Dr. Chen | Applied math prof | [review](dr-chen-academic-review.md) | Cheeger constant WRONG | 3/10 |
| Nadia | Crate author | [review](nadia-crate-author-review.md) | negative-space-testing is the standout | 7-9/10 |

## Actions Taken from Round 1

1. ✅ Fixed Cheeger constant → cathedral-probe v0.1.1 published
2. ✅ Added lib.rs to hermes-construct
3. ✅ Fixed broken crackle-runtime example
4. ✅ Added doc comments to conservation-checker
5. ✅ Removed false no_std claims
6. ✅ Added academic references (Fiedler, Chung, Mohar, Alon-Milman)
7. ✅ Fixed all repos to use `main` as default branch
8. ✅ Documented conservation cost units and routing approach

## Round 2: Re-Testing After Fixes

| Tester | Background | Report | Key Finding | Score |
|--------|-----------|--------|-------------|-------|
| Marcus | Rust systems eng | [retest](marcus-rust-dev-retest.md) | conservation-checker production-ready | 8/10 (cons-checker) |
| Lin | K8s platform eng | [retest](lin-ops-retest.md) | Fiedler concept validated, needs sparse algos | 5/10 |
| Dr. Kim | Spectral graph postdoc | [retest](dr-kim-academic-retest.md) | Cheeger fix verified, up to 6/10 | 6/10 |

## Final Verification

[371 tests across 6 crates, all passing. **9/10 READY FOR BETA.**](final-verification.md)

### Remaining Known Issues (minor):
- cathedral-probe: Dense O(n²) eigensolver, no sparse support
- No interop layer between crates (philosophical siblings, not technical dependencies)
- negative-space-testing duplicates some standalone crate functionality
- crackle-runtime name misleading ("runtime" implies async)
