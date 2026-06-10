#!/usr/bin/env python3
"""List video targets from an OmniBox share: Bilibili (b23.tv/bilibili) + Xiaohongshu type=video.
Usage: list_videos.py --token <share_token> [--root <id>] [--out video_targets.json] [--base https://www.omnibox.pro]
Metadata-only (one cheap /children call per folder, recurses on has_children). No content fetched.
"""
import json, argparse, urllib.request
from urllib.parse import urlparse, parse_qs

def get(base, path):
    req = urllib.request.Request(base + path, headers={"User-Agent": "omnibox-video/1.0"})
    return json.load(urllib.request.urlopen(req, timeout=30))

def walk(base, token, root):
    out, stack = [], [root]
    while stack:
        rid = stack.pop()
        for k in get(base, f"/api/v1/shares/{token}/resources/{rid}/children"):
            out.append(k)
            if k.get("has_children"):
                stack.append(k["id"])
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True)
    ap.add_argument("--root", default=None)
    ap.add_argument("--out", default="video_targets.json")
    ap.add_argument("--base", default="https://www.omnibox.pro")
    a = ap.parse_args()
    meta = get(a.base, f"/api/v1/shares/{a.token}")
    root = a.root or meta["resource"]["id"]
    targets = []
    for k in walk(a.base, a.token, root):
        if k.get("resource_type") != "link":
            continue
        u = (k.get("attrs") or {}).get("url", "")
        host = urlparse(u).netloc.lower().replace("www.", "")
        typ = parse_qs(urlparse(u).query).get("type", [""])[0]
        if "b23.tv" in host or "bilibili" in host:
            targets.append({"id": k["id"], "name": k.get("name", ""), "url": u, "src": "bilibili"})
        elif "xiaohongshu" in host and typ == "video":
            targets.append({"id": k["id"], "name": k.get("name", ""), "url": u, "src": "xhs"})
    json.dump(targets, open(a.out, "w"), ensure_ascii=False, indent=0)
    from collections import Counter
    print(f"video targets: {len(targets)} {dict(Counter(t['src'] for t in targets))} -> {a.out}")

if __name__ == "__main__":
    main()
