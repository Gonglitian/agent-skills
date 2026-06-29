---
name: research-refine
description: Turn a vague research direction into a problem-anchored, concrete method proposal with claim-driven validation. Integrates litian-academic-search (literature grounding), paper-related (citation context), and gap-to-method (design space positioning). Use when user says "refine my approach", "帮我细化方案", "打磨idea", "这个想法可行吗", "refine research plan", or has a fuzzy direction that needs to become a specific, testable research proposal ready for experiment-plan.
---

# Research Refine: Direction → Concrete Proposal

Turn a vague direction into an **anchored, literature-grounded, specific method proposal** with claim-driven validation.

## Core Principles

1. **Problem Anchor is immutable** — freeze it first, check every round
2. **Smallest adequate mechanism wins** — prefer minimal intervention
3. **One dominant contribution** — one sharp thesis, at most one supporting
4. **Literature grounds everything** — every claim references specific papers

## Pipeline

```
Vague direction
  │
  ├─ Phase 0: Freeze Problem Anchor
  ├─ Phase 1: Literature Grounding (litian-academic-search + paper-related)
  ├─ Phase 2: Gap Positioning (gap-to-method)
  ├─ Phase 3: Method Concretization
  ├─ Phase 4: Claim-Driven Validation Sketch
  ├─ Phase 5: Self-Review (internal, or optional external reviewer)
  └─ Output: FINAL_PROPOSAL.md → handoff to experiment-plan
```

## Parameters

- **Direction**: free-text description of the research direction
- **`--no-literature`** — skip literature grounding (when you already know the field)
- **`--reviewer <model>`** — use external reviewer (e.g. `gpt-5.5` via Codex MCP). Default: internal self-review.
- **`--max-rounds <N>`** — max review-revise rounds (default: 3)
- **`--output <dir>`** — output directory (default: `refine-logs/`)

## Phase 0: Freeze Problem Anchor

Before any literature or method design, extract:

```markdown
## Problem Anchor
- **Bottom-line problem**: What technical problem must be solved?
- **Must-solve bottleneck**: What specific weakness in current methods is unacceptable?
- **Non-goals**: What is explicitly NOT the goal?
- **Constraints**: Compute, data, time, tooling.
- **Success condition**: What evidence proves the problem is solved?
```

This anchor is copied verbatim into every round. If reviewer feedback would change the problem → call it **drift** and push back.

## Phase 1: Literature Grounding

Unless `--no-literature`:

### 1a: Broad search
```
/litian-academic-search "<core problem keywords>" --sources omnibox,arxiv,s2 --k 10 --year 2023-
```

### 1b: Targeted citation graph
For top-3 papers found, trace their neighborhood:
```
paper-related <arxiv_id> --lens citation --k 8
```

### 1c: Identify the gap

From the literature, answer:
1. **Current pipeline failure point**: where does the baseline break?
2. **Why naive fixes insufficient**: larger model? more data? prompting?
3. **Closest existing work**: who attempted this, and why didn't they solve it fully?
4. **Core technical gap**: what mechanism is missing?

Every claim about "existing work fails at X" must cite specific papers.

## Phase 2: Gap Positioning

If the direction involves design choices (architecture, training, representation), optionally run:
```
gap-to-method "<direction>" --output docs/reports/
```

This produces a design-space matrix showing exactly which combinations are unexplored. Use it to position the method precisely.

## Phase 3: Method Concretization

Design the method. Must answer "how would we actually build this?":

### 3.1: Route Selection

Before locking the method, compare two routes if both plausible:
- **Route A: Minimal** — smallest mechanism targeting the bottleneck
- **Route B: Modern** — uses current primitives (diffusion, VLM, RL, etc.) if cleaner

Choose based on: novelty clarity, implementation feasibility, venue fit.

### 3.2: Method Specification

```markdown
## Method Thesis
- One-sentence thesis:
- Why this is the smallest adequate intervention:

## Contribution Focus
- Dominant contribution (one):
- Optional supporting (at most one):
- Explicit non-contributions:

## Complexity Budget
- Frozen / reused:
- New trainable components (cap: 2):
- Tempting additions intentionally excluded:

## Core Mechanism
- Input / output:
- Architecture:
- Training signal / loss:
- Why novel:

## Training Plan
- Data source / construction:
- Stagewise or joint:
- Key hyperparameters:
- Estimated GPU-hours:

## Failure Modes
- [Mode]: [Detection] → [Mitigation]
```

If the method is still "add a module" or "use a planner" — it's not concrete enough.

## Phase 4: Claim-Driven Validation Sketch

For each core claim, define the **smallest strong experiment**:

```markdown
## Claim 1: [Main claim]
- Experiment:
- Baseline:
- Metric:
- Expected outcome:

## Claim 2: [Optional supporting]
- Experiment:
- Baseline:
- Metric:
- Expected outcome:
```

Rules:
- Default: 1-3 experiment blocks (leave full experiment matrix to experiment-plan)
- One block must directly validate the Problem Anchor
- If a modern primitive is central → include a necessity check (ablation removing it)

## Phase 5: External Adversarial Review (Codex MCP)

**Default: ON.** Use Codex MCP (`mcp__codex__exec`) to get an independent model (GPT-5.4) to review the proposal as a senior ML reviewer. This is the adversarial check that catches blind spots.

If Codex MCP is unavailable, fall back to internal self-review.

### 5.1: Send to Reviewer

```json
mcp__codex__exec({
  model: "gpt-5.5",
  config: {"model_reasoning_effort": "max"},
  prompt: |
    You are a senior ML reviewer for a top venue (NeurIPS/ICML/ICLR/CoRL).
    This is an early-stage, method-first research proposal.

    Your job is NOT to reward extra modules or a giant benchmark checklist.
    Your job IS to stress-test whether the proposed method:
    (1) still solves the original anchored problem,
    (2) is concrete enough to implement,
    (3) presents a focused, elegant contribution.

    Review principles:
    - Prefer the smallest adequate mechanism over a larger system.
    - Penalize parallel contributions that make the paper feel unfocused.
    - Do not ask for extra experiments unless needed to prove core claims.

    Read the Problem Anchor first. If your suggested fix would change the problem
    being solved, call that out explicitly as DRIFT.

    === PROPOSAL ===
    [Paste the FULL proposal from Phase 3-4]
    === END PROPOSAL ===

    Score these 7 dimensions from 1-10:

    1. **Problem Fidelity** (15%): Does the method still attack the original bottleneck?
    2. **Method Specificity** (25%): Are interfaces, representations, losses, training stages concrete?
    3. **Contribution Quality** (25%): One dominant mechanism-level contribution with real novelty?
    4. **Feasibility** (10%): Can this be built with stated resources?
    5. **Validation Focus** (5%): Are experiments minimal but sufficient for core claims?
    6. **Venue Readiness** (5%): Would the contribution feel sharp enough for a top venue?
    7. **Simplicity** (15%): Is this the smallest adequate mechanism, or is it overbuilt?

    **OVERALL SCORE** (1-10): weighted as above.

    For each dimension scoring < 7: specific weakness + concrete fix + priority (CRITICAL/IMPORTANT/MINOR).
    Then add:
    - **Simplification Opportunities**: 1-3 ways to delete/merge components. Write NONE if tight.
    - **Drift Warning**: NONE if proposal still solves anchored problem; else explain drift.
    - **Verdict**: READY (≥8) / REVISE / RETHINK
})
```

### 5.2: Parse Review & Iterate

Save review to `refine-logs/round-N-review.md`. Track scores in `refine-logs/score-history.md`:

```markdown
| Round | P.Fidelity | M.Specificity | C.Quality | Feasibility | V.Focus | V.Readiness | Simplicity | Overall | Verdict |
|-------|-----------|---------------|-----------|-------------|---------|-------------|------------|---------|---------|
| 1     | X         | X             | X         | X           | X       | X           | X          | X       | REVISE  |
```

### 5.3: Revise With Anchor Check

Before changing anything:
1. Copy **Problem Anchor verbatim**
2. **Anchor Check**: Does the revised method still solve it? Which reviewer suggestions would cause drift?
3. **Simplicity Check**: What can be removed? Which reviewer suggestions add unnecessary complexity?

Process feedback:
- **Valid** → sharpen mechanism, simplify
- **Debatable** → revise with reasoning
- **Drift-causing** → push back with Problem Anchor as evidence

Save revised proposal to `refine-logs/round-N-refinement.md` (full proposal, not just diffs).

### 5.4: Re-evaluate

Send revised proposal back to Codex in a follow-up call. Iterate until:
- Overall score ≥ 8 AND verdict READY AND no unresolved drift
- Or `--max-rounds` reached

### 5.5: Fallback Self-Review (no Codex MCP)

If Codex MCP unavailable, critically self-review on the same 7 dimensions. Flag that no external reviewer was used.

## Output

```
refine-logs/
├── FINAL_PROPOSAL.md        ← Clean final proposal
├── round-0-proposal.md       ← Initial
├── round-1-review.md         ← Codex reviewer response
├── round-1-refinement.md     ← Revised proposal
├── score-history.md          ← Score tracking table
└── literature_grounding.md   ← Phase 1 results
```

## Handoff

When done, the natural next step is:
```
experiment-plan → turns proposal into detailed experiment roadmap
```

## Edge Cases

- **Direction too vague**: ask 2-3 clarifying questions before starting
- **No literature found**: flag as potentially novel (or wrong keywords), widen search
- **Closest work is very close**: run gap-to-method to find the exact differentiation point
- **Reviewer causes drift**: push back with Problem Anchor as evidence
