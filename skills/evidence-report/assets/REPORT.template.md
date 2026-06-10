# Evidence Report — <run-name>

## Question
<the one sentence this run set out to answer>

## Setup
- Target measured: <component / kernel / query / endpoint>
- Inputs: <representative inputs; which regimes; see inputs/>
- Isolation: <standalone harness / in-situ — and the confidence implication>
- Repetitions: <N>, warm-up: <yes/no>
- Baseline (if any): <what, measured under same conditions>

## Headline
<the dominant finding in 1–2 sentences, with the number>

## Evidence
- <metric>: <mean ± stddev> (raw/…, analysis/…)
- Attribution: <breakdown — which stage/op/resource, with %>
- Saturated resource: <…> | Variance: p50 <…> / p99 <…>
- <regime breakdown if the workload is a distribution>

## Recommendations (ranked by evidence × impact)
1. **<change>** — evidence: <…>. Expected impact: <…>. Effort: <…>. Risk: <…>.
2. **<change>** — evidence: <…>. Expected impact: <…>. Effort: <…>. Risk: <…>.
3. **<change>** — …

## Uncertainty / next measurement
- <what's ambiguous, and the single measurement that would disambiguate it>
