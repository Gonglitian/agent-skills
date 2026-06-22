#!/usr/bin/env bash
# Scaffold a Slidev academic deck from this skill's templates — copy, don't hand-write.
#
#   bash scaffold.sh <target_dir> [--install]
#
# Copies the pinned package.json, the Slidev-52 vite.config.ts, the academic style.css
# (flow-diagram primitives + chips/panels/VS/callouts), and a slides.md starter into
# <target_dir>. Existing slides.md / style.css are NOT overwritten. With --install,
# also runs `npm install`. Then edit slides.md and `npm run dev`.
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS="$SKILL_DIR/assets"

TARGET="${1:-}"
if [ -z "$TARGET" ]; then echo "usage: bash scaffold.sh <target_dir> [--install]" >&2; exit 1; fi
mkdir -p "$TARGET/public/figs" "$TARGET/public/media"

# always-safe overwrites (boilerplate the agent should never hand-edit unless extending)
cp "$ASSETS/package.json"   "$TARGET/package.json"
cp "$ASSETS/vite.config.ts" "$TARGET/vite.config.ts"

# do-not-clobber author files
copy_if_absent() { [ -f "$2" ] && echo "kept existing $(basename "$2")" || cp "$1" "$2"; }
copy_if_absent "$ASSETS/style.css"          "$TARGET/style.css"
copy_if_absent "$ASSETS/slides.template.md" "$TARGET/slides.md"

echo "scaffolded Slidev deck at: $TARGET"
if [ "${2:-}" = "--install" ]; then ( cd "$TARGET" && npm install --no-audit --no-fund ); fi
echo "next: cd $TARGET && npm run dev   (build probe: npm run build)"
