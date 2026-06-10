# Executable Plan — <task name>

> Derived from `draft.md`. Each step has an acceptance criterion. Implement one candidate at a time.

## Phase 1 — Correctness-first baseline candidate
- [ ] Step: <...>
  - Acceptance: passes `<validation command>` on the real workload.

## Phase 2 — Structural optimization (attack the evidence-shown bottleneck)
- [ ] Step: <...>
  - Bottleneck evidence: <pointer to profile/REPORT.md>
  - Acceptance: <metric improves under validation; re-measure, bottleneck may move>

## Phase 3 — Distribution analysis & specialization
- [ ] Step: analyze full input distribution
  - Acceptance: per-regime measurements recorded; routing/specialization decision justified by evidence (including "defer to baseline" for regimes where custom path doesn't win).

## Logging
- Record every candidate in `candidates.jsonl` (id, parent, status, metric, reason).
- Append every measurement to `benchmark.csv` (with co-located baseline value).
- Keep measurement runs under `profile/<run>/`.

## Done when
<promotion criteria from contract are met, or remaining blockers are explicit>
