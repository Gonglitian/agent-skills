---
name: engineering-loop
description: Run a long-horizon, evidence-driven engineering loop for any task that is an experiment system, not a one-shot generation — repeatedly proposing, implementing, validating, and promoting candidates against a fixed baseline until a measurable target is met. Use this whenever a task will span many iterations and hours and needs durable state (best-so-far, failed branches, why), an immutable baseline, objective acceptance criteria, and protection against the agent quietly redefining its own success. Trigger for kernel/perf optimization, model/training/RL tuning, compiler passes, data-pipeline or query optimization, long refactors, or research where each step must be justified by evidence. Pairs with the domain-wiki (knowledge) and evidence-report (measurement) skills. Use it even when the user just says "optimize X", "beat the baseline", "iterate until it passes", or "keep improving this" without naming a framework.
---

# Engineering Loop

A reusable harness for **long-horizon, auditable, evidence-driven** engineering work. It generalizes the workflow behind Kernel Design Agents (KDA): the value is not in generating one good candidate, but in keeping a model productive across dozens of iterations and many hours without drifting off-target, repeating dead ends, declaring victory early, or optimizing the wrong number.

## When this loop is the right tool

Use it when the task is an **experiment system**, not a one-shot generation:

- The answer is found by searching: propose → implement → measure → decide → repeat.
- Candidates must be compared against a **fixed baseline** under identical conditions.
- "Correct" and "better" are objectively checkable (a validator, a benchmark, a metric).
- The task is long enough that conversation memory alone will lose the thread.

If the task is a single edit with an obvious right answer, skip this — just do it.

## The golden rules

1. **The baseline is immutable.** Record what it is and where it came from (provenance) before you change anything. Never compare a candidate against your own earlier candidate and call that "beating the baseline" — that is the #1 way this loop silently fails. See [`references/integrity-guards.md`](references/integrity-guards.md).
2. **No promotion without evidence.** A candidate is promoted only when it passes validation AND has a measurement, taken under the same conditions as the baseline, showing it preserves or improves the target. Record *why*.
3. **Failures are data, not garbage.** When a candidate is rejected, write down the reason. A rejected direction you don't record is a direction you will waste time re-exploring.
4. **The agent does not define its own reward.** Correctness checks, the baseline, and the verifier are inputs you do not get to weaken. If a check is inconvenient, that is not license to skip it.
5. **Stop on criteria, not on vibes.** The task is done when the promotion criteria are met, or when the remaining blockers are written down explicitly — never on the conversational impression that "this seems good enough."

## The loop

```
        ┌─────────────────────────────────────────────┐
        │  0. Task Contract  (define before any code)  │
        └─────────────────────────────────────────────┘
                              │
        ┌─────────────────────▼───────────────────────┐
        │  1. Read the workspace + baseline; establish │
        │     the validation/measurement path          │
        └─────────────────────┬───────────────────────┘
                              │
        ┌─────────────────────▼───────────────────────┐
        │  2. draft.md  →  plan.md   (plan before code) │
        └─────────────────────┬───────────────────────┘
                              │
        ┌─────────────────────▼───────────────────────┐
        │  3. Implement ONE candidate                  │
        │  4. Validate correctness                     │
        │  5. Measure the target (vs immutable baseline)│
        │  6. Record candidate + evidence + decision    │◀─┐
        └─────────────────────┬───────────────────────┘  │ keep / revise / reject
                              │                            │ (always record why)
                              └────────────────────────────┘
                              │  until promotion criteria met
                              │  or blockers are explicit
        ┌─────────────────────▼───────────────────────┐
        │  7. Promote best candidate; write final state │
        └───────────────────────────────────────────────┘
```

## How to run it

### Step 0 — Write the Task Contract first

Before touching code, fill in the contract. It is the definition of done and the thing that stops goal-drift. Copy [`assets/task-contract.template.md`](assets/task-contract.template.md) into the workspace as `docs/contract.md` and fill every field. The fields and how to choose them are in [`references/task-contract.md`](references/task-contract.md). Minimum: objective, inputs/outputs, correctness requirement + **validation command**, target metric + **evaluation command**, immutable baseline + provenance, and promotion criteria.

> **If the objective and target haven't been aligned with a human yet, do that first.** Run the `long-horizon-spec` skill to interview the user, lock scope and acceptance criteria, and produce a human-approved `SPEC.md`. Its acceptance section maps field-for-field onto this contract — validation command, target metric + evaluation command, immutable baseline + provenance, promotion criteria — so you derive `docs/contract.md` from an already-approved spec instead of guessing the definition of done. A contract whose success was locked by a human before the loop started is the strongest anti-drift anchor there is.

### Step 1 — Inspect, don't assume

Read the existing implementation, tests, and docs in the workspace. Identify the baseline's actual behavior and run its validation/evaluation path once so you have ground truth before changing anything.

### Step 2 — Draft, then plan

Write `docs/draft.md` (use [`assets/draft.template.md`](assets/draft.template.md)): the baseline and how it's validated, the main risks/unknowns, candidate directions ranked by expected value × risk, the first concrete steps, and the exact validation/evaluation commands. **Do not start implementing until the draft exists.** Then turn it into an executable `docs/plan.md` ([`assets/plan.template.md`](assets/plan.template.md)) with acceptance criteria per step. If the `humanize` plugin is installed, use it for the draft→plan conversion and the execution loop.

### Steps 3–6 — Iterate one candidate at a time

Implement a single candidate, validate, measure, and record it in `candidates.jsonl` with its parent, status, metric, and the reason for the decision. The schema and a helper script are in [`references/evidence-records.md`](references/evidence-records.md) and [`scripts/candidates.py`](scripts/candidates.py). Keep results in `benchmark.csv`; keep profiler/measurement artifacts under `profile/` (use the **evidence-report** skill to turn measurements into the *next* direction). Never skip validation between candidates.

Follow the three-phase search strategy and the promotion rule in [`references/promotion-and-phases.md`](references/promotion-and-phases.md):
- **Phase 1 — correctness first:** get a candidate that passes the official validator on the real workload, even if slow.
- **Phase 2 — structural optimization:** attack the dominant bottleneck the evidence shows (not the one you assume).
- **Phase 3 — distribution & specialization:** analyze the whole input distribution; decide whether different regimes need different implementations (routing/dispatch), and accept that for some regimes the mature baseline may be the right choice.

### Step 7 — Promote and finalize

Promote the best candidate per the promotion rule, then write the final state: which candidate won, the evidence, and any explicit remaining blockers. Anyone reading the workspace afterward should be able to reconstruct what was tried, what passed, and why the winner won.

## Guard against reward-hacking

Long autonomous loops drift toward exploiting the evaluation rather than solving the task. Before trusting any "done", run the checklist in [`references/integrity-guards.md`](references/integrity-guards.md) — it covers baseline drift, incomplete validators (the all-NaN kernel that passes a validator missing its invalid-value check), and writer/verifier role collapse. Keep the verifier independent and read-only where possible, and keep an audit trail of what changed.

## Workspace layout

```
task-workspace/
  docs/
    contract.md      # the Task Contract — definition of done
    draft.md         # first plan draft
    plan.md          # executable plan with acceptance criteria
  candidates.jsonl   # candidate DAG: id, parent, status, metric, reason
  benchmark.csv      # measurements, aligned to the immutable baseline
  profile/           # per-run measurement artifacts (see evidence-report)
  runs/ outputs/     # generated artifacts
```

## Reference files

- [`references/task-contract.md`](references/task-contract.md) — every contract field and how to choose it.
- [`references/evidence-records.md`](references/evidence-records.md) — schemas for `candidates.jsonl`, `benchmark.csv`, and the helper script.
- [`references/promotion-and-phases.md`](references/promotion-and-phases.md) — the promotion rule and the three-phase search strategy.
- [`references/integrity-guards.md`](references/integrity-guards.md) — anti-reward-hacking checklist with real failure modes.
