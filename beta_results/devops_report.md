# DevOps Beta Test Report

## What Worked
The thermal-aware job scheduler successfully modeled heterogeneous devices (GPU, NPU, CPU) and enforced thermal constraints, blocking 4 jobs on the NPU without crashing. The output clearly showed resource utilization percentages and completion status, making it easy to verify the scheduler behaved as intended.

## What Was Confusing
The term "thermal full" was used without explanation—it's unclear whether this refers to a temperature threshold, a thermal budget cap, or a simulated hardware limit. There was no visibility into *why* the NPU specifically hit its thermal limit while GPU and CPU stayed well below capacity, which makes tuning or debugging difficult.

## Rating
⭐⭐⭐⭐ (4/5)

## Top 2 Suggestions
1. Add per-device thermal metrics (e.g., current temperature, thermal budget remaining) to the output for better observability.
2. Provide a brief legend or README explaining what "thermal full" means and how thermal budgets are calculated.
