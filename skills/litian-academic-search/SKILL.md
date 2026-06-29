---
name: litian-academic-search
description: Multi-source academic literature search across 7 data sources (OmniBox local KB, arXiv, Semantic Scholar, OpenAlex, DeepXiv, WebSearch, WebFetch). Use whenever the user asks about research topics, wants literature review, searches for papers, asks "what's the state of X", "find papers about Y", "文献检索", "学术搜索", "找论文", or needs to survey any academic field. De-duplicates and synthesizes results into a structured report. Fan-out by source for speed — all sources queried in parallel.
---

# litian-academic-search

Multi-source academic literature search. Query 7 data sources in parallel, de-duplicate, and synthesize.

## Quick reference

```
/litian-academic-search "embodied ai vla manipulation" --sources all --k 8
/litian-academic-search "diffusion policy" --sources omnibox,arxiv,s2 --k 5
```

## Data sources

| Source | Command | Type | Coverage | Time |
|--------|---------|------|----------|------|
| **OmniBox** | `conda run -n ml python ~/proj/omnibox/index/search.py` | Local vec-db (bge-m3) | 3136 CS papers, full-report chunks | ~3-5s |
| **arXiv** | `curl http://export.arxiv.org/api/query` | Public API | 2.5M+ CS preprints | ~1-3s |
| **Semantic Scholar** | `curl https://api.semanticscholar.org/graph/v1/paper/search` | API (key at `~/.semantic_scholar_key`) | 200M+ published papers | ~1-3s |
| **OpenAlex** | `curl https://api.openalex.org/works?search=` | Public REST API | 250M+ cross-discipline | ~1-2s |
| **DeepXiv** | `conda run -n ocr deepxiv search` | CLI (free token) | 200M+ papers, progressive reading | ~2-4s |
| **WebSearch** | Claude Code built-in | Web search | Whole web | ~2-5s |
| **WebFetch** | Claude Code built-in | Full-text fetch | Any URL | ~2-4s |

Full source profiles: see `references/sources.md`.

## Parameters

Parse from `$ARGUMENTS`:
- **`--sources <list>`** — comma-separated: `omnibox`, `arxiv`, `s2`, `openalex`, `deepxiv`, `web`, `all`. Default: `all`.
- **`--k <N>`** — results per source (default: 8). OmniBox uses `-k`, others `--max/limit`.
- **`--year <YYYY->`** — filter by minimum year (default: none). Applies to arXiv, S2, OpenAlex.
- **`--topic <tag>`** — OmniBox topic filter (e.g. `VLA`, `EmbodiedAI`).
- **`--no-synthesis`** — skip the final synthesis step, just return raw deduped results.
- **`--deep`** — for top-3 results, also fetch full text via WebFetch or DeepXiv `--preview`.

Examples:
```
/litian-academic-search "VLA generalization" --sources omnibox,arxiv,s2,web
/litian-academic-search "diffusion policy" --year 2024- --k 5
/litian-academic-search "3d reconstruction" --sources omnibox --topic AutoFocus3D
```

## Workflow

### Phase 1: Fan-out (parallel)

Dispatch ALL requested sources simultaneously. Each source returns a structured JSON list:

```json
[{"title": "...", "authors": "...", "year": 2025, "venue": "...",
  "arxiv_id": "...", "doi": "...", "citations": 0,
  "abstract": "...", "source": "arxiv", "relevance_score": 0.9}]
```

**OmniBox** (when `omnibox` or `all` in sources):
```bash
conda run -n ml python ~/proj/omnibox/index/search.py "QUERY" -k N [--topic TOPIC] [--only paper] --json 2>/dev/null
```
Returns: `{relevance, arxiv, short, topic, year, tags, summary, hit_section, snippet, hl_path}`. Map to unified schema.

**arXiv** (when `arxiv` or `all` in sources):
```bash
curl -s "http://export.arxiv.org/api/query?search_query=all:QUERY&start=0&max_results=N&sortBy=relevance" 2>/dev/null
```
Parse Atom XML → extract title, authors, arxiv_id, abstract, year, categories.

**Semantic Scholar** (when `s2` in sources):
```bash
S2_KEY=$(cat ~/.semantic_scholar_key)
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=QUERY&limit=N&fields=title,year,authors,venue,citationCount,externalIds,abstract" \
  -H "x-api-key: $S2_KEY" 2>/dev/null
```
Rate limit: 1 req/s. If 429, wait 2s and retry once. If `--year`, add `&year=YYYY-`.

**OpenAlex** (when `openalex` or `all` in sources):
```bash
curl -s "https://api.openalex.org/works?search=QUERY&per_page=N&sort=relevance" 2>/dev/null
```
If `--year`, add `&filter=publication_year:>YYYY`.

**DeepXiv** (when `deepxiv` or `all` in sources):
```bash
conda run -n ocr deepxiv search "QUERY" --limit N [--date-from YYYY-01] 2>/dev/null
```
Returns: title, arxiv_id, score, citations, date, venue, summary snippet.

**WebSearch** (when `web` or `all` in sources):
Use Claude Code `WebSearch` tool with queries:
- `"QUERY" site:arxiv.org`
- `"QUERY" research paper survey`
- `"QUERY" site:scholar.google.com`
Merge results.

### Phase 2: De-duplicate

After all sources return, de-duplicate by priority:
1. Match by **arXiv ID** first (most reliable)
2. Match by **DOI** second
3. Match by **normalized title** (lowercase, strip punctuation, first 50 chars)

When duplicates found:
- Prefer **S2** for citation counts and venue metadata
- Prefer **arXiv** for PDF link
- Prefer **OmniBox** for full-report content (already has `01_highlevel.md` / `02_technical.md`)
- Merge all source labels: `[arxiv, s2, omnibox]`

### Phase 3: Rank & synthesize

1. **Rank** by composite score: OmniBox relevance (if available) + citation count signal + source consensus (found in multiple sources = higher confidence)
2. **Synthesize** (unless `--no-synthesis`):
   - Group papers by approach/theme
   - Identify consensus vs disagreements
   - Note gaps and open problems
   - Highlight papers already in OmniBox (with paths to full reports)

### Phase 4: Output

Structured report:

```markdown
# Literature Search: [QUERY]

**Sources**: [list of sources that contributed] | **Results**: N unique papers

## Top Papers

| # | Title | Venue | Year | Citations | Sources |
|---|-------|-------|------|-----------|---------|
| 1 | ... | ... | ... | ... | arxiv, s2 |

## Thematic Landscape

[3-5 paragraph narrative synthesis]

## Detailed Results

For each top-k paper:
- Title, authors, venue, year
- Abstract / one-sentence summary
- Relevance to query
- Source(s) where found
- OmniBox paths (if available)

## Gaps & Opportunities

[What's missing, underexplored angles]
```

### Deep dive (--deep)

When `--deep` is set, for top-3 results:
- If arXiv ID available: `conda run -n ocr deepxiv paper ARXIV_ID --preview`
- If URL available and no OmniBox report: `WebFetch` the paper page
- Append preview content to each paper's entry

## Edge cases

- **OmniBox unavailable** (conda env `ml` missing, SiliconFlow key missing): skip, mention in output
- **S2 429 rate limit**: wait 2s, retry once, skip on second failure
- **DeepXiv token expired**: auto-refreshes, if fails skip
- **arXiv API timeout**: try once more, skip on second failure
- **Zero results from all sources**: report explicitly, suggest broader query
- **Query too broad** (>1000 total results): cap at k per source, note truncation
