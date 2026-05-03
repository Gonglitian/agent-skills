---
name: paper-intro-writing
description: >
  写出 reviewer 一页之内就买账、相信 story 合理 / 必要 / 有创新的英文 paper Introduction。方法论来自三源融合：
  (1) Western 写作大师 (Widom / SPJ / Black / Ernst / Tokekar / Williams) 的 5-段脚手架与 Goal-Problem-Solution 节律；
  (2) 中文 PhD 场景 (Sida Peng / MLNLP / LARG pre-writing form) 的可审计段落规则；
  (3) 10 篇 famous VLA / robot-learning 论文 (OpenVLA / π0 / π0.5 / π*0.6 / π0.7 / MemoryVLA / RoboMME / MEM / Fast-WAM / DiT4DiT)
  Introduction 全文逐句对照后提炼出的语言级共性。Skill 提供：6 段黄金骨架、4 类开篇 hook archetype、6 类段落 archetype 的句模与多篇真实
  paper 实例、Black-Mad-Libs 风格的 Introduction 整段填空模板、动笔前 13 问表、25 项自检清单、ESL 中文母语者高频雷区列表。
  Use PROACTIVELY whenever the user says "写 intro", "写 introduction", "改 intro", "improve introduction", "introduction 没写好",
  "story 不顺", "怎么开篇", "intro 节奏", "intro 怎么 sell", "rewrite intro", "introduction draft", "怎么 hook reviewer",
  "怎么写 motivation", "motivation 不够强", "introduction polish", "paper 第一节怎么写", "顶会 paper 第一页怎么写",
  "审稿人不买账", "我的 intro 太平", "intro 没有 story", "improve the framing", "intro 改 framing",
  "怎么写 contribution", "contribution 不亮", "怎么写 motivation 段", "怎么 propose method 段", "怎么写 gap 段",
  "为什么我的 intro 像 background", or whenever the user shares an Introduction draft and asks for review/rewrite/critique.
---

# Paper Introduction Writing Skill

> *"You lose a factor of 10, I reckon, after page one."* — Simon Peyton Jones
>
> *"By the end of your intro, the reviewer has likely already decided whether they like the paper or not."* — Michael Black

Reviewer 在读完 abstract + Introduction 时已经做了初步判断；剩下的部分是用来**验证**这个判断，而不是**改变**它。
所以 Introduction 不是"背景介绍"，而是 paper 的 **5 秒电梯演讲 (abstract) → 5 分钟电梯演讲 (Introduction) → 30 分钟全文** 链条中最关键的中段。

本 skill 的目标不是教抽象原则，而是把**可执行的脚手架**交到中文母语 PhD 手上：填空模板、句模、archetype、自检表。

---

## 目录 (skill 文件结构)

```
paper-intro-writing/
├── SKILL.md                              ← 你在这里
├── references/
│   ├── golden_skeleton.md                ⭐ 6 段黄金骨架（每段目标/字数/常见错误/真实 paper 实例对照）
│   ├── case_studies.md                   ⭐ 10 篇 famous paper Introduction 的逐段拆解 + 共性提炼
│   ├── paragraph_archetypes.md           6 类段落 archetype 的句模库
│   ├── hook_strategies.md                4 类开篇 hook：vision / human-analogy / contradiction / question
│   ├── chinglish_pitfalls.md             ESL 中文母语者写 intro 的高频雷区清单
│   ├── checklist.md                      投稿前 25 项 Introduction 自检清单
│   └── raw_introductions.md              10 篇 paper Introduction 原文存档（按需查阅具体段落）
└── templates/
    ├── intro_skeleton.md                 6-段填空骨架（每段标好目标 + 句首挂钩词）
    ├── mad_libs_intro.md                 Black 风格 Introduction 整段填空版
    └── pre_writing_form.md               动笔前 13 问（intro-only 版，T-4 周交导师）
```

**强烈建议在写 / 改 introduction 前**: 先读 `references/golden_skeleton.md` + `references/case_studies.md`，再用 `templates/intro_skeleton.md` 填空。

---

## 核心论断（30 秒读完）

1. **Introduction 不是 Background**。Background 回答 "what's known"; Introduction 回答 "why this paper *had to* exist."
2. **6 段黄金骨架**。Hook → Gap → Insight → Approach → Evidence → Contributions。每段一个 message，第一句即 topic sentence。
3. **Goal-Problem-Solution 节律**递归到段落级；锚词 *Unfortunately / In contrast / However / Therefore* 不是修辞，是结构。
4. **Refutable contributions + forward references**。每条 contribution 必须可被实验证伪，且配 `(§4.2)` / `(Table 2)` 跳转。
5. **第一页留给"why this paper exists"**；related work 挪到第 2 节或之后。
6. **类比 / 灵感来源**先于公式：把 abstract problem 锚到 reader 直觉上（人类、LLM、cognitive science、foundation model 是高频锚）。
7. **具体数字 + "first to demonstrate"**比"提升明显"有力 10×。
8. **ESL 雷区**：不要让 reviewer 的认知预算花在解析你的语法上。

---

## 触发后的标准工作流

按用户输入的"任务类型"分支：

### A) 用户从零开始写 (没有 draft)

1. 读 `references/golden_skeleton.md`，理解 6 段每段的 "input → output" 契约。
2. 让用户填 `templates/pre_writing_form.md` 的 13 问（或 Claude 主动逐问引导）。
3. 把 13 问回答 → 投影到 `templates/intro_skeleton.md` 的 6 段骨架。
4. 每段先用一句话写 message，再扩展到 4-6 句。
5. 用 `templates/mad_libs_intro.md` 检查锚词节奏是否完整。
6. 跑 `references/checklist.md` 25 项；任何 ❌ 都重写对应段。

### B) 用户已有 draft，要 review / 改

1. 用 `references/checklist.md` 25 项逐一对照 → 列出所有 ❌。
2. 同时用 `references/golden_skeleton.md` 的 6 段对位：当前 draft 每段对应到哪个 archetype？哪些段落缺失或重复？
3. **审计 topic sentence**：抽出每段第一句连成一段。如果连起来不能独立讲完整 story → 重写 topic sentence。
4. **审计 contributions 可证伪性**：每条 contribution 检查能否被一个具体实验证伪，能否 forward-reference 到 §X。
5. **ESL pass**：用 `references/chinglish_pitfalls.md` 列表 grep。
6. 给出 diff 式重写建议（保留作者声音，仅改结构 / 节奏 / 锚词），不要从头重写。

### C) 用户问"为什么我的 intro 不行 / reviewer 不买账"

按以下顺序诊断：
1. **是 Background 不是 Introduction**：通篇在 review 别人，没说自己 paper 该存在的理由。
   - 修复：把"我们想做 X 因为 Y"提到第二段；related work 提到第 2 节。
2. **没有 nugget**：读完不能用一句话说出这篇的 single ping。
   - 修复：补"Insight"段（骨架第 3 段）。
3. **方法描述太早或太晚**：开头就讲 architecture，或最后一段才说做了啥。
   - 修复：方法在第 4 段，前面要有 hook + gap + insight 三段铺垫。
4. **Contribution 不可证伪**：写了 "We propose a novel X" 而非 "X reduces Y by Z%"。
   - 修复：把每条 contribution 改写成"可被实验拒绝"的形式。
5. **节奏平**：所有段都是同一种语气 / 没有 *Unfortunately / In contrast* 的对比节律。
   - 修复：在 Gap → Insight 之间硬插一个 contrast 锚词，强迫节律下沉再上升。
6. **图 1 是架构图，不是 teaser**：reviewer 看不到 5 秒 sell。
   - 修复：把架构图挪到 §3，重画一张"输入→输出+nugget 高亮"的 teaser。

### D) 用户问写作技巧 / 看共性

直接读 `references/case_studies.md`：10 篇 famous paper 逐段拆解 + 跨篇共性归纳；可以引用任意一篇作 reference 模仿。

---

## Skill 的语言纪律

- 与用户沟通：**中文为主**（用户多为中文母语 PhD），技术词 / paper 段落引用保留英文原文。
- 写出来的 Introduction 草稿：**英文**。但骨架解释、修改 rationale 用中文，让作者真的理解 *why*。
- 引用 paper 段落时：标注来源（哪篇 + 哪段），方便作者去 `references/raw_introductions.md` 看完整上下文。
- 给修改建议时：**永远展示 before / after** 两个版本 + 一句中文 rationale，不要直接覆盖。

---

## 反模式（不要这样用 skill）

- ❌ 看到"introduction"就直接套 5 段模板生成内容。模板是结构容器，内容必须来自作者本人的 nugget。
- ❌ 把 abstract 拆成 5 段当 introduction。Abstract 是 30 秒电梯，Introduction 是 5 分钟电梯，两者粒度不同。
- ❌ 修改时只改语法不改结构。语法是表层；reviewer 不买账的根因 90% 在结构 / 故事。
- ❌ 用 skill 的句模直接照搬。句模是 *形* 不是 *神*；填进去要二次自然化。
- ❌ 把 related work 写在第一页。SPJ：related work *is like a sandbar between your reader and your key idea*.

---

## 与已有 research_skills 库的关系

本 skill 是 `~/proj/litian-research/research_skills/textbooks/03_writing.md` 第三 / 四章 (Page one is sacred / Goal–Problem–Solution) 的**专门化 + 实例化**版本：把通用写作哲学聚焦到 Introduction，并用 10 篇 2024-2026 年 VLA / robot-learning 顶会论文做出语言级落地。

需要更高 level 的写作哲学（如 nugget 训练、abstract 写法、修订哲学、figure 设计、LaTeX 排版、rebuttal）请回到 `03_writing.md` 第二、四、六、七、八、九章。

---

## 配套阅读路径建议

| 时间预算 | 推荐路径 |
|---------|---------|
| **5 分钟** | 本 SKILL.md + `references/checklist.md` |
| **20 分钟** | + `references/golden_skeleton.md` + `templates/intro_skeleton.md` |
| **1 小时** | + `references/case_studies.md`（精读 OpenVLA / π0.5 / MemoryVLA 三篇拆解）|
| **2 小时（投稿前）** | + `references/raw_introductions.md` 选 1 篇与你方向最近的论文，逐句对照仿写 |
