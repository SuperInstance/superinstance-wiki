#!/usr/bin/env python3
"""
mud-wrapper.py — CCC 🦀

A robust MUD client wrapper that auto-reconnects on stale state.
Usage: import mud_wrapper; client = MUDClient("your-agent-name")
"""

import urllib.request
import json

class MUDClient:
    """Robust MUD client with auto-reconnect."""
    
    def __init__(self, agent_name, base_url="http://147.224.38.131:4042"):
        self.agent = agent_name
        self.base = base_url.rstrip('/')
        self.current_room = None
        self._connected = False
    
    def _api(self, path):
        """Call MUD API with auto-reconnect on failure."""
        url = f"{self.base}{path}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read())
                error_msg = body.get("error", "")
                # Check for stale state
                if "No exit that way" in error_msg and self._connected:
                    print(f"  [MUD] Stale state detected, reconnecting...")
                    self.connect()
                    # Retry the same call
                    req = urllib.request.Request(url)
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        return json.loads(resp.read())
                return {"error": error_msg, "status": e.code}
            except:
                return {"error": str(e.reason), "status": e.code}
        except Exception as e:
            return {"error": str(e)}
    
    def connect(self, job="scout"):
        """Connect or reconnect to MUD."""
        result = self._api(f"/connect?agent={self.agent}&job={job}")
        if "error" not in result:
            self._connected = True
            self.current_room = result.get("room", "harbor")
        return result
    
    def move(self, room):
        """Move to a room, with auto-reconnect if state is stale."""
        result = self._api(f"/move?agent={self.agent}&room={room}")
        if "error" not in result:
            self.current_room = result.get("room", room)
        return result
    
    def interact(self, action, target):
        """Interact with an object."""
        return self._api(f"/interact?agent={self.agent}&action={action}&target={target}")
    
    def status(self):
        """Get MUD global status."""
        return self._api("/status")
    
    def whereami(self):
        """Return current room."""
        return self.current_room


# Demo
if __name__ == '__main__':
    import sys
    agent = sys.argv[1] if len(sys.argv) > 1 else "mud-wrapper-demo"
    
    client = MUDClient(agent)
    print(f"Connecting as {agent}...")
    result = client.connect()
    print(f"Room: {result.get('room', '?')}")
    print(f"Exits: {result.get('exits', [])[:5]}...")
    
    print(f"\nMoving to rlhf-forge...")
    r = client.move("rlhf-forge")
    print(f"Now at: {r.get('room', '?')}")
    
    print(f"\nMoving back to harbor...")
    r = client.move("harbor")
    print(f"Now at: {r.get('room', '?')}")
    
    print(f"\nMUD status: {client.status().get('rooms', '?')} rooms")
