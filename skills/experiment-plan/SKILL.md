---
name: experiment-plan
description: Turn a refined research proposal into a claim-driven, paper-oriented experiment roadmap with progressive 4-stage execution order. Integrates with research-refine output (FINAL_PROPOSAL.md). Designs compact paper storylines: main anchor → novelty isolation → simplicity check → frontier necessity → failure analysis. Produces EXPERIMENT_PLAN.md + EXPERIMENT_TRACKER.md. Includes Embodied AI / VLA specific evaluation concerns (sim-to-real gap, task diversity, real-robot protocols). Use after research-refine, or when user says "实验计划", "experiment plan", "设计实验", "ablation matrix", "evaluation protocol", "run order".
---

# Experiment Plan: Claim-Driven, Paper-Oriented Validation

Turn a method proposal into a **claim → evidence → run order** roadmap. Every experiment must change a reviewer belief or it gets cut.

**References**: ARIS experiment-plan (5-block storyline), Peng Sida (实验能力训练·经典十问), agent-research-skills (4-stage progressive framework from AI-Scientist-v2).

## Constants

- **MAX_PRIMARY_CLAIMS = 2** — one dominant + one supporting
- **MAX_CORE_BLOCKS = 5** — keep the must-run story compact
- **MAX_BASELINE_FAMILIES = 3** — few strong baselines > many weak ones
- **DEFAULT_SEEDS = 3** — for stochastic evaluation
- **OUTPUT_DIR = `refine-logs/`** — shared with research-refine

## Pipeline

```
refine-logs/FINAL_PROPOSAL.md (from research-refine)
  │
  ├─ Phase 0: Load proposal context
  ├─ Phase 1: Freeze paper claims & anti-claims
  ├─ Phase 2: Build 5-block experimental storyline
  ├─ Phase 3: Specify each block (dataset, baselines, metrics, gates)
  ├─ Phase 4: 4-stage progressive run order
  ├─ Phase 5: Domain-specific considerations (VLA / Embodied AI)
  └─ Output: EXPERIMENT_PLAN.md + EXPERIMENT_TRACKER.md
```

## Phase 0: Load Proposal Context

Read existing files if available:
- `refine-logs/FINAL_PROPOSAL.md` — method, claims, constraints
- `refine-logs/REVIEW_SUMMARY.md` — critical reviewer concerns
- `refine-logs/score-history.md` — remaining weaknesses

Extract: **Problem Anchor, dominant contribution, method details, compute/data constraints, reviewer-flagged risks.** If files don't exist, derive from user prompt.

## Phase 1: Freeze Paper Claims & Anti-Claims

Before proposing ANY experiment, write down exactly what must be defended — and what must be ruled out:

```markdown
## Claim Map

| # | Claim | Why It Matters | Anti-Claim to Rule Out | Minimum Convincing Evidence |
|---|-------|----------------|----------------------|----------------------------|
| C1 | [dominant] | ... | "gain is just from more params" | method > baseline by ≥X on metric Y |
| C2 | [supporting, optional] | ... | "component is decorative" | ablation −component < full method by ≥X |
```

**Anti-claims are as important as claims.** For every positive claim, define what the reviewer will suspect instead. The experiment must rule out the anti-claim.

Rules:
- Max 2 claims (one dominant + one supporting)
- No claim without an anti-claim
- "Minimum convincing evidence" must cite specific metric + threshold
- If a claim can't be operationalized into a measurable test, it's not a claim — it's a wish

## Phase 2: Build the 5-Block Experimental Storyline

Adapted from ARIS. Design 5 blocks; delete those that don't apply.

### Block 1: Main Anchor Result
Does the method solve the actual bottleneck? Headline table: our method vs strongest baselines on primary benchmark.

### Block 2: Novelty Isolation
Does the dominant contribution itself matter? Ablation removing ONLY the novel component, keeping everything else equal. If multi-component, test each separately.

### Block 3: Simplicity / Elegance Check
Can a bigger or more complex version be avoided? Compare against an **overbuilt variant** or a **tempting extra component** the paper intentionally rejects. This defends the "smallest adequate mechanism" principle from research-refine.

### Block 4: Frontier Necessity Check
If an LLM / VLM / Diffusion / RL component is central — is it actually the right tool? Compare against the **strongest simpler/older alternative**. If the method is intentionally non-frontier, state this explicitly and skip.

### Block 5: Failure Analysis / Qualitative Diagnosis
What does the method still miss? Error categorization, failure mode taxonomy, qualitative examples. Shows intellectual honesty and guides future work.

For each block, assign: **Main paper** (essential) / **Appendix** (supporting) / **Cut** (not worth budget).

## Phase 3: Specify Each Experiment Block

For every kept block, fully specify:

```markdown
### Block N: [Name] — [MAIN / APPENDIX]

**Claim tested**: C1 / C2
**Why this block exists**: [one sentence]
**Anti-claim this rules out**: [specific reviewer suspicion]

**Dataset / Task**:
- Dataset: [name, version, license]
- Split: [train/val/test sizes, any stratification]
- Task formulation: [input → output, special protocols]

**Compared Systems**:
| System | What It Is | Why Included |
|--------|------------|-------------|
| Strongest baseline | [published SOTA] | upper-bound reference |
| Simpler variant | [ours minus novelty] | novelty isolation |
| Ours (full) | [complete method] | system under test |
| Ours (−component) | [ablation] | component necessity |

**Metrics**:
- Primary: [decisive metric] — must show clear improvement
- Secondary: [supporting metrics]
- Statistical test: [t-test / bootstrap / etc.] at p < 0.05

**Setup Details**:
- Backbone: [frozen / fine-tuned / from scratch]
- Key hyperparameters: [lr, batch, epochs, schedule, seeds]
- Training budget: [GPU-hours per run]
- Seeds: [N per configuration]

**Success Criterion**: [specific threshold that counts as "convincing"]
**Failure Interpretation**: [if negative, does it falsify the claim or was the experiment underpowered?]
**Table / Figure Target**: [where this appears in paper]
**Priority**: MUST-RUN / NICE-TO-HAVE
```

## Phase 4: Progressive 4-Stage Run Order

Adapted from AI-Scientist-v2 / agent-research-skills, with Peng Sida's experimental discipline:

### Stage 1: Sanity (M0)
- Overfit on tiny split (1-5 samples) — verify pipeline end-to-end
- Check: loss decreases, no NaN, metrics compute correctly
- Gate: **pipeline bug-free** → proceed
- Cost: < 0.5 GPU-hours
- **Reference**: Peng Sida 十问 — this catches 80% of setup bugs

### Stage 2: Baseline Calibration (M1)
- Reproduce strongest baselines on full dataset
- Tune their hyperparameters fairly — do NOT sandbag
- Check: our reproduced numbers match published results (± reasonable variance)
- Gate: **baselines credible** → proceed
- **If baselines don't reproduce**: debug before proceeding. This is the #1 paper-killer.

### Stage 3: Main Method (M2)
- Run full method on primary benchmarks (Block 1: Main Anchor)
- Run novelty isolation ablations (Block 2)
- First-pass results inform whether to continue
- Gate: **main claim holds** → proceed to ablations; **fails** → diagnose via Peng Sida 十问, iterate or abort

### Stage 4: Decision & Polish (M3-M4)
- Simplicity check (Block 3) + Frontier necessity (Block 4)
- Failure analysis (Block 5)
- Robustness: additional seeds, datasets, hyperparameter sensitivity
- Appendix material
- Gate: **all MUST-RUN blocks complete** → ready for paper writing

**Run Order Table:**

```markdown
| Milestone | Stage | Goal | Key Runs | Decision Gate | Est. GPU-h | Risk |
|-----------|-------|------|-----------|---------------|------------|------|
| M0 | Sanity | Pipeline works | Overfit test | Loss decreases | 0.5h | Low |
| M1 | Baseline | Reproduce baselines | N baselines × K seeds | Match published ±σ | Xh | Medium |
| M2 | Main | Core claims | Full method + novelty ablation | Claim holds | Xh | **High** |
| M3 | Decision | Simplicity + frontier | Deletion study + alt comparison | No bloat, component needed | Xh | Medium |
| M4 | Polish | Robustness + appendix | Multi-seed, extra datasets | Appendix complete | Xh | Low |
```

## Phase 5: Domain-Specific Considerations

### Embodied AI / VLA / Robot Manipulation

**Simulation evaluation:**
- Simulator + version (Isaac Sim / MuJoCo / LIBERO / CALVIN / RLBench)
- Task distribution: single-task / multi-task / language-conditioned / generalization split
- Domain randomization: lighting, textures, object positions, camera poses
- Success rate: binary (task-complete) or progressive (subtask progress)? Define clearly.
- Episode budget: 100-1000 depending on success-rate variance (higher variance → more episodes)

**Real-robot evaluation (if applicable):**
- Robot platform + sensor suite
- Trials per task: ≥ 20 for statistical meaning
- Object/scene variation: ≥ 3-5 configurations
- Failure taxonomy: perception error / planning error / execution error
- Video recording: side-by-side comparison with baselines

**Sim-to-real gap (if claiming generalization):**
- Train in sim → evaluate zero-shot on real
- Compare sim vs real performance on matched tasks
- Ablation: which domain randomization helps transfer?

**Compute realism:**
- VLA training: 100-1000+ GPU-hours — budget honestly
- Simulation data generation cost: factor into total
- Multi-GPU: DDP / FSDP strategy

### Other Domains

Adapt the 5-block structure: for theoretical work, replace experiments with proofs; for systems work, add throughput/latency blocks.

## Peng Sida 十问 (When Experiments Fail)

When Stage 3 results are negative, systematically check:

1. **Data pipeline** — correct split? no leakage? preprocessing consistent?
2. **Metric correctness** — metric implementation matches definition?
3. **Gradient flow** — vanishing/exploding gradients?
4. **Hyperparameter sensitivity** — tried wider range? learning rate the culprit?
5. **Baseline strength** — baselines properly tuned? not accidentally sandbagged?
6. **Implementation bugs** — dimension mismatch? off-by-one? wrong loss reduction?
7. **Statistical significance** — enough seeds? variance too high?
8. **Task difficulty** — is the benchmark saturated? or impossibly hard?
9. **Overfitting** — training performance >> evaluation performance?
10. **Core hypothesis** — is the fundamental assumption wrong?

Document which questions were checked and the findings. This becomes the "lessons learned" section of the experiment log.

## Output

### EXPERIMENT_PLAN.md

```markdown
# Experiment Plan

**Problem**: [from FINAL_PROPOSAL.md]
**Method Thesis**: [one-sentence]
**Date**: [today]

## Claim Map
| # | Claim | Anti-Claim | Minimum Evidence | Linked Blocks |
|---|-------|-----------|-----------------|---------------|
| C1 | ... | ... | ... | B1, B2 |
| C2 | ... | ... | ... | B3 |

## Paper Storyline
- Main paper must prove: [B1, B2, ...]
- Appendix can support: [...]
- Intentionally cut: [...]

## Experiment Blocks
### Block 1: [Name] — MAIN
[full specification from Phase 3]

### Block 2: [Name] — MAIN
...

## Run Order
| Milestone | Stage | Goal | Runs | Gate | GPU-h | Risk |
|-----------|-------|------|------|------|-------|------|
...

## Compute Budget
- Total estimated GPU-hours:
- Data preparation:
- Biggest bottleneck:

## Risks & Mitigations
- [Risk]: [Mitigation]
```

### EXPERIMENT_TRACKER.md

```markdown
# Experiment Tracker

| Run ID | Milestone | Purpose | System | Dataset | Metric | Target | Priority | Status | Result |
|--------|-----------|---------|--------|---------|--------|--------|----------|--------|--------|
| R001 | M0 | sanity | Ours | toy-5 | loss↓ | <0.01 | MUST | TODO | — |
```

One row per run. Update as experiments progress. Status: TODO → RUNNING → DONE → BLOCKED.

## Key Rules

1. **Every experiment defends or rules out a claim.** No claim = cut it.
2. **Compact paper story.** Design the main table first; add ablations only as needed.
3. **Defend simplicity.** Include a deletion study.
4. **Defend frontier choices.** Prove the modern component beats the simpler alternative.
5. **Strong baselines > long baseline lists.** 3 well-tuned baselines > 10 weak ones.
6. **MUST-RUN separated from NICE-TO-HAVE.** Appendix ideas must not delay core evidence.
7. **Stage 1 sanity saves weeks.** Overfit first, scale later.
8. **Never fabricate results.** Plan evidence; do not claim evidence.
9. **Reuse proposal constraints.** Don't invent budgets the method can't afford.
10. **十问 when stuck.** Document which questions checked and findings.

## Handoff

```
research-refine → experiment-plan (you are here) → manual execution / experiment-bridge → auto-review-loop
```

The experiment-tracker run IDs map to specific launchable experiments. Downstream skills read the tracker to know what to run, monitor, and record.
