---
name: wuyin-gpt-image-2
description: 通过速创API (api.wuyinkeji.com) 调用 GPT-Image-2 文生图/图生图，输出最高 4K、支持中英文精准排版与多张参考图编辑。内置三个论文配图风格预设：「UniVLA 风格」(flat-but-soft pastel macaron)、「Physical Intelligence 风格」(retro-computing monospace + parchment 米白底)、「Fast-WAM 风格」(CVPR/ICLR 标准矢量图 + attention-mask 矩阵 + split layout)。Use this skill whenever the user wants to generate or edit an image via 速创API / 五音科技 / wuyinkeji / GPT-Image-2 / gpt image 2，or says "生成一张图"、"画一张"、"文生图"、"图生图"、"生成海报"、"AI 出图"、"用 GPT-Image-2 画"、"用速创API画"、"render an image with gpt-image-2"、"create a poster with text"、"UniVLA 风格"、"用 UniVLA 风格画"、"univla-style figure"、"Physical Intelligence 风格"、"PI 风格"、"π 风格"、"pi-zero 风格"、"physical-intelligence-style figure"、"retro-computing diagram"、"monospace paper figure"、"Fast-WAM 风格"、"fast-wam 风格"、"fast-wam-style figure"、"CVPR 风格图"、"ICLR 风格图"、"vector-graphics paper diagram"、"attention-mask 矩阵图"、"画一张论文配图"、"NeurIPS/CoRL/RSS/ICRA 风格图"、"科研架构图"、"方法图"、"academic paper figure"、"flat-but-soft illustration"、"pastel macaron diagram"。Also trigger when an image must contain rendered Chinese/English text (signs, posters, UI mocks) or when editing/upscaling a reference photo to 4K via GPT-Image-2. Do NOT trigger for video, audio, or non-wuyinkeji image providers (DALL·E, Midjourney, Stable Diffusion, NanoBanana, Grok Imagine).
---

# wuyin-gpt-image-2 — 速创API · GPT-Image-2 文生图

异步两步流程：`POST image_gpt` 提交 → `GET detail` 轮询 → 拿 PNG URL 下载。

## Setup（一次性）

API key 解析顺序：`--key` 参数 → `$WUYINKEJI_API_KEY` → `~/.config/wuyinkeji/api_key`。推荐写文件：

```bash
mkdir -p ~/.config/wuyinkeji
printf '%s' 'YOUR_KEY_HERE' > ~/.config/wuyinkeji/api_key
chmod 600 ~/.config/wuyinkeji/api_key
```

控制台密钥页：https://api.wuyinkeji.com/user/api-key (登录后)。文档主页 https://api.wuyinkeji.com/doc。

## 快速使用（推荐：用脚本）

```bash
SKILL=~/.claude/skills/wuyin-gpt-image-2

# 文生图
python3 $SKILL/generate.py "中世纪图书馆，书架上写着《Claude Code 手册》，电影级光影" \
    --size 16:9 -o /tmp/out.png

# 图生图 / 编辑参考图（支持多张 --ref）
python3 $SKILL/generate.py "把这张照片改成水彩画风格" \
    --ref https://example.com/photo.jpg -o /tmp/out.png

# 仅打印 URL，不下载
python3 $SKILL/generate.py "..." --no-download

# 续接已提交的任务（脚本意外退出后用 task_id 重新轮询）
python3 $SKILL/generate.py --task-id image_xxx -o /tmp/out.png
```

返回的图片是 PNG。Claude 可直接 `Read` 该 PNG 路径来查看生成结果（`Read` 支持图片）。

## API 完整说明

### 1. 提交任务（异步）

| 项目 | 值 |
|---|---|
| URL | `POST https://api.wuyinkeji.com/api/async/image_gpt` |
| Headers | `Authorization: <API_KEY>`、`Content-Type: application/json` |
| 计费 | 0.1 元/张（=10 点/张，不足 1 点按 1 点；实测 `data.count` 也可能返回 1） |
| QPS | 100/s（余额/点数/次数包用户无日上限） |

请求体字段：

| 字段 | 必填 | 类型 | 说明 |
|---|---|---|---|
| `prompt` | 是 | string | 提示词；建议中英文均可，对文字渲染友好 |
| `size` | 否 | string | 比例，默认 `auto`。可选：`auto, 1:1, 3:2, 2:3, 16:9, 9:16, 4:3, 3:4, 21:9, 9:21, 1:3, 3:1, 2:1, 1:2` |
| `urls` | 否 | string[] | 参考图 URL 数组；提供后即"图生图/编辑/超分"模式 |

成功响应：

```json
{
  "code": 200,
  "msg": "成功",
  "data": { "id": "image_532e60a6-...", "count": "1" },
  "exec_time": 0.28,
  "ip": "x.x.x.x"
}
```

`data.id` 即异步任务 ID，前缀 `image_`，喂给 detail 接口。

### 2. 查询结果（轮询）

| 项目 | 值 |
|---|---|
| URL | `GET https://api.wuyinkeji.com/api/async/detail?id=<task_id>` |
| Headers | `Authorization: <API_KEY>` |
| 计费 | 免费 |
| QPS | 40/s/用户 |

响应 `data.status`：

| 值 | 含义 | 操作 |
|---|---|---|
| 0 | 初始化（已入队） | 继续轮询 |
| 1 | 进行中 | 继续轮询 |
| 2 | 成功 | 读 `data.result[]` 拿 URL |
| 3 | 失败 | 读 `data.message` 报错原因 |

成功响应示例：

```json
{
  "code": 200,
  "msg": "成功",
  "data": {
    "task_id": "image_532e60a6-...",
    "request": { "prompt": "...", "size": "16:9", "count": "1" },
    "status": 2,
    "result": ["https://openpt1.wuyinkeji.com/xxxxxxxx.png"],
    "created_at": "2026-04-27 17:28:27",
    "updated_at": "2026-04-27 17:29:45",
    "count": "1",
    "unit": null,
    "message": ""
  },
  "exec_time": 0.15
}
```

**轮询节奏**：实测 1 张 16:9 ≈ 60–90 秒，轮询间隔 5s 比较合适。`generate.py` 默认 `--interval 5 --timeout 300`；若想更激进可调到 3s（QPS 完全够）。

### 3. 下载图片

`data.result[]` 是 CDN URL（`openpt1.wuyinkeji.com`），直接 `curl -L -o out.png <url>` 即可，无需鉴权。

## 模型能力速览（GPT-Image-2）

- **文字渲染**：中英文海报/UI/招牌都能精准排版（旧版 GPT-Image 的弱项已修）
- **真实感**：人物皮肤、毛发、肌理细节比 NanoBanana 更自然
- **编辑/超分**：通过 `urls` 喂参考图可做风格迁移、局部修改、4K 超分
- **场景理解**：长 prompt 友好，支持复杂构图 + 多主体关系描述

## 错误处理与坑

- **submit 返回 code != 200**：常见是 key 错（403/401），或 prompt 触发内容审核。直接读 `msg`。
- **status=3**：失败原因在 `data.message`；典型为参考图 URL 不可达、prompt 违规、瞬时后端故障——重试通常即恢复。
- **轮询超时**：网络抖动时偶尔 >5 分钟。脚本会打印 `task_id`，用 `--task-id` 续接，无需重新计费。
- **`count` 字段语义**：文档写"消耗点数"，但实测 1 张图返回 `"count":"1"` 而非 10。视为"图片张数"更稳，扣费以控制台为准。
- **size 选错**：传不在白名单的比例（如 `5:4`）会直接报错；要么用 `auto`，要么从上方表里选。
- **不要把 API key 写进 prompt 或参考图 URL**：detail 返回会回显 request 字段。

## 平台其它图片模型（不在本 skill 范围）

速创API 还聚合了 NanoBanana 系列、Grok Imagine。它们各自有独立的 endpoint（如 `/api/async/nano_banana`），参数和返回都不同。本 skill **只覆盖 GPT-Image-2**，需要其它模型时另查 https://api.wuyinkeji.com/type/3。

## 风格预设（Prompt Styles + 参考图）

存放在 `prompt_styles/` 目录，每个文件是一个可直接附加到 `prompt` 的风格说明块。**每个风格还附带一组真实参考图（`style_refs/<style>/`），自动作为 `urls` 喂给 GPT-Image-2 — 这是让风格命中率从 70% 拉到 95% 的关键**。

### 参考图机制（必读）

API 的 `urls` 字段只接受公网可达的 HTTP/HTTPS URL，**不支持本地文件直传**。脚本帮你处理：

- 本地参考图存放在 `style_refs/<style>/` 下
- 第一次用某个风格触发时，脚本会通过 `curl` 把图片匿名上传到 `catbox.moe`，把返回的 URL 写入 `style_refs/<style>/.urls.txt`
- 之后所有调用直接读缓存，**不会重复上传**（catbox 文件长期保留，URL 永久有效）
- 也可手动用 `--ref-local /path/to/img.png` 上传一次性参考图，或用 `--ref https://...` 直接传公网 URL

**触发对应风格时务必加上 `--style <style>`**，让脚本同时挂上 STYLE BLOCK 文字 + 参考图，效果最稳。

| 文件 | 风格名 | 何时使用 |
|---|---|---|
| `prompt_styles/univla.md` | **UniVLA 风格** | 沿用 UniVLA 论文配图视觉语言的 NeurIPS/CoRL/RSS/ICRA 方法图。Soft flat illustration、pastel macaron 配色、capsule 模块、italic 手写感标签、LaTeX 数学、minimalist 机械臂线稿、">>>>>" chevron 数据流、snowflake frozen 标记、纯白背景。触发词：「UniVLA 风格」「论文配图」「方法图」「架构图」「academic paper figure」「flat-but-soft」。 |
| `prompt_styles/physical_intelligence.md` | **Physical Intelligence 风格** | 沿用 Physical Intelligence (π / pi-zero) 论文图风格的 retro-computing 架构图与数据流图。Parchment 米白底、全 monospace 小写、powder-blue capsule 主干、sage-green action capsule、flat-top 梯形视觉编码器、real-photo 缩略图嵌入米色容器、纯黑细描边 + 黑色虚线 V 箭头、curly bracket 分组、严格正交网格布局。触发词：「Physical Intelligence 风格」「PI 风格」「π 风格」「pi-zero 风格」「retro-computing diagram」「monospace paper figure」「typewriter-style figure」。 |
| `prompt_styles/fast_wam.md` | **Fast-WAM 风格** | CVPR / ICLR 标准矢量学术图，crisp + professional + purely geometric。纯白背景、白底灰描边模块、语义色编码（pale sage 文本 / sky-blue 视觉 / mustard-yellow 动作）、标准 sans-serif + LaTeX 下标、symmetrical 梯形 encoder、rounded-rectangle transformer、squoval token、attention-mask 矩阵 grid（蓝/黄/白格 + 灰描边）、overlapping photo stack 表示视频、smooth yellow 曲线表示轨迹、左架构 ‖ 右矩阵 split layout。触发词：「Fast-WAM 风格」「fast-wam-style figure」「CVPR/ICLR 风格图」「vector-graphics paper diagram」「attention-mask 矩阵图」。 |

**使用方式（推荐）**：先用 1–3 句描述图要画什么（模块、token、数据流、stage），再附加 STYLE BLOCK 文字，**同时加 `--style <style>`** 让脚本自动挂上参考图：

```bash
STYLE=$(sed -n '/^<<<STYLE/,/^STYLE>>>/p' \
  ~/.claude/skills/wuyin-gpt-image-2/prompt_styles/univla.md \
  | sed '1d;$d')

python3 ~/.claude/skills/wuyin-gpt-image-2/generate.py \
  "Method overview of a vision-language-action policy. Top: instruction tokens (yellow) + observation thumbnails with light-blue rounded frames. Middle: a pill-shaped 'Main Processor Module' (lavender) takes Q from instructions and KV from vision. Right column (Stage 2, separated by dashed vertical divider): action quantization zone producing latent action tokens (coral). Bottom: minimalist line-art robot arm. Snowflake emoji on the frozen base model. $STYLE" \
  --style univla \
  --size 16:9 -o paper_figure.png
```

`--style <style>` 自动从 `style_refs/<style>/.urls.txt` 读取已缓存的 catbox URL（首次触发会自动上传）。可与 `--ref` / `--ref-local` 叠加使用。

> 想新增风格？(1) 在 `prompt_styles/` 下加一个 `<name>.md`，遵循 `<<<STYLE … STYLE>>>` 结构；(2) 在 `style_refs/<name>/` 下放参考图；(3) 把 `<name>` 加入 `generate.py` 的 `VALID_STYLES`；(4) 在上表登记。

## 文件清单

- `SKILL.md`（本文件）：触发说明 + 完整 API 文档 + 风格预设索引
- `generate.py`：stdlib-only 提交→轮询→下载脚本，带 `--task-id` 续接
- `prompt_styles/{univla,physical_intelligence,fast_wam}.md`：三种风格的 STYLE BLOCK 文字描述
- `style_refs/<style>/*.png`：每种风格的真实参考图（自动上传 catbox 并缓存 URL）
  - `univla/`: 2 张（UniVLA stage1+2 / action decoder）
  - `physical_intelligence/`: 5 张（π0 概览 / VLM+action expert / pre-train‖post-train / π0.5 数据面板 / Recap 闭环）
  - `fast_wam/`: 2 张（架构 + attention masks / 训练 vs 推理多种模式）
- `style_refs/<style>/.urls.txt`：catbox URL 缓存（首次 `--style <name>` 时生成；持久化）
