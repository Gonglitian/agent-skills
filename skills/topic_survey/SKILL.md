---
name: topic-survey
description: Survey a research field interactively, exploring papers by topic and writing a structured literature review.
---

# topic_survey

Interactively survey a research field: discover key papers, explore sub-topics guided by user interest, and produce a structured literature review.

## When to Use

- User wants to understand the landscape of a research area
- User is starting a new project and needs to know the state of the art
- User asks "what are the key papers in X?"
- User wants a literature review or reading list on a topic

## Inputs

| Input | Required | Example |
|-------|----------|---------|
| **Topic** | Yes | "3D point cloud self-supervised learning", "offline RL for robotics" |
| **Scope** | Optional | Time range, venue filter, specific sub-questions |
| **Seed papers** | Optional | Papers the user already knows about |
| **Depth** | Optional | Quick overview (10-15 papers) / Standard (20-30) / Deep (40+) |

Default depth: **Standard (20-30 papers)**.

## Workflow

### Step 1: Scope the Survey

**ASK USER** to clarify scope:

1. "What's the core question you want answered?" (e.g., "Which 3D representations work best for robot manipulation?")
2. "Any papers you already know about?" (seeds help anchor the search)
3. "Time range?" (default: last 3 years)
4. "Any sub-topics you specifically want or don't want covered?"

Define:
- **Core question** — the survey's thesis
- **Boundary** — what's in vs. out of scope
- **Seed papers** — starting points (user-provided or from your knowledge)

### Step 2: Initial Exploration

Perform literature search via the canonical multi-source entry point:

```
/litian-academic-search "<TOPIC>" --sources all --k 12
```

For focused sub-topic queries, use targeted searches:
```
/litian-academic-search "<SUB_TOPIC>" --sources omnibox,s2,arxiv --k 8 --year 2023-
```

**From seed papers (if user provided):**

Use Semantic Scholar citation graph directly (see `paper-discovery-sources` for commands):
- Read each seed's references → find shared citations (convergence = important paper)
- Find successors of each seed → discover recent developments

#### 2b. Build initial paper list

Compile all discovered papers into a working list:

| # | Title | Year | Citations | Sources | Sub-topic | Read? |
|---|-------|------|-----------|---------|-----------|-------|
| 1 | ... | ... | ... | arxiv,s2,omnibox | ... | [ ] |

### Step 3: Present Initial Map & Ask for Direction

**ASK USER** — present what you found and ask for guidance:

```markdown
## Initial Landscape: <Topic>

I found ~N papers spanning these sub-topics:

### Sub-topics Identified
1. **<Sub-topic A>** (N papers) — <1-line description>
   Key papers: <top 2-3 by citations>

2. **<Sub-topic B>** (N papers) — <1-line description>
   Key papers: <top 2-3>

3. **<Sub-topic C>** (N papers) — <1-line description>
   Key papers: <top 2-3>

### Questions for you:
- Which sub-topics are most relevant to your work?
- Any sub-topics I should explore deeper or skip?
- Any specific papers you want me to read in detail?
- Should I look for more papers in any direction?
```

### Step 4: Deep Exploration (Iterative)

Based on user direction, go deeper into selected sub-topics.

**For each priority sub-topic:**

1. **Read key papers** via DeepXiv or PDF (see `paper-discovery-sources` for commands).

2. **Extract per-paper notes:**
   - Problem addressed
   - Method (1-2 sentences)
   - Key results (metrics, benchmarks)
   - Strengths / limitations
   - Relationship to other papers in the survey

3. **Follow citation chains** — if a paper references something important we haven't seen, add it

4. **Check for very recent work** (last 6 months):
   ```
   /litian-academic-search "<sub-topic>" --sources arxiv,web --k 10 --year 2026-
   ```

**After each sub-topic exploration, ASK USER:**

- "Here's what I found in <sub-topic>. Want me to go deeper here, or move to the next area?"
- "I noticed an interesting branch: <observation>. Want me to explore it?"
- "I think we have good coverage of <sub-topic>. Ready to move on?"

**Repeat Step 4 until user is satisfied with coverage.**

### Step 5: Synthesize & Write the Review

Produce a structured topic review document.

#### Review Structure

```markdown
# Topic Review: <Topic>

**Scope:** <what's covered>
**Period:** <time range>
**Papers reviewed:** N

## 1. Introduction & Motivation

<Why this field matters. What problem is being solved.>
<Core question this review addresses.>

## 2. Background & Key Concepts

<Shared foundations that most papers in this area build on.>
<Key terminology, benchmarks, evaluation protocols.>

| Term | Definition |
|------|-----------|
| ... | ... |

## 3. Taxonomy

<How the field breaks down into approaches/sub-topics.>

```
                        <Topic>
                       /       \
              <Approach A>    <Approach B>
              /     \              |
         <A.1>   <A.2>        <B.1>
```

## 4. Sub-topic Reviews

### 4.1 <Sub-topic A>

**Core idea:** <1-2 sentences>

| Paper | Year | Method | Key Result | Venue |
|-------|------|--------|-----------|-------|
| ... | ... | ... | ... | ... |

**Evolution:** <how methods progressed within this sub-topic>
**Current best:** <paper> achieves <metric> on <benchmark>
**Open problems:** <what's unsolved>

### 4.2 <Sub-topic B>
...

## 5. Cross-Cutting Analysis

### Comparison Table

| Method | Approach | Benchmark 1 | Benchmark 2 | Code | Year |
|--------|----------|-------------|-------------|------|------|
| ... | ... | ... | ... | ... | ... |

### Trends
- <Trend 1: e.g., "shift from X to Y">
- <Trend 2>

### Common Limitations
- <Limitation shared across approaches>

## 6. Frontier & Open Questions

- <What's unsolved?>
- <Where is the field heading?>
- <What would a breakthrough look like?>

## 7. Recommended Reading Order

For someone new to this field:
1. <paper> — <why start here>
2. <paper> — <what it adds>
...

For someone working on <specific sub-area>:
1. ...

## 8. Full Paper List

| # | Paper | Authors | Year | Venue | Code | Sub-topic |
|---|-------|---------|------|-------|------|-----------|
| 1 | [Title](https://arxiv.org/abs/...) | ... | ... | ... | [repo](url) | ... |
```

### Report Formatting Rules

**Every paper reference MUST include a clickable link.** Apply to ALL tables and inline mentions:

```markdown
| [Paper Title](https://arxiv.org/abs/XXXX.XXXXX) | Authors | 2025 | Venue | [code](https://github.com/...) |
```

- arXiv papers: link to `https://arxiv.org/abs/<ID>`
- Non-arXiv: link to Semantic Scholar `https://www.semanticscholar.org/paper/<S2_ID>` or DOI
- If code repo exists, always include it in a separate column
- Inline mentions: `[Author et al. (2025)](https://arxiv.org/abs/XXXX.XXXXX)`

### Step 6: Offer Next Steps

After presenting the review:

- "Want me to create skills for any of these papers? (`/create_skill_with_paper`)"
- "Want me to find related works for a specific paper? (`/paper_related_works`)"
- "Want me to explore any sub-topic further?"
- "Want me to save this review to a file?"

If user wants to save:
```bash
# Default save location
mkdir -p doc/surveys
# Save with date and topic slug
cp review.md doc/surveys/<YYYY-MM-DD>_<topic_slug>.md
```

## Exploration Strategies

| Strategy | When to Use |
|----------|------------|
| **Citation snowball** | Start from seed papers, follow references and citations |
| **Keyword search** | Broad initial sweep when no seeds available |
| **Venue scan** | Check top venues (NeurIPS, ICML, ICLR, CoRL, RSS) for topic |
| **Author trace** | Key author's recent publications often show field evolution |
| **Benchmark anchoring** | Find all papers evaluated on the same benchmark |

## Tips

- **Ask early, ask often** — user direction prevents wasted exploration
- **Convergence = importance** — if multiple papers cite the same work, it's foundational
- **Recency vs. citations** — balance well-cited classics with cutting-edge work
- **Don't over-read** — AlphaXiv overviews are sufficient for most papers; only read full PDFs for papers central to the user's interest
- **Track what you've read** — maintain the working paper list throughout to avoid re-fetching

## Error Handling

| Issue | Recovery |
|-------|----------|
| Topic too broad | Ask user to narrow; suggest 2-3 sub-scopes |
| Topic too niche | Broaden search terms; include adjacent fields |
| Few recent papers | Field may be mature; focus on established work + check if topic evolved under new name |
| Search returns few results | Try broader queries via litian-academic-search; add web source |
| User unsure about direction | Present 2-3 concrete options with tradeoffs |
