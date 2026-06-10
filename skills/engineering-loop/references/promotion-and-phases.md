# Promotion Rule & Three-Phase Search

## The promotion rule

Promote a candidate to "current best" only when **all** of these hold:

1. It passes the **validation command** (the official/authoritative one), including invalid-value checks.
2. It has a **measurement** of the target metric, taken under the same conditions as the immutable baseline.
3. The measurement **preserves or improves** the target versus the current best — per the promotion criteria in the contract (e.g. no individual workload regresses below baseline).

If a candidate fails any of these, do not promote it — and **record the reason** in `candidates.jsonl` instead of silently discarding it. A rejection without a recorded reason is a future repeated mistake.

A candidate that is faster but not validated is not a candidate. A candidate that wins on average but regresses a regime you care about is not promoted unless the contract says average-only.

## The three-phase search strategy

Long optimization tasks go wrong when the agent jumps straight to clever micro-optimizations. Impose this order; it front-loads correctness and points optimization at the bottleneck the *evidence* shows, not the one you assume.

### Phase 1 — Correctness-first baseline candidate
Get a candidate that runs the real workload and passes the official validator, even if it is slow. This establishes the validation path end-to-end and gives you a trustworthy starting point. Don't optimize anything yet. Most reward-hacking incidents trace back to skipping a clean correctness baseline.

### Phase 2 — Structural optimization on the dominant bottleneck
Use the **evidence-report** skill to find where the time/cost actually goes, then attack that. The point is structural change (algorithm, data layout, execution strategy), not fiddling. After each structural change, re-measure — the bottleneck often *moves*, and the next phase-2 target is wherever the new evidence points. Stop a direction when the evidence says its remaining headroom is small, and record that it was exhausted.

A direction that looks promising but measures neutral or negative under validation is **rejected, with the reason logged** — not quietly retried with tweaks.

### Phase 3 — Distribution analysis & specialization
Real workloads are rarely one fixed shape. Analyze the **whole input distribution**, not the average case. Then decide whether different regimes deserve different implementations:

- A short-input fast path plus a fallback for long inputs.
- A hybrid **dispatcher/router** that sends each regime to the implementation that wins for it.
- Accepting that for some regime the **mature baseline is the right answer**, and routing only the regimes where your custom path actually wins.

Specialization is not "always replace the baseline everywhere." Sometimes the strongest engineering result is a router that only intervenes where it helps and otherwise defers to the untouched baseline. Measure each regime separately; a single mean number hides the cases where you regressed.

## Stop conditions

Stop when the promotion criteria are met, or when every remaining direction has been measured and the blockers are written down explicitly. "It feels good enough" and "I beat my last version" are not stop conditions.
