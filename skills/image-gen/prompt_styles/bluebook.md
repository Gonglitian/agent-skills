# Style preset · 蓝皮书 BlueBook 风格 (蓝白科技咨询信息图 / AI 科普知识海报)

A reusable prompt block for generating **蓝皮书 (BlueBook) 风格**的知识科普信息图：融合**科技知识科普信息图（Infographic）+ 企业培训 PPT 质感 + 麦肯锡/贝恩式咨询报告的严谨气质 + AI 论文可视化语言**。定位专业理性、偏教育科普，兼具技术白皮书可视化和公众号长图的传播性。**蓝白主色调（深蓝 #1E40AF 主色 + 浅蓝辅 + 白底）、粗黑体大字号疑问句标题、四段式知识拆解（问题→原因→机制→方案）、圆角卡片化模块、扁平 Office 线性图标、论文式流程图/散点图/"正常 VS 坍塌"对比、高信息密度**。Paste into your `prompt` (usually after a one-line description of what the infographic explains), or feed wholesale when you want the look itself.

## When to use

Trigger on user phrases like：
- "蓝皮书风格"、"BlueBook 风格"、"蓝皮书"、"用蓝皮书风格画"、"bluebook-style infographic"
- "蓝白科技风"、"咨询报告风"、"麦肯锡风格信息图"、"企业培训 PPT 风"、"白皮书可视化"
- "AI 科普长图"、"科技信息图"、"知识海报"、"卡片式信息图"、"数据解释型信息图"、"高信息密度知识海报"
- "把这个概念做成科普长图"、"用一张图讲清楚 XXX"、"做一张 AI 技术科普图"（Transformer / 世界模型 / RL / Diffusion / Agent 等）
- 与本 skill 另外三个**论文配图**风格的判别（很重要）：
  - **UniVLA / Physical Intelligence / Fast-WAM** = 投顶会的**论文方法图/架构图**，一张图就是一个 figure，英文标签、学术读者。
  - **蓝皮书 BlueBook** = 面向**大众/学员的科普长图与咨询报告信息图**，粗黑体大标题（**默认英文**，除非用户明确要求中文）、四段式知识拆解、卡片化、可直接转发学习。**不是论文 figure，是知识海报。**

## How to use

1. 用 2–4 句话描述这张图要**讲清楚什么概念**：主题是什么、四段（问题/原因/机制/方案）各讲什么、需要哪些示意图（流程图 / 散点聚类 / 正常 VS 坍塌对比）。**把要渲染的标题与卡片小标题用引号写出来**（**默认用英文**；GPT-Image-2 文字排版服从度高）。
2. Append the **STYLE BLOCK** below verbatim。
3. 推荐尺寸：竖版长图 `3:4` / `2:3`（标准科普图）；超长滚动海报 `9:16` / `1:2` / `1:3`；单概念横版（当 PPT 单页用）`16:9` / `4:3`。**这是长图/竖图风格，默认用 `3:4` 或 `2:3`，不要用 `auto`。**

```bash
STYLE=$(sed -n '/^<<<STYLE/,/^STYLE>>>/p' \
  ~/.claude/skills/wuyin-gpt-image-2/prompt_styles/bluebook.md \
  | sed '1d;$d')

python3 ~/.claude/skills/wuyin-gpt-image-2/generate.py \
  "竖版科普信息图，主题大标题（粗黑体疑问句，英文）'Why Do World Models Collapse?'。四段式知识拆解卡片，从上到下：① 卡片标题 'Problem' 灯泡图标 + 一句话现象；② 卡片 'Cause'；③ 卡片 'Mechanism' 含一张潜在空间散点图（左侧 normal 聚类紧凑、右侧 collapsed 成一团的 Normal VS Collapsed 对比图）+ 流程图箭头；④ 卡片 'Solution' 盾牌图标。底部 'Summary' 星星图标卡片。所有渲染文字用英文。$STYLE" \
  --style bluebook \
  --size 3:4 -o bluebook_demo.png
```

`--style bluebook` 会自动挂上 `style_refs/bluebook/` 里的参考图（首次触发自动上传 catbox 并缓存）。Or just inline-paste the STYLE BLOCK section into your prompt string.

## STYLE BLOCK (paste verbatim)

<<<STYLE
Render in **BlueBook style (蓝皮书)** — a high-information-density **science-popularization infographic / knowledge poster** that fuses (a) a tech-explainer infographic, (b) the polished texture of a corporate training slide deck, (c) the rigorous, trustworthy gravitas of a McKinsey / Bain consulting report or a technical white-paper, and (d) the visual vocabulary of machine-learning paper figures. Tone: professional, rational, educational, authoritative — built to be forwarded and studied like a "paper精读摘要". This is NOT a poster with one big image and few words; it is "small diagrams + lots of structured knowledge", aiming to teach one complete concept in a single image.

COLOR PALETTE — **blue-and-white scheme**, low-saturation, business-like and trustworthy, academic.
- **Deep blue (~#1E40AF)** is the primary color: main title bar, section headers, key strokes, emphasis.
- Light/sky blue (~#DBEAFE / #93C5FD) as secondary: card header tints, sub-panels, connectors.
- **White / very light grey (#FFFFFF / #F8FAFC)** as the base background — clean, airy, generous.
- Strict semantic accent colors, used sparingly: **red (~#DC2626) for risk / warning / the WRONG or collapsed case**, **green (~#16A34A) for the correct solution / the RIGHT case**, **amber-yellow (~#F59E0B) for tips / notes / highlights**. Everything else stays blue-white and low-saturation. No neon, no heavy gradients.

TEXT LANGUAGE — **default to ENGLISH** (concise, technical-figure English); use another language ONLY when the user explicitly asks the image to contain it.
TYPOGRAPHY — **heavy bold sans-serif**, large size, high contrast (clean modern grotesk, e.g. Inter / Helvetica Now / Söhne Bold).
- **Main title: big, bold, high-contrast, usually phrased as a QUESTION** for shareability (e.g. "Why Do World Models Collapse?", "What Makes Transformers So Strong?") — deep-blue or near-black on white, often with a thin blue underline or a deep-blue title ribbon.
- Card sub-titles: medium bold sans-serif, deep blue.
- Body text: clean regular-weight sans-serif, dark grey, short scannable phrases — NOT long paragraphs.
- Numbers / labels can use a clean sans-serif; keep everything crisp and legible on a phone screen.

LAYOUT — **"四段式知识拆解" (four-act knowledge breakdown)**, the classic consulting frame: **问题 → 原因 → 机制 → 方案 (Problem → Cause → Analysis/Mechanism → Solution)**, progressing top-to-bottom, each act layering on the last. A deep-blue title block sits at the very top. Below it, content is organized as **card-based modules (卡片化)** stacked in a clear reading order, well suited to vertical phone scrolling.

CARDS — each card is a **rounded-rectangle panel** with a thin light-blue/grey border (and optional very soft shadow), containing: a **circled number or step badge (①②③④ / 01 02 03)**, a **bold sub-title**, a small **diagram/icon**, and a short text explanation. Cards are evenly aligned to a grid, easy to scan, never crowded into mush despite the high density.

DIAGRAM LANGUAGE — borrow the most common ML-paper visualizations, drawn flat and clean:
- **Flowcharts** with boxes and **arrow connectors** (deep-blue thin arrows with simple triangular heads).
- **Scatter plots** to depict clustering / distribution / latent space (small dots, optionally color-grouped clusters), used to make abstract ML ideas concrete.
- **"正常 VS 坍塌" (normal VS collapsed) comparison diagrams**: a side-by-side contrast — e.g. a healthy spread-out/tight cluster in **green** on the left vs a degenerate/collapsed blob in **red** on the right, with a clear "VS" or divider. This contrast motif is a signature element.
- Simple bar/line micro-charts where useful. All plots are minimalist, flat, axis-light, captioned with short Chinese labels.

ICONS — **flat design, linear, Office-style** (vibe of Fluent Icons / IconPark / Font Awesome), two-tone deep-blue + light-blue, never skeuomorphic or 3D. Conventional mapping:
- **Lightbulb 💡 = explanation / insight**, placed on the 原因/机制 cards.
- **Warning triangle ⚠ = risk / pitfall**, in red, on warning callouts.
- **Shield 🛡 = solution / defense**, in green, on the 解决方案 card.
- **Star ★ = summary / takeaway**, on the closing summary card.
- Other flat icons (gear, magnifier, brain, chip, document, arrows) as needed, all in the same flat linear blue style.

INFORMATION DENSITY — **high**. Pack a complete, self-contained explanation into one image: several cards, multiple small diagrams, structured labels, numbered steps. It should read like a condensed lecture / paper-summary slide — dense but ruthlessly organized, scannable, and phone-friendly. Small diagrams + lots of structured knowledge, not a sparse poster.

OVERALL VIBE — 蓝皮书 BlueBook: blue-white tech-consulting infographic, McKinsey/Bain report rigor + white-paper visualization + AI-paper diagram language + WeChat-长图 shareability. Deep-blue #1E40AF primary on clean white, heavy-bold sans-serif question-style headline (English by default), four-act 问题→原因→机制→方案 breakdown, numbered rounded cards, flat Office-style linear icons (lightbulb/warning-triangle/shield/star), flowcharts + scatter/latent-space plots + green-vs-red "正常 VS 坍塌" comparisons, semantic red/green/amber accents, high information density, professional, educational, trustworthy, designed to be forwarded and studied.
STYLE>>>

## Tips

- **必须把标题与卡片小标题用引号写进描述里**（例：主标题 "Why Do World Models Collapse?"、卡片小标题 "Problem / Cause / Mechanism / Solution"），GPT-Image-2 才会精准排版文字；只给风格块不给文字，会出空卡片。**默认所有渲染文字用英文**（GPT-Image-2 英文排版更稳、效果更好）；仅当用户明确要求图里包含中文时才用中文。
- 想要"四段式"明确：在描述里逐卡列出 ①②③④ 各讲什么，并点名要哪种示意图（"③ 机制卡里放一张潜在空间散点图 + 正常 VS 坍塌对比"）。模型对结构化清单的服从度远高于笼统描述。
- 想强化对比图：明确颜色语义 —— "left cluster spread out in green labeled '正常', right cluster collapsed into one blob in red labeled '坍塌', big 'VS' in the middle"。
- 想要咨询报告/白皮书味更浓："add a thin deep-blue title ribbon, circled step numbers ①②③④, a small page-footer line; low-saturation blue-white only"。
- 信息密度不够 → "more cards, more small labeled sub-diagrams, denser structured text, like a condensed paper summary"。太花/太饱和 → "lower saturation, blue-white only, flatter icons, remove gradients and 3D"。
- 出图比例：竖版科普长图默认 `3:4` 或 `2:3`；超长滚动用 `9:16` / `1:2`；当单页 PPT 用 `16:9` / `4:3`。
- 适合主题：AI 技术科普（Transformer、世界模型、RL、Diffusion、Agent、注意力机制…）、商业分析、教学课件、概念辨析。
