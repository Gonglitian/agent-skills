---
name: comprehensive-survey
description: >
  Full-spectrum research survey pipeline: given a topic (or multiple related topics), orchestrates
  parallel searches across 6 information sources (local vec-db, Semantic Scholar API, WebSearch/arXiv,
  social platforms via MediaCrawler + WebSearch, AlphaXiv paper reading, Brave Search), then produces
  structured survey reports with paper citations, social media insights, and concept glossary documents
  with pseudocode. Use PROACTIVELY whenever the user wants a comprehensive literature survey,
  topic investigation, "全面调研", "综合调研", "survey this topic", "调研一下", "research survey",
  "帮我全面了解一下这个方向", "从论文到社交平台全面搜", or wants multi-source coverage combining
  academic papers AND social media discussions on any research topic. Also trigger when user provides
  a directory path and expects organized multi-file research output.
---

# Comprehensive Research Survey Pipeline

Orchestrate a full-spectrum research investigation combining **academic paper search** (6 sources) and
**social media gathering** (5 platforms: B站/知乎/X/Reddit/Tech Blogs) into structured, cross-referenced survey reports with concept
glossary and pseudocode.

This skill produces the same quality and structure as a manual month-long literature review, but in
one session. The key insight: **parallelism at every level** — multiple search sources, multiple
subagents, multiple topics simultaneously.

---

## Step 0: Environment Check

Before any search, verify all required infrastructure. Run these checks **in parallel**:

### 0.1 Vec-db (REQUIRED)

```bash
cd ${VECDB_PATH:-/home/vla-reasoning/proj/litian-research/vec-db} && npx tsx src/cli.ts status
```

If this fails, **stop and ask the user**:
> "Vec-db is required but not found at the default path. Please provide the path to your vec-db installation, e.g. `/path/to/vec-db`"

Store the path for later use. The vec-db should report 60K+ papers. If it reports 0, the index may not be built — tell the user to run `npx tsx src/cli.ts index`.

### 0.2 MediaCrawler (REQUIRED for social platforms)

```bash
# Check if MediaCrawler exists at common locations
for p in "${MEDIACRAWLER_PATH}" "/home/$(whoami)/MediaCrawler" "/data1/$(whoami)/MediaCrawler"; do
  [ -d "$p" ] && [ -f "$p/main.py" ] && echo "FOUND: $p" && break
done
```

If not found, **stop and ask the user**:
> "MediaCrawler is required for social platform search (Bilibili etc.). Please provide the path to your MediaCrawler installation, or read the installation guide: `references/mediacrawler_setup.md`"

Check if MediaCrawler venv exists and has playwright:
```bash
cd <MediaCrawler_path> && source venv/bin/activate && python -c "import playwright; print('OK')" 2>/dev/null
```

### 0.3 Semantic Scholar API (auto-available)

```bash
curl -s --max-time 5 "https://api.semanticscholar.org/graph/v1/paper/search?query=test&limit=1&fields=title" | head -1
```

If 429 (rate limited), note it — will use with delay or skip gracefully.

### 0.4 Brave Search MCP (optional enhancement)

Check if `mcp__brave-search__brave_web_search` is available. If not, WebSearch will be used as fallback for all web searches.

### 0.5 Crawl4AI MCP (optional enhancement)

Check if `mcp__crawl4ai__scrape` is available. If not, WebFetch will be used as fallback for page scraping.

**Summary**: After checks, report to user:
```
Environment check:
  ✓ Vec-db: <path> (<N> papers)
  ✓ MediaCrawler: <path>
  ✓/✗ Semantic Scholar API
  ✓/✗ Brave Search MCP
  ✓/✗ Crawl4AI MCP
```

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

Each topic directory will contain:
```
<topic-dir>/
├── FINAL_REPORT.md      ← Main deliverable (comprehensive survey)
├── survey_academic.md    ← Academic paper search results
├── survey_social.md      ← Social media discussion results
└── vecdb_papers.md       ← Vec-db top-conference paper list
```

Top-level files:
```
<output_dir>/
├── README.md                  ← Navigation index
├── paper_list_comprehensive.md ← Deduplicated master paper list
└── concepts/                   ← Concept glossary with pseudocode
    ├── <concept_1>.md
    ├── <concept_2>.md
    └── ...
```

---

## Step 3: Launch Parallel Search Agents

This is the core execution step. Launch **ALL search agents in ONE message** for true parallelism.

For each topic, spawn 3 types of agents simultaneously:

### Agent Type A: Academic Paper Search (one per topic)

Each agent performs multi-source paper search:

**Prompt template:**
```
You are a research paper search specialist. Search for papers on "<TOPIC>" using ALL of the following sources:

## Source 1: Vec-db Semantic Search
Run 6-8 diverse semantic queries in parallel:
cd <VECDB_PATH> && npx tsx src/cli.ts search "<query>" --top 15

Query design:
- Mix high-level conceptual + specific technical queries
- Use English (embeddings are English-centric)
- Cover adjacent areas, not just exact matches

## Source 2: Semantic Scholar API
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=<URL_ENCODED>&limit=20&fields=title,year,authors,citationCount,externalIds,abstract&sort=citationCount:desc"
Also search recent papers: &year=2024-2026
Run 2-3 keyword variants. If 429, wait 3s and retry once.

## Source 3: WebSearch
Search for: "<topic> arXiv 2024 2025 survey", "<topic> NeurIPS ICML ICLR 2024 2025", etc.
Use allowed_domains: ["arxiv.org"] for targeted arXiv search.
Run 6-10 diverse web searches.

## Output
Write to <output_dir>/<topic>/survey_academic.md with:
- Structured sections by method/approach
- Every paper: title, authors, year, venue, arXiv link, core contribution
- Comparison tables where appropriate
- At least <N> papers (quick=15, standard=30, deep=50)

Also write <output_dir>/<topic>/vecdb_papers.md with the raw vec-db results table.
```

### Agent Type B: Social Platform Search (one per topic, or one for all topics)

**Prompt template:**
```
Search social platforms and the web for discussions about "<TOPIC>".

## Platform 1: Bilibili (B站) — via MediaCrawler
cd <MEDIACRAWLER_PATH>
source venv/bin/activate
./crawl.sh bili "<中文关键词>" 20

If crawl.sh doesn't exist, run directly:
python main.py --platform bili --lt cookie --type search --keywords "<关键词>"

Read the JSON output from the data directory.

## Platform 2: Zhihu (知乎) — via WebSearch + WebFetch
WebSearch: "<topic> site:zhihu.com"
For top results, WebFetch the full content (may 403, use search snippets as fallback).

## Platform 3: X/Twitter — via WebSearch
WebSearch: "<english topic> site:x.com 2024 2025"

## Platform 4: Reddit — via WebSearch
WebSearch: "<english topic> site:reddit.com discussion"

## Platform 5: Tech Blogs
WebSearch: "<topic> blog deep dive 2024 2025"
WebSearch: "<topic> 技术博客 深度解析"

## Output
Write to <output_dir>/<topic>/survey_social.md with:
- Platform-organized sections (知乎/B站/Twitter/Reddit/博客)
- Each entry: source, link, key points summary
- Community consensus and disagreements section
- Complete source URL list at the end
```

### Agent Type C: Comprehensive Paper List (one agent for all topics)

**Prompt template:**
```
Build a comprehensive, deduplicated paper list covering ALL topics: <TOPIC_1>, <TOPIC_2>, ...

Search strategy:
1. Survey papers: WebSearch "<topic> survey 2024 2025 arXiv"
2. Top conferences: WebSearch "<topic> NeurIPS ICML ICLR CVPR CoRL 2024 2025"
3. Key work series: WebSearch for known paper series in each topic
4. Lab frontiers: WebSearch "<company/lab> <topic> 2025"

Output: <output_dir>/paper_list_comprehensive.md
Format: Tables organized by topic, then by year. Include arXiv links.
Target: 80+ papers total.
```

### Parallelism pattern

For 3 topics at "standard" depth, launch in ONE message:
```
Agent 1: Academic search — Topic 1
Agent 2: Academic search — Topic 2
Agent 3: Academic search — Topic 3
Agent 4: Social search — Topic 1
Agent 5: Social search — Topics 2 & 3 (combined to reduce agents)
Agent 6: Comprehensive paper list — all topics
```

All 6 agents run in background simultaneously.

---

## Step 4: Extract Core Concepts

After search agents complete, analyze all survey files to find high-frequency technical terms:

```bash
cat <output_dir>/*/survey_academic.md | grep -oiE '<concept_regex>' | sort | uniq -ci | sort -rn | head -30
```

Build a concept regex from known domain terms. Select the top 10-15 concepts that:
- Appear frequently across multiple papers
- Are technical enough to warrant explanation
- Would benefit from pseudocode illustration

---

## Step 5: Generate Concept Documents

Launch 2 parallel agents to write concept docs:

**Agent prompt template:**
```
Write detailed concept explanation documents for the following terms.
Each document goes to <output_dir>/concepts/<concept_name>.md

Format per document:

# [Concept Name]

## One-line Definition

## Intuitive Explanation
(Analogy or diagram to build understanding)

## Mathematical Formulation
(Key equations in LaTeX)

## Role in <domain>

## Pseudocode Implementation
```python
# PyTorch-style pseudocode, detailed enough to serve as implementation reference
class ConceptName(nn.Module):
    ...
```

## Relationship to Other Concepts
(Cross-references to other concept docs)

## Representative Papers
(2-3 papers with arXiv links)
```

---

## Step 6: Compile Final Reports

For each topic, launch a final report compilation agent:

**Agent prompt template:**
```
Integrate all research materials into a comprehensive final survey report.

Input files (read all):
- <topic>/survey_academic.md
- <topic>/vecdb_papers.md
- <topic>/survey_social.md
- paper_list_comprehensive.md

Output: <topic>/FINAL_REPORT.md

Structure:
# <Topic> 综述报告

> 生成日期: <date>
> 论文覆盖: X篇
> 信息源: 学术论文 + Vec-db顶会 + Semantic Scholar + 社交平台

---

## 摘要
(300 words)

## 1. 引言与定义

## 2. 发展时间线
(Table: year | paper | link | contribution)

## 3. 技术分类体系
(Multiple subsections by approach/method)

## 4. 关键论文详解 (Top 15-20)
(Each: title+link, contribution, method, experiments, limitations)

## 5. 社区观点与产业动态
(Integrated from social survey)

## 6. 核心概念索引
(Links to ../concepts/*.md)

## 7. 开放问题与未来方向

## 8. 完整论文列表
(Deduplicated, every paper has [title](url) markdown link, grouped by year)

Requirements:
- Every paper MUST have an arXiv or publication link
- Deduplicate across all input sources
- At least 50 unique papers per report (standard depth)
- Chinese text, English paper titles
- 800+ lines
```

---

## Step 7: Generate README Index

Write `<output_dir>/README.md` with:
- Directory structure tree
- Quick navigation table (topic → FINAL_REPORT link)
- Concept glossary table (concept → doc link + one-line definition)
- Relationship diagram between topics (ASCII or description)
- Statistics summary (total files, lines, papers, links)

---

## Step 8: Final Verification

Run a verification pass:

```bash
# Count deliverables
find <output_dir> -name "*.md" -exec sh -c 'echo "$(wc -l < "$1") lines: $1"' _ {} \; | sort -rn

# Verify all FINAL_REPORTs exist
for topic in <topics>; do
  [ -f "<output_dir>/$topic/FINAL_REPORT.md" ] && echo "✓ $topic" || echo "✗ MISSING: $topic"
done

# Count total links
grep -roh '\[.*\](http[^)]*' <output_dir>/*.md <output_dir>/*/*.md | wc -l
```

Report to user:
```
Survey complete!
- X files / Y lines / Z KB
- N total papers with links
- M concept documents with pseudocode
Entry point: <output_dir>/README.md
```

---

## Search Source Reference

### Vec-db (Precision — top-venue papers)

```bash
cd <VECDB_PATH>
npx tsx src/cli.ts search "<query>" --top 15
npx tsx src/cli.ts status  # check paper count
```

**Tips:**
- Run 5-8 diverse queries per topic (different angles)
- Use English queries (embeddings are English-centric)
- Score > 0.25 is relevant; > 0.35 is highly relevant
- Results include title, venue, year, abstract — NOT arXiv ID (look up separately)
- Run ALL queries in parallel (multiple Bash calls in one message)

### Semantic Scholar API (Breadth — 200M+ papers)

**Keyword search (by citation count):**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=<URL_ENCODED>&limit=20&fields=title,year,authors,citationCount,externalIds,abstract&sort=citationCount:desc"
```

**Recent papers:**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=<KEYWORDS>&limit=20&fields=title,year,authors,citationCount,externalIds,abstract&year=2024-2026"
```

**Citation graph (successors):**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/ArXiv:<ID>?fields=title,year,citationCount,citations.title,citations.year,citations.authors,citations.externalIds,citations.citationCount"
```

**Rate limit:** 5000 req/5min unauthenticated. Space 0.5s apart for bulk queries.

### AlphaXiv (Paper Reading — free full text)

```
# Structured overview (try first)
WebFetch: https://alphaxiv.org/overview/<ARXIV_ID>.md

# Full text (if overview insufficient)
WebFetch: https://alphaxiv.org/abs/<ARXIV_ID>.md
```

Fallback: `wget https://arxiv.org/pdf/<ID> -O <ID>.pdf`

### WebSearch (Cutting-edge + blogs)

Use for: latest arXiv preprints, tech blogs, social platforms via `site:` filters, Google Scholar-indexed papers.

### MediaCrawler (Bilibili)

```bash
cd <MEDIACRAWLER_PATH>
source venv/bin/activate

# Bilibili search
python main.py --platform bili --lt cookie --type search --keywords "<关键词>"
```

Data output: JSON files in the configured data directory.

If MediaCrawler is not available or cookies are expired, fall back to WebSearch with `site:bilibili.com`.

### Brave Search MCP (enhanced web search, if available)

```
mcp__brave-search__brave_web_search: "<query>"
mcp__brave-search__brave_local_search: "<query>"  # for local/business results
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Vec-db returns 0 results | Wrong path or unbuilt index | Verify path; run `npx tsx src/cli.ts status` |
| Semantic Scholar 429 | Rate limited | Wait 60s, retry; or skip and rely on vec-db + WebSearch |
| MediaCrawler login failed | Cookie expired | User must re-export cookies from browser |
| AlphaXiv 404 | Paper not indexed | Fall back to PDF download |
| Subagent timeout | Too much work per agent | Split into smaller tasks per agent |
| WebFetch 403 on Zhihu | Server blocks bots | Use search snippets; try Crawl4AI if available |

---

## Depth Presets

| Preset | Papers/topic | Concepts | Vec-db queries | Social platforms | Report lines |
|--------|-------------|----------|----------------|-----------------|-------------|
| quick | ~15 | 5 | 3-4 | WebSearch only | 500+ |
| standard | ~30-50 | 10-15 | 6-8 | All (MediaCrawler + WebSearch) | 800+ |
| deep | ~50-100 | 15-20 | 8-10 | All + deep fetch | 1000+ |
