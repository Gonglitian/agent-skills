# MediaCrawler 安装与配置指南

MediaCrawler 是社交平台爬取工具，支持小红书、B站等平台的内容搜索和采集。

## 安装步骤

### 1. 克隆仓库

```bash
git clone --depth 1 https://github.com/NanmiCoder/MediaCrawler.git
cd MediaCrawler
```

### 2. 创建 Python 环境

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 安装浏览器引擎

```bash
playwright install chromium
```

### 4. 配置文件修改

编辑 `config/base_config.py`，设置以下参数：

```python
HEADLESS = True              # 无头模式，不弹浏览器窗口
ENABLE_CDP_MODE = False      # 禁用 CDP 模式
SAVE_DATA_OPTION = "json"    # 输出 JSON 格式
LOGIN_TYPE = "cookie"        # 使用 cookie 登录
```

### 5. 修复 Bilibili/知乎 的 channel 问题

如果 Bilibili 或知乎爬取报错 "chrome not found"，需要移除 `channel="chrome"` 参数：

```bash
# 在以下文件中搜索并移除 channel="chrome"
# media_platform/bilibili/core.py
# media_platform/zhihu/core.py
grep -rn 'channel="chrome"' media_platform/
# 然后编辑这些文件，删除 channel="chrome" 参数
```

### 6. 安装可选依赖

```bash
# B站音频提取（可选）
pip install yt-dlp

# 系统依赖
sudo apt install ffmpeg  # Ubuntu/Debian
```

---

## Cookie 配置

### 为什么需要 Cookie

小红书、B站等平台需要登录态才能搜索。MediaCrawler 通过 Cookie 模拟已登录状态。

### 如何获取 Cookie

1. 在浏览器中登录目标平台（小红书/B站）
2. 安装浏览器扩展 **Cookie-Editor**（Chrome/Firefox 都有）
3. 打开 Cookie-Editor，点击 "Export" → "Header String"
4. 复制得到的字符串

### Cookie 配置方式

**方式一：直接配置**

编辑 `config/base_config.py`：
```python
# 小红书 cookie
XHS_COOKIES = "a1=xxx;webId=xxx;web_session=xxx;webBuild=xxx"

# B站 cookie
BILI_COOKIES = "SESSDATA=xxx;bili_jct=xxx;DedeUserID=xxx;buvid3=xxx"
```

**方式二：使用 crawl.sh 脚本**

创建 `crawl.sh`：
```bash
#!/bin/bash
PLATFORM=$1
KEYWORDS=$2
COUNT=${3:-20}

# 根据平台切换 cookie
case $PLATFORM in
  xhs)
    export COOKIES="<你的小红书cookie>"
    ;;
  bili)
    export COOKIES="<你的B站cookie>"
    ;;
esac

python main.py --platform $PLATFORM --lt cookie --type search --keywords "$KEYWORDS" --count $COUNT
```

```bash
chmod +x crawl.sh
```

### 各平台所需的 Cookie 字段

| 平台 | 必需 Cookie 字段 | 有效期 |
|------|-----------------|--------|
| 小红书 | a1, webId, web_session, webBuild | ~7天 |
| B站 | SESSDATA, bili_jct, DedeUserID, buvid3 | ~30天 |

Cookie 会过期，遇到登录错误时需要重新导出。

---

## 使用方法

### 小红书搜索

```bash
cd <MediaCrawler_path>
source venv/bin/activate
python main.py --platform xhs --lt cookie --type search --keywords "世界模型,机器人" --count 20
```

### B站搜索

```bash
python main.py --platform bili --lt cookie --type search --keywords "世界模型,具身智能" --count 20
```

### 数据输出

搜索结果默认保存在 `data/` 目录下的 JSON 文件中。

结构示例：
```json
{
  "note_id": "...",
  "title": "...",
  "desc": "...",
  "liked_count": 123,
  "comment_count": 45,
  "user": {"nickname": "..."},
  "note_url": "https://www.xiaohongshu.com/explore/..."
}
```

---

## 数据目录建议

建议将数据放在数据盘而非 home 目录：

```bash
DATA_BASE="/data1/$USER/social_crawler"
mkdir -p $DATA_BASE/{xhs/json,bili/{json,audio},transcripts}
```

然后在 `config/base_config.py` 中配置输出路径。

---

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| "请先登录" | Cookie 过期或未配置 | 重新导出 Cookie |
| "chrome not found" | playwright 未安装 chromium | `playwright install chromium` |
| 搜索无结果 | 关键词不匹配或平台限制 | 换关键词；检查是否被限流 |
| JSON 解析错误 | 平台返回 HTML 而非 API 数据 | 检查 Cookie 是否有效 |
| 连接超时 | 网络问题或平台封 IP | 等待后重试；考虑代理 |

---

## 验证安装

```bash
cd <MediaCrawler_path>
source venv/bin/activate

# 检查依赖
python -c "import playwright; print('playwright OK')"
python -c "import httpx; print('httpx OK')"

# 测试搜索（需要有效 Cookie）
python main.py --platform xhs --lt cookie --type search --keywords "测试" --count 1
```
