---
name: multi-platform-search
description: "Cross-platform information gathering from Xiaohongshu, Bilibili, Zhihu, and X/Twitter. Trigger when user wants to search, collect, or gather information across social platforms, says '全网搜索', '多平台搜索', '从各个平台搜', '搜集信息', 'search all platforms', '帮我搜一下', '调研一下社交媒体上的讨论', or mentions wanting opinions/discussions from Chinese social media and Twitter. Also trigger when user gives a topic and expects comprehensive coverage across platforms."
---

# Multi-Platform Social Media Search & Collection

Search and collect information from 4 platforms simultaneously: Xiaohongshu (小红书), Bilibili (B站), Zhihu (知乎), and X/Twitter.

## Prerequisites & Installation

This skill depends on several tools. Follow these steps to set up from scratch.

### 1. MediaCrawler (for Xiaohongshu + Bilibili)

```bash
# Clone
git clone --depth 1 https://github.com/NanmiCoder/MediaCrawler.git
cd MediaCrawler

# Python environment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Browser engine
playwright install chromium

# Config: set headless mode and disable CDP
# In config/base_config.py, change:
#   HEADLESS = True
#   ENABLE_CDP_MODE = False
#   SAVE_DATA_OPTION = "json"
#   LOGIN_TYPE = "cookie"

# If Bilibili uses channel="chrome", remove it:
# In media_platform/bilibili/core.py and media_platform/zhihu/core.py
# Remove all channel="chrome" parameters (use bundled chromium instead)
```

**Cookie setup**: Export cookies from your browser (using Cookie-Editor extension) for each platform, then paste them into `config/base_config.py` as `COOKIES = "key=val;key=val;..."`. The provided `crawl.sh` script handles this per-platform.

**crawl.sh helper script**: Create a shell script that:
- Accepts platform name (xhs/bili) and keywords as arguments
- Swaps the correct cookies into `config/base_config.py`
- Runs `python main.py --platform <name> --lt cookie --type search`

### 2. yt-dlp (for Bilibili audio extraction)

```bash
# Install in MediaCrawler's venv
source venv/bin/activate
pip install yt-dlp
```

Also requires **ffmpeg** on the system:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg
# or check: ffmpeg -version
```

### 3. Crawl4AI MCP Server (for Zhihu + X/Twitter)

```bash
# Clone
git clone --depth 1 https://github.com/sadiuysal/crawl4ai-mcp-server.git
cd crawl4ai-mcp-server

# Python environment
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

**Important**: The default MCP server ignores cookies passed via the `crawler` parameter. To enable cookie + delay support (required for X/Twitter), patch `crawler_agent/mcp_server.py`:

In both `_run_scrape()` and `_persist_scrape()`, replace the fixed `BrowserConfig(verbose=False)` with:
```python
browser_kwargs = {"verbose": False}
run_kwargs = {}
if args.crawler and isinstance(args.crawler, dict):
    if "cookies" in args.crawler:
        browser_kwargs["cookies"] = args.crawler["cookies"]
    if "headers" in args.crawler:
        browser_kwargs["headers"] = args.crawler["headers"]
    if "delay" in args.crawler:
        run_kwargs["delay_before_return_html"] = float(args.crawler["delay"])
    if "wait_until" in args.crawler:
        run_kwargs["wait_until"] = args.crawler["wait_until"]
browser_cfg = BrowserConfig(**browser_kwargs)
run_cfg = None
if run_kwargs:
    from crawl4ai.async_configs import CrawlerRunConfig
    run_cfg = CrawlerRunConfig(**run_kwargs)
```

**Suppress startup warnings** (breaks MCP stdio): Create `run_mcp_clean.py`:
```python
import warnings; warnings.filterwarnings("ignore")
import os; os.environ["PYTHONWARNINGS"] = "ignore"
from crawler_agent.mcp_server import main; main()
```

**Register with Claude Code**:
```bash
claude mcp add crawl4ai -s user \
  -e PYTHONWARNINGS=ignore \
  -- /path/to/crawl4ai-mcp-server/.venv/bin/python \
  /path/to/crawl4ai-mcp-server/run_mcp_clean.py
```

### 4. Brave Search MCP (for Zhihu + X/Twitter search)

```bash
claude mcp add brave-search -s user \
  -e BRAVE_API_KEY=<your-key> \
  -- npx -y @modelcontextprotocol/server-brave-search
```

Get a free API key at https://brave.com/search/api/

### 5. Data Directory Setup

```bash
# Create data directories on your data disk
DATA_BASE="/data1/$USER/social_crawler"  # adjust to your setup
mkdir -p $DATA_BASE/{xhs/json,bili/{json,audio},zhihu/crawl4ai,x/crawl4ai,transcripts}
```

### 6. Platform Cookies

Each platform needs cookies exported from your logged-in browser session:

| Platform | Required Cookies | How to Get |
|----------|-----------------|------------|
| **Xiaohongshu** | a1, webId, web_session, webBuild | Login on xiaohongshu.com → Cookie-Editor → Export JSON |
| **Bilibili** | SESSDATA, bili_jct, DedeUserID, buvid3 | Login on bilibili.com → Cookie-Editor → Export JSON |
| **X/Twitter** | auth_token, ct0, twid, kdt | Login on x.com → Cookie-Editor → Export JSON |
| **Zhihu** | Not needed | Uses Brave Search (public) + Crawl4AI (no login) |

Cookies expire periodically. Re-export when you get login errors.

---

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

Example: User says "世界模型" →
- XHS/Bili/Zhihu: "世界模型,world model"
- X/Twitter: "world model robotics"

### Step 2: Launch Searches in Parallel

Run all 4 platform searches simultaneously for maximum speed.

#### 2a. Xiaohongshu (小红书)

```bash
cd <MediaCrawler_path>
source venv/bin/activate
./crawl.sh xhs "<中文关键词>" <数量>
```

Data saves to: `<data_base>/xhs/json/`

#### 2b. Bilibili (B站)

```bash
./crawl.sh bili "<中文关键词>" <数量>
```

Data saves to: `<data_base>/bili/json/`

**Optional audio extraction**:
```bash
./bili_audio_extract.sh from_json <数量>
```

#### 2c. Zhihu (知乎)

**Search**: Brave Search MCP with `site:zhihu.com`
```
mcp__brave-search__brave_web_search: "site:zhihu.com <关键词>"
```

**Fetch full content**: Crawl4AI MCP
```
mcp__crawl4ai__scrape: url=<zhihu_url>, output_dir=<data_base>/zhihu/crawl4ai
```

#### 2d. X/Twitter

**Search**: Brave Search MCP with `site:x.com`
```
mcp__brave-search__brave_web_search: "site:x.com <english keywords>"
```

**Fetch full tweet**: Crawl4AI MCP with cookies and delay
```
mcp__crawl4ai__scrape:
  url=<tweet_url>
  output_dir=<data_base>/x/crawl4ai
  crawler={"cookies": [...], "delay": 5, "wait_until": "domcontentloaded"}
```

### Step 3: Summarize Results

After all searches complete:
1. Read collected data from each platform
2. Present a unified summary organized by theme (not by platform)
3. Highlight key insights, trending opinions, notable posts
4. Include links for follow-up

## Data Path Management

All data goes to the data disk, never the home directory:

```
<data_base>/
├── xhs/json/           ← Xiaohongshu posts + comments
├── bili/
│   ├── json/           ← Bilibili video info + comments
│   └── audio/          ← Extracted audio (MP3)
├── zhihu/crawl4ai/     ← Zhihu full articles (Markdown)
├── x/crawl4ai/         ← X/Twitter tweets (Markdown)
└── transcripts/        ← Audio transcriptions
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| MediaCrawler login failed | Cookie expired | Re-export from browser |
| X/Twitter returns login page | Cookie not passed or expired | Check Crawl4AI cookie patch; re-export cookies |
| Zhihu 403 error | Server IP blocked | Use Brave Search (works) instead of direct API |
| Bilibili "chrome not found" | Missing browser | Remove `channel="chrome"` from bilibili/core.py |
| Crawl4AI MCP "Failed to connect" | Startup warnings | Use `run_mcp_clean.py` wrapper |
