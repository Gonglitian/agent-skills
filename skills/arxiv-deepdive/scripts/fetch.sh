#!/usr/bin/env bash
# arxiv-deepdive · fetch helper
# Downloads paper.pdf and (optionally) shallow-clones the official repo with a size cap.
#
# Usage:
#   fetch.sh <arxiv_id> <target_dir> [repo_url] [max_repo_mb]
#
# Examples:
#   fetch.sh 2406.09246 ./2406.09246_openvla
#   fetch.sh 2406.09246 ./2406.09246_openvla https://github.com/openvla/openvla 800
#
# Output lines (parse these): PDF_OK / PDF_FAIL, REPO_OK <mb>, REPO_LARGE <mb>,
# REPO_CLONE_FAILED, NO_REPO. A REPO_LARGE clone is left on disk so you can read it,
# and REPO_URL.txt is written; per the skill, read what you need then `rm -rf <dir>/repo`.
set -u

ARXIV_ID="${1:?need arxiv id}"
DIR="${2:?need target dir}"
REPO_URL="${3:-}"
MAX_MB="${4:-800}"

mkdir -p "$DIR"

# strip any version suffix (2406.09246v3 -> 2406.09246) for the PDF endpoints
ID_NOVER="$(printf '%s' "$ARXIV_ID" | sed -E 's/v[0-9]+$//')"

# ---------- PDF ----------
PDF="$DIR/paper.pdf"
ok_pdf() { [ -s "$PDF" ] && head -c 5 "$PDF" 2>/dev/null | grep -q '%PDF' && [ "$(stat -c%s "$PDF" 2>/dev/null || echo 0)" -gt 50000 ]; }
for url in "https://arxiv.org/pdf/${ID_NOVER}" "https://export.arxiv.org/pdf/${ID_NOVER}"; do
  curl -fsSL --retry 3 --retry-delay 5 -A "Mozilla/5.0 (arxiv-deepdive)" -o "$PDF" "$url" 2>/dev/null
  ok_pdf && break
  sleep 2
done
if ok_pdf; then echo "PDF_OK $(stat -c%s "$PDF") bytes"; else echo "PDF_FAIL"; fi

# ---------- repo ----------
if [ -z "$REPO_URL" ]; then
  echo "NO_REPO"
  exit 0
fi
RD="$DIR/repo"
rm -rf "$RD"
if GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --filter=blob:none "$REPO_URL" "$RD" >/dev/null 2>&1; then
  SZ="$(du -sm "$RD" 2>/dev/null | cut -f1)"
  if [ "${SZ:-0}" -gt "$MAX_MB" ]; then
    printf '%s\n' "$REPO_URL" > "$DIR/REPO_URL.txt"
    echo "REPO_LARGE ${SZ}MB  (read what you need, then: rm -rf '$RD' ; URL saved to REPO_URL.txt)"
  else
    echo "REPO_OK ${SZ}MB"
  fi
else
  printf '%s\n' "$REPO_URL" > "$DIR/REPO_URL.txt"
  echo "REPO_CLONE_FAILED (URL saved to REPO_URL.txt; read files via WebFetch on the GitHub page)"
fi
