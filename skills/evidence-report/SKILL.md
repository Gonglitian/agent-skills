---
name: evidence-report
description: Turn objective measurements into a ranked, evidence-backed diagnosis and a next-step plan — instead of guessing at what's slow/wrong and changing things hopefully. Use this whenever you need to understand why something underperforms (a slow kernel/query/endpoint/job, a regression, a model that's underperforming, high cost/memory) and decide what to fix first, grounded in profiler output, benchmark numbers, traces, or logs rather than intuition. The golden rule it enforces — Measure then Diagnose then Plan, never guess; never write a wall of suggestions, rank them by evidence times expected impact. Trigger for "profile this", "why is X slow", "diagnose this bottleneck", "read this profiler/benchmark report", "what should I optimize next", or when a long optimization loop needs to pick its next direction from data. Pairs with the engineering-loop and domain-wiki skills.
---

# Evidence Report

A reusable discipline for turning raw measurements into an actionable diagnosis. It generalizes the ncu-report-skill: most underperforming systems underperform for a small number of reasons that a profiler/benchmark can show you in seconds — but only if you measure first, parse the data properly, and rank fixes by evidence rather than dumping every idea you have.

## Golden rule

**Measure → Diagnose → Plan, in that order. Never guess.**

- Don't invent hypotheses before you have the measurement.
- Don't start coding a fix before you've matched the observed pattern to a known diagnosis.
- Don't write a wall of suggestions — rank them by **evidence × expected impact**, and lead with the one the data most supports.

This is domain-agnostic: the "profiler" might be Nsight Compute, `perf`, an APM trace, `EXPLAIN ANALYZE`, a training/eval curve, a flamegraph, or a benchmark harness. The discipline is the same.

## Quickstart — when someone says "why is this slow / what should I fix"

0. **One run, one directory.** Create `profile/<run-name>/` and never reuse it. Each run holds its own `inputs/`, `raw/`, `analysis/`, and `REPORT.md`. This keeps every conclusion traceable to the exact measurement that produced it. See [`references/01-workflow.md`](references/01-workflow.md).

1. **Decide what you're measuring and on which inputs.** What question do you want answered? If behavior depends on input size/shape/load, pick **specific representative inputs** from the real workload — don't measure arbitrary ones, and don't measure a single point if the workload is a distribution. See [`references/02-collection.md`](references/02-collection.md).

2. **Isolate and measure.** Where possible, measure the component in isolation (a standalone harness, a focused benchmark) so the signal isn't buried in everything else. Capture both an **overview** measurement and a **fine-grained / attribution** measurement. Write raw output to `raw/`. Repeat enough times to see variance, not one noisy sample.

3. **Parse the data programmatically, not by eye.** Extract the numbers with a script into `analysis/`, so the diagnosis rests on actual values and the parse is reproducible. A helper for aggregating repeated runs (mean ± stddev, regression vs baseline) is in [`scripts/aggregate.py`](scripts/aggregate.py).

4. **Work the analysis dimensions.** Go through the dimensions in [`references/03-analysis-dimensions.md`](references/03-analysis-dimensions.md) — throughput vs latency, bottleneck localization, resource saturation, distribution/variance, regression-vs-baseline. On any given case only 1–2 dominate; find which.

5. **Match to the diagnosis playbook.** [`references/04-diagnosis-playbook.md`](references/04-diagnosis-playbook.md) maps signal → likely cause → candidate fix. Match the pattern you observed to a known diagnosis before proposing a change. Beware the *assumed* bottleneck — measure which one is real (e.g. a latency-bound problem misread as a compute problem).

6. **Write the report.** Use the template in [`references/05-report-template.md`](references/05-report-template.md) ([`assets/REPORT.template.md`](assets/REPORT.template.md)). Recommendations ranked by expected impact, each tied to the specific evidence that supports it, with rough effort and risk.

## How this feeds the loop

The report's top recommendation becomes the next candidate direction in the **engineering-loop**. After you implement it, **re-measure** — the bottleneck usually moves, and the next report points at wherever it went. A recommendation that, once tried, measures neutral or negative is recorded as a rejected direction (with the reason), not silently retried. That measure-diagnose-fix-remeasure cycle is the whole point.

## What a good diagnosis looks like

- **Evidence-led:** "p99 latency is 4× p50 and the trace shows it's all in the lock-wait section" — not "it's probably lock contention."
- **Ranked:** the single highest-leverage fix first, with the number that justifies it.
- **Honest about uncertainty:** if the data is ambiguous, say what additional measurement would disambiguate, rather than guessing.
- **Bounded:** 2–4 recommendations, not 15. A wall of untriaged suggestions is the failure mode this skill exists to prevent.

## Directory layout

```
profile/<run-name>/
  inputs/      # the exact representative inputs measured (or a note of where they came from)
  raw/         # unmodified profiler / benchmark / trace output
  analysis/    # parsed numbers, aggregates, intermediate computations
  REPORT.md    # the ranked, evidence-backed diagnosis + plan
```

## Reference files

- [`references/01-workflow.md`](references/01-workflow.md) — end-to-end checklist from request to report.
- [`references/02-collection.md`](references/02-collection.md) — choosing inputs, isolating, overview vs attribution, handling variance.
- [`references/03-analysis-dimensions.md`](references/03-analysis-dimensions.md) — the dimensions to work through.
- [`references/04-diagnosis-playbook.md`](references/04-diagnosis-playbook.md) — signal → cause → fix, with the domain-specialization guidance.
- [`references/05-report-template.md`](references/05-report-template.md) — how to structure the report.
