# Sandbox Experiment Summary

## 5 experiments launched, 2 produced data, 3 rate-limited

### Key Finding: conservation-checker is the universal entry point
Both successful agents independently chose conservation-checker first.
Neither chose cathedral-probe or crackle-runtime.

Why:
- 'Budget tracking' maps to the most universal developer pain point
- 'Things that should not decrease' is intuitive without reading docs
- The concept needs zero math background to understand the value

### What This Tells Us
1. **conservation-checker should be our flagship crate** — it's the one external devs reach for first
2. **cathedral-probe and crackle-runtime need simpler onboarding** — their value isn't immediately obvious from descriptions
3. **The commit trail pattern is**: read repo → identify pain point → cargo add → plan integration → (rate limited before writing code)
4. **We need longer agent runtimes** — 90 seconds isn't enough to write and test integration code

### For Next Session
- Retry trippy, arroyo, gdext experiments
- Give agents more time (5-10 min instead of 90s)
- Track whether cathedral-probe gets chosen with longer exploration time

