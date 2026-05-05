#!/usr/bin/env python3
"""
plato-query.py — CCC 🦀

Query and search PLATO tiles. Find knowledge by domain, tags, or keywords.

Usage:
    python3 plato-query.py --room curriculum-recruit
    python3 plato-query.py --tags "curriculum,http_curl"
    python3 plato-query.py --search "GUARD"
    python3 plato-query.py --status
"""

import sys
import json
import urllib.request

PLATO_BASE = "http://147.224.38.131:8847"

def plato_api(path):
    url = f"{PLATO_BASE}{path}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def get_status():
    return plato_api("/status")

def get_room_tiles(room):
    return plato_api(f"/room/{room}")

def search_tiles(query):
    # PLATO may not have a search endpoint, but we can query status and filter
    status = get_status()
    if "error" in status:
        return status
    
    rooms = status.get("rooms", {})
    results = []
    
    for room_name, room_data in rooms.items() if isinstance(rooms, dict) else []:
        # Try to get tiles for this room
        tiles = get_room_tiles(room_name)
        if "error" in tiles:
            continue
        
        # Filter tiles by query
        for tile in tiles.get("tiles", []):
            text = f"{tile.get('question', '')} {tile.get('answer', '')}"
            if query.lower() in text.lower():
                results.append({
                    "room": room_name,
                    "tile": tile,
                })
    
    return {"results": results, "count": len(results)}

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 plato-query.py --status")
        print("  python3 plato-query.py --room ROOM_NAME")
        print("  python3 plato-query.py --search KEYWORD")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "--status":
        status = get_status()
        if "error" in status:
            print(f"Error: {status['error']}")
            return
        
        print("PLATO Status")
        print("=" * 50)
        rooms = status.get("rooms", {})
        if isinstance(rooms, dict):
            print(f"Rooms: {len(rooms)}")
            for name, data in sorted(rooms.items()):
                if isinstance(data, dict):
                    count = data.get("tile_count", data.get("count", "?"))
                else:
                    count = data
                print(f"  {name}: {count} tiles")
        
        tiles = status.get("tiles", {})
        if isinstance(tiles, dict):
            print(f"Tiles accepted: {tiles.get('accepted', '?')}")
            print(f"Tiles rejected: {tiles.get('rejected', '?')}")
    
    elif cmd == "--room" and len(sys.argv) > 2:
        room = sys.argv[2]
        tiles = get_room_tiles(room)
        if "error" in tiles:
            print(f"Error: {tiles['error']}")
            return
        
        print(f"Room: {room}")
        print("=" * 50)
        for tile in tiles.get("tiles", []):
            q = tile.get("question", "?")[:80]
            a = tile.get("answer", "?")[:120]
            print(f"Q: {q}")
            print(f"A: {a}")
            print(f"  Source: {tile.get('source', '?')} | Confidence: {tile.get('confidence', '?')}")
            print()
    
    elif cmd == "--search" and len(sys.argv) > 2:
        query = sys.argv[2]
        results = search_tiles(query)
        if "error" in results:
            print(f"Error: {results['error']}")
            return
        
        print(f"Search: '{query}'")
        print(f"Results: {results.get('count', 0)}")
        print("=" * 50)
        for r in results.get("results", []):
            tile = r["tile"]
            print(f"Room: {r['room']}")
            print(f"Q: {tile.get('question', '?')[:80]}")
            print()
    
    else:
        print(f"Unknown command: {cmd}")
        print("Use --status, --room, or --search")

if __name__ == '__main__':
    main()
