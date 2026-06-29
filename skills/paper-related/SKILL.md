---
name: paper-related
description: Given a paper (arXiv ID / URL / title), find its related works through three complementary lenses: (1) citation graph — predecessors (references) and successors (citations) via Semantic Scholar + OpenAlex, (2) semantic similarity via litian-academic-search, (3) shared references/citations analysis. Outputs a structured related-work map suitable for paper writing or literature review. Use whenever the user wants to find related papers, expand from a seed paper, do citation snowballing, "找相关论文", "这个方向还有哪些工作", "citation graph", "related works", or needs to map the literature around a specific paper.
---

# paper-related: Related Work Discovery

Given one seed paper, trace its academic neighborhood through three independent lenses, then synthesize.

## Pipeline

```
seed paper (arXiv ID)
  │
  ├─ Lens 1: Citation Graph (S2 + OpenAlex)
  │   ├── predecessors (what it cites)
  │   └── successors (what cites it)
  │
  ├─ Lens 2: Semantic Similarity (litian-academic-search)
  │   └── conceptually similar papers
  │
  └─ Lens 3: Shared Context (S2)
      ├── co-cited papers (shared references with successors)
      └── common citation patterns
```

## Parameters

- **Paper**: arXiv ID, URL, or title (resolve to arXiv ID via paper-read Step 1)
- **`--k <N>`** — max results per lens (default: 10)
- **`--lens <list>`** — which lenses: `citation`, `semantic`, `shared`, `all` (default: all)
- **`--no-ingest`** — skip OmniBox ingestion of discovered papers (default: auto-ingest via paper-read --light)
- **`--year <YYYY->`** — filter by year (default: none)

## Lens 1: Citation Graph

### 1a: Predecessors — what this paper cites (references)

```bash
S2_KEY=$(cat ~/.semantic_scholar_key)
curl -s "https://api.semanticscholar.org/graph/v1/paper/ArXiv:<ID>/references?limit=<K>&fields=title,year,authors,venue,citationCount,externalIds,abstract" \
  -H "x-api-key: $S2_KEY"
```

Sort by citation count (desc) — high-citation references are foundational papers.

**OpenAlex fallback** (if S2 returns empty or for richer metadata):
```bash
curl -s "https://api.openalex.org/works?filter=cites:arxiv:<ID>&per_page=<K>&sort=cited_by_count:desc"
```

### 1b: Successors — what cites this paper (citations)

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/ArXiv:<ID>/citations?limit=<K>&fields=title,year,authors,venue,citationCount,externalIds,abstract" \
  -H "x-api-key: $S2_KEY"
```

Sort by:
1. **Influential citations first** (S2 `isInfluential: true`)
2. **Recency** (newer papers more likely to be relevant for current research)
3. **Citation count**

**OpenAlex fallback:**
```bash
curl -s "https://api.openalex.org/works?filter=cites:arxiv:<ID>&per_page=<K>&sort=publication_date:desc"
```

## Lens 2: Semantic Similarity

Use litian-academic-search to find conceptually similar papers that may NOT be in the citation graph (different communities, concurrent work, pre-citation):

```
/litian-academic-search "<PAPER_TITLE_OR_CORE_IDEA>" --sources omnibox,arxiv,s2 --k <K> --year 2022-
```

This catches:
- Concurrent papers that haven't cited each other yet
- Papers from adjacent fields using different terminology
- Papers already in your OmniBox that are topically related

## Lens 3: Shared Context (only when Lens 1 successors exist)

Find papers that are co-cited with the seed paper — these represent the broader conversation:

For top-5 successors, check which references they share with the seed paper:
```bash
# For each successor, get its references, find intersection with seed's references
# Use S2 bulk endpoint for efficiency
curl -s "https://api.semanticscholar.org/graph/v1/paper/batch" \
  -H "x-api-key: $S2_KEY" \
  -H "Content-Type: application/json" \
  -d '{"ids": ["ArXiv:<ID1>", "ArXiv:<ID2>", ...]}' \
  -d 'fields=references'
```

Shared references that appear across multiple successors are **foundational papers** everyone in this subfield cites.

## Output Structure

```markdown
# Related Work Map: <Paper Title>

**Seed**: <arxiv_id> | <year> | <citations> citations

## 1. Foundational Papers (Predecessors — what this paper builds on)

| # | Title | Year | Citations | Relation |
|---|-------|------|-----------|----------|
| 1 | ... | ... | ... | core method |
| 2 | ... | ... | ... | evaluation benchmark |

## 2. Recent Developments (Successors — what builds on this paper)

| # | Title | Year | Citations | Delta |
|---|-------|------|-----------|-------|
| 1 | ... | 2025 | ... | adds X, improves Y |

## 3. Conceptually Similar (beyond citation graph)

| # | Title | Year | Source | Why relevant |
|---|-------|------|--------|-------------|
| 1 | ... | ... | arxiv,s2 | ... |

## 4. Shared Foundations (co-cited across the field)

Papers cited by both the seed and its successors — the consensus foundation.

## 5. Citation Map (ASCII)

```
  [Foundational A]  [Foundational B]  [Foundational C]
        \               |               /
         \              |              /
          └─────────► [SEED] ◄─────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    [Successor 1]  [Successor 2]  [Successor 3]
    (2024, 45 cit) (2025, 12 cit) (2025, 8 cit)
```

## 6. Gaps & Opportunities

What's NOT cited but should be? What citation patterns reveal about the field's direction?
```

## OmniBox Ingestion

After discovering related papers, auto-ingest new ones:

```bash
for arxiv_id in $discovered_papers; do
  paper-read $arxiv_id --topic <detected> --light
done
```

Skip papers already in OmniBox (paper-read handles this internally).

## Edge Cases

- **Very new paper (0 citations, 0 successors)**: Lens 1b empty — rely on Lens 2 (semantic) + Lens 3 (shared foundations from references)
- **Very old / highly-cited paper (1000+ citations)**: Cap successors at k, sort by recency + influence
- **arXiv ID not in S2**: Fall back to OpenAlex; if also missing, use litian-academic-search title search
- **S2 rate limit (429)**: Wait 2s, retry once; skip lens on second failure
- **Seed already in OmniBox**: note this; the user has already read it deeply
