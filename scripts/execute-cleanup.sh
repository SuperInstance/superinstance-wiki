#!/bin/bash
# Fleet Cleanup Executor
# Run from /tmp/superinstance-wiki-push/

set -euo pipefail

cd /tmp/superinstance-wiki-push

# --- PRIVATE batch (38 repos) ---
echo "=== PRIVATIZING 38 scaffolds ==="
private_repos=(
  active-probe avx512-constraint-checker cat-agent collective-inference
  desire-loop dotfiles egg eisenstein-cuda eisenstein-vs-z2 embryo
  emergence-detector fleet-consciousness fleet-intel fleet-math-ts
  fleet-miner fleet-phase fleet-simulation fleet-yaw gpu-scaling
  horse-shell mitochondria model-breaking plato-hardware-engine
  plato-voice plato-watch prophet-agent room-micro-models scale-fold
  shell snap-lut-eisenstein sonar-vision-landing spreadsheet-projection
  superinstance-hdc-core test-pages-repo test-tool-extract tile-lifecycle
  training-throttle zhc-yang-mills
)

count=0
for repo in "${private_repos[@]}"; do
  echo "  [PRIVATE] $repo"
  gh repo edit "SuperInstance/$repo" --visibility private 2>/dev/null || echo "    FAILED: $repo"
  count=$((count+1))
  if [ $((count % 5)) -eq 0 ]; then
    echo "  -- paused 2s ($count/${#private_repos[@]}) --"
    sleep 2
  fi
done

echo ""
echo "=== PRIVATIZATION COMPLETE: $count repos ==="

# --- ARCHIVE batch (307 repos) ---
echo ""
echo "=== ARCHIVING 307 dormant orphans ==="

# Read archive list from CLEANUP.md
archive_repos=($(grep "^gh repo archive SuperInstance/" CLEANUP.md | sed 's/gh repo archive SuperInstance\///'))

count=0
for repo in "${archive_repos[@]}"; do
  echo "  [ARCHIVE] $repo"
  gh repo archive "SuperInstance/$repo" --yes 2>/dev/null || echo "    FAILED: $repo"
  count=$((count+1))
  if [ $((count % 5)) -eq 0 ]; then
    echo "  -- paused 2s ($count/${#archive_repos[@]}) --"
    sleep 2
  fi
done

echo ""
echo "=== ARCHIVAL COMPLETE: $count repos ==="

# --- Summary ---
echo ""
echo "=== FLEET CLEANUP SUMMARY ==="
echo "Scaffolds privatized: ${#private_repos[@]}"
echo "Orphans archived: ${#archive_repos[@]}"
echo "Total modified: $(( ${#private_repos[@]} + ${#archive_repos[@]} ))"
