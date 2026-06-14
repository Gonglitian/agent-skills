#!/usr/bin/env bash
# Export a Slidev deck to pdf / pptx / png.
# Usage: export.sh <deck_dir> [format=pdf] [extra slidev args...]
#   format: pdf | pptx | png
# Needs deps installed (npm install in deck_dir) incl. playwright-chromium.
set -euo pipefail

DECK_DIR="${1:?usage: export.sh <deck_dir> [pdf|pptx|png] [extra args]}"
FORMAT="${2:-pdf}"
shift || true; shift || true

cd "$DECK_DIR"

if [ ! -d node_modules ]; then
  echo "node_modules missing — running npm install first..."
  npm install
fi

case "$FORMAT" in
  pdf)  npx slidev export slides.md --format pdf "$@" ;;
  pptx) npx slidev export slides.md --format pptx "$@" ;;
  png)  npx slidev export slides.md --format png --output slides-png/ "$@" ;;
  *) echo "unknown format: $FORMAT (use pdf|pptx|png)"; exit 1 ;;
esac

echo "done. output in $DECK_DIR (pptx is per-slide images; not text-editable —"
echo "to get an editable Google Slides, upload the .pptx via Drive with target"
echo "mimeType application/vnd.google-apps.presentation, or use gogcli-slides MCP)."
