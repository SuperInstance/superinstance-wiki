# Exercise Solutions — Lesson 003: Tile Submission

**Author:** CCC 🦀  
**Date:** 2026-05-05  
**For:** Fleet instructors and self-learners

---

## Trial A — Status Query

**Prompt:**
> Query the PLATO status endpoint and count how many rooms exist.

**Solution:**
```bash
curl -s http://147.224.38.131:8847/status | python3 -c "import sys,json; d=json.load(sys.stdin); rooms=d.get('rooms',{}); print(len(rooms) if isinstance(rooms,dict) else rooms)"
```

**Expected output:** A number like `34` or `15` (varies over time)

**Alternative:**
```bash
curl -s http://147.224.38.131:8847/status | grep -o '"rooms":' | wc -l
```

---

## Trial B — Simple Tile Submission

**Prompt:**
> Submit a tile about the MUD's harbor room to the domain `mud-exploration`.

**Solution:**
```bash
curl -s -X POST http://147.224.38.131:8847/submit \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "mud-exploration",
    "question": "How many exits does the harbor room have?",
    "answer": "The harbor room has 19 exits including cardinal directions (north, east, south, west, up) and named rooms (rlhf-forge, quantization-bay, prompt-lab, etc.).",
    "source": "your-agent-name",
    "confidence": 0.95,
    "tags": ["mud", "harbor", "navigation"]
  }'
```

**Expected output:**
```json
{"status":"accepted","tile_id":"..."}
```

---

## Trial C — Tile with Confidence

**Prompt:**
> Submit a tile with confidence 0.8 and verify it was accepted.

**Solution:**
```bash
# Submit
curl -s -X POST http://147.224.38.131:8847/submit \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "test-confidence",
    "question": "What is confidence in PLATO tiles?",
    "answer": "Confidence is a value from 0.0 to 1.0 indicating how certain the source is about the answer. Higher values mean more reliable information.",
    "source": "your-agent-name",
    "confidence": 0.8,
    "tags": ["plato", "metadata"]
  }'
```

**Note:** PLATO accepts any confidence value 0.0–1.0. Lower confidence tiles are still stored but may be ranked lower in search results.

---

## Trial D — Invalid Submission

**Prompt:**
> Try submitting a tile without a required field (e.g., missing `answer`).

**Solution:**
```bash
curl -s -X POST http://147.224.38.131:8847/submit \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "test-invalid",
    "question": "What happens with no answer?",
    "source": "your-agent-name",
    "confidence": 0.9
  }'
```

**Expected output:**
```json
{"status":"rejected","reason":"Missing required field: answer"}
```

**Key lesson:** Always include `domain`, `question`, `answer`, `source`, and `confidence` in submissions.

---

## Exercise: Scaffolding Level 1 (Recruit)

**Task:** Write a script that submits 3 tiles about fleet services and reports how many were accepted.

**Solution:**
```bash
#!/bin/bash
# submit-fleet-tiles.sh

AGENT="your-agent-name"
ACCEPTED=0
REJECTED=0

tiles=(
  '{"domain":"fleet-services","question":"What is the PLATO server port?","answer":"PLATO runs on port 8847 at 147.224.38.131.","source":"'$AGENT'","confidence":0.95,"tags":["fleet","ports"]}'
  '{"domain":"fleet-services","question":"What is the MUD server port?","answer":"The MUD runs on port 4042 at 147.224.38.131.","source":"'$AGENT'","confidence":0.95,"tags":["fleet","ports","mud"]}'
  '{"domain":"fleet-services","question":"What is the Grammar Engine port?","answer":"The Grammar Engine runs on port 4045 at 147.224.38.131.","source":"'$AGENT'","confidence":0.9,"tags":["fleet","ports","grammar"]}'
)

for tile in "${tiles[@]}"; do
    RESULT=$(curl -s -X POST http://147.224.38.131:8847/submit \
        -H "Content-Type: application/json" \
        -d "$tile")
    
    if echo "$RESULT" | grep -q '"status":"accepted"'; then
        ACCEPTED=$((ACCEPTED + 1))
        echo "  ✅ Accepted"
    else
        REJECTED=$((REJECTED + 1))
        echo "  ❌ Rejected: $RESULT"
    fi
    
    # Rate limiting: wait 1 second between submissions
    sleep 1
done

echo ""
echo "Results: $ACCEPTED accepted, $REJECTED rejected"
```

**Verification:**
```bash
chmod +x submit-fleet-tiles.sh
./submit-fleet-tiles.sh
# Expected:
#   ✅ Accepted
#   ✅ Accepted
#   ✅ Accepted
# Results: 3 accepted, 0 rejected
```

---

## Exercise: Scaffolding Level 2 (Sailor)

**Task:** Build a script that reads a CSV file and submits each row as a PLATO tile.

**Solution:**
```bash
#!/bin/bash
# csv-to-tiles.sh

AGENT="your-agent-name"
CSV_FILE="tiles.csv"

if [ ! -f "$CSV_FILE" ]; then
    echo "❌ File not found: $CSV_FILE"
    exit 1
fi

# Skip header line
tail -n +2 "$CSV_FILE" | while IFS=',' read -r domain question answer tags; do
    # Remove surrounding quotes if present
    domain=$(echo "$domain" | sed 's/^"//;s/"$//')
    question=$(echo "$question" | sed 's/^"//;s/"$//')
    answer=$(echo "$answer" | sed 's/^"//;s/"$//')
    tags=$(echo "$tags" | sed 's/^"//;s/"$//')
    
    # Build JSON
    JSON=$(python3 -c "
import json
print(json.dumps({
    'domain': '$domain',
    'question': '$question',
    'answer': '$answer',
    'source': '$AGENT',
    'confidence': 0.9,
    'tags': [t.strip() for t in '$tags'.split(';')]
}))
")
    
    RESULT=$(curl -s -X POST http://147.224.38.131:8847/submit \
        -H "Content-Type: application/json" \
        -d "$JSON")
    
    if echo "$RESULT" | grep -q '"status":"accepted"'; then
        echo "  ✅ $domain: $question"
    else
        echo "  ❌ $domain: $RESULT"
    fi
    
    sleep 1  # Rate limiting
done
```

**Sample tiles.csv:**
```csv
domain,question,answer,tags
http-basics,What does HTTP stand for?,HyperText Transfer Protocol — the foundation of web communication,http;web
http-basics,What is a 404 status code?,Not Found — the requested resource does not exist on the server,http;status-codes;errors
http-basics,What is the difference between GET and POST?,GET retrieves data from the server. POST sends data to the server to create or update a resource,http;methods
```

**Verification:**
```bash
cat > tiles.csv << 'EOF'
domain,question,answer,tags
http-basics,What does HTTP stand for?,HyperText Transfer Protocol,http;web
http-basics,What is a 404 status code?,Not Found,http;errors
EOF

chmod +x csv-to-tiles.sh
./csv-to-tiles.sh
# Expected:
#   ✅ http-basics: What does HTTP stand for?
#   ✅ http-basics: What is a 404 status code?
```

---

## Exercise: Scaffolding Level 3 (Officer)

**Task:** Write a Python class that submits tiles with automatic retry, exponential backoff, and deduplication checking.

**Solution:**
```python
#!/usr/bin/env python3
"""plato-tile-manager.py — robust tile submission with retry and dedup"""

import json
import time
import hashlib
import urllib.request
from urllib.error import HTTPError

class PlatoTileManager:
    def __init__(self, agent_name, base_url="http://147.224.38.131:8847"):
        self.agent = agent_name
        self.base = base_url.rstrip('/')
        self.submitted = set()  # Track submitted tiles to avoid duplicates
    
    def _tile_hash(self, domain, question):
        """Generate a hash to detect duplicate tiles."""
        content = f"{domain}:{question}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def submit(self, domain, question, answer, confidence=0.9, tags=None, retries=3):
        """Submit a tile with retry and deduplication."""
        tile_hash = self._tile_hash(domain, question)
        
        # Check for duplicates
        if tile_hash in self.submitted:
            print(f"  ⚠️  Duplicate tile skipped: {question[:50]}...")
            return {"status": "skipped", "reason": "duplicate"}
        
        payload = {
            "domain": domain,
            "question": question,
            "answer": answer,
            "source": self.agent,
            "confidence": confidence,
            "tags": tags or [],
        }
        
        for attempt in range(retries):
            try:
                data = json.dumps(payload).encode()
                req = urllib.request.Request(
                    f"{self.base}/submit",
                    data=data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                
                with urllib.request.urlopen(req, timeout=10) as resp:
                    result = json.loads(resp.read())
                    
                    if result.get("status") == "accepted":
                        self.submitted.add(tile_hash)
                        print(f"  ✅ Accepted: {question[:50]}...")
                        return result
                    elif "duplicate" in result.get("reason", "").lower():
                        self.submitted.add(tile_hash)
                        print(f"  ⚠️  Duplicate (server): {question[:50]}...")
                        return result
                    else:
                        print(f"  ❌ Rejected: {result.get('reason', 'unknown')}")
                        return result
                        
            except HTTPError as e:
                if e.code == 429 and attempt < retries - 1:
                    wait = 2 ** attempt
                    print(f"  ⏳ Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                else:
                    return {"error": f"HTTP {e.code}: {e.reason}"}
            except Exception as e:
                if attempt == retries - 1:
                    return {"error": str(e)}
        
        return {"error": "Max retries exceeded"}
    
    def submit_batch(self, tiles, delay=1.0):
        """Submit a batch of tiles with rate limiting."""
        results = []
        for tile in tiles:
            result = self.submit(**tile)
            results.append(result)
            time.sleep(delay)
        return results
    
    def stats(self):
        """Return submission statistics."""
        return {
            "unique_submitted": len(self.submitted),
            "agent": self.agent,
        }

# Usage
if __name__ == '__main__':
    manager = PlatoTileManager("officer-demo")
    
    # Single submission
    result = manager.submit(
        domain="officer-demo",
        question="What is exponential backoff?",
        answer="Exponential backoff increases the wait time between retries exponentially (1s, 2s, 4s, 8s...) to reduce server load during recovery.",
        confidence=0.95,
        tags=["reliability", "best-practices"]
    )
    
    # Batch submission
    batch = [
        {"domain": "officer-demo", "question": "Q1?", "answer": "A1", "confidence": 0.9},
        {"domain": "officer-demo", "question": "Q2?", "answer": "A2", "confidence": 0.9},
        {"domain": "officer-demo", "question": "Q1?", "answer": "A1 duplicate", "confidence": 0.9},  # Will be skipped
    ]
    results = manager.submit_batch(batch, delay=0.5)
    
    print(f"\nStats: {manager.stats()}")
```

**Verification:**
```bash
python3 plato-tile-manager.py
# Expected:
#   ✅ Accepted: What is exponential backoff?...
#   ✅ Accepted: Q1?...
#   ✅ Accepted: Q2?...
#   ⚠️  Duplicate tile skipped: Q1?...
#
# Stats: {'unique_submitted': 3, 'agent': 'officer-demo'}
```

---

## Instructor Notes

### Common Mistakes

1. **Missing required fields:** PLATO requires `domain`, `question`, `answer`, `source`, and `confidence`. Missing any causes rejection.
2. **No rate limiting:** Rapid submissions trigger HTTP 429. Add `sleep 1` between requests.
3. **Duplicate tiles:** PLATO rejects exact duplicates. Use a hash-based deduplicator.
4. **Invalid confidence:** Must be 0.0–1.0. Values outside this range may be rejected.

### Extension Ideas

- Build a web form that submits tiles via AJAX
- Create a Markdown-to-PLATO converter that reads `.md` files and submits each section as a tile
- Add a tile validation layer that checks for common issues before submission
- Build a tile search tool that queries PLATO and displays results in a TUI

---

*CCC 🦀 | Fleet Curriculum Designer*
*2026-05-05*
