---
name: review-ral
description: >
  IEEE RA-L 论文审稿助手。输入一篇待审稿 PDF，自动完成：初读论文提取关键信息 → 多源文献检索
  (Semantic Scholar + WebSearch/arXiv + vec-db) → 并行 agent 深读相关论文 → 带着领域知识精读
  待审稿论文 → 输出完整的 RA-L 审稿意见（含评分、推荐、双语评审意见）。审稿风格追求独到犀利，
  不千篇一律。Use PROACTIVELY whenever the user asks to review a paper for RA-L, IEEE Robotics
  and Automation Letters, or says "审稿", "review this paper", "帮我审稿", "写review",
  "RA-L review", "审一下这篇", "peer review", or provides a PDF and mentions reviewing.
  Also trigger when user mentions PaperCept, reviewer form, or review deadline.
---

# IEEE RA-L Paper Review Skill

Generate expert-level, incisive peer reviews for IEEE Robotics and Automation Letters submissions.

The core philosophy: **a great review comes from deep domain knowledge, not templates**. First
understand the field landscape through targeted literature search, then critique the paper from
a position of genuine expertise. This produces reviews with unique insights that authors actually
find useful — not generic checklists that could apply to any paper.

---

## Overview of the Pipeline

```
Phase 1: Initial Read     → Extract paper's claims, methods, key results, field keywords
Phase 2: Literature Search → Multi-source search for related work (3 sources, parallel)
Phase 3: Deep Read Related → Download top papers, parallel agents read them
Phase 4: Expert Re-read   → Re-read target paper armed with domain knowledge
Phase 5: Generate Review  → Bilingual review output matching RA-L form exactly
```

Total expected time: 5-10 minutes depending on search depth.

---

## Phase 1: Initial Paper Read

Read the submitted PDF to build a first-pass understanding.

### 1.1 Read the PDF

Use the `Read` tool to read the PDF file. If it's long, read in sections. Extract:

1. **Title & Abstract** — verbatim
2. **Claimed contributions** — list each claim the authors make (usually in intro or contributions section)
3. **Method summary** — what they actually did, in 3-5 sentences
4. **Key results** — main quantitative results, benchmarks used, metrics reported
5. **Datasets** — which datasets, train/test splits, evaluation protocols
6. **Baselines compared** — which methods they compare against, and how recent those baselines are
7. **Field keywords** — 8-12 specific terms for literature search (method names, problem names, dataset names, technique names)

### 1.2 Identify Search Targets

Based on the initial read, formulate:

- **3-4 core search queries** — the paper's main topic and close variants
- **2-3 method-specific queries** — the specific technique family (e.g., "iterative refinement stereo matching", "cost volume stereo")
- **1-2 application queries** — the downstream application if relevant
- **Competing method names** — specific method names mentioned as baselines, to find their papers and successors

---

## Phase 2: Literature Search (Parallel)

Launch **all search sources in parallel** in a single message. The goal is to find 20-30 candidate
papers, from which we'll select 8-12 for deep reading.

### 2.1 Search Sources

**Source A: Semantic Scholar API**

```bash
# High-citation classics
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=<URL_ENCODED_QUERY>&limit=20&fields=title,year,authors,citationCount,externalIds,abstract&sort=citationCount:desc"

# Recent papers (2023-2026)
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=<URL_ENCODED_QUERY>&limit=20&fields=title,year,authors,citationCount,externalIds,abstract&year=2023-2026"

# Citation graph: find papers that cite the key baselines
curl -s "https://api.semanticscholar.org/graph/v1/paper/ArXiv:<ID>?fields=citations.title,citations.year,citations.citationCount,citations.externalIds"
```

Rate limit: 5000 req/5min. Space bulk queries by 0.5s. If 429, wait 3s and retry once.

Run 3-5 query variants covering the core topic + method family + competing approaches.

**Source B: WebSearch (arXiv focus)**

Run 6-8 targeted web searches:
- `"<topic> arXiv 2024 2025"` — recent preprints
- `"<method name> survey"` — find survey papers
- `"<baseline method> improved OR better OR outperform 2024 2025"` — find papers that beat the baselines
- `"<dataset name> state-of-the-art SOTA 2024 2025"` — current SOTA on the benchmarks
- Include top venue filters: CVPR, ICCV, ECCV, NeurIPS, ICML, ICLR, IROS, ICRA, CoRL, RA-L, T-RO

**Source C: Vec-db Semantic Search (if available)**

```bash
cd ${VECDB_PATH:-/home/vla-reasoning/proj/litian-research/vec-db}
npx tsx src/cli.ts search "<query>" --top 15
```

Run 4-6 diverse queries. Score >0.25 = relevant, >0.35 = highly relevant.
If vec-db is not available, skip gracefully and rely on Sources A and B.

### 2.2 Paper Selection

From all search results, select **8-12 papers** for deep reading, prioritizing:

1. **Direct competitors** — papers solving the exact same problem with different methods (highest priority)
2. **Very recent work** (2024-2026) — papers the authors may have missed
3. **Foundational/highly cited** — seminal papers the submission should cite
4. **Same-benchmark SOTA** — papers reporting results on the same datasets
5. **Method-family papers** — papers using similar techniques in different domains

For each selected paper, record: title, authors, year, venue, arXiv ID (if available), why it's relevant.

---

## Phase 3: Deep Read Related Papers (Parallel Agents)

This is the key step that separates shallow reviews from expert ones. Spawn **parallel agents**
to read 8-12 related papers simultaneously.

### 3.1 Access Paper Full Text

For each selected paper, try in order:
1. **AlphaXiv** (preferred — structured markdown): `https://alphaxiv.org/abs/<ARXIV_ID>.md`
2. **Direct PDF download**: `wget https://arxiv.org/pdf/<ARXIV_ID> -O /tmp/papers/<ARXIV_ID>.pdf`
3. **WebFetch on paper page**: if no arXiv ID, try fetching the paper's URL

Create a working directory for downloaded papers:
```bash
mkdir -p /tmp/ral-review-papers/
```

### 3.2 Spawn Parallel Reading Agents

Launch all reading agents in **ONE message**. Each agent reads one paper and extracts:

**Agent prompt template:**
```
Read this paper and extract a structured summary for peer review comparison purposes.

Paper: <title>
Source: <alphaxiv URL or PDF path>

Extract:
1. **Core contribution**: What is the main idea? (2-3 sentences)
2. **Method details**: Key technical approach, architecture, loss functions
3. **Results on shared benchmarks**: Performance numbers on <list relevant benchmarks from target paper>
4. **Strengths**: What does this paper do well?
5. **Limitations**: What are the known weaknesses?
6. **Comparison points**: How does this relate to <target paper title>? What does it do differently?
7. **Key numbers**: Report specific metrics (e.g., EPE, D1-error, FPS, parameters, FLOPs)

Write the summary to: /tmp/ral-review-papers/summary_<paper_id>.md
```

### 3.3 Synthesize Domain Knowledge

After all agents complete, read all summaries and build a **field landscape**:

- Current SOTA on each benchmark the target paper uses
- Common techniques and their trade-offs
- Open problems and active research directions
- What's actually novel vs. what's incremental vs. what's already known
- Missing references the target paper should cite

Write this synthesis to `/tmp/ral-review-papers/field_landscape.md`.

---

## Phase 4: Expert Re-read

Now re-read the target paper with deep domain knowledge. This time, read critically:

### 4.1 Novelty Assessment

- Which claimed contributions are genuinely new vs. already explored in related work?
- Is the combination of known techniques actually novel, or just engineering?
- Does the paper clearly distinguish its contribution from prior work?

### 4.2 Technical Scrutiny

Apply the critical lens from `references/review-philosophy.md`. Key angles:

- **Hidden assumptions**: What assumptions does the method rely on that aren't stated?
- **Experimental fairness**: Are baselines compared under identical conditions? Same hardware, same training data, same evaluation protocol?
- **Cherry-picking**: Do they only report metrics where they win? Missing metrics that would show weaknesses?
- **Ablation rigor**: Does the ablation study truly isolate each contribution? Or are components entangled?
- **Statistical significance**: Are improvements within noise range? Do they report variance/std?
- **Scalability**: Do claims generalize beyond the specific benchmarks tested?
- **Computational cost**: Is the speed/accuracy trade-off actually favorable when properly measured?
- **Reproducibility**: Are enough details provided to reproduce? Missing hyperparameters, training details?

### 4.3 Presentation Quality

- Is the writing clear and self-contained?
- Are figures informative or decorative?
- Is the paper well-structured?
- Are there grammatical issues that impede understanding?

### 4.4 Citation Completeness

Compare the paper's references against the field landscape:
- Missing important baselines or comparisons?
- Missing foundational work?
- Missing very recent relevant work (which is understandable but worth noting)?
- Self-citation bias?

---

## Phase 5: Generate Review Output

Produce the final review following the exact RA-L form structure. Output **two files**:

### 5.1 English Review (for submission)

Write to `<output_dir>/review_en.md` — this is what gets pasted into PaperCept.

Use the **exact template** from `references/review-template.md`.

### 5.2 Chinese Analysis Notes (for reviewer's reference)

Write to `<output_dir>/review_cn.md` — the reviewer's personal analysis notes.

This includes:
- 中文审稿思路分析
- 每个评分的详细理由
- 相关论文对比表格
- 论文的核心优缺点
- 对领域的价值判断

### 5.3 Review Quality Checklist

Before finalizing, verify:

- [ ] Every criticism is specific — points to exact section/figure/table/equation
- [ ] Every claim of "missing reference" includes the actual reference
- [ ] No generic phrases like "the paper is well-written" without specific evidence
- [ ] Technical issues are explained clearly enough for authors to understand and fix
- [ ] The review tone is professional and constructive, even when critical
- [ ] Comments to Author do NOT reveal the recommendation
- [ ] No identifying information about the reviewer
- [ ] Comments to Author ≤ 10000 characters
- [ ] Confidential Comments ≤ 2000 characters
- [ ] All 7 assessment scores are filled with justification

---

## Assessment Scoring Guide

These are the exact options from the RA-L PaperCept form:

### Paper contribution
- **Exceptional** — groundbreaking new direction or major theoretical/practical advance
- **Major** — significant contribution that clearly advances the field
- **Minor** — incremental improvement or limited novelty
- **Questionable** — unclear contribution or already known results
- **None** — no discernible contribution

### Technical quality / Originality / Thoroughness of results / Clarity of presentation / Adequacy of citation / Relevance to field
Each uses: **Excellent** / **Good** / **Fair** / **Poor**

### Overall Recommendation
- **Accept** — solid work, ready for publication with at most minor edits
- **Revise and resubmit** — has merit but needs significant improvements
- **Reject** — fundamental issues that cannot be fixed in revision
- **Unsuitable due to scope** — doesn't fit RA-L's scope

### Reviewer Confidence
- **Very confident** — deep expertise in this exact sub-area
- **Confident** — solid knowledge of the broader field
- **Fairly confident** — familiar with the area but not an expert
- **Not very confident** — limited knowledge of this specific topic
- **No confidence** — outside area of expertise

### Other Fields
- **Multimedia attachment**: Yes / No (and brief justification)
- **Best paper award finalist**: Yes / No
- **Wish to see revision**: checkbox (recommend checking if "Revise and resubmit")

---

## Writing Style for Reviews

Read `references/review-philosophy.md` for the full guide. Key principles:

1. **Be specific, never generic.** Instead of "the experiments are insufficient", say "Table 2 is missing comparison with RAFT-Stereo [ref] on KITTI 2015, which currently holds SOTA on the leaderboard."

2. **Provide evidence for every claim.** If you say the method is not novel, cite the specific prior work that already did it.

3. **Distinguish fatal flaws from fixable issues.** Major issues that affect the core claims should be clearly separated from minor presentation issues.

4. **Be constructive even when rejecting.** Tell the authors exactly what they'd need to do to make the paper publishable.

5. **Find what's genuinely good.** Even weak papers usually have some redeeming quality. Acknowledge it — this makes your criticism more credible.

6. **Question the things others wouldn't.** Go beyond surface-level checking. Ask: "Why this architecture choice and not the obvious alternative?" "What happens at the failure cases?" "Is the improvement consistent across all scenes or driven by a few easy cases?"

---

## Output Directory Structure

```
<output_dir>/
├── review_en.md              ← English review for PaperCept submission
├── review_cn.md              ← 中文审稿分析笔记
├── field_landscape.md        ← Domain knowledge synthesis
└── related_papers/           ← Summaries of related papers read
    ├── summary_<paper1>.md
    ├── summary_<paper2>.md
    └── ...
```

Default output directory: same directory as the input PDF, in a `review_output/` subdirectory.

---

## Quick Reference: The Pipeline in Practice

When the user gives you a PDF to review:

1. **Ask** (if not provided): output directory preference, any specific concerns they want addressed
2. **Read the PDF** — build initial understanding (Phase 1)
3. **Search in parallel** — launch Semantic Scholar + WebSearch + vec-db agents simultaneously (Phase 2)
4. **Select papers** — pick 8-12 most relevant from search results (Phase 2.2)
5. **Download & parallel read** — spawn one agent per paper, all in one message (Phase 3)
6. **Synthesize** — build field landscape from all paper summaries (Phase 3.3)
7. **Expert re-read** — critically re-read the target paper with domain knowledge (Phase 4)
8. **Generate review** — produce bilingual output following the exact RA-L form (Phase 5)
9. **Present to user** — show the review and ask if they want adjustments

The whole process should feel like handing the paper to a senior researcher who happens to have
perfect recall of the recent literature and returns with a thoughtful, sharp review.
