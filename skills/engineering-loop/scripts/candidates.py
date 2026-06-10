#!/usr/bin/env python3
"""Append-only manager for candidates.jsonl — the candidate DAG of the engineering loop.

No third-party deps. Run from the task workspace (where candidates.jsonl lives), or
pass --file. Every terminal status should carry a --reason so dead ends are never
re-explored.

Examples:
  python3 candidates.py add  --id c4 --parent c3 --summary "multi-block radix" --status exploring
  python3 candidates.py set  c4 --status rejected --reason "sync overhead cancels gain"
  python3 candidates.py set  c3 --status promoted --metric latency_us=7.1 --baseline latency_us=73.6
  python3 candidates.py list --status promoted
  python3 candidates.py tree
"""
import argparse, json, os, sys

DEFAULT = "candidates.jsonl"


def _load(path):
    rows = []
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def _dump(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _kv(pairs):
    out = {}
    for p in pairs or []:
        if "=" not in p:
            sys.exit(f"expected key=value, got {p!r}")
        k, v = p.split("=", 1)
        try:
            v = float(v) if ("." in v or "e" in v.lower()) else int(v)
        except ValueError:
            pass
        out[k] = v
    return out


def cmd_add(a):
    rows = _load(a.file)
    if any(r["id"] == a.id for r in rows):
        sys.exit(f"id {a.id!r} already exists; use 'set' to update it")
    parent = a.parent or None  # treat "" as no parent (root)
    rows.append({
        "id": a.id, "parent": parent, "summary": a.summary,
        "status": a.status, "validated": a.validated,
        "metric": _kv(a.metric), "baseline_metric": _kv(a.baseline),
        "reason": a.reason or "", "created": a.created or "",
    })
    _dump(a.file, rows)
    print(f"added {a.id}")


def cmd_set(a):
    rows = _load(a.file)
    hit = next((r for r in rows if r["id"] == a.id), None)
    if not hit:
        sys.exit(f"no candidate {a.id!r}")
    if a.status: hit["status"] = a.status
    if a.reason is not None: hit["reason"] = a.reason
    if a.validated is not None: hit["validated"] = a.validated
    if a.metric: hit["metric"] = _kv(a.metric)
    if a.baseline: hit["baseline_metric"] = _kv(a.baseline)
    if a.status in ("promoted", "rejected") and not hit.get("reason"):
        print("WARNING: terminal status with no reason — record why.", file=sys.stderr)
    _dump(a.file, rows)
    print(f"updated {a.id}")


def cmd_list(a):
    rows = _load(a.file)
    if a.status:
        rows = [r for r in rows if r.get("status") == a.status]
    for r in rows:
        m = r.get("metric") or {}
        b = r.get("baseline_metric") or {}
        ms = " ".join(f"{k}={v}" for k, v in m.items())
        bs = " ".join(f"{k}={v}" for k, v in b.items())
        print(f"{r['id']:<6} {r.get('status',''):<10} val={r.get('validated')} "
              f"[{ms}] vs base[{bs}]  {r.get('summary','')}")
        if r.get("reason"):
            print(f"       └─ {r['reason']}")


def cmd_tree(a):
    rows = _load(a.file)
    by_parent = {}
    for r in rows:
        by_parent.setdefault(r.get("parent"), []).append(r)

    def walk(pid, depth):
        for r in by_parent.get(pid, []):
            print("  " * depth + f"{r['id']} [{r.get('status','')}] {r.get('summary','')}")
            walk(r["id"], depth + 1)
    walk(None, 0)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", default=DEFAULT)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add"); a.set_defaults(fn=cmd_add)
    a.add_argument("--id", required=True)
    a.add_argument("--parent", default=None)
    a.add_argument("--summary", required=True)
    a.add_argument("--status", default="exploring")
    a.add_argument("--validated", type=lambda s: s.lower() == "true", default=None)
    a.add_argument("--metric", nargs="*", help="key=value ...")
    a.add_argument("--baseline", nargs="*", help="key=value ...")
    a.add_argument("--reason", default=None)
    a.add_argument("--created", default=None)

    s = sub.add_parser("set"); s.set_defaults(fn=cmd_set)
    s.add_argument("id")
    s.add_argument("--status", default=None)
    s.add_argument("--validated", type=lambda x: x.lower() == "true", default=None)
    s.add_argument("--metric", nargs="*")
    s.add_argument("--baseline", nargs="*")
    s.add_argument("--reason", default=None)

    l = sub.add_parser("list"); l.set_defaults(fn=cmd_list)
    l.add_argument("--status", default=None)

    t = sub.add_parser("tree"); t.set_defaults(fn=cmd_tree)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
