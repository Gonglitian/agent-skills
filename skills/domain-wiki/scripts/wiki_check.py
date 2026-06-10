#!/usr/bin/env python3
"""Validate a domain wiki: schema, provenance, duplicate ids, freshness.

Stdlib only. Run from the wiki root (containing entries/ and meta.yaml), or pass --root.
Exit code is non-zero with --strict if any problem is found (useful for pre-commit/CI).

Checks per entry:
  - required frontmatter fields present
  - source_date is a valid YYYY-MM-DD
  - body contains a verbatim quote (a '>' blockquote) — unsupported claims are flagged
  - id is unique
Freshness: entries older than (refresh_cutoff - freshness_window_days) are listed.
"""
import argparse, datetime, glob, os, sys

REQUIRED = ["id", "title", "type", "tags", "source", "source_ref", "source_date", "confidence"]
TYPES = {"pattern", "reference", "pitfall", "concept", "result"}
CONF = {"low", "medium", "high"}


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm = text[3:end].strip("\n")
    body = text[end + 4:]
    meta = {}
    for line in fm.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#") or ":" not in line:
            continue
        k, _, v = line.partition(":")
        k, v = k.strip(), v.strip()
        if v.startswith("[") and v.endswith("]"):
            meta[k] = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        else:
            meta[k] = v.strip("'\"")
    return meta, body


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", default=".")
    p.add_argument("--strict", action="store_true")
    a = p.parse_args()

    problems = []
    seen_ids = {}
    paths = sorted(glob.glob(os.path.join(a.root, "entries", "*.md")))
    if not paths:
        sys.exit(f"no entries under {os.path.join(a.root, 'entries')}/")

    for path in paths:
        name = os.path.basename(path)
        with open(path) as f:
            meta, body = parse_frontmatter(f.read())
        for field in REQUIRED:
            if not meta.get(field):
                problems.append(f"{name}: missing required field '{field}'")
        if meta.get("type") and meta["type"] not in TYPES:
            problems.append(f"{name}: type '{meta['type']}' not in {sorted(TYPES)}")
        if meta.get("confidence") and meta["confidence"] not in CONF:
            problems.append(f"{name}: confidence '{meta['confidence']}' not in {sorted(CONF)}")
        if meta.get("source_date"):
            try:
                datetime.date.fromisoformat(meta["source_date"])
            except ValueError:
                problems.append(f"{name}: source_date '{meta['source_date']}' is not YYYY-MM-DD")
        if not any(l.lstrip().startswith(">") for l in body.splitlines()):
            problems.append(f"{name}: no verbatim quote ('>' blockquote) — claim is unsupported")
        eid = meta.get("id")
        if eid:
            if eid in seen_ids:
                problems.append(f"{name}: duplicate id '{eid}' (also in {seen_ids[eid]})")
            seen_ids[eid] = name

    # freshness
    meta_path = os.path.join(a.root, "meta.yaml")
    stale = []
    if os.path.exists(meta_path):
        mm = {}
        with open(meta_path) as f:
            for line in f:
                if ":" in line and not line.startswith(" "):
                    k, _, v = line.partition(":")
                    mm[k.strip()] = v.strip()
        try:
            cutoff = datetime.date.fromisoformat(mm.get("refresh_cutoff", ""))
            window = int(mm.get("freshness_window_days", "180"))
            threshold = cutoff - datetime.timedelta(days=window)
            for path in paths:
                with open(path) as f:
                    meta, _ = parse_frontmatter(f.read())
                try:
                    if datetime.date.fromisoformat(meta.get("source_date", "")) < threshold:
                        stale.append(f"{os.path.basename(path)}: source_date {meta['source_date']} < {threshold}")
                except ValueError:
                    pass
        except (ValueError, TypeError):
            problems.append("meta.yaml: refresh_cutoff missing or invalid")

    print(f"Checked {len(paths)} entries.")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for x in problems:
            print(f"  ✗ {x}")
    else:
        print("  ✓ no schema/provenance problems")
    if stale:
        print(f"\n{len(stale)} stale entry(ies) to re-verify:")
        for x in stale:
            print(f"  ⏳ {x}")

    if a.strict and problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
