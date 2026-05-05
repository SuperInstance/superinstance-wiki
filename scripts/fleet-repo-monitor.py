#!/usr/bin/env python3
"""
fleet-repo-monitor.py — CCC 🦀

Monitor all fleet repos for new commits and report changes.
Run periodically (e.g., via cron) to track fleet activity.

Usage:
    python3 fleet-repo-monitor.py
    python3 fleet-repo-monitor.py --since 2026-05-01  # Only commits since date
    python3 fleet-repo-monitor.py --json               # Output JSON

Repos tracked:
    SuperInstance/fleet-bottles       — CCC's relay
    SuperInstance/flux-research       — FM's dissertation + EMSOFT paper
    SuperInstance/cocapn-curriculum   — Fleet learning system
    SuperInstance/cocapn-reviews      — Design reviews
    SuperInstance/cocapn-ai           — Landing page (if accessible)
    SuperInstance/plato-voice         — Voice interface
    SuperInstance/plato-room-phi      — Room coherence
    SuperInstance/flux-c-vm           — FLUX-C VM (if exists)
    SuperInstance/purplepincher.org   — Scholar recruitment
"""

import sys
import json
import subprocess
import urllib.request
from datetime import datetime, timezone

REPOS = [
    ("fleet-bottles", "SuperInstance/fleet-bottles"),
    ("flux-research", "SuperInstance/flux-research"),
    ("cocapn-curriculum", "SuperInstance/cocapn-curriculum"),
    ("cocapn-reviews", "SuperInstance/cocapn-reviews"),
    ("cocapn-ai", "SuperInstance/cocapn.ai"),
    ("plato-voice", "SuperInstance/plato-voice"),
    ("plato-room-phi", "SuperInstance/plato-room-phi"),
    ("purplepincher", "SuperInstance/purplepincher.org"),
]

def get_commits(repo_slug, since=None, limit=5):
    """Fetch recent commits from GitHub API."""
    url = f"https://api.github.com/repos/{repo_slug}/commits?per_page={limit}"
    if since:
        url += f"&since={since}T00:00:00Z"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('Accept', 'application/vnd.github.v3+json')
        req.add_header('User-Agent', 'fleet-monitor-ccc')
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return [
                {
                    "sha": c["sha"][:7],
                    "message": c["commit"]["message"].split('\n')[0],
                    "author": c["commit"]["author"]["name"],
                    "date": c["commit"]["author"]["date"],
                    "url": c["html_url"],
                }
                for c in data
            ]
    except Exception as e:
        return [{"error": str(e)}]

def get_repo_info(repo_slug):
    """Fetch repo metadata."""
    url = f"https://api.github.com/repos/{repo_slug}"
    try:
        req = urllib.request.Request(url)
        req.add_header('Accept', 'application/vnd.github.v3+json')
        req.add_header('User-Agent', 'fleet-monitor-ccc')
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return {
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "issues": data.get("open_issues_count", 0),
                "updated": data.get("updated_at"),
                "language": data.get("language"),
            }
    except Exception as e:
        return {"error": str(e)}

def main():
    since = None
    json_mode = False
    
    for i, arg in enumerate(sys.argv[1:]):
        if arg == '--since' and i + 1 < len(sys.argv[1:]):
            since = sys.argv[i + 2]
        elif arg == '--json':
            json_mode = True
    
    results = []
    
    for name, slug in REPOS:
        info = get_repo_info(slug)
        commits = get_commits(slug, since)
        
        result = {
            "name": name,
            "slug": slug,
            "info": info,
            "commits": commits,
        }
        results.append(result)
    
    if json_mode:
        print(json.dumps(results, indent=2))
        return
    
    print("=" * 70)
    print("FLEET REPO MONITOR — CCC 🦀")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    if since:
        print(f"Since: {since}")
    print("=" * 70)
    
    for repo in results:
        print(f"\n📦 {repo['name']}")
        print(f"   https://github.com/{repo['slug']}")
        
        info = repo['info']
        if 'error' in info:
            print(f"   ⚠️  Error: {info['error']}")
            continue
        
        print(f"   ⭐ {info.get('stars', 0)}  🍴 {info.get('forks', 0)}  🐛 {info.get('issues', 0)}  📅 {info.get('updated', '?')[:10]}")
        
        print(f"   Recent commits:")
        for commit in repo['commits'][:3]:
            if 'error' in commit:
                print(f"      ⚠️  {commit['error']}")
                break
            date_str = commit['date'][:10]
            print(f"      {date_str}  {commit['sha']}  {commit['message'][:50]}")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
