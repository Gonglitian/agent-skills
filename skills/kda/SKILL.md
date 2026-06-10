---
name: kda
description: The orchestration entry point for running a Kernel-Design-Agents-style engineering loop on any domain — it ties together three sibling skills (engineering-loop for control, domain-wiki for knowledge, evidence-report for measurement) into one long-horizon, auditable, evidence-driven workflow. Use this when a task is an experiment system rather than a one-shot generation and you want the full framework, not just one layer — e.g. the user says "use the KDA approach", "set up the whole loop for this", "optimize X end to end with knowledge + profiling + iteration", or asks how the engineering-loop / domain-wiki / evidence-report skills fit together. Start here to decide which layers a task needs and in what order; this skill is thin and delegates the actual work to the three specialized skills.
---

# KDA — Kernel Design Agents, generalized

A thin orchestrator. The real work lives in three sibling skills; this skill exists to answer one question well: **for a long-horizon, evidence-driven task, which layers do I need and in what order?** It then hands off to them.

The core idea — borrowed from Kernel Design Agents and made domain-agnostic — is that hard engineering/research tasks are not one-shot generation problems but **long experiment systems**. The win comes from putting the model in a persistent, auditable, evidence-driven loop with clear boundaries, not from a cleverer single prompt. Three layers make that work:

| Layer | KDA original | This framework's skill | Job |
|---|---|---|---|
| **Control** | Humanize + 3-stage prompts | **`engineering-loop`** | Task Contract, draft→plan, candidate DAG, evidence-based promotion, anti-reward-hacking guards, stop conditions |
| **Knowledge** | KernelWiki | **`domain-wiki`** | Provenance + freshness + confidence-tracked, multi-axis-indexed corpus the loop queries on demand |
| **Evidence** | ncu-report-skill | **`evidence-report`** | "Measure → Diagnose → Plan, never guess": turn objective measurements into the *next* direction, ranked by evidence × impact |

## Is this the right framework for the task?

Use the full KDA loop when **most** of these hold:

- The answer is found by searching: propose → implement → measure → decide → repeat.
- Candidates must be compared against a **fixed baseline** under identical conditions.
- "Correct" and "better" are objectively checkable.
- The task is long enough (many iterations / hours) that conversation memory alone loses the thread.
- Domain knowledge matters and the model is likely to get it subtly wrong or stale.

If it's a single edit with an obvious answer, don't invoke the framework — just do it. If only *one* layer applies (e.g. you just need to diagnose one slow query), invoke that one skill directly instead of the whole loop.

## The end-to-end orchestration

This is the order the layers compose. Each step delegates to a skill — read that skill's SKILL.md when you reach the step; don't duplicate its detail here.

1. **Frame & scope (control).** Invoke **`engineering-loop`**. Write the Task Contract first: objective, inputs/outputs (and their *distribution*), correctness + validation command, target metric + evaluation command, **immutable baseline + provenance**, promotion criteria. This is the definition of done and the anti-drift anchor.

   > **If the target hasn't been aligned with a human yet, run `long-horizon-spec` before this step.** It interviews the user, locks scope and acceptance criteria, and produces a human-approved `SPEC.md` whose acceptance section maps field-for-field onto the Task Contract. Deriving the contract from an already-approved spec beats guessing the definition of done — and a human-locked success criterion is the strongest version of this anti-drift anchor. Skip it only when the objective and metric are already unambiguous and agreed.

2. **Stand up knowledge (knowledge).** If the task leans on hard-won domain facts, invoke **`domain-wiki`** — either query an existing corpus or scaffold one from the authoritative sources (PRs, source, specs, papers, docs). Pull in only the entries relevant to the current sub-problem; trust them by their source/date/confidence.

3. **Phase 1 — correctness first (control).** Get a candidate that passes the official validator on the real workload, even if slow. Record it in `candidates.jsonl`. Don't optimize yet.

4. **Phase 2 — structural optimization (evidence → control).** Invoke **`evidence-report`** to find where the cost *actually* concentrates (beware the assumed bottleneck). Its top recommendation becomes the next candidate direction in **`engineering-loop`**. Implement, validate, **re-measure** — the bottleneck moves; the next report points where it went. A direction that measures neutral/negative is recorded as rejected *with the reason*, not retried.

5. **Phase 3 — distribution & specialization (evidence → control).** Analyze the whole input distribution per regime (evidence-report's grouped aggregation makes the hidden regressions visible). Decide whether to specialize — a fast path + fallback, a router/dispatcher, or **deferring to the mature baseline** for regimes where a custom path doesn't win.

6. **Promote & finalize (control).** Promote per the promotion rule, write the final state, and run the integrity checklist before believing "done".

7. **When returns flatten, feed knowledge back (knowledge).** Several low-yield iterations in a row is the cue to read new sources and add/refresh **`domain-wiki`** entries — not to keep micro-tweaking the same local spot. This is the KDA "supplement references when stuck" behavior.

## The one rule that ties it all together

**The agent must not define, weaken, or silently modify its own reward.** The baseline stays immutable with recorded provenance; correctness reuses the official harness with explicit invalid-value checks; the verifier stays independent and as read-only as possible; an audit trail records what changed. The full checklist and the three real failure modes (baseline drift, incomplete validator, writer/verifier role collapse) are in `engineering-loop`'s `references/integrity-guards.md`. Read it before trusting any completion claim.

## Where the pieces live

These four skills are independent siblings under the skills directory:

- `kda` — this orchestrator (start here for the full loop).
- `engineering-loop` — control layer; the entry point for the actual iteration.
- `domain-wiki` — knowledge layer.
- `evidence-report` — evidence/measurement layer.

Invoke them by name as you reach each step. This skill stays thin on purpose — its only job is sequencing.
