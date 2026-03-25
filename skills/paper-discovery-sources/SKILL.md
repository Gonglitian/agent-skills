---
name: paper-discovery-sources
description: "Shared reference for all paper search skills. Defines the unified 3-source paper discovery strategy: local vec-db (96K top-venue papers), Semantic Scholar API (200M+ papers + citation graph), and AlphaXiv (free full-text reading). This skill is NOT user-invokable — it is a reference loaded by other skills (research-survey, gap-to-method, paper_related_works, idea_refinery, topic_survey)."
---

# Unified Paper Discovery Sources

This is a shared reference document. Other paper-related skills should follow these strategies.

## The Three Sources

### Source 1: Local Vec-db (Precision — 96K top-venue papers)

**What**: LanceDB vector database with ~96K papers from CoRL, ICRA, IROS, RSS, NeurIPS, ICML, ICLR, CVPR, etc.
**Best for**: Finding highly relevant top-venue papers via semantic similarity.
**Limitation**: Only indexed conferences; no arXiv-only papers; no citation info.

```bash
cd /home/vla-reasoning/proj/litian-research/vec-db
npx tsx src/cli.ts search "<query>" --top 15
```

**Tips**:
- Run 5-8 diverse queries per topic (different angles)
- Use English queries (embeddings are English-centric)
- Score > 0.25 is relevant
- Results include title, venue, year, abstract — but NOT arXiv ID (need to look up separately)

### Source 2: Semantic Scholar API (Breadth — 200M+ papers)

**What**: Free academic search API with citation graph, covering all major publishers.
**Best for**: Keyword search across ALL papers; finding citing/cited papers; getting citation counts.
**Limitation**: No full text; rate limited (5000 req/5min unauthenticated).

**Search by keyword**:
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=<URL_ENCODED_KEYWORDS>&limit=20&fields=title,year,authors,citationCount,externalIds,abstract&sort=citationCount:desc"
```

**Search recent papers**:
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=<KEYWORDS>&limit=20&fields=title,year,authors,citationCount,externalIds,abstract&year=2024-2026"
```

**Get citations of a paper (successors)**:
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/ArXiv:<ID>?fields=title,year,citationCount,citations.title,citations.year,citations.authors,citations.externalIds,citations.citationCount"
```

**Get references of a paper (predecessors)**:
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/ArXiv:<ID>?fields=title,year,references.title,references.year,references.externalIds,references.citationCount"
```

### Source 3: AlphaXiv (Reading — free full text)

**What**: Free structured Markdown rendering of arXiv papers.
**Best for**: Reading paper content without downloading PDF. Much faster than PDF parsing.
**Limitation**: Only arXiv papers; some papers may 404.

**Structured overview** (try first, faster):
```
WebFetch: https://alphaxiv.org/overview/<ARXIV_ID>.md
```

**Full text** (if overview lacks detail):
```
WebFetch: https://alphaxiv.org/abs/<ARXIV_ID>.md
```

**Fallback**: If AlphaXiv returns 404, download and read the PDF directly:
```bash
wget -q "https://arxiv.org/pdf/<ARXIV_ID>" -O "<ARXIV_ID>.pdf"
```

## Recommended Discovery Strategy by Goal

### Goal A: "Survey a topic" (research-survey, topic_survey)

```
1. Vec-db semantic search (5-8 queries, --top 15 each)     → top-venue papers
2. Semantic Scholar keyword search (2-3 queries)            → broader coverage + recent
3. Web search for arXiv (补充最新未索引论文)                → cutting-edge
4. Deduplicate by title similarity
5. Read top papers via AlphaXiv
```

### Goal B: "Find gaps / propose method" (gap-to-method)

```
1. Vec-db semantic search (per design dimension)            → map the design space
2. Semantic Scholar keyword search (per dimension)          → fill matrix gaps
3. Web search for very recent work                          → ensure no one beat you
4. Build literature matrix from combined results
5. Read gap-adjacent papers via AlphaXiv for evidence
```

### Goal C: "Map related works of a paper" (paper_related_works)

```
1. Read the paper via AlphaXiv                              → understand it first
2. Semantic Scholar citations API                           → predecessors + successors
3. Vec-db search with paper's key concepts                  → find related top-venue work
4. Web search for concurrent/recent follow-ups              → very latest
```

### Goal D: "Refine a research idea" (idea_refinery)

```
1. Vec-db search (idea's key concepts)                      → closest existing work
2. Semantic Scholar search + citation snowball               → validate novelty
3. AlphaXiv to read key competitors                         → understand deeply
4. Web search for latest arXiv preprints                    → check no overlap
```

## Rate Limiting & Best Practices

- **Vec-db**: No limit. Run as many queries as needed.
- **Semantic Scholar**: 5000 req/5min (unauthenticated). Space requests 0.5s apart for bulk.
- **AlphaXiv**: No documented limit. Be reasonable (~1 req/sec).
- **Always deduplicate** across sources before reading — same paper may appear in multiple sources.
- **Prefer AlphaXiv over PDF** for reading — faster, structured, no parsing errors.
- **Use Semantic Scholar for citation counts** to prioritize influential papers.
- **Use vec-db for top-venue filtering** — it only contains accepted papers, not random preprints.
