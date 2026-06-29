---
name: paper-discovery-sources
description: "Shared reference for all paper search skills. Points to litian-academic-search as the canonical multi-source search entry point (7 sources: OmniBox, arXiv, Semantic Scholar, OpenAlex, DeepXiv, WebSearch, WebFetch). This skill is NOT user-invokable — it is a reference loaded by other skills (comprehensive-survey, gap-to-method, paper_related_works, idea_refinery, topic_survey, survey-to-deck, paper-talk-deck)."
---

# Unified Paper Discovery Sources

**All paper search skills now delegate to `/litian-academic-search`** as the single canonical multi-source search entry point. This file documents the contract and provides source reference for skills that need to understand what's available.

## Canonical Search Entry Point

```
/litian-academic-search "QUERY" --sources <list> --k <N> [--year YYYY-] [--topic <tag>] [--deep]
```

This replaces all individual curl/API calls previously documented here. The skill queries 7 sources in parallel, de-duplicates by arXiv ID → DOI → title, and returns a structured report.

## Available Sources (for --sources parameter)

| Source | What | Key |
|--------|------|-----|
| `omnibox` | Local vec-db: 3136 CS papers, full-report chunks (bge-m3) | conda env `ml`, SiliconFlow key |
| `arxiv` | 2.5M+ CS preprints, daily updates | Public API, no key |
| `s2` | Semantic Scholar: 200M+ published papers, citation graph | Key at `~/.semantic_scholar_key` |
| `openalex` | 250M+ cross-discipline, institutions, funding | Public API, no key |
| `deepxiv` | 200M+ papers, progressive reading (brief → section → full) | conda env `ocr` |
| `web` | WebSearch: whole web, arXiv, Google Scholar, blogs, social | Built-in Claude Code tool |
| `all` | All of the above | — |

Full source profiles: `skills/litian-academic-search/references/sources.md`.

## Strategy by Goal (delegated to litian-academic-search)

### Goal A: "Survey a topic"

```
/litian-academic-search "TOPIC" --sources all --k 10
```

### Goal B: "Find gaps / propose method"

```
/litian-academic-search "DIMENSION_QUERY" --sources omnibox,s2,arxiv --k 5 --year 2023-
```

### Goal C: "Map related works of a paper"

```
/litian-academic-search "PAPER_KEY_CONCEPT" --sources omnibox,s2,web --k 10
```

### Goal D: "Refine a research idea"

```
/litian-academic-search "IDEA_CONCEPT" --sources omnibox,s2,arxiv -k 8 --year 2024-
```

## Additional: Citation Graph (Semantic Scholar direct)

For citation-chain operations (successors/predecessors of a specific paper), litian-academic-search doesn't cover this yet. Use S2 API directly:

```bash
S2_KEY=$(cat ~/.semantic_scholar_key)
# Successors (who cited this paper)
curl -s "https://api.semanticscholar.org/graph/v1/paper/ArXiv:<ID>?fields=title,year,citationCount,citations.title,citations.year,citations.externalIds,citations.citationCount" -H "x-api-key: $S2_KEY"
# Predecessors (papers this paper cited)
curl -s "https://api.semanticscholar.org/graph/v1/paper/ArXiv:<ID>?fields=title,year,references.title,references.year,references.externalIds,references.citationCount" -H "x-api-key: $S2_KEY"
```

## Additional: Full-text reading

For reading a specific paper beyond what litian-academic-search returns:

```bash
# DeepXiv progressive reading
conda run -n ocr deepxiv paper ARXIV_ID --preview

# arXiv PDF
wget -q "https://arxiv.org/pdf/ARXIV_ID" -O "ARXIV_ID.pdf"

# AlphaXiv (may 403 without auth)
curl -sL -A "Mozilla/5.0" "https://www.alphaxiv.org/overview/ARXIV_ID.md"
```
