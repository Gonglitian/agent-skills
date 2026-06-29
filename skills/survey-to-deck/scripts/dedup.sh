#!/usr/bin/env bash
# survey-to-deck 阶段②:对 OmniBox 语料去重。
# 用法: dedup.sh <arxiv_id> [<arxiv_id> ...]
#   或: dedup.sh -f ids.txt          # 从文件读(每行一个 id,# 注释忽略)
# 打印每个 id 是 NEW(库里没有,要深读) 还是 SKIP(已有目录),并在末尾汇总。
# 末尾把 NEW 的 id 各占一行打印到 stderr 之外的 fd? —— 简单起见全部走 stdout,NEW 行以 "NEW " 前缀,便于 grep。
set -euo pipefail

CORPUS="${OMNIBOX_CORPUS:-$HOME/proj/omnibox/papers}"

ids=()
if [ "${1:-}" = "-f" ]; then
  [ -n "${2:-}" ] || { echo "usage: dedup.sh -f ids.txt" >&2; exit 2; }
  while IFS= read -r line; do
    line="${line%%#*}"; line="$(echo "$line" | tr -d '[:space:]')"
    [ -n "$line" ] && ids+=("$line")
  done < "$2"
else
  [ "$#" -ge 1 ] || { echo "usage: dedup.sh <arxiv_id> [...]  |  dedup.sh -f ids.txt" >&2; exit 2; }
  ids=("$@")
fi

new=0; skip=0
for id in "${ids[@]}"; do
  id="${id%v[0-9]}"; id="${id%v[0-9][0-9]}"   # 去掉尾部版本号 v1/v2/...
  hit="$(find "$CORPUS" -maxdepth 2 -type d -name "${id}_*" 2>/dev/null | head -1)"
  if [ -n "$hit" ]; then
    echo "SKIP $id  -> ${hit#$CORPUS/}"
    skip=$((skip+1))
  else
    echo "NEW  $id"
    new=$((new+1))
  fi
done

echo "----- $new NEW / $skip SKIP (corpus: $CORPUS) -----" >&2
