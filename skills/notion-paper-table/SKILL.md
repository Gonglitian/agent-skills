---
name: notion-paper-table
description: Create a structured literature survey database in Notion with paper metadata (title, arXiv link, venue, category, relevance). Use PROACTIVELY whenever the user wants to organize research papers, build a literature table, create a related-work database, or track surveyed papers in Notion. Also trigger on phrases like "paper table", "literature database", "把论文放到notion", "创建文献表格", "paper list to notion", "survey table", or any request to push paper references into Notion.
---

# Notion Paper Table

Create a well-structured literature survey database in Notion and populate it with paper entries extracted from local documents, markdown files, or user-provided lists.

## When to Use

- User wants to create a paper/literature database in Notion
- User has surveyed papers (in markdown, docs, or conversation) and wants them organized in Notion
- User says things like "put papers in Notion", "create a literature table", "论文表格", "文献数据库"

## Prerequisites

- Notion MCP tools must be available (`mcp__claude_ai_Notion__notion-create-database`, `mcp__claude_ai_Notion__notion-create-pages`, `mcp__claude_ai_Notion__notion-fetch`)
- A target Notion page URL or ID where the database should be created

## Workflow

### Step 1: Identify the Target Page

Ask the user for a Notion page URL if not already provided. Fetch the page to confirm it exists and get the page ID.

### Step 2: Gather Paper Data

Papers can come from multiple sources — check them all:

1. **Local files**: Scan the project for markdown files containing paper references (proposals, literature reviews, related work sections). Look for patterns like:
   - Tables with columns like "Method | Venue | ..."
   - Numbered reference lists with arXiv IDs
   - BibTeX entries
   - Any structured paper listing

2. **Conversation context**: Papers mentioned in the current conversation

3. **User-provided list**: Direct input from the user

For each paper, extract:
- **Paper name** (short name or full title)
- **Category** (research area / topic group)
- **Venue** (conference/journal + year, e.g., "CVPR 2025", "arXiv 2026")
- **Year** (publication year as number)
- **arXiv ID** (e.g., "2504.00420") — leave empty if not available
- **arXiv Link** (full URL like `https://arxiv.org/abs/2504.00420`) — set to null if no arXiv ID
- **One-liner** (brief description of what the paper does / why it matters)
- **Relevance** (how important it is to the project: Core / Reference / Background)

### Step 3: Determine Categories

Analyze all papers and group them into meaningful categories. Good categories are research-area-based, typically 4-8 groups. Assign each a distinct color from: `blue`, `green`, `purple`, `orange`, `pink`, `brown`, `red`, `yellow`, `gray`.

Examples of category schemes:
- For a robotics CL project: `CL for VLA`, `MoE for Manipulation`, `MoE + CL`, `Multi-Demonstrator`, `Benchmark`, `Base VLA`
- For an NLP project: `Language Models`, `Retrieval`, `Alignment`, `Evaluation`, `Datasets`
- For a CV project: `Detection`, `Segmentation`, `Generation`, `Self-Supervised`, `Benchmarks`

Categories should be tailored to the specific project's research landscape.

### Step 4: Create the Database

Use `mcp__claude_ai_Notion__notion-create-database` with this schema:

```sql
CREATE TABLE (
  "Paper" TITLE,
  "Category" SELECT(<categories with colors>),
  "Venue" RICH_TEXT,
  "Year" NUMBER,
  "arXiv ID" RICH_TEXT,
  "arXiv Link" URL,
  "One-liner" RICH_TEXT,
  "Relevance" SELECT('Core':red, 'Reference':blue, 'Background':gray)
)
```

Fill in the `<categories with colors>` based on Step 3 analysis.

Set parent to `{"page_id": "<target-page-id>"}`.

### Step 5: Populate with Papers

Use `mcp__claude_ai_Notion__notion-create-pages` to insert papers in batches. Notion API accepts up to 100 pages per call, so batch accordingly.

Each page goes under the data source ID returned from Step 4.

```json
{
  "parent": {"data_source_id": "<data-source-id>"},
  "pages": [
    {
      "properties": {
        "Paper": "Paper Name",
        "Category": "Category Name",
        "Venue": "CVPR 2025",
        "Year": 2025,
        "arXiv ID": "2504.00420",
        "arXiv Link": "https://arxiv.org/abs/2504.00420",
        "One-liner": "Brief description of the paper",
        "Relevance": "Core"
      }
    }
  ]
}
```

Important rules:
- `arXiv Link` must be a full URL or `null` (not empty string) — it's a URL type field
- `Year` must be a number (not string)
- `Category` and `Relevance` values must exactly match the options defined in Step 4
- Batch papers in groups of ~20 per API call to avoid timeouts
- If a paper has no arXiv ID, set `"arXiv ID": ""` and `"arXiv Link": null`

### Step 6: Report Results

Tell the user:
- How many papers were added
- Category breakdown (how many per category)
- Link to the Notion database
- Any papers that couldn't be processed (missing data, etc.)

## Relevance Guidelines

Assign relevance based on how central the paper is to the user's project:

| Relevance | Criteria |
|-----------|----------|
| **Core** | Directly competing methods, primary technical references, key benchmarks used |
| **Reference** | Related techniques, secondary references, complementary approaches |
| **Background** | Tangential work, general background, platform/tool papers |

## Tips for Extracting Papers from Markdown

When scanning markdown files for paper references:

- Look for `###` sections that group papers by topic — these map to categories
- Tables with `|` delimiters often contain structured paper data
- Numbered lists under "References" sections contain citation data
- arXiv IDs follow patterns like `arXiv:XXXX.XXXXX` or `arXiv XXXX.XXXXX`
- Venue info is often in parentheses: `(CVPR 2025)`, `(ICLR'26)`
- Chinese text may describe papers — extract the English paper name if present
