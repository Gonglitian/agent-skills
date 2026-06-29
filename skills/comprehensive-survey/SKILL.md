---
name: comprehensive-survey
description: >
  Full-spectrum research survey pipeline: given a topic (or multiple related topics), uses
  litian-academic-search (7 sources: OmniBox, arXiv, Semantic Scholar, OpenAlex, DeepXiv,
  WebSearch, WebFetch) for academic paper discovery, plus social media gathering via WebSearch
  site: filters, then produces structured survey reports with paper citations, social media
  insights, and concept glossary documents with pseudocode. Use PROACTIVELY whenever the user
  wants a comprehensive literature survey, topic investigation, "全面调研", "综合调研",
  "survey this topic", "调研一下", "research survey", "帮我全面了解一下这个方向",
  "从论文到社交平台全面搜", or wants multi-source coverage combining academic papers AND
  social media discussions on any research topic. Also trigger when user provides a directory
  path and expects organized multi-file research output.
---

# Comprehensive Research Survey Pipeline

Orchestrate a full-spectrum research investigation combining **academic paper search** (via `/litian-academic-search` — 7 parallel sources) and **social media gathering** (5 platforms via WebSearch `site:` filters) into structured, cross-referenced survey reports with concept glossary and pseudocode.

---

## Step 1: Understand the Survey Scope

Gather from the user (ask if not provided):

1. **Topic(s)** — One or multiple related research directions. If multiple, each gets its own sub-report.
2. **Output directory** — Where to write all files. Create if needed.
3. **Depth level** — "quick" (~20 papers total), "standard" (~50 papers), or "deep" (~100+ papers). Default: standard.
4. **Language** — Report language. Default: 中文 with English paper titles.
5. **Focus angles** — Any specific aspects to emphasize (e.g., "focus on robotics applications").
6. **Concept docs** — Whether to generate concept glossary with pseudocode. Default: yes.

---

## Step 2: Create Directory Structure

```bash
mkdir -p <output_dir>/{<topic-1>,<topic-2>,...,concepts}
```

Each topic directory receives:
```
<topic-dir>/
├── FINAL_REPORT.md      ← Main deliverable
├── survey_academic.md    ← Academic paper search results
└── survey_social.md      ← Social media discussion results
```

Top-level:
```
<output_dir>/
├── README.md                  ← Navigation index
├── paper_list_comprehensive.md ← Deduplicated master paper list
└── concepts/                   ← Concept glossary with pseudocode
```

---

## Step 3: Academic Paper Search (via litian-academic-search)

Launch **one search per topic** using the canonical multi-source entry point. For N topics, fire N calls in parallel:

```
/litian-academic-search "<TOPIC>" --sources all --k <K>
```

K values by depth: quick=8, standard=15, deep=25.

For each topic, also run focused sub-queries for key aspects (parallel with the main search):
```
/litian-academic-search "<topic> survey review" --sources arxiv,s2,web --k 5
/litian-academic-search "<topic> benchmark comparison" --sources web,s2 --k 5
```

The skill handles de-duplication, ranking, and synthesis automatically.

**After search completes, ingest each paper into OmniBox:**

For every top-k paper found, call `paper-read` in light mode for fast ingestion:
```
paper-read <arxiv_id> --topic <detected_topic> --light
```

This is the global contract: ALL papers discovered through the research pipeline get ingested into OmniBox.

**Output**: For each topic, write `survey_academic.md` containing:
- Structured sections by method/approach (from litian-academic-search synthesis)
- Every paper: title, authors, year, venue, arXiv link, core contribution
- Comparison tables where appropriate
- OmniBox report paths (for papers already in local KB)

---

## Step 4: Social Platform Search

For each topic, gather social media discussions. Use WebSearch with site: filters:

```
WebSearch: "<中文关键词> site:bilibili.com"
WebSearch: "<topic> 知乎 site:zhihu.com"
WebSearch: "<english topic> site:x.com 2024 2025"
WebSearch: "<english topic> site:reddit.com discussion"
WebSearch: "<topic> blog deep dive 2024 2025"
```

**Output**: For each topic, write `survey_social.md` with:
- Platform-organized sections (知乎/B站/Twitter/Reddit/博客)
- Each entry: source, link, key points summary
- Community consensus and disagreements section

---

## Step 5: Comprehensive Paper List

Build a deduplicated master paper list across all topics. Read all `survey_academic.md` files, merge, and de-duplicate.

**Output**: `<output_dir>/paper_list_comprehensive.md`
- Tables organized by topic, then by year
- Include arXiv links for all papers

---

## Step 6: Extract Core Concepts

Analyze all survey files for high-frequency technical terms. Select top 10-15 concepts that:
- Appear frequently across multiple papers
- Are technical enough to warrant explanation
- Would benefit from pseudocode illustration

---

## Step 7: Generate Concept Documents

For each concept, write `<output_dir>/concepts/<concept_name>.md`:

```markdown
# [Concept Name]

## One-line Definition

## Intuitive Explanation

## Mathematical Formulation

## Pseudocode Implementation
```python
class ConceptName(nn.Module):
    ...
```

## Representative Papers
(2-3 papers with arXiv links)
```

---

## Step 8: Compile Final Reports

For each topic, integrate all materials into `FINAL_REPORT.md`:

```markdown
# <Topic> 综述报告

> 生成日期: <date> | 论文覆盖: X篇 | 信息源: 7 academic sources + 5 social platforms

## 摘要 (300 words)

## 1. 引言与定义

## 2. 发展时间线

## 3. 技术分类体系

## 4. 关键论文详解 (Top 15-20)

## 5. 社区观点与产业动态 (from survey_social.md)

## 6. 核心概念索引 (links to ../concepts/*.md)

## 7. 开放问题与未来方向

## 8. 完整论文列表
```

Requirements:
- Every paper MUST have an arXiv or publication link
- At least 50 unique papers per report (standard depth)
- Chinese text, English paper titles
- 800+ lines

---

## Step 9: Generate README Index

Write `<output_dir>/README.md` with:
- Directory structure tree
- Quick navigation table
- Concept glossary table
- Statistics summary

---

## Step 10: Final Verification

```bash
find <output_dir> -name "*.md" -exec sh -c 'echo "$(wc -l < "$1") lines: $1"' _ {} \; | sort -rn
for topic in <topics>; do
  [ -f "<output_dir>/$topic/FINAL_REPORT.md" ] && echo "✓ $topic" || echo "✗ MISSING: $topic"
done
```

---

## Depth Presets

| Preset | Papers/topic | Concepts | litian-academic-search --k | Social platforms | Report lines |
|--------|-------------|----------|---------------------------|-----------------|-------------|
| quick | ~15 | 5 | 8 | Skip or 1-2 WebSearch | 500+ |
| standard | ~30-50 | 10-15 | 15 | All 5 via WebSearch | 800+ |
| deep | ~50-100 | 15-20 | 25 | All 5 + deep dive | 1000+ |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| litian-academic-search returns few results | Try broader query; add `--sources all` |
| OmniBox unavailable | litian-academic-search skips it gracefully |
| Semantic Scholar 429 | litian-academic-search handles retry internally |
| WebFetch 403 on Zhihu | Use search snippets only |
