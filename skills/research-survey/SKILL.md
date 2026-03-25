---
name: research-survey
description: >
  Deep literature survey pipeline: semantic search via local vec-db, web search for arXiv papers,
  download PDFs, parallel subagent reading, and structured report generation.
  Use this skill whenever the user asks to survey, research, or find related papers on a topic,
  especially when they mention vec-db, arXiv, literature review, paper search, or updating an
  idea/survey note. Also trigger when the user says things like "调研", "查论文", "找相关工作",
  "literature survey", "related work", "search papers", or "read papers and summarize".
  This skill orchestrates the full pipeline from search to structured markdown report.
---

# Research Survey Pipeline

Orchestrate a full literature survey: vec-db semantic search → web search → download → parallel subagent reading → structured report.

## Overview

This skill automates the research paper discovery-and-analysis workflow. It combines a local vector database of ~60K+ indexed top-venue papers with web search for broader coverage, then deploys **parallel subagents** to deep-read each paper and produce a structured comparative analysis anchored to the user's research idea.

The goal is not just to list papers, but to produce actionable competitive intelligence: how does each paper relate to the user's proposed work, what can be borrowed, what differentiates the user's approach.

## Prerequisites

- **Vec-db**: LanceDB semantic search database at `/home/vla-reasoning/proj/litian-research/vec-db/`
  - Query: `cd /home/vla-reasoning/proj/litian-research/vec-db && npx tsx src/cli.ts search "<query>" --top <N>`
  - Status: `cd /home/vla-reasoning/proj/litian-research/vec-db && npx tsx src/cli.ts status`
- **arXiv access**: For downloading PDFs (`wget https://arxiv.org/pdf/<id> -O <id>.pdf`)
- **Subagents**: Agent tool — **MUST launch all reading agents in ONE message for true parallelism**
- **Target note**: A markdown file to update with findings (user specifies path)

## Workflow

### Step 1: Understand the Research Context

Before searching, gather from the conversation or by asking:
1. **Research topic/idea** — Read the user's idea note if it exists
2. **Target note path** — Where to write/update the survey
3. **Papers already surveyed** — Read existing note to avoid duplicates
4. **Number of papers** — Default 10
5. **Focus angles** — What aspects matter most for comparison

### Step 2: Multi-Angle Vec-db Search

Run **5-8 diverse semantic queries** against the vec-db to maximize coverage. Each query approaches the topic from a different angle.

**Query design principles:**
- Mix high-level conceptual queries with specific technical queries
- Include both the method name and the problem it solves
- Cover adjacent areas (not just exact matches)
- Use English for queries (the embeddings are English-centric)
- Request `--top 15` per query to get broad coverage

**CRITICAL: Run all queries in parallel** — issue multiple Bash tool calls in a single message. Do NOT run them sequentially.

**Example for a "3D point cloud + VLA" topic:**
```bash
# Angle 1: Direct topic
npx tsx src/cli.ts search "3D point cloud reconstruction for vision-language-action robot manipulation" --top 15

# Angle 2: Method-focused
npx tsx src/cli.ts search "depth prediction auxiliary task for imitation learning robot policy" --top 15

# Angle 3: Application-focused
npx tsx src/cli.ts search "vision language action model with 3D spatial understanding" --top 15

# Angle 4: Competing approach
npx tsx src/cli.ts search "implicit 3D grounding spatial representation for robotic grasping" --top 15

# Angle 5: Adjacent technique
npx tsx src/cli.ts search "auxiliary reconstruction loss for robot learning visual representation" --top 15

# Angle 6: Specific method name (if user mentions one)
npx tsx src/cli.ts search "spatial forcing depth estimation multi-view geometry for VLA" --top 15
```

### Step 2b: Semantic Scholar API Search (Broader Coverage)

Complement vec-db with Semantic Scholar to catch papers outside the indexed conferences:

```bash
# Keyword search (high citation)
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=<URL_ENCODED_KEYWORDS>&limit=20&fields=title,year,authors,citationCount,externalIds,abstract&sort=citationCount:desc"

# Recent papers (last 2 years)
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=<KEYWORDS>&limit=20&fields=title,year,authors,citationCount,externalIds,abstract&year=2024-2026"
```

Run 2-3 keyword variants. Semantic Scholar covers 200M+ papers including workshops, journals, and preprints that vec-db may miss. Use citation counts to prioritize.

### Step 3: Select Candidate Papers

From the combined vec-db + Semantic Scholar results, select ~10 papers that are:
1. **Accepted at top venues** (ICLR, ICML, NeurIPS, CVPR, ICCV, ECCV, CoRL, RSS, ICRA, IROS, etc.) — prioritize these
2. **Not already in the user's survey** — cross-reference with existing note
3. **Highly relevant** — score > 0.25 is useful, but relevance to user's idea matters more
4. **Diverse** — cover different sub-aspects, don't pick 10 papers doing the same thing

### Step 4: Find arXiv IDs and Read via AlphaXiv

For papers without arXiv IDs in vec-db results, check Semantic Scholar's `externalIds.ArXiv` field first, then fall back to WebSearch:
```
WebSearch: "<paper title>" arXiv <year>
  allowed_domains: ["arxiv.org"]
```

**Run multiple WebSearch calls in parallel** for different papers.

If a paper has no arXiv preprint, replace it with another candidate that does.

### Step 5: Read Papers — AlphaXiv First, PDF as Fallback

**Prefer AlphaXiv** over downloading PDFs — it's faster and returns structured Markdown:

```
# Try AlphaXiv overview first (fast, structured)
WebFetch: https://alphaxiv.org/overview/<ARXIV_ID>.md

# If overview lacks detail, get full text
WebFetch: https://alphaxiv.org/abs/<ARXIV_ID>.md
```

**Only download PDFs** if AlphaXiv returns 404:

```bash
cd <papers-dir>/raw
for id in <id1> <id2> ...; do
  [ -f "${id}.pdf" ] && echo "SKIP ${id}" || \
  (wget -q "https://arxiv.org/pdf/${id}" -O "${id}.pdf" && echo "OK ${id}" || echo "FAIL ${id}")
done
```

Verify all downloads succeeded before proceeding.

### Step 6: Parallel Subagent Reading — THE MOST IMPORTANT STEP

**CRITICAL REQUIREMENT: Launch ALL reading agents in a SINGLE message.**

This is non-negotiable. Do NOT launch agents one by one. Do NOT wait for one to finish before starting the next. Issue all Agent tool calls in one response so they run truly in parallel.

For 10 papers, launch **5 agents in the first batch** (each reading 2 papers), or **10 agents** (each reading 1 paper) if the system supports it. The key is: **one message, all agents, true parallelism**.

**Agent prompt template:**

```
Read the paper at <pdf_path> (<paper_title>, <venue>).

This is for a literature survey on "<user's research topic>".
Our proposed idea: <1-2 sentence description of user's work>

Provide a structured analysis:

1. **Core Method**: What does this paper do and how? (2-3 sentences)
2. **Architecture**: Key components, modules, design choices
3. **Training**: Losses, data requirements, does it need depth/3D at inference?
4. **Key Results**: Performance numbers on main benchmarks. Key ablation findings.
5. **Relation to Our Work**:
   - How does this paper's approach compare to ours?
   - What can we learn from or differentiate against?
   - Is this complementary or competing?

Be concise but thorough. Focus on technical details for comparison.
```

**Parallelism patterns:**

Pattern A — 10 agents, 1 paper each (preferred if feasible):
```
[Single message with 10 Agent tool calls]
Agent 1: Read paper_1.pdf → analysis
Agent 2: Read paper_2.pdf → analysis
...
Agent 10: Read paper_10.pdf → analysis
```

Pattern B — 5 agents, 2 papers each (if agent count is limited):
```
[Single message with 5 Agent tool calls]
Agent 1: Read paper_1.pdf AND paper_2.pdf → two analyses
Agent 2: Read paper_3.pdf AND paper_4.pdf → two analyses
...
Agent 5: Read paper_9.pdf AND paper_10.pdf → two analyses
```

**NEVER do this (anti-pattern):**
```
# BAD: Sequential launches — defeats the purpose
Agent 1: Read paper_1.pdf → wait → get result
Agent 2: Read paper_2.pdf → wait → get result  # WRONG: should be parallel
```

### Step 7: Compile and Update the Note

After ALL agents return, synthesize findings into the target note:

1. **Read the existing note** to understand its structure and style
2. **Add new papers** to appropriate categories/tables
3. **Add deep analysis section** for each paper with key technical details
4. **Update the positioning/differentiation** — explicitly state how user's work differs
5. **Update the paper list** at the bottom
6. **Sharpen the "gap" statement** — what does no existing work do that ours does?
7. **Preserve existing content** — add/modify, don't delete prior work

Writing style:
- **输出语言为中文**，技术术语保留英文（如 "Chamfer loss"、"auxiliary task"、"VLA"）
- Be specific: numbers, method names, layer counts, loss weights
- Focus on actionable insights: "可以借鉴什么" and "如何差异化"
- Use comparison tables for clear positioning
- Section headings in Chinese (e.g., "## 相关工作调研", "### 关键洞见总结")

### Step 8: Commit and Push

```bash
git add <note_path>
git commit -m "Update survey with N new top-venue papers

Added analysis of:
- Paper1 (Venue): one-line summary
- Paper2 (Venue): one-line summary
...

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

## Tips for High-Quality Surveys

- **Don't just summarize — position.** Every paper is analyzed through "how does this relate to OUR work?"
- **Find the debate.** Identify disagreements in the field and position the user's work within them.
- **Quote specific numbers.** "98.5% on LIBERO, +1.4% over SOTA" beats "outperforms baselines."
- **Identify the gap.** State what combination of properties no existing work has.
- **Track criticisms.** If Paper A criticizes an approach the user also uses — flag it as threat or rebuttal opportunity.
- **Speed matters.** The entire pipeline (search → read → write) should complete in one session. Parallelism is the key enabler.
