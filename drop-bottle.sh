#!/bin/bash
# CCC Bottle Drop — Quick push script for real-time bottle delivery
# Usage: ./drop-bottle.sh "description" filepath.md

REPO="https://github.com/SuperInstance/fleet-bottles"
DATE=$(date +%Y-%m-%d)
BOTTLE_DIR="bottles/$DATE"

cd /tmp/fleet-bottles 2>/dev/null || {
  git clone --depth 1 $REPO /tmp/fleet-bottles
  cd /tmp/fleet-bottles
}

mkdir -p "$BOTTLE_DIR"
cp "$2" "$BOTTLE_DIR/"
git add "$BOTTLE_DIR/"
git commit -m "CCC: $1 ($DATE)"
git push

echo "Bottle dropped: $REPO/blob/master/$BOTTLE_DIR/$(basename $2)"
