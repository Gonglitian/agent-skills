# Data Source Profiles — litian-academic-search

## 1. OmniBox (Local Knowledge Base)

| Dimension | Detail |
|-----------|--------|
| **Depth** | ⭐⭐⭐⭐⭐ Full-report chunk-level semantic search. Indexes `01_highlevel.md` + `02_technical.md` full text (not just abstracts). Returns hit section + snippet with file path for direct reading. |
| **Breadth** | ⭐⭐⭐ ~3136 papers, CS/AI focused. Indexed from arxiv-deepdive pipeline reports. |
| **Call time** | ~3-5s (SiliconFlow bge-m3 embedding API + local sqlite-vec) |
| **Strengths** | Your own processed knowledge — papers you've already read and analyzed. Chunk-level retrieval finds deep technical details. |
| **Limitations** | Only papers you've already processed. Not real-time. |
| **Dependencies** | conda env `ml`, `sqlite-vec`, SiliconFlow API key at `~/.siliconflow_key` |
| **CLI** | `conda run -n ml python ~/proj/omnibox/index/search.py "QUERY" -k 8 [--json] [--topic X] [--only paper]` |

## 2. arXiv API

| Dimension | Detail |
|-----------|--------|
| **Depth** | ⭐⭐ Title + abstract only. No full text. |
| **Breadth** | ⭐⭐⭐⭐⭐ 2.5M+ CS preprints, daily updates. Covers math, physics, CS, stats, econ, q-bio, q-fin. |
| **Call time** | ~1-3s |
| **Strengths** | Earliest access to new research. Free, no key. Structured XML/Atom format. |
| **Limitations** | Preprints only (not peer-reviewed). No citation data. |
| **Dependencies** | None (public API) |
| **CLI** | `curl "http://export.arxiv.org/api/query?search_query=all:QUERY&max_results=10&sortBy=relevance"` |

## 3. Semantic Scholar

| Dimension | Detail |
|-----------|--------|
| **Depth** | ⭐⭐⭐ Abstract + structured metadata (authors, venue, citations, external IDs). TLDR summaries available. |
| **Breadth** | ⭐⭐⭐⭐ 200M+ published papers across all disciplines. Includes IEEE, ACM, Springer venues not on arXiv. |
| **Call time** | ~1-3s |
| **Strengths** | Best source for published/peer-reviewed venue papers. Citation counts. Venue metadata. |
| **Limitations** | 1 req/s rate limit. Need API key. |
| **Dependencies** | API key at `~/.semantic_scholar_key` (free, 1 req/s) |
| **CLI** | `curl -H "x-api-key: $(cat ~/.semantic_scholar_key)" "https://api.semanticscholar.org/graph/v1/paper/search?query=QUERY&limit=10&fields=title,year,authors,venue,citationCount,externalIds,abstract"` |

## 4. OpenAlex

| Dimension | Detail |
|-----------|--------|
| **Depth** | ⭐⭐ Metadata-rich (abstract, topics, institutions, funding). No full text. |
| **Breadth** | ⭐⭐⭐⭐⭐ 250M+ works, all disciplines. Fully open citation graph. |
| **Call time** | ~1-2s |
| **Strengths** | Institutional affiliations, funding data, cross-discipline coverage. Complements arXiv's CS focus. |
| **Limitations** | Less CS-specific than arXiv/S2. Abstract quality varies. |
| **Dependencies** | None (public REST API) |
| **CLI** | `curl "https://api.openalex.org/works?search=QUERY&per_page=10&sort=relevance"` |

## 5. DeepXiv

| Dimension | Detail |
|-----------|--------|
| **Depth** | ⭐⭐⭐⭐ Search + progressive reading (brief → head → section → full paper in Markdown). |
| **Breadth** | ⭐⭐⭐⭐ 200M+ papers (arXiv + PMC + S2 metadata). |
| **Call time** | ~2-4s (search), +5-10s for deep reading |
| **Strengths** | Progressive reading saves token budget. Built-in research agent. MCP server mode. |
| **Limitations** | Heavier install. 1000 req/day free limit. |
| **Dependencies** | conda env `ocr`, `pip install deepxiv-sdk[all]`. Auto-registers free token. |
| **CLI** | `conda run -n ocr deepxiv search "QUERY" --limit 10` |

## 6. WebSearch (Claude Code built-in)

| Dimension | Detail |
|-----------|--------|
| **Depth** | ⭐⭐ Search result snippets. Best used as discovery layer. |
| **Breadth** | ⭐⭐⭐⭐⭐ Entire web: arXiv, Google Scholar, blogs, docs, social media, news. |
| **Call time** | ~2-5s |
| **Strengths** | No setup. Catches everything other APIs miss (new blogs, pre-prints on personal sites, industry reports). |
| **Limitations** | Shallow snippets. No structured metadata. |
| **Dependencies** | None (Claude Code built-in) |
| **Usage** | `WebSearch` tool with targeted queries |

## 7. WebFetch (Claude Code built-in)

| Dimension | Detail |
|-----------|--------|
| **Depth** | ⭐⭐⭐⭐ Full page content. Use for paper landing pages, blog posts, documentation. |
| **Breadth** | ⭐⭐⭐ Any publicly accessible URL. |
| **Call time** | ~2-4s |
| **Strengths** | Deep dive into specific pages. Use for papers found by other sources. |
| **Limitations** | Need a URL first (not a search tool). Some sites block (AlphaXiv 403, some paywalls). |
| **Dependencies** | None (Claude Code built-in) |

---

## Source Selection Guide

| Scenario | Recommended Sources |
|----------|-------------------|
| Quick survey of a new field | `arxiv,s2,web` |
| Deep dive in your expertise area | `omnibox,arxiv,s2,deepxiv` |
| Cross-discipline search | `openalex,s2,web` |
| Finding whether you've already read something | `omnibox` |
| Full comprehensive search | `all` |
| Minimal token budget | `omnibox,arxiv` (fastest, most relevant) |
