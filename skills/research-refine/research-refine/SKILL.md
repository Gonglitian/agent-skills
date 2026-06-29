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
- **`--reviewer <model>`** — use external reviewer (e.g. `gpt-5.4` via Codex MCP). Default: internal self-review.
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

## Phase 5: Self-Review

Before finalizing, critically review the proposal:

1. **Anchor check**: Does the method still solve the original problem?
2. **Simplicity check**: Can anything be removed without weakening the main claim?
3. **Novelty check**: Is the dominant contribution clearly different from closest work?
4. **Feasibility check**: Can this be built with stated resources?
5. **Drift check**: Did we accidentally change the problem?

If `--reviewer <model>` is set and Codex MCP is available, send to external reviewer for independent scoring (7 dimensions: Problem Fidelity, Method Specificity, Contribution Quality, Feasibility, Validation Focus, Venue Readiness). Iterate up to `--max-rounds` until score ≥ 8.

## Output

```
refine-logs/
├── FINAL_PROPOSAL.md        ← Clean final proposal
├── round-0-proposal.md       ← Initial
├── round-1-review.md         ← (if reviewer used)
├── round-1-refinement.md     ← (if reviewer used)
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
