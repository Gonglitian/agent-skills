# Paper Writing Reference Guide

Extracted from `~/proj/research-kb/research-guidance/03_writing.md` (820 lines, 9 chapters).
Read the relevant sections when executing paper-write phases.

## Key Techniques by Phase

### Before Writing: Philosophy (Ch1-2)
- **Write the paper first** (Eisner): LaTeX skeleton BEFORE experiments. Empty tables with headers.
- **Nugget / single ping** (SPJ/Black): one idea, one sentence. Test: can you state it in 中文 + English?
- **Refutable contributions** (SPJ): must be falsifiable. "Method M reduces X by Y% on benchmark Z."
- **Black 12 Qs**: written answers to 12 pre-writing questions before starting.

### Page One (Ch3)
- **Page one 10× weight** (SPJ/Black): reviewer decides on first page.
- **Widom 5-paragraph Intro**: problem → importance → difficulty → insight → contributions.
- **Related work goes AFTER Introduction** (SPJ): "like a sandbar between reader and key idea."

### Story (Ch4)
- **Goal–Problem–Solution recursion** (Black): applies at paper/section/subsection/paragraph level.
- **Mad-Libs abstract** (Black): *Unfortunately / In contrast / While promising / Therefore*.
- **Running example first** (SPJ/Ernst/Black): explain with text + figure + equation.
- **Tokekar 5 Qs**: Q2(community learned) ≠ Q3(you did); Q5(still unknown) must be non-empty.

### Daily Writing (Ch5)
- **15 minutes/day minimum** (Bolker): dated thesis journal.
- **Uneven U paragraph** (Hayot): abstract → evidence → rise (not to original height).

### Style Craft (Ch6)
- **Ernst 4-round revision**: section → paragraph → sentence → word.
- **Williams characters-as-subjects**: subjects are actors, verbs are actions.
- **Zinsser clutter removal**: delete 85% of Thus/Hence/Moreover.
- **Pinker curse of knowledge**: you think readers know what you know. They don't.
- **Peng 段落纪律**: one message per paragraph; first sentence = topic sentence.
- **LARG 30+ micro-rules**: "we believe" → "we hypothesize", "showing" → "evaluating".

### Figures (Ch7)
- **Teaser = 5-second explainer** (Black): not architecture diagram.
- **Vector > bitmap** (Spinellis/Wookai): PDF from Inkscape/TikZ/matplotlib.
- **One script per figure** (Wookai): data changes → one command → updated figure.
- **MLNLP 9 TikZ templates**: copy-paste starting points.

### LaTeX (Ch8)
- **Semantic line breaks** (Spinellis/Wookai): one sentence per line.
- **20 micro-rules**: `~` before `\cite`, `booktabs` no vertical lines, `\emph` not `\textit`.
- **Git for papers**: annotated tags per submission, CI `latexmk` on push.
- **latexmk + Makefile + bibtool**: reproducible builds.

### Rebuttal (Ch9)
- **Concede–Clarify–Commit**: admit gap → correct misunderstanding → commit fix with data.
- **Table R1** (Peng): one consolidated table, all reviewer blocks point to it.
- **1-week playbook**: Day 1 identify score-moving ablation, Day 6 Table R1, Day 7 write.

### ESL / Chinese PhD (Coda)
- **"读 Western for why, 读 Chinese for how"**: templates over abstract principles.
- **Common Chinglish**: article omission, comma splices, Thus/Hence overuse, passive voice pile-up, citation as subject.
- **Tools**: Grammarly + LanguageTool + Academic-Writing-Check.

## Submission Checklist (Appendix A)

### T-4 weeks: [ ] LARG pre-writing form → advisor, [ ] nugget 中+英, [ ] Black 12 Qs, [ ] empty tables, [ ] LaTeX skeleton, [ ] Git init + CI green
### T-2 weeks: [ ] first draft + labmate read, [ ] teaser 5-sec test, [ ] abstract ≥2 rounds, [ ] Widom 5-para Intro, [ ] topic-sentence audit, [ ] refutable contributions
### T-1 week: [ ] Ernst revision ≥3 rounds, [ ] Related Work thematic, [ ] figures scripted, [ ] Grammarly pass, [ ] advisor 2nd draft
### T-1 day: [ ] anonymization, [ ] page limit, [ ] fill the pages (Black: "Fill the 8 pages"), [ ] lacheck+chktex clean, [ ] read abstract+S1+conclusion aloud
