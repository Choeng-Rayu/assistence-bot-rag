#!/usr/bin/env bash
# Verify the frozen corpus has exactly 14 Markdown docs and print their hashes.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/data/docs"

count="$(find "$DEST" -maxdepth 1 -name '*.md' -type f | wc -l | tr -d ' ')"
if [ "$count" -ne 14 ]; then
  echo "error: expected 14 docs in $DEST, found $count" >&2
  exit 1
fi

echo "OK: 14 frozen docs in $DEST"
# shellcheck disable=SC2012
ls "$DEST"/*.md | sort | xargs sha256sum
