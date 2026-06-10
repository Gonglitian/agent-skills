#!/usr/bin/env python3
"""Query a domain wiki: search and fetch entries by text / tag / type / source / symptom.

Stdlib only. Parses a minimal subset of YAML frontmatter (scalars + [inline, lists]).
Run from the wiki root (containing entries/ and meta.yaml), or pass --root.

Examples:
  python3 wiki_query.py "idempotency on retried charges"
  python3 wiki_query.py --tag idempotency --type pattern
  python3 wiki_query.py --symptom duplicate-charge --confidence high --compact
  python3 wiki_query.py --id pattern-idempotency-keys --show
  python3 wiki_query.py --stale
"""
import argparse, datetime, glob, os, re, sys

CONF_RANK = {"low": 0, "medium": 1, "high": 2}


def parse_frontmatter(text):
    """Return (meta: dict, body: str). Minimal YAML: 'key: value' and 'key: [a, b]'."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm = text[3:end].strip("\n")
    body = text[end + 4:].lstrip("\n")
    meta = {}
    for line in fm.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            meta[key] = [v.strip() for v in val[1:-1].split(",") if v.strip()]
        else:
            meta[key] = val.strip("'\"")
    return meta, body


def load_entries(root):
    out = []
    for path in sorted(glob.glob(os.path.join(root, "entries", "*.md"))):
        with open(path) as f:
            meta, body = parse_frontmatter(f.read())
        meta["_path"] = path
        meta["_body"] = body
        out.append(meta)
    return out


def load_meta(root):
    p = os.path.join(root, "meta.yaml")
    meta = {}
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                if ":" in line and not line.startswith(" "):
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip()
    return meta


def matches(e, a):
    if a.type and e.get("type") != a.type:
        return False
    if a.source and e.get("source") != a.source:
        return False
    if a.symptom and e.get("symptom") != a.symptom:
        return False
    if a.tag:
        etags = set(e.get("tags") or [])
        if not set(a.tag).issubset(etags):
            return False
    if a.confidence:
        if CONF_RANK.get(e.get("confidence", "low"), 0) < CONF_RANK.get(a.confidence, 0):
            return False
    return True


def score(e, terms):
    if not terms:
        return 0
    hay = " ".join([e.get("title", ""), e.get("_body", ""), " ".join(e.get("tags") or [])]).lower()
    return sum(hay.count(t) for t in terms)


def fmt(e, compact):
    if compact:
        return f"{e.get('id','?'):<32} [{e.get('confidence','?')}]  {e.get('title','')}  ({e.get('source','')})"
    head = f"{e.get('id','?')}  [{e.get('confidence','?')}]  ({e.get('source','')}, {e.get('source_date','?')})"
    line2 = f"  {e.get('title','')}"
    bits = []
    if e.get("symptom"):
        bits.append(f"symptom: {e['symptom']}")
    if e.get("tags"):
        bits.append("tags: " + ", ".join(e["tags"]))
    line3 = "  → " + "   ".join(bits) if bits else ""
    return "\n".join(x for x in [head, line2, line3] if x)


def cmd_stale(root, entries):
    meta = load_meta(root)
    try:
        cutoff = datetime.date.fromisoformat(meta.get("refresh_cutoff", ""))
    except ValueError:
        sys.exit("meta.yaml has no valid refresh_cutoff")
    window = int(meta.get("freshness_window_days", "180"))
    threshold = cutoff - datetime.timedelta(days=window)
    stale = []
    for e in entries:
        try:
            d = datetime.date.fromisoformat(e.get("source_date", ""))
        except ValueError:
            stale.append((e, "no/invalid source_date"))
            continue
        if d < threshold:
            stale.append((e, f"source_date {d} < {threshold}"))
    if not stale:
        print(f"No stale entries (threshold {threshold}).")
        return
    print(f"Stale entries (re-verify; threshold {threshold}):")
    for e, why in stale:
        print(f"  {e.get('id','?'):<32} {why}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("text", nargs="*")
    p.add_argument("--root", default=".")
    p.add_argument("--tag", action="append")
    p.add_argument("--type")
    p.add_argument("--source")
    p.add_argument("--symptom")
    p.add_argument("--confidence", choices=["low", "medium", "high"])
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--compact", action="store_true")
    p.add_argument("--id")
    p.add_argument("--show", action="store_true")
    p.add_argument("--stale", action="store_true")
    a = p.parse_args()

    entries = load_entries(a.root)
    if not entries:
        sys.exit(f"no entries found under {os.path.join(a.root, 'entries')}/")

    if a.stale:
        cmd_stale(a.root, entries)
        return

    if a.id:
        hit = next((e for e in entries if e.get("id") == a.id), None)
        if not hit:
            sys.exit(f"no entry with id {a.id!r}")
        print(fmt(hit, compact=False))
        if a.show:
            print("\n" + "-" * 60)
            print(hit.get("_body", "").rstrip())
        return

    terms = " ".join(a.text).lower().split()
    cands = [e for e in entries if matches(e, a)]
    cands.sort(key=lambda e: (-score(e, terms), -CONF_RANK.get(e.get("confidence", "low"), 0)))
    if terms:
        cands = [e for e in cands if score(e, terms) > 0]
    cands = cands[: a.limit]
    if not cands:
        print("No matching entries.")
        return
    for e in cands:
        print(fmt(e, a.compact))
        if not a.compact:
            print()


if __name__ == "__main__":
    main()
