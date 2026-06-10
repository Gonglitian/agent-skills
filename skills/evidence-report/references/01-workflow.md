# Workflow — request to report

A checklist from "why is this slow / what should I fix next" to a report someone can act on.

1. **Frame the question.** Write down, in one sentence, what you're trying to answer. "Why is the p99 of endpoint X 4× its p50?" is answerable; "make it fast" is not. The question determines what to measure.

2. **Create the run directory.** `profile/<run-name>/` with `inputs/`, `raw/`, `analysis/`. **One run = one directory, never reused.** This is the rule that keeps every later claim traceable to the measurement that produced it. If you re-measure after a change, that's a *new* run directory — so you can diff runs.

3. **Pick representative inputs.** If behavior depends on size/shape/load/data, choose specific inputs drawn from the real workload, and cover the **distribution** if there is one (small/medium/large, hot/cold, etc.) — not a single arbitrary point. Record what you chose in `inputs/` (the data or a note of its provenance).

4. **Isolate.** Measure the component on its own where you can (standalone harness, focused benchmark, single query). Isolation makes the signal legible; measuring through the whole system buries the thing you care about in noise.

5. **Collect overview + attribution.** Take a coarse measurement (where does the time/cost go at a high level?) and a fine-grained one (which line/op/stage/resource specifically?). Write raw output to `raw/`. Run enough repetitions to estimate variance.

6. **Parse programmatically.** Extract numbers into `analysis/` with a script, not by eyeballing console output. Use [`../scripts/aggregate.py`](../scripts/aggregate.py) to get mean ± stddev and a baseline delta from repeated runs.

7. **Work the dimensions, match the playbook.** [`03-analysis-dimensions.md`](03-analysis-dimensions.md) then [`04-diagnosis-playbook.md`](04-diagnosis-playbook.md). Identify the 1–2 dominant factors; match the observed pattern to a known cause *before* proposing a fix.

8. **Write `REPORT.md`.** Ranked recommendations, each tied to evidence, with effort/risk. See [`05-report-template.md`](05-report-template.md).

9. **Hand the top recommendation to the loop, then re-measure.** After the fix lands, start a new run — the bottleneck usually moved. Stop when the remaining headroom is small (and say so) rather than chasing diminishing returns.
