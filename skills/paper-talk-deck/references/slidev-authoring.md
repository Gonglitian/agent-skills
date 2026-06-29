# Slidev 语法手册(论文串讲专用)

只收录装配论文串讲 deck 真正用得到的语法。完整文档 https://sli.dev 。

## 目录
- [文件结构与分页](#文件结构与分页)
- [全局 frontmatter（headmatter）](#全局-frontmatter-headmatter)
- [单页 frontmatter（layout / class / transition）](#单页-frontmatter)
- [代码：逐行高亮（灵魂功能）](#代码逐行高亮)
- [代码：Magic Move 演进动画](#代码magic-move-演进动画)
- [两栏布局（图文对照）](#两栏布局)
- [图片（method 原图）](#图片method-原图)
- [Mermaid（框图重绘）](#mermaid框图重绘)
- [数学公式 KaTeX](#数学公式-katex)
- [逐步揭示 v-click](#逐步揭示-v-click)
- [Presenter notes](#presenter-notes)
- [用 src 拆分每篇论文](#用-src-拆分每篇论文)
- [导出与转 Google Slides](#导出与转-google-slides)

---

## 文件结构与分页

一份 deck 就是一个 `slides.md`。用 `---` 单独成行分隔每一页:

```md
# 第一页标题

内容

---

# 第二页标题

内容
```

第一页的 `---` 之前(或第一页 frontmatter)是**全局 headmatter**;每页开头的 `---\n...\n---` 是**单页 frontmatter**。

## 全局 frontmatter（headmatter）

deck 第一页顶部:

```md
---
theme: seriph          # 学术风推荐 seriph;开发风 default;另有 apple-basic 等
title: 论文串讲 — XXX
favicon: /favicon.png
highlighter: shiki      # 代码高亮引擎,默认 shiki(支持逐行/magic-move)
lineNumbers: true       # 代码块默认显示行号
transition: slide-left  # 翻页动画
mdc: true               # 启用 MDC 语法(组件/属性),建议开
fonts:
  sans: Noto Sans SC    # 中文字体,避免方块
  mono: Fira Code
---
```

主题装在 `package.json` 里(如 `@slidev/theme-seriph`),`new-deck.sh` 已配好 seriph。

## 单页 frontmatter

每页可单独设布局等:

```md
---
layout: section     # 章节分隔页(每篇论文用它起头)
---

# 1 / OpenVLA
> 大词模型 → 机器人动作
```

常用 `layout`:
- `cover` — 封面页
- `section` — 章节分隔(**每篇论文 section 的起头页用这个**)
- `default` — 普通页
- `two-cols` — 两栏(图文对照,见下)
- `image-right` / `image-left` — 一侧整图、另一侧正文(放 method 原图最顺手)
- `center` — 居中(放一句话核心 idea / 金句)
- `fact` / `quote` — 强调一个数字或一句话

其它有用单页字段:`class: text-sm`(整页缩字)、`transition: fade`、`clicks: 3`。

## 代码逐行高亮

**这是论文代码走读的核心。** 在代码块语言后用 `{}` 写要高亮的行,用 `|` 分隔点击步骤——讲到哪、高亮到哪:

````md
```python {1-2|4|6-8|all}{lines:true}
def forward(self, obs):
    feat = self.encoder(obs)          # 1-2: 编码
    # ...
    z = self.fuse(feat, self.memory)  # 4: 与记忆融合 ★ 本文关键
    # ...
    a = self.action_head(z)           # 6-8: 解码动作
    a = self.unnormalize(a)
    return a
```

<div class="text-xs opacity-60 mt-2">policy/model.py:142 · OpenVLA 官方实现</div>
````

- `{1-2|4|6-8|all}`:4 个点击步骤,第一步高亮 1-2 行,第二步只高亮第 4 行……最后 `all` 全亮。讲解时按空格/方向键推进。
- `{lines:true}` 显示行号;`{startLine:140}` 让行号从 140 开始(对齐真实 file:line)。
- 代码太长:`{maxHeight:'400px'}` 加滚动;高亮行会自动滚到视口。
- **每段代码下用小字标 `file:line`**(上例的 `<div>`),来自 `02_technical.md`,证明是真代码。

## 代码：Magic Move 演进动画

讲"从朴素实现 → 本文改法",或代码逐步长出来,用 magic-move:同一块代码在多个版本间**平滑变形**,逐次点击切换。用 ` ````md magic-move ` 包住多个代码块:

`````md
````md magic-move
```python
# 朴素:每步都重算全部 KV
attn = softmax(q @ k.T) @ v
```
```python
# 本文:缓存历史 KV,只算新 token  ★
k = cat([self.kv_cache, k_new])
attn = softmax(q @ k.T) @ v
self.kv_cache = k
```
````
`````

每个 ```` ``` ```` 代码块是一个步骤,点击在相邻版本间做 token 级 diff 动画。讲"改进点"时极有说服力。

## 两栏布局

`layout: two-cols`,用 `::right::` 分隔(左栏在前,无需 `::left::`;要显式可用 `::left::`):

```md
---
layout: two-cols
layoutClass: gap-8
---

## Method

- 输入:RGB + 指令
- 编码器:ViT-L
- 关键:记忆库 read/write

::right::

![method](/2406.09246/fig2.png)
```

## 图片（method 原图）

抽出的图放 deck 的 `public/` 目录(`new-deck.sh` 已建),Slidev 把 `public/` 当根,引用时用 `/` 开头的绝对路径(**不要**写 `./public/...`):

```md
![架构图](/2406.09246/fig2_arch.png)
```

控制尺寸/位置(mdc 语法):

```md
![架构图](/2406.09246/fig2_arch.png){width=480px class="mx-auto rounded shadow"}
```

整页大图:用 `layout: image` + frontmatter 里 `image: /xxx.png`;或 `layout: image-right` 把图甩到右半屏、左半写讲解。

> ⚠️ **裁图陷阱(头号翻车点)**:`layout: image` / `image-left` / `image-right` **默认 `backgroundSize: cover`,会把图裁掉以填满区域**——method 框图常因此"显示不全"。两种修法:
>
> 1. **要整图必加 `backgroundSize: contain`**:
>    ```md
>    ---
>    layout: image-right
>    image: /2406.09246/fig2_arch.png
>    backgroundSize: contain   # 默认是 cover(裁切);contain = 整图缩放进区域
>    ---
>    ```
> 2. **宽幅架构图更推荐用居中 `<img>` + `object-contain` + 限高**(普通页,版面更可控、图也更大):
>    ```md
>    # Method 框图：<标题>
>    <img src="/2406.09246/fig2_arch.png" class="block mx-auto object-contain max-h-[56vh] max-w-[94%] rounded shadow" />
>    <div class="grid grid-cols-3 gap-3 text-sm mt-3"> …3 个要点… </div>
>    ```
>    `object-contain` + `max-h-[..vh]` / `max-w-[..%]` 保证**整图不被裁、任何分辨率不溢出页面**。`<img>` 比 `![]()` 更方便加这些 class。
>
> 配套:图本身要先**整张抽出来**(别用裁过的图),见 SKILL.md 步骤 2 的 `scripts/extract_full_figure.py`。

## Mermaid（框图重绘）

原图不够清楚时,直接在 slide 写 Mermaid 画 pipeline / 数据流:

````md
```mermaid {scale: 0.8}
flowchart LR
  O[Obs] --> E[Encoder]
  E --> F{Fuse}
  M[(Memory)] --> F
  F --> H[Action Head] --> A[Action]
```
````

- `{scale: 0.7}` 缩放以适配页面。
- 适合 flowchart(架构/数据流)、sequence(交互时序)。导出 PPTX 时 Mermaid 会被渲染成图片嵌入。
- 复杂/要精修的框图用 `drawio` skill 出 svg/png 再当图片插入,别硬用 Mermaid 堆。

> ⚠️ **Mermaid 会溢出页面(高频翻车)。** Mermaid 按**内容自然尺寸**渲染,**Slidev 不会自动缩放它去适配页面**——图比页面宽就直接溢出右边缘。两个根因 + 对策:
>
> 1. **横向 fan-out 太宽**:`flowchart TB` 会把**所有叶子节点排成一行**——叶子一多(>5)或文字一长,整图就宽到几千 px,`{scale}` 只能等比缩小(缩到能放下时字也看不清了),救不回来。
>    - 对策:**砍掉节点里的冗长文字**(模型名挪到表格页),把宽树**改成纵向堆叠**;节点多就别用单一 flowchart。
> 2. **`subgraph` 内的 `direction` 不可靠**:一旦 subgraph 之间有连线(含 `~~~` 隐形连线),内部 `direction LR` 常被父图方向**覆盖**,节点又竖排回去 → 改成纵向溢出。别指望它。
>
> **宽表/分类体系/卡片网格,优先用 HTML+UnoCSS 的 `flex flex-wrap` / `grid`,而不是硬掰 Mermaid**——它会自动换行,**永不溢出**,还更好看:
> ```md
> <div class="flex flex-col gap-3 text-sm">
>   <div class="flex gap-3">
>     <div class="w-52 shrink-0 px-3 py-2 rounded bg-blue-100 dark:bg-blue-900/40 font-bold">① 类别</div>
>     <div class="flex flex-wrap gap-2">
>       <span class="px-3 py-1.5 rounded border border-gray-300 dark:border-gray-600">条目 A</span>
>       <span class="px-3 py-1.5 rounded border border-gray-300 dark:border-gray-600">条目 B</span>
>     </div>
>   </div>
> </div>
> ```
> **无论用 Mermaid 还是别的,装配后务必导出该页 PNG 亲眼看有没有溢出**(见手册末"渲染自检"),别假设放得下。

## 数学公式 KaTeX

行内 `$\mathcal{L} = \mathbb{E}[\|a - \hat a\|^2]$`;独立公式:

```md
$$
\mathcal{L}_{\text{flow}} = \mathbb{E}_{t,x_0,x_1}\big[\| v_\theta(x_t,t) - (x_1-x_0) \|^2 \big]
$$
```

讲 loss / objective / 采样过程时用,比纯文字清楚。可加 `{1|2}` 对多行公式逐行揭示。

> **一律用 KaTeX,别敲裸文本数学。** 张量形状、上下标、loss 都写成 KaTeX——`$x\in\mathbb{R}^{T\times K\times 3\times H\times W}$`、`$z_\tau$`、`$$\mathcal{L}=\mathbb{E}[\|a-\hat a\|^2]$$`——**不要**直接写 `x∈R^{T×K×3×H×W}`、`z_τ` 这种伪文本(渲染丑且常错位)。但只包**真公式**:指标名词/数值(`FID 14.9`、`L2`、碰撞率)和代码块里的代码保持原样,不要包成公式。KaTeX 默认开启,无需配置。
>
> ⚠️ **两个"公式不渲染、显示成生 `$...$`"的坑:**
> 1. **裸 `<div>` 里的行内 `$...$` 不被处理。** 行内数学只在 markdown 上下文渲染;塞进原始 `<div>…</div>` 里就当纯文本显示。要带样式又要渲染公式,用 MDC 容器 `::: ... :::` 而非裸 `<div>`,或干脆把公式放普通 markdown 行/`$$` 独立块。
> 2. **行内 `$` 紧贴全角标点会失配。** 如 `(Eq.1)：$z...$` 开头 `$` 直接贴着全角冒号 `：`,触发 markdown 的 flanking 规则失败 → 不渲染(而被空格包住的 `$I$` 却正常)。**`$...$` 两侧留普通空格**,长公式直接用 `$$...$$` 独立块(无 flanking 限制、更稳)。

## 逐步揭示 v-click

让要点一条条出现(配合讲解节奏):

```md
<v-clicks>

- 第一点(先出)
- 第二点(点一下才出)
- 第三点

</v-clicks>
```

单个元素用 `<v-click>...</v-click>`。代码用上面的 `{a|b|c}` 已经自带分步,不必再包 v-click。

## Presenter notes

每页最后用 HTML 注释写演讲备注,只在 presenter 模式(访问 `/presenter/`,**没有 `p` 快捷键**)可见——把"想说但不想上屏"的话放这:

```md
# 这页标题

要点...

<!--
这里是讲稿:展开讲为什么这个 fuse 是关键,对比上一篇的做法。
听众可能问 X,准备好答 Y。
-->
```

## 用 src 拆分每篇论文

大 deck 串讲多篇时,把每篇拆成单独文件,主 `slides.md` 只放封面/总览/收尾 + 引入:

```md
---
src: ./papers/2406.09246.md
---

---
src: ./papers/2410.12345.md
---
```

`papers/<arxiv>.md` 里写该篇的所有页(第一页用 `layout: section` 起头)。好处:主文件可读、每篇可单独迭代、并行装配不打架。被引入文件的第一页 frontmatter 会和引入处合并。

## 现场快捷键(回报给用户时别说错)

`空格`/`→` 下一步动画或页 · `←` 上一步 · `↑`/`↓` 跳整页 · **`o` 全屏缩略图总览** · `f` 全屏 · `d` 暗色 · `g` 跳页。
**讲稿(presenter notes)只在 presenter 模式可见**:开 `http://localhost:3030/presenter/`,或鼠标移到**左下角**让导航条浮出再点 presenter 图标。**Slidev 没有 `p` 快捷键**(别让用户按 `p` 看讲稿)。总览是 `o` 出来的网格。

## ⚠️ Goto 跳转列表"自动冒出来盖住幻灯片"(Slidev 51.x bug,52 已修)

**现象**:dev 页面加载 1-3 秒后,右侧自动浮出一个"编号+标题"的幻灯片清单(从顶部垂下来盖住右半屏),鼠标移开/按 `Esc` 都关不掉。**这是 Slidev 自带的**(来自 `@slidev/client/internals/Goto.vue` 的 `.autocomplete-list`),不是浏览器扩展——别误判成扩展。

**根因**:`g` 跳转对话框关闭时只把容器移到 `-top-20`(上移 80px),但 51.x 里列表是 `v-if="result.length>0"` 且空查询的 Fuse 返回了全部幻灯片→列表恒有内容且很长(~600px),关闭态只有顶部 80px 移出屏幕,剩下垂进可视区。它**只是 dev 导航 UI,不会进导出的 PDF/PPTX/PNG**。

**✅ 根治 = 升级到 Slidev ≥52**(已被上游 PR #2597 修复:`v-if="showGotoDialog && result.length>0"`;PR #2520 修了空 Fuse)。`new-deck.sh` 的 package.json 已默认 `@slidev/cli ^52.16.0`,新 deck 不会再有这毛病。
**若被迫锁在 51.x**:建 `<deck>/styles/index.ts`(`import './goto-fix.css'`)+ `styles/goto-fix.css`:`#slidev-goto-dialog[class~="-top-20"] .autocomplete-list { display: none !important; }`,新建 `styles/` 入口要重启 dev server。

## ⚠️ Slidev 52 引 public 图必须用 `:src` 绑定(否则 dev/build 全 500)

Slidev 52 换了 rolldown 打包器 + 新增 `slide-import-guard`:`<img src="/<arxiv>/fig.png">` 会被当成静态 import,绝对路径解析到 fs.allow 之外 → **dev 按需转换和 build 都报 500 / RolldownError**。**改用运行时绑定**:`<img :src="'/<arxiv>/fig.png'">`(字符串字面量 → 不被静态分析 → 照常从 public/ 服务,51/52 都兼容)。`![](/x.png)` 同理会挂,也改 `:src`。验证:headless 取 `img.naturalWidth>0` 且 console 无 500。`assets/deck-template.md` 已用 `:src`。

## 导出与转 Google Slides

```bash
# dev(主交付:浏览器现场讲,动画/交互全保留)
npm run dev          # → http://localhost:3030 ;presenter 模式访问 /presenter/

# 导出(需要 playwright-chromium,package.json 已含)
npx slidev export --format pdf          # PDF 讲义/存档
npx slidev export --format pptx         # PPTX(每页转成图;Mermaid/代码渲染为图片嵌入)
npx slidev export --format png --output slides-png/   # 逐页 PNG
```

> 注意:PPTX 导出是**每页作为图片**,文本/代码不可再编辑。要在 PPTX/Google Slides 里二次编辑文字,得手动重排,或改用 marp/原生方式。串讲场景一般以 HTML 现场讲为主,PPTX 只作分享存档。

**PPTX → 原生 Google Slides**(Drive 自动转换):上传 `.pptx` 时把目标 `mimeType` 设成 `application/vnd.google-apps.presentation`,Drive 会转成可编辑的 Google Slides。本机连了 `gogcli-slides` MCP:
- 用其 Drive/Slides 上传工具上传导出的 pptx 并指定转换 mimeType;或
- 若只是要一份 Slides 大纲,`gog_slides_create_from_markdown` 可从 markdown 直接建原生 Slides(版式弱于 Slidev,但完全可编辑)。

两种交付权衡:**Slidev HTML/PDF** = 代码动画 + 框图最好看,但不可在 Slides 里改字;**Google Slides** = 可协作可编辑,但 Slidev 的逐行/magic-move 动画会丢失(变静态图)。按用户实际分享需求选。

## 渲染自检（装配后必做，别假设放得下）

幻灯片的"溢出/不渲染"问题肉眼看源码看不出来——**必须导出成图亲眼看**。重点查:框图/表格/图片是否超出页面边缘、公式有没有渲染成生 `$...$`、内容有没有被截断。

```bash
# 导出全部页为 PNG(需 playwright-chromium,package.json 已含)
cd <deck_dir> && npx slidev export --format png --output /tmp/deck-png/
```

然后用 Read 工具逐张(至少抽查有框图/公式/大表的页)打开 PNG 核对。发现溢出就回去改(缩窄内容 / 换 flex-wrap 网格 / 调 max-h / 降 scale),**改完再导出再看**,直到干净。
> 注:`slidev export` 目前会导出全部页(`--range` 可能不生效),挑你要看的页号读对应 `<n>.png` 即可。这一步是 deck 质量的最后一道关,别省。
