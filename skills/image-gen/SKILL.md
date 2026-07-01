---
name: image-gen
description: 统一绘图 skill——文生图 / 图生图 / 多图合成 / 编辑 / 论文与科普配图。两个后端由用户指定：nano(默认，Google Gemini "Nano Banana"，快 3-10s、便宜、原生中英文文字渲染、可 1K/2K/4K，含 lite/nb2/pro 三档) 或 gpt(速创API GPT-Image-2，真实感/精细文字更强，异步稍慢 60-90s)。四个专用风格预设也由用户按名指定，两后端通用：UniVLA(pastel macaron 论文方法图)、Physical Intelligence(π/pi-zero retro-computing monospace 图)、Fast-WAM(CVPR/ICLR 矢量图+attention-mask 矩阵)、蓝皮书 BlueBook(蓝白科技科普/咨询长图)。Use this skill for ANY image generation or editing request. 触发词：「画一张」「生成一张图」「出张图」「文生图」「图生图」「改这张图」「编辑图片」「把这张图改成…」「合成/融合这几张图」「做张海报」「配图」「方法图」「架构图」「用 nano/gemini 画」「用 GPT 画」「generate/edit/compose an image」「make a poster」「render a figure」，以及风格名「UniVLA 风格」「Physical Intelligence / PI / π 风格」「Fast-WAM 风格」「蓝皮书 / BlueBook 风格」。默认走 nano；用户点名「用 GPT」时走 gpt。
---

# image-gen — 统一绘图（Nano Banana + GPT-Image-2，双后端）

一个脚本 `generate.py`，两个后端由 `--backend` 选（用户指定），四个风格由 `--style` 选（两后端通用）。

## 后端（用户指定；默认 nano）

| backend | 引擎 | 速度 | 计费 | 强项 |
|---|---|---|---|---|
| `nano`（默认） | 官方 Gemini "Nano Banana" | ~3-10s，同步 | $0.034–0.134/张 | 快、便宜、宽高比/分辨率可控、参考图可直接用本地文件 |
| `gpt` | 速创API GPT-Image-2 | ~60-90s，异步轮询 | ~0.1 元/张 | 真实感（皮肤/毛发）、精细/长文字排版、编辑超分 |

**路由规则**：用户没点名 → `nano`；用户说“用 GPT / GPT-Image / 速创”→ `--backend gpt`。

## nano 三档模型（`--model`，默认 nb2）

| alias | model id | 单张(1K) | 说明 |
|---|---|---|---|
| `lite` | gemini-3.1-flash-lite-image | **$0.034**（~3s，仅1K） | 最快最省，批量 |
| `nb2`(默认) | gemini-3.1-flash-image | **$0.067**（1K/2K/4K） | pro 级质量@flash 速度，日常首选 |
| `pro` | gemini-3-pro-image | **$0.134**（2K 同价；4K $0.24） | 复杂构图、精准/长文字、4K |

实测 1 张 = 1120 image tokens。脚本会打印 尺寸/KB/耗时/tokens/单张与总成本。

## 快速使用

```bash
SKILL=~/.claude/skills/image-gen

# ── nano（默认）───────────────────────────────
python3 $SKILL/generate.py "赛博朋克东京雨夜，霓虹倒影" --aspect 16:9 -o /tmp/a.jpg
python3 $SKILL/generate.py "白底产品图，一根香蕉" --model lite --aspect 1:1 -o /tmp/b.jpg
python3 $SKILL/generate.py "把它改成夜晚霓虹，保留主体" --ref /tmp/a.jpg -o /tmp/a2.jpg   # 图生图/编辑
python3 $SKILL/generate.py "把这两张合成一张" --ref x.jpg --ref y.jpg -o /tmp/merge.jpg    # 多图合成
python3 $SKILL/generate.py "会议海报，标题 'Nano Banana Day'" --model pro --aspect 9:16 --res 2K -o /tmp/p.jpg
python3 $SKILL/generate.py "logo 创意" -n 3 -o /tmp/logo.jpg                              # N 张变体

# ── gpt（用户点名时）──────────────────────────
python3 $SKILL/generate.py "写实人像，胸牌上写 'HELLO'，柔光" --backend gpt --aspect 3:4 -o /tmp/g.png
python3 $SKILL/generate.py --backend gpt --task-id image_xxx -o /tmp/g.png                # 续接(不重复计费)

# ── 风格预设（两后端通用，--style 自动挂 STYLE 文字块 + 参考图）──
python3 $SKILL/generate.py "VLA 策略方法总览：顶部指令 token，中间 pill 主处理器，右侧 latent action token，底部机械臂" \
  --style univla --aspect 16:9 -o /tmp/fig.jpg                       # nano + 风格（本地参考图直挂）
python3 $SKILL/generate.py "用一张图讲清楚：世界模型为什么会坍塌？" \
  --backend gpt --style bluebook --aspect 3:4 -o /tmp/blue.png       # gpt + 蓝皮书长图
```

生成图 Claude 可直接 `Read` 查看。

## 风格预设（`--style`，两后端通用）

`--style X` 会自动：① 从 `prompt_styles/X.md` 抽取 `<<<STYLE…STYLE>>>` 文字块拼到 prompt 末尾；② 挂上 `style_refs/X/` 参考图（nano 用本地文件直挂；gpt 上传 catbox 并缓存 `.urls.txt`，不重复上传）。你只需在 prompt 里用 1–3 句描述图要画什么。

| style | 用途 | 触发词 |
|---|---|---|
| `univla` | NeurIPS/CoRL/RSS/ICRA 方法图：soft flat、pastel macaron、capsule 模块、italic 标签、LaTeX、机械臂线稿、">>>>>" 数据流、雪花 frozen | 「UniVLA 风格」「论文配图」「方法图」「架构图」 |
| `physical_intelligence` | π/pi-zero retro-computing：parchment 米白底、全 monospace、powder-blue/sage capsule、梯形编码器、黑虚线 V 箭头、正交网格 | 「Physical Intelligence / PI / π / pi-zero 风格」「monospace paper figure」 |
| `fast_wam` | CVPR/ICLR 矢量图：白底灰描边、语义色、梯形 encoder、attention-mask 矩阵 grid、左架构‖右矩阵 split | 「Fast-WAM 风格」「vector paper diagram」「attention-mask 矩阵图」 |
| `bluebook` | 中文科普/咨询长图（非论文图）：蓝白主色、疑问句大标题、四段式拆解、圆角编号卡片、扁平图标、高信息密度，默认竖版 `3:4` | 「蓝皮书 / BlueBook 风格」「科普长图」「知识海报」「用一张图讲清楚 X」 |

新增风格：`prompt_styles/<name>.md`(含 `<<<STYLE…STYLE>>>`) + 可选 `style_refs/<name>/` 参考图 + 加入 `VALID_STYLES`。参考图缺失时自动降级为纯文字（命中率 ~70%，补参考图可拉到 ~95%）。

## 参数
- `--backend nano|gpt`（默认 nano）
- `--model lite|nb2|pro`（nano）
- `--style univla|physical_intelligence|fast_wam|bluebook`
- `--ref PATH_OR_URL`（可重复）：参考图。nano 本地/URL 均直接内联；gpt 本地会自动上传 catbox
- `--aspect`：`1:1 16:9 9:16 4:3 3:4 21:9 …`（gpt 白名单同旧版；nano 更自由）
- `--res 1K|2K|4K`（nano；2K/4K 仅 nb2 & pro；lite 固定 1K）
- `-n N`（nano 出 N 张变体）
- gpt 专属：`--task-id`（续接）`--interval`(默认5s) `--timeout`(默认300s) `--no-download`
- `--key`、`-o`

## Key 设置
- nano：`--key` → `$GEMINI_API_KEY` → `$GOOGLE_API_KEY` → `~/.config/gemini/api_key`（已配）。控制台 https://aistudio.google.com/apikey（设 Spend Cap 封顶 / rotate）
- gpt：`--key` → `$WUYINKEJI_API_KEY` → `~/.config/wuyinkeji/api_key`（已配）。控制台 https://api.wuyinkeji.com/user/api-key

## ⚠️ Agent 调用纪律
- 脚本**同步阻塞**：nano lite ~3s / nb2 ~10s；**gpt ~60-90s（偶尔 >5min）**。多张/gpt 放**一个**前台 Bash 调用并把工具 `timeout` 设大（如 `600000`）。别用后台+结束回合（会变孤儿丢图）。
- gpt 意外断掉不丢图：日志里有 `task_id`，用 `--backend gpt --task-id image_xxx` 续接（不重复计费）。
- gpt 结果 CDN（scapi.net）对默认 UA 返 403，脚本已改用 `curl` 下载（失败回退 UA）。
- nano 官方图默认 **JPEG**、每张嵌不可见 **SynthID 水印**（不可关）；gpt 返回 PNG。
- **批量论文图优先 gpt + `batch.py`**（并行提交→统一轮询，总耗时≈最慢一张）：
  ```bash
  python3 $SKILL/batch.py --backend gpt --style fast_wam --aspect 16:9 \
    --job fig1.png=prompt1.txt --job fig2.png=prompt2.txt --resume fig3.png=image_xxx
  ```
