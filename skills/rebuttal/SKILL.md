---
name: rebuttal
description: Write a structured rebuttal using Concede–Clarify–Commit structure. Parses reviewer comments, identifies overlapping concerns across reviewers, builds consolidated Table R1, produces venue-formatted rebuttal. Use when user says "写 rebuttal", "rebuttal", "回复审稿意见", "response to reviewers", or receives paper reviews and needs to respond.
---

# Rebuttal: Concede–Clarify–Commit

Parse reviews → find overlapping concerns → respond with data. **Reference: 03_writing.md Ch9.**

## Pipeline

```
Reviews (OpenReview / email / PDF)
  │
  ├─ P1: Parse reviews → extract all concerns per reviewer
  ├─ P2: Overlap map → find concerns shared across reviewers
  ├─ P3: Build consolidated Table R1 (one table answers all reviewers)
  ├─ P4: Write per-reviewer responses (Concede–Clarify–Commit)
  ├─ P5: Format for venue
  └─ Output: rebuttal.pdf / response.txt
```

## Parameters

Parse from `$ARGUMENTS`:
- **Positional**: path to reviews file or paste inline
- `--venue <name>` — `NeurIPS` (OpenReview per-reviewer), `ICLR` (OpenReview, ≤5000 char), `CVPR` (single-page PDF, ~900 words), `CoRL` (OpenReview), `ICRA` (no rebuttal usually)
- `--new-experiments` — path to new experiment results (Table R1 data)

## P1: Parse Reviews

For each reviewer (R1, R2, R3...), extract:
- **Score** (if given)
- **Strengths** (leverage these in response)
- **Weaknesses** (each becomes a Q1, Q2, ...)
- **Questions** (explicit questions must be answered)
- **Suggestions** (optional improvements, lower priority)

```markdown
## R1 (Score: 6)
**Strengths**: [S1] ... [S2] ...
**Weaknesses**:
- Q1: [concern] — SCORE-MOVING / CLARIFICATION / SUGGESTION
- Q2: [concern]
```

Classify each concern:
- **SCORE-MOVING**: fixing this changes the reviewer's vote
- **CLARIFICATION**: misunderstanding that text can fix
- **SUGGESTION**: nice-to-have, won't change score

## P2: Overlap Map

Find concerns shared across reviewers. Shared concerns = highest priority.

```markdown
| Concern | R1 | R2 | R3 | Priority |
|---------|----|----|----|----|
| Missing Baseline-X comparison | Q1 | Q3 | — | CRITICAL (2 reviewers) |
| Method description unclear | Q2 | — | Q1 | CRITICAL (2 reviewers) |
| Limited real-robot evaluation | — | Q4 | Q2 | IMPORTANT (2 reviewers) |
```

If one answer satisfies 3 reviewers, put it in Table R1 and make all reviewer blocks point to it.

## P3: Build Table R1

One consolidated table that answers the most common SCORE-MOVING concerns. This is the **centerpiece** of the rebuttal.

```markdown
**Table R1: Additional experiments in response to all reviewers.**

| Experiment | Baseline | Ours | Δ | Answers |
|------------|----------|------|---|---------|
| Baseline-X on benchmark Y | 72.3 | 84.1 | +11.8 | R1.Q1, R2.Q3 |
| Ablation: −component Z | 84.1 | 78.5 | −5.6 | R1.Q4 |
```

**If `--new-experiments` is provided**: use those results. Otherwise: identify which experiments can be run in the rebuttal window and run them now. Day 1: identify score-moving ablation → Day 2-5: run → Day 6: Table R1 done.

## P4: Per-Reviewer Response

**Concede–Clarify–Commit** for each concern. One block per concern, numbered Q1/Q2/...

```markdown
**R1.Q1: Missing Baseline-X comparison**

We thank R1 for this suggestion. We agree that Baseline-X is an important comparison point. We have now run this experiment: [result in Table R1, Row 1]. Our method outperforms Baseline-X by +11.8 points, confirming that [mechanism] provides gains beyond [Baseline-X's approach]. We will add this comparison to Table 2 in the camera-ready.

**R1.Q2: Method description unclear in §3.2**

We apologize for the lack of clarity. The key point is: [one-sentence clarification]. We have revised §3.2 (L234-L256) to make this explicit, adding a step-by-step description of the [mechanism] with a new Figure 3.
```

**Rules:**
- Every block starts with a **bold一句话答案**
- **Never say "the reviewer is wrong"** → say "we may not have been clear"
- SCORE-MOVING: answer + new data (Table R1) + camera-ready commitment
- CLARIFICATION: one-sentence fix + line number reference + camera-ready commitment
- SUGGESTION: thank + brief response. If infeasible, explain why politely.
- Concede precisely: "R1 correctly points out X. We agree. [fix]."
- Paragraphs ≤ 4 lines. Reviewer fatigue is real.

## P5: Format for Venue

| Venue | Format | Key constraints |
|-------|--------|----------------|
| NeurIPS | OpenReview per-reviewer | Soft limit ~2-5k chars per reviewer, new experiments encouraged |
| ICLR | OpenReview per-reviewer | ≤5000 chars per reviewer, multi-round discussion |
| CVPR/ICCV | Single-page PDF | ~900 words, figures allowed, no new methods |
| CoRL | OpenReview | ~5000 chars, new experiments allowed |
| ICRA/IROS | Usually no rebuttal | — |

Top of document: consolidated Table R1 (all reviewers point to it).
Bottom of document: per-reviewer blocks with Q1/Q2 numbering.
Final line: "We will incorporate all changes in the camera-ready."

## 1-Week Rebuttal Playbook

| Day | Action |
|-----|--------|
| Day 1 | Parse reviews, build overlap map. Identify 1-2 score-moving ablations. |
| Day 2-5 | Run experiments. Small backbone / subset for speed. Same split for comparability. |
| Day 6 | Table R1 complete. Write per-reviewer responses. |
| Day 7 | Labmate reads. Final polish. Submit. |

## Output

```
refine-logs/
├── rebuttal/
│   ├── review-parse.md       ← P1: parsed concerns
│   ├── overlap-map.md         ← P2: shared concerns
│   ├── table-r1.md            ← P3: consolidated results
│   ├── response-r1.md         ← P4: per-reviewer response
│   ├── response-r2.md
│   ├── response-r3.md
│   └── rebuttal-final.pdf     ← P5: venue-formatted
```

## Key Rules

1. **Concede precisely, never deflect.** Admitting a weakness is a technical demonstration of maturity.
2. **Data first.** Every SCORE-MOVING concern needs new data.
3. **Overlap = leverage.** One Table R1 answering 3 reviewers > 3 separate tables.
4. **Bold one-sentence answer per block.** Reviewers skim; make it impossible to miss.
5. **Line numbers.** "L234-L256" shows you actually fixed it.
6. **Camera-ready commitment.** Every block ends with what changes in the final paper.
7. **1-week playbook.** Day 1 identify, Day 7 submit. Don't over-promise experiments you can't run.

## Calls

- Codex MCP (GPT-5.5) — optional: use as adversarial "reviewer of the rebuttal" before submission
- Reads: paper/ (from paper-write), reviews file (user-provided)

## Called by

manual invocation after receiving reviews
