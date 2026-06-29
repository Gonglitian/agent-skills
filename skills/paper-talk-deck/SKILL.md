---
name: paper-talk-deck
description: >-
  把一组论文(arXiv 链接 / ID / 标题)做成一份"大 deck 串讲"形式的 Slidev HTML 演示——多篇 paper 合成一份连续幻灯片,
  带封面、总览、逐篇 section、跨篇对比收尾。每篇 paper 一个 section:动机 → method 框图(复用论文原图 + 可选 Mermaid 重绘)
  → 核心代码片段(逐行 focus / magic-move 讲解,带 file:line 引用)→ 结果。引擎用 Slidev(代码高亮/数学/图表一等公民),
  以 HTML 现场演示为主,PDF/PPTX 为备份,PPTX 可再转成 Google Slides。
  复用本机已有 skill 取素材:omnibox-search(库里已有的工程报告)、arxiv-deepdive(库里没有的现产代码级报告)、
  read-paper(VLM 抽 method 原图)、drawio/Excalidraw(精修框图)。
  Use PROACTIVELY whenever the user wants to TURN PAPERS INTO A TALK / PRESENTATION — triggers:
  "把这几篇论文做成 slides / PPT 讲", "串讲这 10 篇 paper", "组会要讲这几篇", "做个论文分享/讲解的 deck",
  "带代码细节的论文 presentation", "paper walkthrough slides", "讲解论文 + method 框图 + 代码",
  "用 Slidev 把论文做成演示", "把 arxiv-deepdive 的报告做成幻灯片"。
  这是"论文 → 可讲的演示"的总装 skill;若用户只想读论文出报告/笔记,用 arxiv-deepdive / read-paper;
  若只要简单纯文字 Markdown 幻灯片用 marp-slide。
---

# paper-talk-deck:把一组论文做成 Slidev 串讲

把 N 篇论文装配成**一份连续的、可现场讲的 HTML 演示**。它不是"读论文"(那是 `arxiv-deepdive` / `read-paper` 干的),而是把读论文的产物(工程报告里的代码细节 + 论文 method 原图)**重组成幻灯片语言**:逐行高亮的代码走读、清晰的 method 框图、跨篇对比。引擎选 [Slidev](https://sli.dev) 是因为代码高亮(Shiki 逐行 focus、magic-move 动画)、Mermaid 图表、KaTeX 数学都是一等公民,而且整份 deck 就是一个 Markdown 文件 —— 这让"自动组装"成为可能。

## 何时用

用户想把**一篇或一组论文**变成**可以讲的演示**(组会串讲、论文分享、课程、技术分享),尤其当要求里出现"带代码细节""画 method 框图""串讲 10 篇"这类信号。典型说法见 frontmatter。只想出报告/笔记的,别用本 skill,用 `arxiv-deepdive`(代码级工程报告)或 `read-paper`(带图笔记)。

## 默认形态(本机用户偏好,除非用户另说)

- **一个大 deck 串讲**:所有论文合成一份连续演示,有封面 + 总览(贯穿主线)+ 逐篇 section + 跨篇对比收尾。
- **Slidev HTML 为主**:现场在浏览器讲,代码动画/交互全保留;PDF/PPTX 作为备份导出;需要分享/协作再把 PPTX 转 Google Slides。
- **代码 = 核心片段 + 逐行讲解**:每篇挑 2-4 段关键代码,用逐行 focus / magic-move 讲清 forward / loss / 采样等核心逻辑,带 `file:line` 引用。
- **中文** deck(用户偏好中文)。

用户给了别的要求(每篇独立 deck、必须 Google Slides 交付、只放伪代码等)就按用户的来。

## 总流程

```
论文清单 ──► [每篇] 取素材 ──► 规划 deck 大纲 ──► 装配 slides.md ──► 预览 / 导出
              omnibox-search                                    npm run dev
              arxiv-deepdive                                    export pdf/pptx
              read-paper(抽图)                                   → Google Slides
```

### 1. 解析输入,定位每篇论文

把用户给的清单解析成 `{arxiv_id, title}` 列表(链接/ID/标题都接受;只给标题先 WebSearch 找 arXiv ID)。确认篇数与顺序——**顺序就是串讲顺序**,如果用户没指定,按逻辑主线排(早→晚、基础→进阶、或按主题聚类),并在总览页画出这条主线。

### 2. 每篇取素材(这步决定 deck 质量,别跳)

每篇需要三类素材。**优先复用已有产物,不要重复读论文**:

1. **代码级内容(动机/核心 idea/代码片段/结果)**:
   - **先查 OmniBox 知识库**——很可能已经有现成工程报告。调 `/litian-academic-search "<论文标题>" --sources omnibox --k 5`。
     命中(相关度高、arxiv 对得上)就直接 `Read` 那篇的 `~/proj/omnibox/papers/<topic>/<arxiv>_<slug>/02_technical.md`(代码细节、file:line、超参、结果都在里面)和 `01_highlevel.md`(动机、核心 idea、定位)。
   - **库里没有 → 现产**:调 `arxiv-deepdive` 跑这篇,得到 `01_highlevel.md` + `02_technical.md`(它会克隆官方 repo、把代码坐实到 file:line)。这是代码 slide 的素材来源。
2. **method 框图原图**:论文自己的 Figure 往往是最准的 method 图。**抽图必须拿到整张图,不能裁切图内容**(实战里"框图显示不全"是头号翻车点)。两条路,优先第一条:
   - **首选 · 整图抽取(按图注定位,保证不裁)**——本 skill 自带脚本,自动找到 `Figure N` 图注所在页、把图注以上的全部绘制元素并成 bbox、高 DPI 裁出**完整**框图(矢量图也稳):
     ```bash
     # PDF 没有就先 curl -sL -o /tmp/<id>.pdf https://arxiv.org/pdf/<id>
     uv run --with pymupdf python ~/.claude/skills/paper-talk-deck/scripts/extract_full_figure.py \
       /tmp/<id>.pdf --find "Figure 2" --output <deck_dir>/public/<arxiv_id>/<name>.png --dpi 220
     ```
     抽完**必须用 Read 工具打开 PNG 肉眼核对**:四边完整、没被切、没混入大段正文。被切→加大 `--pad 24`;图在半页→`--page N --clip top|bottom`;兜底 `--fullpage --page N` 取整页。
   - **退路 · read-paper 抽图脚本**(`uv run ~/.claude/skills/read-paper/scripts/extract_figures.py <pdf> --output-dir <deck_dir>/public/<arxiv_id> --min-size 150`):它对**位图**插图好用,但对**矢量框图常把整图碎成无法用的小片**——所以架构/pipeline 这类图优先用上面的整图脚本。
   - ⚠️ **不要自己"渲染整页再手动裁一刀"**——徒手裁极易切掉图的一角。要么用整图脚本(已自动算 bbox),要么 `--fullpage` 取整页。
   抽出的图进 deck 的 `public/` 目录,Slidev 里用 `/<arxiv_id>/<name>.png`(绝对路径,public 为根)引用。挑 method/architecture/pipeline 那张,不是结果曲线。
3. **(可选)框图重绘**:原图太糊/太满/想强调某条数据流时,用 `drawio` skill 或 Excalidraw 重画,或直接在 slide 里写 Mermaid(见装配)。Mermaid 适合 pipeline / 数据流,改起来最快。

> 批量(如 10 篇):每篇的"取素材"互相独立,可并行 fan-out——一篇一个 subagent,各自完成 omnibox 查找 / arxiv-deepdive / 抽图,返回 `{动机要点, 核心idea, method图路径, 2-4段代码+file:line, 关键结果}` 结构化结果。主代理再统一装配。

### 3. 规划大纲

装配前先写一份大纲(可以是临时 markdown 或直接在脑子里过),确认:
- **总览页主线**:这 N 篇为什么放一起讲?一句话串起来(如"从 X 到 Y 的三代演进""同一问题的三种解法")。
- **每篇 section 的取舍**:动机 1 页、核心 idea 1 页、method 框图 1-2 页、代码 2-4 页、结果 1 页。不要每篇都堆满——次要论文可压缩到 3-4 页,重点论文展开。
- **跨篇对比收尾**:用一张表对比 N 篇的关键维度(方法/数据/结果/优劣),这是串讲相比单篇讲解的最大价值。

### 4. 装配 slides.md

读 `references/slidev-authoring.md`(Slidev 语法手册:逐行代码高亮、magic-move、两栏、Mermaid、KaTeX、图片定位、presenter notes、用 `src:` 拆分每篇),然后从 `assets/deck-template.md` 起步装配。先用脚手架建项目:

```bash
bash ~/.claude/skills/paper-talk-deck/scripts/new-deck.sh <deck_dir> "<deck 标题>"
```

它会建好 `<deck_dir>/`(含 `slides.md` 模板、`package.json`、`public/`)。然后按大纲填充:**每篇一个 section divider(`layout: section`)起头**,后接动机/idea/框图/代码/结果各页。每篇内容多时,建议拆成 `<deck_dir>/papers/<arxiv>.md` 再在主 `slides.md` 用 `---\nsrc: ./papers/<arxiv>.md\n---` 引入,主文件保持可读。

**装配要点**(详见 reference,这里是必须记住的):
- **代码逐行讲**:` ```py {1-3|5-8|all}{lines:true} ` —— 竖线分隔的每组是一个点击步骤,讲到哪高亮到哪。多段代码演进用 ` ````md magic-move ` 包多个代码块,逐次平滑变形。这是本 deck 的灵魂,别只贴一坨静态代码。
- **代码出处**:每段代码下用小字标 `file:line`(来自 `02_technical.md`),让听众知道"这是真代码不是伪代码"。
- **method 框图(务必整图可见、不溢出)**:⚠️ `layout: image` / `image-left` / `image-right` **默认 `backgroundSize: cover`,会把图裁掉填满半屏**——这是"框图显示不全"的另一根因。两种正确写法:
  - **宽幅架构图(推荐)**:普通页 + 居中 `<img>` 限高,`object-contain` 保证整图缩放进页面、任何分辨率不超边:
    `<img src="/<arxiv>/<f>.png" class="block mx-auto object-contain max-h-[56vh] max-w-[94%] rounded shadow" />`,说明要点压成 `grid-cols-2/3` 放图下。
  - **竖长图**:可留 `layout: image-right`,但**必须**在该页 frontmatter 加 `backgroundSize: contain`。
  - 重绘用 Mermaid ` ```mermaid ` 内联(Mermaid 不会被裁)。
- **数学一律 KaTeX,别写裸文本**:行内 `$...$`、独立 `$$...$$`。张量形状/上下标/loss 写成 KaTeX(如 `$x\in\mathbb{R}^{T\times K\times3\times H\times W}$`、`$z_\tau$`、`$$\mathcal{L}=\dots$$`),**不要**直接敲 `x∈R^{T×K...}`、`z_τ` 这种伪文本(渲染丑、易错)。但只包**真公式**——指标名词/数值(FID 14.9、L2、碰撞率)保持普通文本,代码块里的代码不动。⚠️ 行内 `$...$` **别塞进裸 `<div>`**(不渲染)、**别紧贴全角标点**(如 `：$x$` 失配);长公式用 `$$...$$` 独立块最稳。
- **Mermaid/框图会溢出页面**:Mermaid 按内容自然尺寸渲染,**Slidev 不自动缩放它适配页面**——横向叶子一多(`flowchart TB` 把所有叶子排一行)就溢出右边缘,`{scale}` 救不回来;`subgraph` 内 `direction` 在有连线时还会被覆盖。**宽表/分类体系/卡片网格优先用 HTML `flex flex-wrap`/`grid`(自动换行、永不溢出),别硬掰 Mermaid**。详见 reference 的 Mermaid 节。
- **节制**:每页 3-5 个要点,标题短。代码页可以满,叙述页留白。

### 5. 预览与导出

脚手架(`new-deck.sh`)已钉 **`@slidev/cli ^52.16.0`**(52.x = Slidev 当前主版本,已去掉 `0.` 前缀,**不是 `0.52`**;别误降到 `0.x`,旧 deck 在 `0.4x/0.5x` 的要升上来)+ `@slidev/theme-seriph ^0.25.0`。

```bash
cd <deck_dir> && npm install        # 首次:装 slidev + 主题 + playwright(导出用)
npm run dev                          # 浏览器现场演示(http://localhost:3030),代码动画全保留 —— 主交付物
```

**渲染自检(装配后必做,别省)**:溢出/公式不渲染等问题看源码看不出来——导出 PNG 亲眼看:
```bash
npx slidev export --format png --output /tmp/deck-png/   # 全部页导成图
```
用 Read 工具逐张(至少抽查所有带框图/公式/大表的页)核对:框图/表格/图片有没有超出页面边缘、公式有没有渲染成生 `$...$`、内容有没有被截断。有问题就改(缩窄内容 / 换 flex-wrap 网格 / 调 max-h / 降 scale),**改完再导再看**,直到干净。(`--range` 可能不生效,导全部后读对应页号的 `<n>.png`。)

导出备份(需要 `playwright-chromium`,`new-deck.sh` 的 package.json 已含):
```bash
bash ~/.claude/skills/paper-talk-deck/scripts/export.sh <deck_dir> pdf      # PDF(讲义/存档)
bash ~/.claude/skills/paper-talk-deck/scripts/export.sh <deck_dir> pptx     # PPTX(Mermaid/代码渲染成图嵌入)
```

**PPTX → Google Slides**(需要分享/协作时):把导出的 `.pptx` 用 Drive 上传并把目标 `mimeType` 设为 `application/vnd.google-apps.presentation`,Drive 会自动转成原生可编辑的 Google Slides。本机已连 `gogcli-slides` MCP,可用其上传/转换工具一步完成;细节见 `references/slidev-authoring.md` 末节"导出与转 Google Slides"。

## 交付时回报

简要告诉用户:deck 目录在哪、几篇 / 共几页、`npm run dev` 怎么起、导出了哪些格式、每篇的 method 图来自原图还是重绘、有没有"某篇没官方代码所以代码页用伪代码"这类注记。

**现场操作要点(回报时一并给对,别说错)**:
- 翻页/动画:`空格`/`→` 下一步、`←` 上一步、`↑`/`↓` 跳整页;`o` 全屏缩略图**总览**;`f` 全屏;`d` 暗色;`g` 跳页。
- **讲稿(presenter notes)在 presenter 模式看**:开 `http://localhost:3030/presenter/`,或鼠标移到**左下角**让导航条浮出再点 presenter 图标。**Slidev 没有 `p` 快捷键**——别让用户按 `p`。
- Slidev 自带总览是 `o` 出来的网格;它**没有**常驻右侧的标题清单,若用户看到这种侧栏,那是浏览器扩展,与 deck 无关。

## 质量准则

- **是"讲"不是"读"**:幻灯片承载的是讲解节奏(一页一个点、代码逐行揭示),不是把报告段落搬上去。文字密就拆页或转成 presenter notes。
- **代码要真**:贴官方 repo 真实代码 + file:line;没有官方实现的论文,明确用"伪代码/算法框"并在页上标注,别假装。
- **框图优先用原图**:论文 Figure 是作者认证过的 method 表达,优先复用;重绘只在能讲得更清楚时做。
- **串讲的价值在对比**:总览的主线 + 收尾的对比表,是一组论文相比单篇的增量,务必有。
- **诚实标注边界**:某篇素材只来自论文正文(无代码)、某数字来自论文 vs 代码不一致——沿用 arxiv-deepdive 的诚实准则,在 notes 或页面标出。
- **眼见为实,别假设排版没问题**:框图/图片/公式/大表是溢出和不渲染的重灾区,源码看不出来。装配后**导出 PNG 逐页核对**(见步骤 5 渲染自检),发现问题改到干净——这是质量的最后一道关。

## 资源

- `references/slidev-authoring.md` — Slidev 语法手册(逐行高亮、magic-move、两栏、Mermaid、KaTeX、图片、notes、src 拆分、导出与转 Google Slides)。装配前必读。
- `assets/deck-template.md` — 起步用的 `slides.md`(封面 + 总览 + 单篇 section 模板 + 对比收尾 + 致谢)。
- `scripts/new-deck.sh` — 脚手架:建 deck 目录 + slides.md + package.json + public/。
- `scripts/extract_full_figure.py` — **整图抽取**(按 `Figure N` 图注定位 → 并起图注上方绘制元素当 bbox → 高 DPI 裁出完整框图,矢量图也不被切)。`uv run --with pymupdf python … <pdf> --find "Figure 2" --output …png`;选项 `--page/--clip/--fullpage/--pad/--dpi`。
- `scripts/export.sh` — 导出 PDF / PPTX / PNG。
- 外部:Slidev 官网 https://sli.dev · 代码高亮 https://sli.dev/features/line-highlighting · magic-move https://sli.dev/features/shiki-magic-move · Mermaid https://sli.dev/features/mermaid
