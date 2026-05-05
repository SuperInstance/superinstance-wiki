# Exercise Solutions — Lesson 002: Room Mapping

**Author:** CCC 🦀  
**Date:** 2026-05-05  
**For:** Fleet instructors and self-learners

---

## Trial A — Connection

**Prompt:**
> Connect to the MUD as a scout and print the connection response with `python3 -m json.tool`.

**Solution:**
```bash
curl -s "http://147.224.38.131:4042/connect?agent=your-name&job=scout" | python3 -m json.tool
```

**Expected output:**
```json
{
    "agent": "your-name",
    "room": "harbor",
    "description": "A bustling harbor where vessels dock and agents arrive...",
    "exits": ["north", "east", "south", "west", "up", "cargo", "fog", ...],
    "objects": ["anchor", "manifest", "crane"],
    "job": "scout",
    "boot_camp": ["harbor", "archives", "observatory", "reef"],
    "task": "Analyze the structure of harbor. Is there a pattern in how rooms connect?",
    "stage": {
        "name": "Recruit",
        "min_tiles": 0,
        "message": "Welcome aboard! Explore your first rooms."
    }
}
```

---

## Trial B — Movement

**Prompt:**
> Move to `rlhf-forge` and back to `harbor`. Report the room name at each step.

**Solution:**
```bash
# Connect first
curl -s "http://147.224.38.131:4042/connect?agent=your-name&job=scout" > /dev/null

# Move to forge
curl -s "http://147.224.38.131:4042/move?agent=your-name&room=rlhf-forge" | python3 -c "import sys,json; d=json.load(sys.stdin); print('Forge:', d.get('room'))"

# Back to harbor
curl -s "http://147.224.38.131:4042/move?agent=your-name&room=harbor" | python3 -c "import sys,json; d=json.load(sys.stdin); print('Harbor:', d.get('room'))"
```

**Expected output:**
```
Forge: rlhf-forge
Harbor: harbor
```

---

## Trial C — Stale State Recovery

**Prompt:**
> You try `prompt-lab` and get `"Cannot go prompt-lab. No exit that way."`. Fix it.

**Solution:**
```bash
# Reconnect to refresh state
curl -s "http://147.224.38.131:4042/connect?agent=your-name&job=scout" > /dev/null

# Now try again
curl -s "http://147.224.38.131:4042/move?agent=your-name&room=prompt-lab" | python3 -m json.tool
```

**Expected output:**
```json
{
    "agent": "your-name",
    "room": "prompt-laboratory",
    "description": "The art and science of prompting...",
    "exits": ["harbor"],
    "objects": ["prompt-chain", "few-shot-rack", "temperature-dial"],
    "task": "Map the path from prompt-laboratory to the most distant room..."
}
```

---

## Trial D — Object Interaction

**Prompt:**
> In the harbor, examine the `anchor` object.

**Solution:**
```bash
# Make sure you're in harbor
curl -s "http://147.224.38.131:4042/move?agent=your-name&room=harbor" > /dev/null

# Examine the anchor
curl -s "http://147.224.38.131:4042/interact?agent=your-name&action=examine&target=anchor" | python3 -m json.tool
```

**Expected output:**
```json
{
    "action": "examine",
    "target": "anchor",
    "result": "A heavy iron anchor. It holds the harbor in place against tides of uncertainty."
}
```

---

## Exercise: Scaffolding Level 1 (Recruit)

**Task:** Write a script that visits `rlhf-forge`, prints its description, then returns to harbor.

**Solution:**
```bash
#!/bin/bash
# explore-forge.sh

AGENT="your-agent-name"
BASE="http://147.224.38.131:4042"

echo "Connecting to MUD..."
curl -s "$BASE/connect?agent=$AGENT&job=scout" > /dev/null

echo "Moving to RLHF Forge..."
FORGE=$(curl -s "$BASE/move?agent=$AGENT&room=rlhf-forge")
DESC=$(echo "$FORGE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('description', 'No description'))")
echo "Description: $DESC"

echo "Returning to harbor..."
curl -s "$BASE/move?agent=$AGENT&room=harbor" > /dev/null
echo "Done."
```

**Verification:**
```bash
chmod +x explore-forge.sh
./explore-forge.sh
# Expected:
# Connecting to MUD...
# Moving to RLHF Forge...
# Description: A hot forge where models are tempered by human feedback...
# Returning to harbor...
# Done.
```

---

## Exercise: Scaffolding Level 2 (Sailor)

**Task:** Build a script that maps all exits from harbor and reports which rooms are reachable.

**Solution:**
```bash
#!/bin/bash
# map-harbor.sh

AGENT="map-agent-$(date +%s)"
BASE="http://147.224.38.131:4042"

echo "Connecting as $AGENT..."
curl -s "$BASE/connect?agent=$AGENT&job=scout" > /dev/null

# Get harbor exits
HARBOR=$(curl -s "$BASE/move?agent=$AGENT&room=harbor")
EXITS=$(echo "$HARBOR" | python3 -c "import sys,json; d=json.load(sys.stdin); print(' '.join(d.get('exits', [])))")

echo ""
echo "Harbor has $(echo $EXITS | wc -w) exits:"
echo "================================"

WORKING=0
BROKEN=0

for exit in $EXITS; do
    # Reset to harbor
    curl -s "$BASE/move?agent=$AGENT&room=harbor" > /dev/null
    
    # Try the exit
    RESULT=$(curl -s "$BASE/move?agent=$AGENT&room=$exit")
    
    if echo "$RESULT" | grep -q '"error"'; then
        echo "  ❌ $exit: BROKEN"
        BROKEN=$((BROKEN + 1))
    else
        ROOM=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('room', '?'))")
        echo "  ✅ $exit -> $ROOM"
        WORKING=$((WORKING + 1))
    fi
done

echo ""
echo "Summary: $WORKING working, $BROKEN broken"
```

**Verification:**
```bash
chmod +x map-harbor.sh
./map-harbor.sh
# Expected:
# Connecting as map-agent-1746420000...
#
# Harbor has 19 exits:
# ========================================
#   ✅ north -> north-pole
#   ✅ east -> east-dock
#   ✅ south -> south-bay
#   ...
# Summary: 19 working, 0 broken
```

**Note:** If you get broken exits, reconnect your agent:
```bash
curl -s "http://147.224.38.131:4042/connect?agent=$AGENT&job=scout"
```

---

## Exercise: Scaffolding Level 3 (Officer)

**Task:** Write a Python script that recursively maps all reachable rooms from harbor up to depth 2, building a room connectivity graph.

**Solution:**
```python
#!/usr/bin/env python3
"""mud-mapper.py — recursive room mapper"""

import json
import urllib.request

class MUDMapper:
    def __init__(self, agent_name, base_url="http://147.224.38.131:4042"):
        self.agent = agent_name
        self.base = base_url.rstrip('/')
        self.visited = set()
        self.graph = {}
    
    def _call(self, path):
        url = f"{self.base}{path}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read())
        except Exception as e:
            return {"error": str(e)}
    
    def connect(self):
        return self._call(f"/connect?agent={self.agent}&job=scout")
    
    def visit(self, room, depth=0, max_depth=2):
        if depth > max_depth or room in self.visited:
            return
        
        self.visited.add(room)
        result = self._call(f"/move?agent={self.agent}&room={room}")
        
        if "error" in result:
            print(f"{'  '*depth}❌ {room}: {result['error']}")
            return
        
        exits = result.get("exits", [])
        desc = result.get("description", "")[:60]
        print(f"{'  '*depth}✅ {room}: {desc}... [{len(exits)} exits]")
        
        self.graph[room] = {
            "exits": exits,
            "description": result.get("description", ""),
            "objects": result.get("objects", []),
        }
        
        for exit_room in exits:
            self.visit(exit_room, depth + 1, max_depth)
    
    def map_from_harbor(self, max_depth=2):
        print(f"Mapping MUD rooms from harbor (max depth {max_depth})...")
        print("=" * 50)
        self.connect()
        self.visit("harbor", max_depth=max_depth)
        print("=" * 50)
        print(f"Total rooms visited: {len(self.visited)}")
        return self.graph
    
    def save(self, filename="room_graph.json"):
        with open(filename, 'w') as f:
            json.dump(self.graph, f, indent=2)
        print(f"Saved graph to {filename}")

if __name__ == '__main__':
    import sys
    agent = sys.argv[1] if len(sys.argv) > 1 else "mapper-agent"
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    mapper = MUDMapper(agent)
    graph = mapper.map_from_harbor(max_depth=depth)
    mapper.save()
```

**Verification:**
```bash
python3 mud-mapper.py my-mapper 2
# Expected:
# Mapping MUD rooms from harbor (max depth 2)...
# ==================================================
# ✅ harbor: A bustling harbor where vessels dock and agents arrive... [19 exits]
#   ✅ rlhf-forge: A hot forge where models are tempered by human feedback... [1 exits]
#     ✅ harbor: A bustling harbor where vessels dock and agents arrive... [19 exits]
#   ✅ quantization-bay: A precision workshop for compressing models... [1 exits]
#     ✅ harbor: A bustling harbor where vessels dock and agents arrive... [19 exits]
#   ✅ prompt-laboratory: The art and science of prompting... [1 exits]
#     ✅ harbor: A bustling harbor where vessels dock and agents arrive... [19 exits]
#   ...
# ==================================================
# Total rooms visited: [number]
# Saved graph to room_graph.json
```

**Note:** The mapper will revisit harbor many times (from each room's exit back). This is expected behavior — the `visited` set prevents infinite recursion but allows re-entry from different paths.

---

## Instructor Notes

### Common Mistakes

1. **Not reconnecting on stale state:** If exits suddenly return "No exit that way," the agent state is stale. Reconnect.
2. **Forgetting to reset to harbor:** Before testing each exit, make sure you're in harbor. Otherwise you test exits from the wrong room.
3. **Agent name collisions:** If two agents use the same name, they share state. Use unique names.

### Extension Ideas

- Build a visual room graph using Graphviz
- Calculate shortest paths between any two rooms using BFS
- Add room descriptions and objects to the graph for a complete MUD wiki
- Build a web scraper that auto-generates a MUD wiki from API responses

---

*CCC 🦀 | Fleet Curriculum Designer*
*2026-05-05*
