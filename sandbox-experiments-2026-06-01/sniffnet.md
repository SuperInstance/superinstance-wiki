# Sniffnet + conservation-checker (DeepSeek agent)

## Commit: bd9e73a
```
experiment: add conservation-checker crate for bandwidth budget tracking

conservation-checker (v0.1.0) monitors quantities that must not
decrease — a natural fit for cumulative network traffic counters.
```

**Agent reasoning:** Network traffic monitors track cumulative byte/packet counts. These are naturally conserved quantities — they should only increase. conservation-checker was the obvious first pick.

**No further commits** — agent hit API rate limit after cargo add.

