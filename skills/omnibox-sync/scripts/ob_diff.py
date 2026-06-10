#!/usr/bin/env python3
"""omnibox-sync · incremental DIFF puller for an OmniBox (小黑) public share.

Minimal-token strategy: list the share tree with METADATA ONLY (cheap), diff the
resource ids + updated_at against a persistent snapshot, and fetch full content
(the expensive call) ONLY for new + changed resources. Then update the snapshot.

Usage:
  ob_diff.py --token <share_token> [--root <id>] \
             [--snapshot ~/.claude/omnibox-sync/<token>.json] \
             [--out-dir .] [--no-changed] [--seed-from-children <children.json>] \
             [--base https://www.omnibox.pro] [--now <iso8601>]

A share token is the slug in omnibox.pro/s/<token>. --root is auto-discovered
from the share metadata when omitted. First run (no snapshot) treats the whole
share as "new" (a full sync); pass --seed-from-children to migrate an existing
metadata dump into the snapshot so a first run only reports the true delta.

Outputs (to --out-dir):
  omnibox_delta_<token>_<stamp>.json   structured: new[] + changed[] + removed[] (+content/tags)
  omnibox_delta_<token>_<stamp>.md     human-readable summary
Exit code 0 always (a no-op delta is a success).
"""
import sys, os, json, time, argparse, urllib.request, urllib.error
import concurrent.futures as cf
from datetime import datetime, timezone

def get(base, path, tries=5):
    url = base + path
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "omnibox-sync/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(1.5 + 1.5 * t); continue
            raise
        except Exception:
            time.sleep(0.8 + 0.5 * t)
    raise RuntimeError(f"GET failed after {tries} tries: {path}")

def walk_tree(base, token, root):
    """Return list of current nodes (METADATA ONLY) via recursion over folders."""
    out = []
    stack = [root]
    while stack:
        rid = stack.pop()
        kids = get(base, f"/api/v1/shares/{token}/resources/{rid}/children")
        for k in kids:
            out.append({
                "id": k["id"],
                "name": k.get("name", ""),
                "resource_type": k.get("resource_type"),
                "url": (k.get("attrs") or {}).get("url", ""),
                "created_at": k.get("created_at"),
                "updated_at": k.get("updated_at"),
                "parent_id": k.get("parent_id"),
            })
            if k.get("has_children"):
                stack.append(k["id"])
    return out

def fetch_content(base, token, node):
    try:
        d = get(base, f"/api/v1/shares/{token}/resources/{node['id']}")
        node = dict(node)
        node["content"] = d.get("content") or ""
        node["tags"] = [t["name"] for t in d.get("tags", [])]
        return node
    except Exception as e:
        node = dict(node); node["content"] = ""; node["tags"] = []; node["fetch_error"] = str(e)
        return node

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True)
    ap.add_argument("--root", default=None)
    ap.add_argument("--snapshot", default=None)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--base", default="https://www.omnibox.pro")
    ap.add_argument("--no-changed", action="store_true", help="ignore updated_at changes; only act on additions")
    ap.add_argument("--seed-from-children", default=None,
                    help="initialize snapshot from a prior children dump (list of {id,updated_at}) if no snapshot exists")
    ap.add_argument("--now", default=None, help="ISO timestamp for stamping (default: system time)")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    snap_path = args.snapshot or os.path.expanduser(f"~/.claude/omnibox-sync/{args.token}.json")
    os.makedirs(os.path.dirname(snap_path), exist_ok=True)
    os.makedirs(args.out_dir, exist_ok=True)
    now_iso = args.now or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    stamp = now_iso.replace(":", "").replace("-", "").replace("T", "_").rstrip("Z")

    # --- discover root ---
    meta = get(args.base, f"/api/v1/shares/{args.token}")
    owner = meta.get("username")
    root = args.root or meta["resource"]["id"]
    print(f"[omnibox-sync] share={args.token} owner={owner} root={root}", file=sys.stderr)

    # --- current tree (metadata only) ---
    current = walk_tree(args.base, args.token, root)
    cur_by_id = {n["id"]: n for n in current}
    print(f"[omnibox-sync] current nodes: {len(current)} (metadata-only, no content)", file=sys.stderr)

    # --- load / seed snapshot ---
    seen = {}  # id -> {updated_at}
    if os.path.exists(snap_path):
        snap = json.load(open(snap_path))
        seen = {i: v for i, v in snap.get("seen", {}).items()}
    elif args.seed_from_children and os.path.exists(args.seed_from_children):
        for k in json.load(open(args.seed_from_children)):
            seen[k["id"]] = {"updated_at": k.get("updated_at")}
        print(f"[omnibox-sync] seeded snapshot from {args.seed_from_children}: {len(seen)} ids", file=sys.stderr)
    first_sync = not seen

    # --- diff (ids + updated_at) ---
    new_ids = [i for i in cur_by_id if i not in seen]
    changed_ids = []
    if not args.no_changed and not first_sync:
        for i in cur_by_id:
            if i in seen and seen[i].get("updated_at") != cur_by_id[i]["updated_at"]:
                changed_ids.append(i)
    removed_ids = [i for i in seen if i not in cur_by_id]
    delta_ids = new_ids + changed_ids
    print(f"[omnibox-sync] DIFF: new={len(new_ids)} changed={len(changed_ids)} removed={len(removed_ids)} "
          f"(first_sync={first_sync})", file=sys.stderr)

    # --- fetch content ONLY for delta ---
    delta_nodes = []
    if delta_ids:
        targets = [cur_by_id[i] for i in delta_ids]
        with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
            delta_nodes = list(ex.map(lambda n: fetch_content(args.base, args.token, n), targets))
    new_set = set(new_ids)
    for n in delta_nodes:
        n["delta_kind"] = "new" if n["id"] in new_set else "changed"

    # --- write delta outputs ---
    base_name = f"omnibox_delta_{args.token}_{stamp}"
    out_json = os.path.join(args.out_dir, base_name + ".json")
    payload = {
        "token": args.token, "owner": owner, "root": root, "synced_at": now_iso,
        "first_sync": first_sync,
        "counts": {"current_total": len(current), "new": len(new_ids),
                   "changed": len(changed_ids), "removed": len(removed_ids)},
        "new": [n for n in delta_nodes if n["delta_kind"] == "new"],
        "changed": [n for n in delta_nodes if n["delta_kind"] == "changed"],
        "removed": [{"id": i, **{k: seen[i].get(k) for k in seen[i]}} for i in removed_ids],
    }
    json.dump(payload, open(out_json, "w"), ensure_ascii=False, indent=1)

    out_md = os.path.join(args.out_dir, base_name + ".md")
    L = [f"# OmniBox delta · `{args.token}` · {now_iso}",
         f"\n> owner: {owner} · 当前总数 {len(current)} · 新增 **{len(new_ids)}** · 变更 **{len(changed_ids)}** · 删除 {len(removed_ids)}"
         + ("  · ⚠️首次全量同步" if first_sync else "") + "\n"]
    def section(title, nodes):
        L.append(f"\n## {title}（{len(nodes)}）\n")
        if not nodes:
            L.append("（无）"); return
        L.append("| # | 类型 | 标题 | 链接 | 标签 | 正文字数 |")
        L.append("|---:|---|---|---|---|---:|")
        for i, n in enumerate(nodes, 1):
            nm = (n["name"] or "").replace("|", "／")[:50]
            url = n.get("url") or ""
            link = f"[↗]({url})" if url else "—"
            tags = "、".join(n.get("tags", [])[:3])
            L.append(f"| {i} | {n.get('resource_type')} | {nm} | {link} | {tags} | {len(n.get('content',''))} |")
    section("新增", payload["new"])
    if not args.no_changed:
        section("变更（已重拉正文）", payload["changed"])
    if removed_ids:
        L.append(f"\n## 删除（仅记录，{len(removed_ids)}）\n")
        for i in removed_ids[:50]:
            L.append(f"- `{i}`")
    open(out_md, "w").write("\n".join(L))

    # --- update snapshot (seen = full current state) ---
    json.dump({
        "token": args.token, "root": root, "owner": owner, "last_sync": now_iso,
        "seen": {n["id"]: {"updated_at": n["updated_at"], "name": n["name"],
                           "resource_type": n["resource_type"]} for n in current},
    }, open(snap_path, "w"), ensure_ascii=False)

    print(f"[omnibox-sync] wrote {out_json}")
    print(f"[omnibox-sync] wrote {out_md}")
    print(f"[omnibox-sync] snapshot updated: {snap_path} ({len(current)} ids)")
    print(f"DELTA_NEW={len(new_ids)} DELTA_CHANGED={len(changed_ids)} DELTA_REMOVED={len(removed_ids)}")

if __name__ == "__main__":
    main()
