# Report Structure

The report turns a measurement into a decision. It is short, ranked, and every claim is tied to a number in `analysis/` that traces back to `raw/`. Use the template in [`../assets/REPORT.template.md`](../assets/REPORT.template.md).

## Required sections

1. **Question** — the one-sentence thing this run set out to answer.
2. **Setup** — what was measured, on which representative inputs, in isolation or not, how many repetitions. Enough that someone could reproduce it.
3. **Headline** — the dominant finding in one or two sentences, with the number. ("p99 is 4.2× p50; the trace attributes 78% of p99 to lock wait in `acquire_slot`.")
4. **Evidence** — the measurements that support the headline. Mean ± stddev, the attribution breakdown, the saturated resource. Point at the files in `analysis/`/`raw/`.
5. **Recommendations (ranked)** — 2–4, each with:
   - the change,
   - the evidence that motivates it,
   - rough expected impact,
   - effort and risk.
   Lead with the highest evidence × impact.
6. **Uncertainty / next measurement** — what's ambiguous, and the measurement that would resolve it. Don't paper over ambiguity with a confident guess.

## Tone rules

- **No wall of suggestions.** If you have 12 ideas, the report shows the 3 the data supports and you discard the rest. A long untriaged list pushes the diagnosis back onto the reader — the opposite of this skill's job.
- **Every number has a source.** A claim with no measurement behind it doesn't belong in the report; move it to "uncertainty / next measurement."
- **Rank, don't enumerate.** Order matters more than completeness. The reader should be able to act on #1 immediately.
