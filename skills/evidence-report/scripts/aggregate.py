#!/usr/bin/env python3
"""Aggregate repeated measurements: mean ± stddev, min/max, and delta vs a baseline.

Stdlib only. Input is a CSV with at least a numeric value column; optionally group by
another column (e.g. workload/regime) so you get per-regime stats instead of one mean
that hides the regimes where you regressed.

Examples:
  python3 aggregate.py raw/runs.csv --value latency_us
  python3 aggregate.py raw/runs.csv --value latency_us --group workload
  python3 aggregate.py raw/runs.csv --value latency_us --baseline 73.6
  python3 aggregate.py raw/runs.csv --value latency_us --group workload --baseline-col baseline_us
"""
import argparse, csv, math, sys
from collections import defaultdict


def stats(xs):
    n = len(xs)
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / n if n > 1 else 0.0
    return {"n": n, "mean": mean, "std": math.sqrt(var), "min": min(xs), "max": max(xs)}


def fmt_row(label, s, baseline):
    line = (f"{label:<24} n={s['n']:<3} mean={s['mean']:.4g} ± {s['std']:.3g}  "
            f"[min {s['min']:.4g}, max {s['max']:.4g}]")
    if baseline is not None and s["mean"] != 0:
        speedup = baseline / s["mean"]
        line += f"   vs baseline {baseline:.4g} → {speedup:.4g}×"
    return line


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv_path")
    p.add_argument("--value", required=True, help="numeric column to aggregate")
    p.add_argument("--group", help="column to group by (e.g. workload/regime)")
    p.add_argument("--baseline", type=float, help="single baseline value for speedup")
    p.add_argument("--baseline-col", help="per-row baseline column (mean used per group)")
    a = p.parse_args()

    groups = defaultdict(list)
    base_vals = defaultdict(list)
    with open(a.csv_path, newline="") as f:
        reader = csv.DictReader(f)
        if a.value not in reader.fieldnames:
            sys.exit(f"column {a.value!r} not in {reader.fieldnames}")
        for row in reader:
            try:
                v = float(row[a.value])
            except (ValueError, KeyError):
                continue
            key = row.get(a.group, "all") if a.group else "all"
            groups[key].append(v)
            if a.baseline_col and row.get(a.baseline_col):
                try:
                    base_vals[key].append(float(row[a.baseline_col]))
                except ValueError:
                    pass

    if not groups:
        sys.exit("no numeric rows found")

    for key in sorted(groups):
        baseline = a.baseline
        if a.baseline_col and base_vals.get(key):
            baseline = sum(base_vals[key]) / len(base_vals[key])
        print(fmt_row(key, stats(groups[key]), baseline))

    if a.group and len(groups) > 1:
        allxs = [v for xs in groups.values() for v in xs]
        print("-" * 60)
        print(fmt_row("ALL (pooled)", stats(allxs), a.baseline))
        worst = max(groups, key=lambda k: stats(groups[k])["mean"])
        print(f"note: worst regime is {worst!r} — check it didn't regress below baseline "
              f"even if the pooled mean looks fine")


if __name__ == "__main__":
    main()
