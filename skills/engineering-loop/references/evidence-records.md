# Evidence Records

The loop only works if state lives in files, not in conversation memory. Three records carry that state. The exact format matters less than consistency — a future reader (or a future you, after a context reset) must be able to reconstruct what was tried, what was measured, and why the winner won.

## `candidates.jsonl` — the candidate DAG

One JSON object per line, one line per candidate. Candidates form a tree/DAG via `parent`, so you can see which idea descended from which and which branches died.

```json
{"id": "c3", "parent": "c1", "summary": "tcgen05 tensor-core score path", "status": "promoted", "metric": {"latency_us": 7.1}, "baseline_metric": {"latency_us": 73.6}, "validated": true, "reason": "10.4x over c1 on score stage; passes all 23 workloads", "created": "2026-06-09"}
{"id": "c4", "parent": "c3", "summary": "multi-block radix-select", "status": "rejected", "validated": true, "reason": "sync + launch overhead cancels the gain; net neutral", "created": "2026-06-09"}
```

Fields:
- `id` — short stable handle (`c1`, `c2`, …).
- `parent` — the candidate this was derived from, or `null` for the first.
- `summary` — one line: what's different about this candidate.
- `status` — `exploring` | `promoted` | `rejected` | `parked`.
- `metric` / `baseline_metric` — the measured target and the **immutable baseline** measured under the same conditions. Keep them side by side so the comparison is never ambiguous.
- `validated` — did it pass the official validation command? A candidate that isn't validated cannot be promoted, no matter how fast.
- `reason` — *why* it was promoted/rejected. This is the field that saves you from re-exploring dead ends. Never leave it empty on a terminal status.

Use [`../scripts/candidates.py`](../scripts/candidates.py) to append and query without hand-editing JSON:

```bash
python3 scripts/candidates.py add  --id c4 --parent c3 --summary "multi-block radix" --status exploring
python3 scripts/candidates.py set  c4 --status rejected --reason "sync overhead cancels gain"
python3 scripts/candidates.py list --status promoted
python3 scripts/candidates.py tree            # show the DAG
```

## `benchmark.csv` — the measurement log

Append-only. One row per measurement, always including the baseline measured in the same environment so rows are comparable across time.

```
timestamp,candidate_id,workload,metric_name,value,baseline_value,speedup,validated,notes
2026-06-09T10:00,c3,trace-all,latency_us,7.1,73.6,10.366,true,score stage only
```

Keep `baseline_value` in every row. A speedup number with no co-located baseline is the seed of baseline-drift (see `integrity-guards.md`).

## `profile/<run>/` — measurement artifacts

One directory per profiling/measurement run, never reused. Raw profiler output, parsed analysis, and a `REPORT.md`. This is owned by the **evidence-report** skill; the loop just reads its conclusions to choose the next direction.

## `docs/` — the plan trail

- `contract.md` — the Task Contract (definition of done).
- `draft.md` — the first plan draft.
- `plan.md` — the executable plan with per-step acceptance criteria.

## Why this much bookkeeping

Over a multi-hour search the dominant failure isn't bad code — it's lost context: re-trying a branch you already killed, forgetting which number is the real baseline, or promoting on a half-remembered impression. These records are cheap to maintain and they are what let the loop survive context resets and hand-offs.
