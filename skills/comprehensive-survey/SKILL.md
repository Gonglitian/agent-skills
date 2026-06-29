---
name: comprehensive-survey
description: Automated full-spectrum research survey. Uses litian-academic-search (7-source) for academic papers + WebSearch site: filters for social media. Ingests all found papers via paper-read --light. Produces structured FINAL_REPORT.md per topic + concept glossary with pseudocode. Use when user wants "全面调研", "综合调研", "survey this topic", "调研一下", "帮我全面了解一下这个方向".
---

# Comprehensive Survey Pipeline

Automated multi-source survey: academic papers via litian-academic-search + social media via WebSearch + auto-ingestion into OmniBox.

## Pipeline

```
Topic(s) → litian-academic-search (all sources) + social WebSearch
  │
  ├─ P1: Academic search per topic
  ├─ P2: Social platform search (WebSearch site: filters)
  ├─ P3: Ingest all found papers → paper-read --light
  ├─ P4: Comprehensive paper list (dedup, sort, link)
  ├─ P5: Concept extraction + glossary with pseudocode
  ├─ P6: Compile FINAL_REPORT.md per topic
  └─ P7: README + verification
```

## Parameters

Parse from `$ARGUMENTS`:
- **Topic(s)**: one or more research directions
- `--depth <quick|standard|deep>` — papers per topic: quick=15, standard=30, deep=50. Default: standard.
- `--output <dir>` — output directory

## Phases

### P1: Academic Search

For each topic:
```
/litian-academic-search "<TOPIC>" --sources all --k <K>
/litian-academic-search "<topic> survey review" --sources arxiv,s2,web --k 5
```

K = depth: quick=8, standard=15, deep=25.

### P2: Social Search

```bash
WebSearch "<中文关键词> site:bilibili.com"
WebSearch "<topic> site:zhihu.com"
WebSearch "<english topic> site:x.com"
WebSearch "<topic> site:reddit.com"
WebSearch "<topic> blog deep dive"
```

### P3: OmniBox Ingestion

For every top-k paper found: `paper-read <arxiv_id> --topic <detected> --light`

### P4: Comprehensive Paper List

Deduplicate across all topics + sources. Write `paper_list_comprehensive.md`.

### P5-P7: Concept Extraction + Reports + README

Standard structure. See `references/output-spec.md` for exact formats.

## Depth Presets

| Preset | Papers/topic | litian-academic-search --k | Social | Report |
|--------|-------------|---------------------------|--------|--------|
| quick | ~15 | 8 | Skip or 1-2 | 500+ lines |
| standard | ~30 | 15 | All 5 platforms | 800+ lines |
| deep | ~50 | 25 | All 5 + deep dive | 1000+ lines |

## Calls

- litian-academic-search (P1)
- paper-read --light (P3)

## Called by

manual invocation, survey-to-deck (as step ① of the pipeline)
