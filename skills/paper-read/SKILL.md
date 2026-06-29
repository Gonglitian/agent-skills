---
name: paper-read
description: Deep-read a single academic paper (arXiv ID / URL / title) and produce structured engineering reports, then DEFAULT auto-ingest into the OmniBox local knowledge base. Combines code-level deep read (arxiv-deepdive pattern: clone repo, read PDF, 01_highlevel + 02_technical with file:line) with VLM figure extraction (read-paper pattern). Use whenever the user wants to read a paper, take notes, "读论文", "paper notes", "深读这篇", "read this paper", or needs a single paper processed. Also called by orchestration skills (comprehensive-survey, topic_survey, survey-to-deck) for each paper found. The default behavior is ALWAYS ingest into OmniBox — this is the global contract: every paper found in the research pipeline gets ingested.
---

# paper-read: Single Paper Deep Read → OmniBox Ingestion

One paper in, structured reports + indexed knowledge out. This is the canonical entry point for reading ANY paper — standalone or called by orchestrators.

## Pipeline

```
arXiv ID / URL / title
  │
  ├─ Step 1: Resolve → arXiv ID
  ├─ Step 2: Check OmniBox (skip if already present, unless --force)
  ├─ Step 3: Deep read (fan-out):
  │   ├── PDF + code repo → 01_highlevel.md + 02_technical.md
  │   └── VLM figure extraction → figures/
  ├─ Step 4: Write to OmniBox path with frontmatter
  ├─ Step 5: update_index.py (incremental)
  └─ Step 6: search.py verify
```

## Parameters

Parse from `$ARGUMENTS`:
- **Paper**: arXiv ID (`2406.09246`), URL (`https://arxiv.org/abs/2406.09246`), or title
- **`--topic <tag>`** — OmniBox topic folder (e.g. `VLA`, `diffusion`, `manipulation`). If omitted, auto-detect from paper content.
- **`--no-ingest`** — skip OmniBox ingestion (rare — default is always ingest)
- **`--no-figures`** — skip VLM figure extraction (faster, ~60% of full time)
- **`--no-repo`** — skip code repo clone (use when no official code or just want text)
- **`--force`** — re-read even if already in OmniBox
- **`--light`** — light mode: no repo, no figures, just high-level report

## Step 1: Resolve Input → arXiv ID

- If arXiv URL: extract ID (e.g. `2406.09246`)
- If arXiv ID: use directly
- If title: search via `/litian-academic-search "<title>" --sources arxiv --k 1`, extract arXiv ID

## Step 2: Check OmniBox

```bash
ls ~/proj/omnibox/papers/*/<ARXIV_ID>_*/01_highlevel.md 2>/dev/null
```

If found and not `--force`:
- Read existing reports
- Skip to Step 5 (re-index) and Step 6 (verify)
- Report: "Already in OmniBox — re-indexed. Use --force to re-read."

## Step 3: Deep Read (parallel fan-out)

### 3a: Code-level engineering reports (from arxiv-deepdive pattern)

**If `--no-repo` is NOT set:**
1. Clone the paper's official repo (find via Papers With Code / GitHub link in arXiv page / WebSearch)
2. Read PDF (first 8 pages: abstract, intro, method, experiments overview)
3. Read key source files from repo (model architecture, training loop, config)

Produce two reports:

**`01_highlevel.md`** — High-level narrative:
```markdown
---
arxiv: "<ID>"
title: "<Title>"
aliases: ["<ShortName>", "<Abbreviation>"]
topic: "<topic>"
year: <YYYY>
tags: ["topic/<t>", "method/<m>", "capability/<c>", ...]
summary: "<1-sentence Chinese summary>"
related: ["<arxiv_id>", ...]
---

# <ShortName> — <1-line core contribution>

## 动机与背景
...

## 核心 Idea
...

## 关键结果
...

## 定位与贡献
...
```

**`02_technical.md`** — Engineering deep dive:
```markdown
# <ShortName> 技术深挖

## 架构细节 (file:line)
...

## 训练超参与策略 (file:line)
...

## 推理流程 (file:line)
...

## 代码级复现要点
...

## 实验设定与消融
...
```

**If `--light`:** only produce `01_highlevel.md`.

### 3b: VLM figure extraction (from read-paper pattern)

If NOT `--no-figures` and NOT `--light`:
- Extract all figures from PDF
- Describe each via VLM (what it shows, key insight)
- Save to `figures/` directory

## Step 4: Write to OmniBox

Determine topic (first match wins):
1. `--topic <tag>` if provided
2. Auto-detect from paper content (check against `~/proj/omnibox/index/canonical.json` topic list)
3. Fallback: `papers/` (ungrouped)

```bash
TOPIC="<detected>"
DIR=~/proj/omnibox/papers/$TOPIC/<ARXIV_ID>_<slug>
mkdir -p "$DIR"
# Write reports with frontmatter
# Copy figures/ if present
```

**Topic detection**: grep paper title/abstract against canonical topic keywords. Use the most relevant existing topic folder. If genuinely new, create a new topic folder.

## Step 5: Ingest into OmniBox Index

```bash
conda run -n ml python ~/proj/omnibox/index/update_index.py
```

This is incremental — only new/changed papers are re-embedded. Takes ~3-10 seconds.

## Step 6: Verify

```bash
conda run -n ml python ~/proj/omnibox/index/search.py "<paper title>" -k 3 --json
```

Confirm the paper appears in results with relevance > 0.5.

## Output

```
✓ paper-read complete: <Title>
  OmniBox: papers/<topic>/<ARXIV_ID>_<slug>/
  ├── 01_highlevel.md   (X KB)
  ├── 02_technical.md   (X KB)
  └── figures/          (N figures, if enabled)
  Index: ✓ verified (relevance: 0.XX)
```

## Default behavior contract

**ALL research pipeline skills that find papers MUST call paper-read on each paper.** This ensures every paper discovered through any path (comprehensive-survey, topic_survey, gap-to-method, manual search) gets ingested into OmniBox. Orchestration skills pass `--topic` to pre-classify, and use `--light` for high-throughput batch ingestion.

The contract:
- `comprehensive-survey` → for each paper found: `paper-read <arxiv_id> --topic <t> --light`
- `topic_survey` → for each paper selected: `paper-read <arxiv_id> --topic <t>`
- `survey-to-deck` → for each paper in deck: `paper-read <arxiv_id> --topic <t>`
- User manually: `paper-read <arxiv_id>` (full mode, all features)

## Edge cases

- **No official repo**: `--no-repo`, note in reports
- **Paper behind paywall**: use arXiv preprint
- **OmniBox conda env broken**: skip ingest with warning, write reports to local dir
- **Topic unknown**: use `papers/` root, flag for later classification
