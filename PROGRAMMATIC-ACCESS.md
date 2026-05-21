# Programmatic Access

**Query the fleet with code, not just your eyes.**

---

## data/repos.json

The entire fleet, as JSON. Generated every Monday at 05:00 UTC (or on demand via `make regenerate`).

```bash
curl -s https://raw.githubusercontent.com/SuperInstance/superinstance-wiki/main/data/repos.json | jq '.total'
# → 1785
```

### Schema

```json
{
  "generated": "2026-05-21T02:41:00",
  "org": "SuperInstance",
  "total": 1785,
  "repos": [
    {
      "name": "flux-research",
      "created": "2026-04-10T07:17:55Z",
      "pushed": "2026-05-20T12:34:56Z",
      "description": "FLUX Deep Research — Compiler/interpreter taxonomy...",
      "language": "Python",
      "is_fork": false,
      "is_archived": false,
      "tier": "Production",
      "relevance": "Core Fleet",
      "lifecycle": "Active Dev",
      "action": "KEEP",
      "days_since_push": 1,
      "desc_len": 67
    }
  ]
}
```

### Quick Queries

```bash
# Count KEEPers
cat data/repos.json | jq '[.repos[] | select(.action == "KEEP")] | length'

# List abandoned orphans
cat data/repos.json | jq '.repos[] | select(.lifecycle == "Abandoned" and .relevance == "Orphan") | .name'

# Find scaffolds
cat data/repos.json | jq '.repos[] | select(.tier == "Scaffold") | {name, created, description}'

# Production repos by language
cat data/repos.json | jq '.repos[] | select(.tier == "Production" and .language == "Rust") | .name'

# Monthly creation histogram
cat data/repos.json | jq '.repos | group_by(.created[:7]) | map({month: .[0].created[:7], count: length})'
```

### Python Example

```python
import json

with open('data/repos.json') as f:
    data = json.load(f)

# Find all experimental repos that are active
active_experimental = [
    r for r in data['repos']
    if r['relevance'] == 'Experimental'
    and r['lifecycle'] == 'Active Dev'
]

print(f"Active experimental repos: {len(active_experimental)}")
for r in active_experimental[:5]:
    print(f"  {r['name']}: {r['description'][:50]}")
```

### JavaScript Example

```javascript
const data = require('./data/repos.json');

// Find all Core Fleet repos
const core = data.repos.filter(r => r.relevance === 'Core Fleet');
console.log(`Core Fleet: ${core.length} repos`);

// Find repos needing attention
const attention = data.repos.filter(r =>
  (r.action === 'PRIVATE' || r.action === 'ARCHIVE')
);
console.log(`Needs attention: ${attention.length} repos`);
```

---

## data/all-repos.csv

Pipe-delimited CSV for spreadsheet import.

```bash
# Open in LibreOffice
libreoffice --calc data/all-repos.csv

# Or parse with awk
awk -F'|' '$6 == "true" {print $1}' data/all-repos.csv | head -20
# → List of forks
```

---

## GitHub API

For real-time data, hit the API directly:

```bash
# List all repos
curl -s "https://api.github.com/orgs/SuperInstance/repos?per_page=100" | jq '.[].name'

# Get specific repo details
curl -s "https://api.github.com/repos/SuperInstance/flux-research" | jq '{name, created_at, pushed_at, description}'
```

---

## Webhook Integration

The `regenerate-triage.py` script can be triggered by:

1. **GitHub Actions** — Weekly cron (already configured)
2. **Local make** — `make regenerate`
3. **Webhook** — Set up a repository webhook to POST to a server that runs the script

---

*Last updated: 2026-05-21*
