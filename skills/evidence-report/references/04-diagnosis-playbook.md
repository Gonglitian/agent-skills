# Diagnosis Playbook

Map an observed **signal** to a likely **cause** to a candidate **fix**. The point is to match the pattern you measured to a known diagnosis *before* you change anything — and to rank candidate fixes by evidence × expected impact, not to list everything possible.

This is a generic starter playbook. **Specialize it for your domain** — fill in the concrete signals your profiler emits, the metric names (keep these in your domain-wiki), and the fixes that apply to your stack. The structure is what's reusable; the rows are examples.

| Signal (what you measured) | Likely cause | Candidate fix |
|---|---|---|
| One stage/op dominates total time | Hotspot concentration | Restructure or replace that stage; everything else is rounding error |
| Resource X near 100%, others idle | Bound by resource X | Reduce demand on X or shift work to an idle resource |
| Latency-bound: waiting, not working (high stall/idle, low utilization) | Dependency/memory/IO latency on the critical path | Overlap/prefetch, hide latency, cut the dependency chain, batch to amortize |
| Work units tiny; overhead ≈ work | Launch/dispatch/per-call overhead dominates | Fuse, batch, amortize setup; fewer-bigger units |
| p99 ≫ p50, high variance | Contention / GC / cold path / tail | Find the tail's cause (lock, allocation, cache miss); fix the worst case, not the mean |
| Great on average, bad on one regime | One implementation can't fit all regimes | Specialize: fast path for that regime + fallback, or a router/dispatcher |
| Throughput flat as you add parallelism | Serialized section / shared bottleneck (Amdahl) | Find and parallelize (or remove) the serial part |
| Repeated identical work across calls | Missing caching/memoization / N+1 | Cache, batch, hoist the repeated work out of the loop |
| Regression vs baseline, same inputs | A specific change moved it | Bisect the change set; isolate the delta, don't blanket-optimize |

## How to rank recommendations

For each candidate fix, weigh:

- **Evidence strength** — how directly does the measurement support this being the cause? (A confirmed saturated resource beats a plausible hypothesis.)
- **Expected impact** — roughly how much of the total cost does it address? (Fixing a 60%-of-time hotspot ≫ a 5% one, even if the 5% is easier.)
- **Effort & risk** — how much work, and how likely to break correctness or other regimes?

Lead with the highest evidence × impact. Keep the report to 2–4 recommendations. A wall of 15 untriaged suggestions is exactly the anti-pattern this skill prevents — it offloads the diagnosis back onto the reader.

## After the fix: re-measure

The bottleneck moves. Once the top recommendation lands, take a fresh measurement (new run directory) — the next-dominant dimension is now the target. Stop when the remaining headroom is small, and say so explicitly rather than chasing diminishing returns. A fix that measures neutral/negative is recorded as a rejected direction (with the reason) in the engineering-loop, not quietly retried.
