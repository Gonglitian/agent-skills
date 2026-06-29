---
name: paper-improve
description: Adversarial paper review + improvement loop. Sends paper PDF/manuscript to Codex GPT-5.5 as a senior ML reviewer, scores 7 dimensions, then iteratively fixes weaknesses until score ≥ 8. Use after paper-write, or when user says "improve paper", "审稿", "review my paper", "polish paper", "paper review", "提升论文质量", "review loop".
---

# Paper Improve: Adversarial Review → Fix → Repeat

Send the paper to Codex GPT-5.5 for adversarial review, then fix weaknesses. Iterate until score ≥ 8 or max rounds reached.

## Pipeline

```
paper/ (from paper-write)
  │
  ├─ P1: Send full paper to GPT-5.5 (senior reviewer, 7-dimension scoring)
  ├─ P2: Parse review → identify CRITICAL / IMPORTANT issues
  ├─ P3: Fix issues (delegate to paper-intro-writing if Intro is weak)
  ├─ P4: Re-send revised paper → re-score
  └─ Repeat P2-P4 until score ≥ 8 or --max-rounds reached
```

## Parameters

Parse from `$ARGUMENTS`:
- `--paper <path>` — path to paper directory or main.tex (default: `paper/`)
- `--max-rounds <N>` — max review-revise rounds (default: 3)
- `--score-threshold <N>` — stop when overall ≥ N (default: 8)
- `--focus <section>` — focus review on specific section (intro/method/experiments/related/conclusion)

## P1: Send to Reviewer

```json
mcp__codex__ask-codex({
  model: "gpt-5.5",
  config: {"model_reasoning_effort": "max"},
  prompt: |
    You are a senior reviewer for a top venue (NeurIPS/ICML/ICLR/CoRL).
    Review this paper critically but fairly.

    Score 7 dimensions (1-10):
    1. Problem Fidelity (15%): Does it solve the stated bottleneck?
    2. Method Specificity (25%): Concrete enough to implement?
    3. Contribution Quality (25%): One focused, novel contribution?
    4. Experimental Rigor (15%): Claims adequately supported?
    5. Clarity (5%): Well-written, easy to follow?
    6. Related Work Coverage (5%): Properly contextualized?
    7. Venue Readiness (10%): Camera-ready quality?

    OVERALL SCORE (1-10): weighted as above.

    For each dimension < 7: specific weakness + concrete fix + priority (CRITICAL/IMPORTANT/MINOR).
    Then: Simplification Opportunities, Missing Ablations, Overclaiming Check, Verdict (ACCEPT/WEAK_ACCEPT/REJECT).

    === PAPER ===
    [Full paper text]
    === END PAPER ===
})
```

## P2: Parse Review

Extract: scores, critical issues, simplification opportunities, missing ablations, overclaiming warnings.

Save to `refine-logs/review-round-N.md`. Track scores in `refine-logs/review-scores.md`.

## P3: Fix Issues

Process by priority:
- **CRITICAL**: fix immediately. If Intro is the issue → delegate to `paper-intro-writing`.
- **IMPORTANT**: fix unless it would cause drift from Problem Anchor.
- **MINOR**: fix if time permits.

**Rules:**
- Never add a component just to satisfy reviewer — ask "does this sharpen the nugget?"
- If reviewer suggests drift, push back with Problem Anchor as evidence.
- Track changes in Git: one commit per fix category.

## P4: Re-evaluate

Send revised paper back to GPT-5.5 in a follow-up call. Include the change log.

Stop conditions:
- Overall ≥ `--score-threshold` AND no CRITICAL issues → **READY**
- `--max-rounds` reached → **BEST EFFORT** (report remaining weaknesses)
- Score decreases two rounds in a row → **STOP** (over-fitting to reviewer)

## Output

```
refine-logs/
├── review-round-1.md       ← Raw GPT-5.5 review
├── review-round-2.md
├── review-scores.md         ← Score evolution table
│   | Round | P.Fid | M.Spec | C.Qual | E.Rigor | Clarity | RW.Cov | V.Ready | Overall | Verdict |
│   |-------|-------|--------|--------|---------|---------|--------|---------|---------|---------|
│   | 1     | 6     | 7      | 7      | 5       | 6       | 7      | 6       | 6.4     | WEAK    |
│   | 2     | 7     | 8      | 8      | 7       | 7       | 7      | 7       | 7.5     | WEAK    |
│   | 3     | 8     | 8      | 8      | 8       | 7       | 7      | 8       | 8.1     | ACCEPT  |
└── FINAL_VERDICT.md         ← Summary + remaining weaknesses

paper/                       ← Updated with fixes
```

## Key Rules

1. **Adversarial, not adversarial-for-its-own-sake.** The goal is a better paper, not a higher score.
2. **Don't over-fit to the reviewer.** If score decreases 2 rounds in a row, stop.
3. **Problem Anchor is sacred.** Reviewer suggestions that change the problem = drift → push back.
4. **One commit per fix category.** Never mix content + formatting changes.
5. **Focus flag.** If `--focus intro`, only review and fix the Introduction.

## Calls

- paper-intro-writing (P3, if Intro is weak)
- Codex MCP (GPT-5.5, P1 + P4)
- Reads: paper/ (from paper-write)

## Called by

paper-write → paper-improve (YOU ARE HERE)
