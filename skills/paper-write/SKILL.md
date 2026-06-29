---
name: paper-write
description: Full paper writing orchestration — from blank LaTeX project to camera-ready PDF. Chains 10 phases: LaTeX init → nugget freeze → empty tables/figures → abstract → introduction (delegates to paper-intro-writing) → method → experiments → related work (delegates to paper-related) → conclusion → Ernst 4-round revision → submission checklist. Reads from research-refine (FINAL_PROPOSAL.md) and experiment-plan (EXPERIMENT_PLAN.md). Integrated with 03_writing.md textbook (Widom/SPJ/Black/Ernst/Peng), Peng Sida templates, and ARIS paper-writing orchestration patterns. Use when user says "写论文", "write paper", "开始写 paper", "paper writing", "从实验到论文", "draft paper", or has experiment results ready and wants to produce a submission-ready paper.
---

# Paper Write: Full Paper Writing Orchestration

Orchestrate the complete paper writing pipeline — from blank LaTeX project to camera-ready PDF. **Delegates** to paper-intro-writing, paper-related, and reads research-refine/experiment-plan outputs.

**Core philosophy**: *"Writing is the machinery of research, not the printer."* Write the paper first, let it drive experiments.

## Read Before Starting

This skill synthesizes three knowledge sources. The orchestrator (you, the LLM) should read at least these excerpts before Phase 1:

- **03_writing.md §Ch1**: "Write the paper first" — Eisner SOP, LaTeX skeleton before experiments
- **03_writing.md §Ch2**: Nugget / single ping — the one idea the paper communicates
- **03_writing.md §Ch3**: Page one is sacred — Widom 5-paragraph, Black 12-question pre-check

Full reference: `~/proj/research-kb/research-guidance/03_writing.md` (820 lines, 9 chapters + 3 appendices).

## Pipeline

```
Experiment results ready
  │
  ├─ Phase 0: LaTeX project init (template, Git, CI, semantic line breaks)
  ├─ Phase 1: Nugget & Story (freeze nugget, single-ping test, Black 12 Qs)
  ├─ Phase 2: Empty tables & figures first (Eisner SOP)
  ├─ Phase 3: Abstract (Black Mad-Libs fill-in-the-blank)
  ├─ Phase 4: Introduction → delegate to paper-intro-writing
  ├─ Phase 5: Method (from research-refine FINAL_PROPOSAL.md)
  ├─ Phase 6: Experiments (from experiment-plan EXPERIMENT_PLAN.md)
  ├─ Phase 7: Related Work → delegate to paper-related
  ├─ Phase 8: Conclusion
  ├─ Phase 9: Ernst 4-round revision (section → paragraph → sentence → word)
  └─ Phase 10: Submission checklist (T-4w → T-1d)
```

## Parameters

- **`--venue <name>`** — target venue: `ICLR`, `NeurIPS`, `ICML`, `CVPR`, `CoRL`, `ICRA`, `RSS` (default: from FINAL_PROPOSAL.md context)
- **`--overleaf`** — use Overleaf instead of local LaTeX (default: local LaTeX with Git)
- **`--skip-intro`** — skip Phase 4 if paper-intro-writing already run
- **`--light`** — fast mode: skip Phases 9-10 (revision + checklist), draft only

## Phase 0: LaTeX Project Init

```bash
# Create paper directory structure
mkdir -p paper/{figures,data,tables}
git init paper/
cd paper/

# Download venue template
# For arXiv/ICLR/NeurIPS: use Overleaf template or venue GitHub
# For CVPR/ICCV: guanyingc/latex_paper_writing_tips
# For general: Eisner's skeleton approach

# Initialize with empty sections
cat > main.tex << 'LATEX'
\documentclass[conference]{IEEEtran}  % or venue-specific
\title{<PLACEHOLDER>}
\author{<ANONYMIZED>}

\begin{document}
\maketitle
\begin{abstract}\end{abstract}
\section{Introduction}\label{sec:intro}
\section{Related Work}\label{sec:related}
\section{Method}\label{sec:method}
\section{Experiments}\label{sec:experiments}
\section{Conclusion}\label{sec:conclusion}
\bibliographystyle{IEEEtran}
\bibliography{references}
\end{document}
LATEX

# Git setup
cat > .gitignore << 'EOF'
*.aux *.log *.out *.bbl *.blg *.pdf *.synctex.gz
EOF
git add -A && git commit -m "Empty LaTeX skeleton"
```

**Key rules from 03_writing.md Ch8:**
- Semantic line breaks: one sentence per line in `.tex` source
- `latexmk` as build driver
- Annotated Git tags for each submission: `git tag -a neurips26-submission`
- CI: GitHub Actions `latexmk` on every push

## Phase 1: Nugget & Story

Before writing a single word of content, answer these:

### Nugget (from 03_writing.md Ch2, SPJ / Black)

Write in one sentence each:
- **中文 nugget**: 这篇论文的单一核心洞察是什么？
- **English nugget**: What is the one idea a reader remembers 10 years later?

**Test**: If you can't write it in one sentence, the paper isn't ready to write.

### Black's 12-Question Pre-Check (from 03_writing.md Ch3)

Answer these in writing before proceeding:
1. What is the goal of this paper? Why should anyone care?
2. Who is the target audience?
3. **Hypothesis**: "My hypothesis is…" (even if not in the final paper)
4. What is the problem/obstacle?
5. **Nugget** — key insight?
6. Elevator pitch (≤3 sentences)
7. What will the teaser figure be?
8. Key previous works — where do they fall short?
9. How will you evaluate quantitatively?
10. What is your demo?
11. Key risks?
12. Is the data ready?

## Phase 2: Empty Tables & Figures First

**Eisner SOP** (from 03_writing.md Ch1): *"Make empty result tables with row and column headers and explanatory captions. Make empty graphs with axes and captions."*

From `refine-logs/EXPERIMENT_PLAN.md`:
1. Create **empty tables** with all row/column headers, captions
2. Create **placeholder figures** with axes labels, captions
3. Add `\input{}` and `\includegraphics{}` commands in the LaTeX source

This step **materializes the experiment plan** — you immediately see what's missing.

## Phase 3: Abstract

**Black Mad-Libs template** (from 03_writing.md Ch4):

> *"[Task] is widely used in [domain A] and has applications in [domain B]. Recent work has addressed this problem by [approach]. **Unfortunately**, all of these approaches [limitation]. **In contrast**, we [nugget]. This fixes [fix]; **however**, it does not solve [new problem]. **Consequently**, we develop [second contribution]. **While promising**, [next obstacle]. **Therefore**, we further [third contribution]. We evaluate [qualitative + quantitative] on [datasets] and find that it is more accurate than the state of the art."*

Iterate 2-3 rounds. The abstract is the paper's DNA — get it right before writing the rest.

## Phase 4: Introduction → paper-intro-writing

**Delegate to `paper-intro-writing` skill.** It provides:
- 6-paragraph golden skeleton (Widom 5-paragraph + Kaiming)
- 4 hook archetypes
- 6 paragraph archetypes with sentence templates
- Black Mad-Libs intro fill-in-the-blank
- 25-item self-check checklist

Do NOT reimplement Introduction writing here. The paper-intro-writing skill is already comprehensive.

## Phase 5: Method

Source material: `refine-logs/FINAL_PROPOSAL.md` from research-refine.

Transform from proposal to paper Method section:

1. **Start with a running example** (from 03_writing.md Ch4). Ernst/SPJ/Black: *"A running example used throughout the paper is helpful."* Show the example BEFORE equations — text → figure → equation.

2. **Problem formalization**: one paragraph, notation consistent throughout.

3. **Method subsections**: map to the proposal's complexity budget
   - Frozen/reused backbone
   - Core mechanism (the nugget — this section should be the paper's second-most-important after Introduction)
   - Optional supporting component
   - Training recipe

4. **Every equation must be explained three ways** (Black): text, figure, equation.

5. **Don't describe what you tried** — describe what worked (Ernst). This is not a lab notebook.

**Self-check**: Can an experienced PhD student implement your method from this section alone?

## Phase 6: Experiments

Source material: `refine-logs/EXPERIMENT_PLAN.md` from experiment-plan.

Transform from experiment plan to paper Experiments section:

1. **Start with the main anchor table** (Block 1). This is the paper's headline result.

2. **One claim per subsection**. Map from the Claim Map in EXPERIMENT_PLAN.md.

3. **Every number must answer "compared to what?"** — include the baseline number in the same sentence.

4. **Ablations defend claims, not curiosity**. Only include ablations that change a reviewer belief (from experiment-plan Block 2-4).

5. **Failure analysis** (from experiment-plan Block 5) shows intellectual honesty.

6. **Metrics**: primary first, secondary supporting. Statistical significance clearly reported.

## Phase 7: Related Work → paper-related

**Delegate to `paper-related` skill** for citation graph data. Then organize:

**The cardinal rule** (from 03_writing.md Ch3): Related Work goes AFTER the Introduction, not before. SPJ: *"This related work section is like a sandbar or barrier between your reader and your key idea."*

Organize thematically, NOT as a laundry list:
- **Group A**: works that share your goal but use a different approach
- **Group B**: works that use similar techniques but for a different problem
- **Group C**: works you directly improve upon

Each paragraph: "Prior work X does Y [cite]. However, it does not address Z [cite]. In contrast, we…"

**Never**: "[Smith 2020] proposes X. [Jones 2021] proposes Y. [Lee 2022] proposes Z." This is a bibliography, not related work.

## Phase 8: Conclusion

Four paragraphs (from 03_writing.md patterns):
1. **Restate the problem and nugget** — what was the key insight?
2. **Summarize results** — what did we prove? (not re-listing numbers, but interpreting them)
3. **Limitations** — honest, specific, 2-3 items. This builds reviewer trust.
4. **Future work** — what does this enable? (Not "we will do X" — "this opens the door to X")

Tokekar's 5 Qs self-check (from 03_writing.md Ch4):
- Q1: Before this paper, what did the community know?
- Q2: After this paper, what did the community learn?
- Q3: What exactly did you do?
- Q4: Why should the community care?
- Q5: What does the community still not know? ← **Must be non-empty**

## Phase 9: Ernst 4-Round Revision

From 03_writing.md Ch6 (Ernst + Peng Sida):

**Round 1 — Section level**: Does each section serve the main thesis? No → delete or restructure.

**Round 2 — Paragraph level**: Does each paragraph have a single message? First sentence = topic sentence? Peng audit: extract all first sentences, read as one paragraph — does it tell the paper's story?

**Round 3 — Sentence level**: Williams character-as-subject test. Pinker curse-of-knowledge check. Zinsser clutter removal (删 85% 的 Thus/Hence/Moreover).

**Round 4 — Word level**: LARG 30+ micro-rules (03_writing.md Ch6.3). Academic-Writing-Check linter. TTS read-aloud for rhythm.

Each round produces a new Git commit. Semantic commits only: one commit = one type of change (never mix content + formatting).

## Phase 10: Submission Checklist

From 03_writing.md Appendix A:

### T-4 weeks
- [ ] LARG pre-writing form completed, sent to advisor
- [ ] Nugget written (中文 + English, one sentence each)
- [ ] Black 12 Qs answered
- [ ] Empty tables/figures in place
- [ ] LaTeX template downloaded, all section headers in place
- [ ] Git repo initialized, CI green

### T-2 weeks
- [ ] First draft complete, at least one labmate has read it
- [ ] Figure 1 (teaser) complete, passes 5-second test
- [ ] Abstract iterated ≥ 2 rounds
- [ ] Widom 5-paragraph Intro complete
- [ ] Peng topic-sentence audit passed
- [ ] Every contribution refutable + has forward reference

### T-1 week
- [ ] Ernst 4-round revision ≥ 3 rounds
- [ ] Related Work is thematic, not laundry list
- [ ] All figures generated by scripts (LaTeX comments contain the generation command)
- [ ] Grammarly / Academic-Writing-Check pass
- [ ] Advisor second draft feedback incorporated
- [ ] Rebuttal-ready backup ablations prepared

### T-1 day
- [ ] Anonymization checked (authors, git clone URLs, acknowledgments)
- [ ] Page limit respected (fill the pages — Black: *"Fill the 8 pages."*)
- [ ] PDF metadata does not leak authors
- [ ] `lacheck` + `chktex` clean
- [ ] Read abstract + Section 1 + Conclusion aloud

## Output

```
paper/
├── main.tex              ← Full paper source
├── references.bib         ← Central bibliography
├── figures/               ← All figures (vector PDF preferred)
│   ├── teaser.pdf
│   ├── method_overview.pdf
│   ├── main_table.pdf
│   └── ...
├── tables/                ← LaTeX table files (auto-generated from experiments)
├── data/                  ← Intermediate data files for plots
├── Makefile               ← latexmk automation
├── .gitignore
└── README.md              ← Build instructions + venue info
```

## Integration with Other Skills

```
research-refine → experiment-plan → paper-write (YOU ARE HERE)
                                       │
                                       ├─ paper-intro-writing (Phase 4)
                                       ├─ paper-related (Phase 7)
                                       └─ → auto-review-loop / paper-talk-deck
```

After paper-write completes, the natural next step is either:
- **paper-talk-deck**: turn the paper into a presentation
- **auto-review-loop** (ARIS): adversarial review + paper improvement
- **Rebuttal** (future skill): concede-clarify-commit structure

## Edge Cases

- **No FINAL_PROPOSAL.md**: derive method from user explanation; skip Phase 5 auto-generation
- **No EXPERIMENT_PLAN.md**: derive experiments from user-provided results; Phase 6 becomes manual
- **Venue-specific formatting**: adjust Phase 0 based on `--venue`
- **Co-author collaboration**: Git-based; semantic line breaks make diff reviewable
- **ESL / Chinese-native author**: run Chinglish pitfall checks from paper-intro-writing references
