#!/usr/bin/env python3
"""
submit-curriculum-tiles.py — CCC 🦀

Batch-submit all curriculum lessons as PLATO tiles.
Run this after curriculum updates to populate the knowledge lattice.

Usage:
    python3 submit-curriculum-tiles.py --dry-run    # Preview
    python3 submit-curriculum-tiles.py              # Live submit
"""

import sys
import os
import json
import glob
import urllib.request
from datetime import datetime

PLATO_URL = "http://147.224.38.131:8847/submit"

def parse_lesson(path):
    import re
    with open(path) as f:
        content = f.read()
    
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else os.path.basename(path)
    
    level_match = re.search(r'\*\*Level:\*\*\s*(\w+)', content)
    level = level_match.group(1) if level_match else "Unknown"
    
    competency_match = re.search(r'\*\*Competency:\*\*\s*(\w+)', content)
    competency = competency_match.group(1) if competency_match else "general"
    
    # Extract first learning objective
    obj_match = re.search(r'\d+\.\s+(.+?)(?=\n\d+\.|\n##)', content, re.DOTALL)
    objective = obj_match.group(1).strip() if obj_match else "Fleet skill"
    
    return {
        "title": title,
        "level": level,
        "competency": competency,
        "objective": objective,
        "path": path,
    }

def submit_tile(tile, dry_run=False):
    if dry_run:
        print(f"  [DRY] {tile['domain']}: {tile['question'][:60]}...")
        return True
    
    try:
        data = json.dumps(tile).encode('utf-8')
        req = urllib.request.Request(
            PLATO_URL,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            accepted = result.get('status') == 'accepted' or result.get('accepted', False)
            status = "✅" if accepted else "❌"
            print(f"  {status} {tile['question'][:60]}...")
            if not accepted:
                print(f"     Response: {json.dumps(result)[:200]}")
            return accepted
    except urllib.error.HTTPError as e:
        print(f"  ❌ HTTP {e.code}: {e.reason}")
        try:
            err_body = e.read().decode()
            print(f"     Body: {err_body[:200]}")
        except:
            pass
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def lesson_to_tile(lesson, unique_id=""):
    domain = f"curriculum-{lesson['level'].lower()}"
    # Make question unique to avoid duplicate rejection
    uid = unique_id or f"{datetime.now().strftime('%Y%m%d')}"
    return {
        "domain": domain,
        "question": f"[Fleet Curriculum v{uid}] What competency does '{lesson['title']}' teach?",
        "answer": f"Competency: {lesson['competency']}. Level: {lesson['level']}. Objective: {lesson['objective'][:120]}. Full lesson: https://github.com/SuperInstance/cocapn-curriculum/tree/main/lessons",
        "source": "ccc-curriculum",
        "confidence": 0.95,
        "tags": ["curriculum", lesson['competency'], lesson['level'].lower(), "fleet-training"],
    }

def main():
    dry_run = '--dry-run' in sys.argv
    lessons_dir = os.path.join(os.path.dirname(__file__), '..', 'lessons')
    
    if not os.path.exists(lessons_dir):
        print(f"Lessons directory not found: {lessons_dir}")
        sys.exit(1)
    
    pattern = os.path.join(lessons_dir, '*.md')
    files = sorted(glob.glob(pattern))
    
    print(f"Found {len(files)} lessons")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"PLATO endpoint: {PLATO_URL}")
    print()
    
    total = 0
    accepted = 0
    
    for path in files:
        lesson = parse_lesson(path)
        tile = lesson_to_tile(lesson)
        print(f"Submitting: {lesson['title'][:50]}")
        if submit_tile(tile, dry_run):
            accepted += 1
        total += 1
    
    print()
    print(f"{'='*50}")
    print(f"Total: {total}")
    print(f"Accepted: {accepted}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
