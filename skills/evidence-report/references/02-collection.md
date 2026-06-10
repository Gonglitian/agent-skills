# Collection — getting trustworthy measurements

A diagnosis is only as good as the measurement under it. Most wrong conclusions come from measuring the wrong thing, the wrong input, or a single noisy sample.

## Choose representative inputs

If behavior depends on input size/shape/load/data characteristics, the input you measure *is* the experiment. Rules:

- **Draw from the real workload**, not arbitrary toy inputs. A kernel that's fast on length-1024 may be slow on length-6; an endpoint fast on a warm cache may be slow cold.
- **Cover the distribution.** If the workload spans regimes (small/medium/large, hot/cold, sparse/dense, low/high concurrency), measure several points across it. A single mean hides the regimes where you regress — and the decision to specialize per regime can only come from per-regime data.
- **Record what you measured** in `inputs/` so the run is reproducible and the report's claims are pinned to specific conditions.

## Isolate the component

Measure the thing you care about on its own where you can — a standalone harness, a focused micro-benchmark, a single query with `EXPLAIN ANALYZE`, one operator. Isolation makes the signal legible. Measuring end-to-end through the whole system buries a 5% component under everything else and invites wrong attribution.

When you can't isolate (the cost only appears under real load), say so in the report and treat the attribution as lower-confidence.

## Overview + attribution

Take two kinds of measurement:

- **Overview** — where does the time/cost go at a high level? (Which stage? Compute vs memory vs wait? Which query? Which layer?) This tells you *which* part to zoom into.
- **Attribution** — within that part, which line/op/resource specifically? (Per-line stalls, per-op timings, the specific lock, the specific index scan.) This tells you *what* to change.

Don't skip straight to attribution — you'll attribute the wrong thing if you haven't confirmed where the cost actually concentrates.

## Handle variance — never trust one sample

Run enough repetitions to see the spread, and warm up first if the system has cold-start effects. Report **mean ± stddev**, not a single number. High variance is itself a finding (a flaky path, GC, contention, thermal throttling) and changes what you should investigate. Use [`../scripts/aggregate.py`](../scripts/aggregate.py) to compute mean/stddev/min/max and a delta versus a baseline from repeated runs.

## Parse programmatically

Extract numbers with a script into `analysis/`, not by reading console output by eye. Eyeballing is slow, error-prone, and unreproducible; a parse script can be reused across every run and across iterations of the loop. Keep the raw output in `raw/` untouched so the parse can be re-checked.

## Keep raw output immutable

`raw/` holds the unmodified profiler/benchmark/trace output. Never edit it. Every number in the report should be traceable back to a file in `raw/` via the parse in `analysis/`. This is the measurement-side analogue of the engineering-loop's immutable baseline.
