---
name: paper-write
description: Full paper writing orchestration — from blank LaTeX project to camera-ready PDF. Delegates to paper-intro-writing (Introduction), paper-related (Related Work), and reads research-refine/experiment-plan outputs. Use when user says "写论文", "write paper", "开始写 paper", "paper writing", "draft paper", or wants to produce a submission-ready paper from experiment results.
---

# Paper Write: Full Paper Writing Orchestration

Orchestrate blank LaTeX → camera-ready PDF. **Delegates to atomics; does NOT reimplement.** Writing philosophy and technique references live in `references/writing-guide.md`.

## Pipeline

```
Experiment results → refine-logs/
  │
  ├─ P0: LaTeX init (template, Git, CI)
  ├─ P1: Nugget freeze (single-ping test)
  ├─ P2: Empty tables & figures (Eisner SOP)
  ├─ P3: Abstract (Black Mad-Libs)
  ├─ P4: Introduction     → delegate to paper-intro-writing
  ├─ P5: Method           → from refine-logs/FINAL_PROPOSAL.md
  ├─ P6: Experiments      → from refine-logs/EXPERIMENT_PLAN.md
  ├─ P7: Related Work     → delegate to paper-related
  ├─ P8: Conclusion
  ├─ P9: Ernst 4-round revision
  └─ P10: Submission checklist
```

The writing philosophy, sentence-level techniques, and ESL pitfalls are in `references/writing-guide.md`. Read it before starting.

## Parameters

Parse from `$ARGUMENTS`:
- `--venue <name>` — `ICLR`, `NeurIPS`, `ICML`, `CVPR`, `CoRL`, `ICRA`, `RSS`
- `--overleaf` — use Overleaf instead of local LaTeX
- `--skip-intro` — skip P4 (paper-intro-writing already run)
- `--light` — skip P9-P10

## Phases

### P0: LaTeX Init

```bash
mkdir -p paper/{figures,data,tables} && cd paper && git init
# Download venue template, create main.tex with empty sections
# .gitignore: *.aux *.log *.out *.pdf
# Semantic line breaks: one sentence per line
```

### P1: Nugget Freeze

Write one sentence each: 中文 nugget + English nugget. If you can't, the paper isn't ready.

### P2: Empty Tables & Figures

From EXPERIMENT_PLAN.md: create empty tables with headers + captions, placeholder figures. `\input{}` them into main.tex.

### P3: Abstract

Fill in Black Mad-Libs template. Iterate 2-3 rounds. Structure words: *Unfortunately → In contrast → While promising → Therefore*.

### P4: Introduction → **`paper-intro-writing`**

Delegate. Read its output, verify Widom 5-paragraph structure, verify topic-sentence audit passes.

### P5: Method

Read `refine-logs/FINAL_PROPOSAL.md`. Transform proposal → paper Method section. Start with running example. Every equation: text + figure + equation.

### P6: Experiments

Read `refine-logs/EXPERIMENT_PLAN.md`. Transform plan → paper Experiments section. Headline table first. Each subsection = one claim. Every number answers "compared to what?"

### P7: Related Work → **`paper-related`**

Run paper-related on the paper's own arXiv ID + key competitors. Organize thematically (not laundry list). Each paragraph ends with gap → "In contrast, we…"

### P8: Conclusion

Four paragraphs: restate nugget → summarize results → limitations (2-3, honest) → future work. Tokekar Q5 must be non-empty.

### P9: Ernst 4-Round Revision

Round 1: section-level (serves thesis?). Round 2: paragraph-level (single message? topic sentence?). Round 3: sentence-level (Williams subject-verb, Zinsser clutter removal). Round 4: word-level (LARG micro-rules, linter, TTS read-aloud).

### P10: Submission Checklist

See `references/writing-guide.md` Appendix A for T-4w / T-2w / T-1w / T-1d checklists.

## Output

```
paper/
├── main.tex, references.bib, Makefile
├── figures/ (vector PDF), tables/ (auto-generated), data/
└── README.md
```

## Called by

manual invocation, survey-to-deck (indirect, via research-refine chain)

## Calls

- paper-intro-writing (P4)
- paper-related (P7)
- Reads: refine-logs/FINAL_PROPOSAL.md, refine-logs/EXPERIMENT_PLAN.md
