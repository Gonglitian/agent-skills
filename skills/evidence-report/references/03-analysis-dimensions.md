# Analysis Dimensions

Work through these dimensions on the measurement. On any given case only one or two dominate — your job is to find which, with numbers, before proposing a fix. These are domain-agnostic; the specific metric names differ by tool (see your domain-wiki for the names that apply).

## 1. Throughput vs latency
Are you bound by *how much work per unit time* (throughput) or *how long one unit takes* (latency)? They demand opposite fixes — batching/parallelism for throughput, shortening the critical path for latency. Misreading one as the other wastes the whole optimization.

## 2. Bottleneck localization
Where does the cost actually concentrate? The 80/20 question: which stage/op/line/query accounts for most of the time or cost? Optimizing anything outside the dominant contributor is, at best, rounding error. Confirm with attribution data — don't trust the part you *assume* is hot.

## 3. Resource saturation
Which resource is the limiter — compute, memory bandwidth, memory capacity, I/O, network, a lock, a connection pool, a rate limit? A system bound by one resource won't speed up by optimizing another. Look for the resource sitting near 100% (or the queue that's always full).

## 4. Distribution & variance
Look at the spread, not just the mean. p50 vs p99, best vs worst input regime, run-to-run variance. High tail latency points at contention/GC/cold paths; a metric that's great on average but terrible on one regime is the signal that you may need **per-regime specialization** rather than one implementation. This dimension is what turns "optimize the average" into "route each regime to what wins for it."

## 5. Regression vs baseline
If this is a regression hunt, the dimension is *what changed*. Compare against the immutable baseline measured under identical conditions. Bisect the change set; isolate the commit/config/input that moved the number. Don't optimize — find the delta.

## The assumed-bottleneck trap

The most common diagnostic error is fixing the bottleneck you *expected* instead of the one the data shows. Classic cases:
- A problem that "must be compute-bound" turns out to be **latency-bound on memory** (waiting on loads, not computing).
- A "slow algorithm" is actually **launch/overhead-bound** because each unit of work is tiny.
- A "database is slow" is actually **the connection pool** or **N+1 queries**, not the query plan.

Always confirm the dominant dimension with a measurement before committing to a direction. If the data is ambiguous between two dimensions, the right next step is the measurement that disambiguates them — not a hopeful fix.
