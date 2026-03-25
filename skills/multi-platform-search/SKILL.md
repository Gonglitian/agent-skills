---
name: multi-platform-search
description: "Cross-platform information gathering from Xiaohongshu, Bilibili, Zhihu, and X/Twitter. Trigger when user wants to search, collect, or gather information across social platforms, says '全网搜索', '多平台搜索', '从各个平台搜', '搜集信息', 'search all platforms', '帮我搜一下', '调研一下社交媒体上的讨论', or mentions wanting opinions/discussions from Chinese social media and Twitter. Also trigger when user gives a topic and expects comprehensive coverage across platforms."
---

# Multi-Platform Social Media Search & Collection

Search and collect information from 4 platforms simultaneously: Xiaohongshu (小红书), Bilibili (B站), Zhihu (知乎), and X/Twitter.

## When to Use

- User asks to "search everywhere" or "全网搜索" on a topic
- User wants to see what people are discussing about a topic across platforms
- User mentions collecting social media opinions, trends, or discussions
- User gives a keyword and expects multi-platform coverage

## Platform Capabilities

| Platform | Tool | Search | Content | Speed |
|----------|------|--------|---------|-------|
| Xiaohongshu | MediaCrawler | Batch keyword search | Text + comments + engagement | ~1.5s/post |
| Bilibili | MediaCrawler + yt-dlp | Batch keyword search | Text + comments + audio extraction | ~2s/post |
| Zhihu | Brave Search + Crawl4AI | `site:zhihu.com` search | Full article text (Markdown) | ~3s/page |
| X/Twitter | Brave Search + Crawl4AI | `site:x.com` search | Full tweet + replies (needs Cookie) | ~6.2s/post |

## Execution Steps

### Step 1: Prepare Keywords

Take the user's topic and prepare platform-appropriate keywords:
- **Chinese platforms** (小红书, B站, 知乎): Use Chinese keywords
- **X/Twitter**: Translate to English keywords
- If the topic is already bilingual, use both

Example: User says "世界模型" →
- XHS/Bili/Zhihu: "世界模型,world model"
- X/Twitter: "world model robotics"

### Step 2: Launch Searches in Parallel

Run all 4 platform searches simultaneously for maximum speed.

#### 2a. Xiaohongshu (小红书)

```bash
cd /home/vla-reasoning/proj/research_tracker/social_tools/MediaCrawler
source venv/bin/activate
./crawl.sh xhs "<中文关键词>" <数量>
```

Data saves to: `/data1/vla-reasoning/social_crawler/xhs/json/`
- `search_contents_YYYY-MM-DD.json` — post content + engagement metrics
- `search_comments_YYYY-MM-DD.json` — comments

#### 2b. Bilibili (B站)

```bash
cd /home/vla-reasoning/proj/research_tracker/social_tools/MediaCrawler
source venv/bin/activate
./crawl.sh bili "<中文关键词>" <数量>
```

Data saves to: `/data1/vla-reasoning/social_crawler/bili/json/`

**Optional: Extract audio from videos**
```bash
./bili_audio_extract.sh from_json <数量>
```
Audio saves to: `/data1/vla-reasoning/social_crawler/bili/audio/`

#### 2c. Zhihu (知乎)

Zhihu blocks server IP for direct API access. Use two-step approach:

**Search**: Use Brave Search MCP with `site:zhihu.com`
```
mcp__brave-search__brave_web_search: "site:zhihu.com <关键词>"
```

**Fetch full content**: Use Crawl4AI MCP to scrape each URL
```
mcp__crawl4ai__scrape: url=<zhihu_url>, output_dir=/data1/vla-reasoning/social_crawler/zhihu/crawl4ai
```

Data saves to: `/data1/vla-reasoning/social_crawler/zhihu/crawl4ai/`

#### 2d. X/Twitter

**Search**: Use Brave Search MCP with `site:x.com`
```
mcp__brave-search__brave_web_search: "site:x.com <english keywords>"
```

**Fetch full tweet**: Use Crawl4AI MCP with cookies and delay for JS rendering
```
mcp__crawl4ai__scrape:
  url=<tweet_url>
  output_dir=/data1/vla-reasoning/social_crawler/x/crawl4ai
  crawler={"cookies": [
    {"name": "auth_token", "value": "883c4b2927acc6599bedcc2fef7dc57d34463080", "domain": ".x.com", "path": "/", "secure": true, "httpOnly": true},
    {"name": "ct0", "value": "1d9c3b00442989430d4efee6e26e642c828dba1031efae1ced0e4b0ee9fd22cb51245041e88d921b78b1276bc38667dc45821ae8c70741dfdd1aed7d9f06a39fdc0c566d6a9bcb4860525819d7419207", "domain": ".x.com", "path": "/", "secure": true},
    {"name": "twid", "value": "u%3D1874611787418779648", "domain": ".x.com", "path": "/", "secure": true},
    {"name": "kdt", "value": "Mn5U67CWPzCq6mX1B05qXQLiInODN17FVJrZ77Dc", "domain": ".x.com", "path": "/", "secure": true},
    {"name": "lang", "value": "en", "domain": ".x.com", "path": "/"}
  ], "delay": 5, "wait_until": "domcontentloaded"}
```

Data saves to: `/data1/vla-reasoning/social_crawler/x/crawl4ai/`

### Step 3: Collect and Summarize Results

After all searches complete, summarize findings:

1. Read collected data from each platform
2. Present a unified summary organized by theme (not by platform)
3. Highlight key insights, trending opinions, notable posts
4. Include links for the user to follow up

### Step 4: Optional Audio Transcription

If Bilibili videos were collected and user wants transcripts:
```bash
conda run -n whisper python /home/vla-reasoning/proj/research_tracker/transcribe.py \
  /data1/vla-reasoning/social_crawler/bili/audio/ \
  --language zh --gpus 0,1,2,3,4 \
  --context "<topic-specific terms>" \
  --output-dir /data1/vla-reasoning/social_crawler/transcripts/batch
```

## Data Path Management

All data goes to the data disk, never the home directory:

```
/data1/vla-reasoning/social_crawler/
├── xhs/json/           ← 小红书 posts + comments
├── bili/
│   ├── json/           ← B站 video info + comments
│   └── audio/          ← B站 extracted audio (MP3)
├── zhihu/crawl4ai/     ← 知乎 full articles (Markdown)
├── x/crawl4ai/         ← X/Twitter tweets (Markdown)
└── transcripts/        ← Audio transcriptions
    ├── batch/          ← Batch transcription results
    └── models/         ← Model symlinks
```

## Important Notes

- **MediaCrawler requires cookies** — XHS and Bilibili cookies are pre-configured in `crawl.sh`
- **X/Twitter cookies expire** — if Crawl4AI returns login page, ask user to export fresh cookies
- **Zhihu has strict anti-crawl** — only Brave Search + Crawl4AI works from this server
- **Run XHS and Bilibili searches sequentially** (they share config file), but run Zhihu and X in parallel via MCP
- **Chinese output** — summarize in Chinese with English technical terms preserved
