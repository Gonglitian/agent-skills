---
name: experiment-plan
description: Turn a refined research proposal into a claim-driven experiment roadmap with progressive 4-stage execution order. Reads from research-refine output (FINAL_PROPOSAL.md). Produces EXPERIMENT_PLAN.md + EXPERIMENT_TRACKER.md. Use after research-refine, or when user says "实验计划", "experiment plan", "设计实验", "ablation matrix", "evaluation protocol", "run order".
---

# Experiment Plan: Claim → Evidence → Run Order

Turn method proposal into a claim-driven experiment roadmap. Every experiment must change a reviewer belief or it gets cut.

**Domain-specific details** (VLA sim-to-real protocols, Peng Sida 十问, etc.) are in `references/domain-guide.md`.

## Constants

- **MAX_CLAIMS = 2** — one dominant + one supporting
- **MAX_BLOCKS = 5** — compact paper story
- **MAX_BASELINES = 3** — few strong > many weak
- **DEFAULT_SEEDS = 3**
- **OUTPUT = `refine-logs/`** — shared with research-refine

## Pipeline

```
refine-logs/FINAL_PROPOSAL.md
  │
  ├─ P0: Load proposal (Problem Anchor, method, constraints)
  ├─ P1: Freeze claims & anti-claims
  ├─ P2: Build 5-block experimental storyline
  ├─ P3: Specify each block (dataset, baselines, metrics, success criteria)
  ├─ P4: 4-stage progressive run order
  └─ Output: EXPERIMENT_PLAN.md + EXPERIMENT_TRACKER.md
```

## P0: Load Proposal

Read `refine-logs/FINAL_PROPOSAL.md`. Extract: Problem Anchor, dominant contribution, method details, compute/data constraints, reviewer-flagged risks.

## P1: Freeze Claims & Anti-Claims

```markdown
| # | Claim | Anti-Claim to Rule Out | Minimum Convincing Evidence | Blocks |
|---|-------|----------------------|----------------------------|--------|
| C1 | [dominant] | "gain is just from more params" | method > baseline by ≥X on Y | B1,B2 |
| C2 | [supporting] | "component is decorative" | −component < full by ≥X | B3 |
```

**Anti-claims are as important as claims.** No claim without an anti-claim. Evidence must cite specific metric + threshold. Max 2 claims.

## P2: Build 5-Block Storyline

| Block | Question | Type |
|-------|----------|------|
| **B1: Main Anchor** | Does the method solve the bottleneck? vs strongest baselines on primary benchmark | Main paper |
| **B2: Novelty Isolation** | Does the dominant contribution itself matter? Ablation removing only the novel component | Main paper |
| **B3: Simplicity Check** | Can a bigger version be avoided? Overbuilt variant comparison | Main or Appendix |
| **B4: Frontier Necessity** | Is the modern primitive actually needed? vs strongest simpler alternative | Main or Appendix |
| **B5: Failure Analysis** | What does the method still miss? Error taxonomy, qualitative diagnosis | Main paper |

Delete blocks that don't apply. Add domain-specific blocks if needed (see `references/domain-guide.md`).

## P3: Specify Each Block

For each kept block:

```markdown
### B<N>: [Name] — [MAIN/APPENDIX]

**Claim**: C1/C2 | **Anti-claim**: [what this rules out]
**Dataset**: [name, split, task formulation]
**Compared**: Strongest baseline | Simpler variant | Ours (full) | Ours (−component)
**Primary metric**: [must show clear improvement]
**Setup**: backbone, key hyperparams, GPU-h/run, seeds
**Success**: [specific threshold = "convincing"] | **Failure means**: [interpretation]
**Priority**: MUST-RUN / NICE-TO-HAVE
```

## P4: 4-Stage Run Order

| Stage | Goal | Gate | Cost |
|-------|------|------|------|
| **M0: Sanity** | Overfit tiny split, verify pipeline | Loss decreases, no NaN | < 0.5h |
| **M1: Baseline** | Reproduce strongest baselines fairly | Match published ±σ | Xh |
| **M2: Main** | Full method + novelty ablation (B1+B2) | Claim holds | Xh |
| **M3: Decision** | Simplicity + frontier checks (B3+B4) | No bloat | Xh |
| **M4: Polish** | Multi-seed, failure analysis (B5), appendix | All MUST-RUN done | Xh |

If Stage M2 fails: diagnose via Peng Sida 十问 (see `references/domain-guide.md`).

## Output

### EXPERIMENT_PLAN.md
```
# Experiment Plan
**Problem**: [...] | **Method Thesis**: [...] | **Date**: [...]

## Claim Map (table)
## Paper Storyline (B1-B5, main/appendix/cut)
## Experiment Blocks (B1-B5 full specs)
## Run Order (M0-M4 table with gates, GPU-h, risks)
## Compute Budget (total GPU-h, data prep, bottleneck)
## Risks & Mitigations
```

### EXPERIMENT_TRACKER.md
```
| Run ID | Stage | Purpose | System | Dataset | Metric | Target | Priority | Status |
|--------|-------|---------|--------|---------|--------|--------|----------|--------|
| R001   | M0    | sanity  | Ours   | toy-5   | loss↓  | <0.01  | MUST     | TODO   |
```

## Key Rules

1. Every experiment defends or rules out a claim. No claim → cut.
2. Compact story. Main table first, add ablations only as needed.
3. Defend simplicity. Include deletion study.
4. Strong baselines > long lists. 3 well-tuned > 10 weak.
5. MUST-RUN vs NICE-TO-HAVE. Appendix must not delay core evidence.
6. Stage M0 sanity saves weeks. Overfit first, scale later.
7. Never fabricate results. Plan evidence; don't claim evidence.

## Calls

- Reads: refine-logs/FINAL_PROPOSAL.md (from research-refine)

## Called by

research-refine → experiment-plan (YOU ARE HERE) → paper-write
