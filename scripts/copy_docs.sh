#!/usr/bin/env bash
# Copy the 14 frozen Markdown docs from the reference rayu-web checkout.
#
# The source repository is read-only: this script only copies files. Never
# edit files under $SRC. Re-running is idempotent.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${RAYU_WEB_DIR:-/home/rayu/rayu/rayu-web}/public/docs"
DEST="$ROOT/data/docs"

DOCS=(
  01-installation
  02-quickstart
  03-providers
  04-models
  05-configuration
  06-cli-reference
  07-slash-commands
  10-troubleshooting
  15-api-keys
  17-vscode-extension
  18-subscription-plans
  19-credits-and-limits
  20-how-token-credit-charge
  21-policies
)

if [ ! -d "$SRC" ]; then
  echo "error: source docs directory not found: $SRC" >&2
  echo "hint: set RAYU_WEB_DIR to the rayu-web checkout" >&2
  exit 1
fi

mkdir -p "$DEST"
for name in "${DOCS[@]}"; do
  cp "$SRC/$name.md" "$DEST/$name.md"
done

count="$(find "$DEST" -maxdepth 1 -name '*.md' -type f | wc -l | tr -d ' ')"
if [ "$count" -ne 14 ]; then
  echo "error: expected 14 docs in $DEST, found $count" >&2
  exit 1
fi

echo "copied 14 docs into $DEST"
