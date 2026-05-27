---
name: paper_related_works
description: Given a paper, find its related works (cited references and successor/citing papers) and produce a structured map.
---

# paper_related_works

Given an academic paper, build a comprehensive related-works map covering both **predecessors** (papers it cites) and **successors** (papers that cite it or build on it).

## When to Use

- User provides a paper (arXiv link, PDF, paper ID, or title)
- User wants to understand what a paper builds on
- User wants to find follow-up work or improvements
- User wants to trace a line of research

## Workflow

### Step 1: Identify the Paper

> **检索命令语法的唯一来源**：AlphaXiv 读取、Semantic Scholar citations/references API、vec-db 检索的精确命令、限流与去重规则，统一定义在 `../paper-discovery-sources/SKILL.md`（见其中 Goal C 检索策略）。需要命令细节时加载它；下面只写本 skill 特有的策略。

Parse the paper from user input (arXiv URL, ID, title, PDF path), then read it via AlphaXiv (overview first, full text if references are thin, PDF fallback on 404) — see the reference doc for the exact commands.

Extract the full paper content for the walkthrough and related works analysis.

### Step 2: Paper Walkthrough

Write a structured walkthrough of the paper. This goes at the top of the final report.

#### 2a. Background & Problem

- What problem does the paper address?
- Why is it important? (real-world motivation, limitations of prior work)
- What gap in existing methods does it target?

#### 2b. Motivation & Key Insight

- What is the core insight or observation that drives the approach?
- What makes this paper's angle different from prior attempts?
- Any motivating examples or failure cases of existing methods?

#### 2c. Method

- High-level approach (1-2 paragraphs, not full math)
- Architecture diagram or pipeline description
- Key design choices and why they matter
- Core algorithm steps (numbered list or pseudocode if helpful)
- Important hyperparameters or training details

#### 2d. Results Overview

- Main benchmarks and datasets used
- Key quantitative results (table format):

```markdown
| Method | Benchmark | Metric | Value |
|--------|-----------|--------|-------|
| This paper | ... | ... | ... |
| Best baseline | ... | ... | ... |
```

- Most important ablation findings
- Qualitative results or visualizations (describe key figures)

#### 2e. Limitations & Future Work

- Limitations acknowledged by the authors
- Limitations you observe (not mentioned in paper)
- Future directions proposed by the authors
- Open questions that remain

### Step 3: Extract Cited Works (Predecessors)

From the paper's references and related work section, identify papers grouped by role:

| Role | Description | Example |
|------|-------------|---------|
| **Foundation** | Core method this paper builds on | "We build on DP3 [Ze et al.]" |
| **Baseline** | Methods compared against in experiments | "We compare with ACT, DP..." |
| **Component** | Borrowed modules (encoder, loss, etc.) | "We use PTv3 as backbone" |
| **Concurrent** | Independent parallel work on same problem | "Concurrent to ours, X also..." |
| **Problem** | Papers defining the problem or benchmark | "On the RLBench benchmark [James et al.]" |

For each cited paper, extract:
- Title, authors, year
- arXiv ID (if identifiable)
- Role (from table above)
- One-line description of relationship

### Step 4: Find Successor Works

Search for papers that cite or build on the target paper using multiple sources (exact commands in `../paper-discovery-sources/SKILL.md`):

**4a. Semantic Scholar API (primary)** — the citation graph gives both directions in one call:
- **`citations` field → successors** (papers that cite this one): this is the primary signal for Step 4/5.
- **`references` field → predecessors** (papers this one cites): use this in Step 3 to corroborate/augment the references you pulled from the paper text.
- If the paper isn't found by arXiv ID, look it up by title first, then fetch its citation graph.

**4b. Local Vec-db semantic search (find related top-venue work)**

Search vec-db with the paper's key concepts. This finds top-venue papers with similar themes that may not directly cite the target but are closely related. Especially useful for discovering parallel/concurrent work.

**4c. Web search (supplementary)**

```
WebSearch: "<paper_title>" improvements OR "builds on" OR "extends" site:arxiv.org
WebSearch: "<paper_title>" cite OR citing 2024 2025 2026
```

**4d. AlphaXiv (if available)**

Check the AlphaXiv overview for mentions of follow-up or concurrent work.

**4d. Connected Papers / Papers With Code**

```
WebSearch: "<paper_title>" site:paperswithcode.com
WebSearch: "<paper_title>" site:connectedpapers.com
```

### Step 5: Classify & Rank Successors

For each successor found, classify:

| Relationship | Description |
|-------------|-------------|
| **Direct extension** | Explicitly builds on this paper's method |
| **Application** | Applies the method to a new domain/task |
| **Improvement** | Proposes fixes or enhancements |
| **Comparison** | Uses as baseline in experiments |
| **Integration** | Combines with other methods |

Rank by relevance: direct extensions > improvements > applications > comparisons.

### Step 6: Produce the Report

**ASK USER** before generating: "I found N predecessors and M successors. Want me to:
1. Full map (all papers, grouped and annotated)
2. Key papers only (most influential predecessors + direct successors)
3. Focus on a specific branch (e.g., only RL-based successors)?"

Output format:

```markdown
# Paper Walkthrough & Related Works: <Paper Title>

**Paper:** <title> (<authors>, <year>)
**arXiv:** <link>
**Core contribution:** <1 sentence>

---

## 1. Paper Walkthrough

### Background & Problem
<What problem, why it matters, what gap exists>

### Motivation & Key Insight
<Core insight, what's different from prior work>

### Method
<High-level approach, architecture, key design choices>

### Results
| Method | Benchmark | Metric | Value |
|--------|-----------|--------|-------|
| This paper | ... | ... | ... |
| Best baseline | ... | ... | ... |

<Key ablation findings, qualitative highlights>

### Limitations & Future Work
- <Author-stated limitations>
- <Observed limitations>
- <Proposed future directions>

---

## 2. Predecessors (Papers This Work Builds On)

### Foundations
| Paper | Year | Relationship | Code |
|-------|------|-------------|------|
| [Title](https://arxiv.org/abs/...) | ... | ... | [repo](url) |

### Baselines
| Paper | Year | Relationship | Code |
|-------|------|-------------|------|

### Components
| Paper | Year | Relationship | Code |
|-------|------|-------------|------|

### Concurrent Work
| Paper | Year | Relationship | Code |
|-------|------|-------------|------|

## 3. Successors (Papers That Build on This Work)

### Direct Extensions
| Paper | Year | What They Add | Citations | Code |
|-------|------|--------------|-----------|------|
| [Title](https://arxiv.org/abs/...) | ... | ... | ... | [repo](url) |

### Improvements
| Paper | Year | What They Fix/Improve | Citations | Code |
|-------|------|----------------------|-----------|------|

### Applications
| Paper | Year | Domain/Task | Citations | Code |
|-------|------|------------|-----------|------|

## 4. Research Lineage

<ASCII diagram showing the main line of research>

<target_paper>
├── built on: <foundation_1> → <foundation_2> → ...
├── extended by: <successor_1>, <successor_2>
└── applied to: <application_1>

## 5. Suggested Reading Order

1. <paper> — <why read this first>
2. <paper> — <builds on #1>
...
```

### Step 7: Save Report

**Always save the report to a file.** Ask user for preferred location, default:

```bash
mkdir -p doc/related_works
```

Save as `doc/related_works/<paper_short_name>_related.md`.

**Every paper entry MUST include a clickable link.** Use this format for all tables:

```markdown
| [Paper Title](https://arxiv.org/abs/XXXX.XXXXX) | 2025 | Relationship | `XXXX.XXXXX` |
```

If no arXiv ID, use Semantic Scholar link: `https://www.semanticscholar.org/paper/<S2_ID>`

For papers with code, add repo link:

```markdown
| [Paper Title](https://arxiv.org/abs/XXXX.XXXXX) | 2025 | Description | [code](https://github.com/...) |
```

### Step 8: Offer Next Steps

After presenting the map, ask:

- "Want me to deep-dive into any of these papers? (I can create a skill with `/create_skill_with_paper`)"
- "Want me to survey the broader topic? (I can run `/topic_survey`)"
- "Want me to find the code repos for any of these?"

## Tips

- Semantic Scholar API is rate limited (see reference doc); space requests if doing bulk lookups.
- Papers <6 months old may have few/no citations yet. Rely more on web search for recent successors.
- Some papers cite predecessors only in supplementary material — check appendices.
- For very popular papers (>500 citations), filter successors by citation count or recency to keep the map manageable.

## Error Handling

| Issue | Recovery |
|-------|----------|
| AlphaXiv 404 | Fall back to reading PDF directly |
| Semantic Scholar rate limit | Wait 60s and retry, or switch to web search |
| Paper not on arXiv | Search by title on Semantic Scholar, Google Scholar |
| Too many successors | Filter: citations > 10, or last 2 years only |
| No successors found | Paper may be very recent; note this and rely on web search |
