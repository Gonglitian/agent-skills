#!/usr/bin/env bash
# Scaffold a Slidev paper-talk deck.
# Usage: new-deck.sh <deck_dir> ["Deck Title"]
# Creates <deck_dir>/{slides.md, package.json, public/, papers/} from the skill's assets.
set -euo pipefail

DECK_DIR="${1:?usage: new-deck.sh <deck_dir> [\"Deck Title\"]}"
TITLE="${2:-论文串讲}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ASSETS="$SKILL_DIR/assets"

mkdir -p "$DECK_DIR/public" "$DECK_DIR/papers"

# slides.md from template (only if absent — don't clobber an in-progress deck)
if [ -f "$DECK_DIR/slides.md" ]; then
  echo "NOTE: $DECK_DIR/slides.md already exists, leaving it untouched."
else
  sed "s|论文串讲 — <主题>|$TITLE|; s|# 论文串讲：<主题>|# $TITLE|" \
    "$ASSETS/deck-template.md" > "$DECK_DIR/slides.md"
  echo "wrote $DECK_DIR/slides.md"
fi

# package.json (always refresh deps file; harmless to overwrite)
cp "$ASSETS/package.json" "$DECK_DIR/package.json"
echo "wrote $DECK_DIR/package.json"

# keep public/ tracked even when empty
touch "$DECK_DIR/public/.gitkeep"

cat <<EOF

deck scaffolded at: $DECK_DIR
  slides.md   主文件(已套用模板,按大纲填充;每篇可拆到 papers/<arxiv>.md 用 src 引入)
  public/     放抽出的 method 原图,slide 里用 /<arxiv>/fig.png 引用
  papers/     每篇论文单独的 .md(可选)

next:
  cd "$DECK_DIR"
  npm install          # 首次:装 slidev + 主题 + playwright(导出用)
  npm run dev          # 浏览器现场演示 http://localhost:3030
EOF
