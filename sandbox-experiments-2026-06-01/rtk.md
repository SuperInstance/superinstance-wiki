# rtk + conservation-checker (DeepSeek agent)

## Commit: 00995f0
```
experiment: add conservation-checker v0.1.0 for token budget tracking

Adds the conservation-checker crate (SuperInstance) for tracking
one-sided conservation of quantities. This will be used to model
the Claude Code token budget as a conserved quantity — detecting
drift rates, phase transitions (e.g. when spending accelerates),
and budget violations.

The conservation-checker takes snapshots over time and can report:
- Drift rate (tokens/snapshot)
- Phase (Stable, Transitioning, Exhausted)
- Violations (when budget drops below initial - tolerance)
```

**Agent reasoning:** Token budgets are conserved quantities. The agent immediately identified drift rate, phase detection, and budget violation as the value proposition. Was about to add a Conservation CLI subcommand when rate-limited.

**No further commits** — agent hit API rate limit while reading main.rs.

