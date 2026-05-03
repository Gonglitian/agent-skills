# Introduction 6-段填空骨架

> 用法: 复制本模板到你的草稿文件，按段填空。每段先写"中文 message 一句话"，再写"英文 4-6 句"。
> 配套阅读: `references/golden_skeleton.md`（每段的详细解释）+ `references/paragraph_archetypes.md`（句模库）。

---

## ¶1 · Hook（150-250 词，2-4 句）

**这段的 message（先用中文写出来，1 句话）**: ___________________________________________

**Hook 类型** (4 选 1)：☐ Vision-driven  ☐ Human-analogy  ☐ Foundation-model-analogy  ☐ Epigraph

**句首挂钩词候选**（选一个）:
- *Building [system X] requires...*
- *Recent advances in [field] have demonstrated...*
- *[Capability X] represents one of the biggest open problems in...*
- *Foundation models operate on a principle that...*
- *[Epigraph quote] — Author*

**段落（英文，4-6 句）**:
```
[第 1 句: 把读者拉到 vision / 普世原则的高度]
[第 2 句: 引入领域的进展或承诺]
[第 3 句: 暗示一个张力或未解的问题（为 Gap 段铺垫）]
[可选第 4 句: 总结 hook 立场]
```

**自检**: ☐ 第一句不是 "In this paper..." ☐ 没有具体方法名 ☐ 不是 "Recent X has attracted increasing attention" 套话

---

## ¶2 · Gap（200-350 词，3-5 句）

**这段的 message（中文一句话）**: ___________________________________________

**Gap 表达形式** (1+ 选)：☐ 编号子 gap  ☐ 具体失败例子  ☐ 直接 cite 竞品  ☐ 给 obvious solution 并解释为何不行

**句首挂钩词**:
- *However, [现有方法] suffer from...*
- *Yet, despite this progress,...*
- *Most existing [methods] follow a [paradigm], incurring...*
- *A naive strategy is to [obvious solution]. However, it faces [N] critical limitations: (1) ..., (2) ...*

**段落（英文，3-5 句）**:
```
[第 1 句: 现状概括，承认进展]
[第 2-3 句: 具体短板（不是 "limited"，是某个可指认的问题）]
[第 4 句: 短板的下游后果]
[可选第 5 句: 提一个 obvious solution 并指出为何不够]
```

**自检**: ☐ Gap 不是 "X is limited" 这种空话 ☐ 至少给一个具体例子或编号 ☐ 没把 Gap 写成 related-work 段

---

## ¶3 · Insight / Nugget（100-250 词，1 段，2-4 句）

**这段的 message（中文一句话） — 这就是你的 single ping**: ___________________________________________

**类比锚点候选**（选一个）:
☐ 人类能力  ☐ Cognitive science  ☐ LLM/Foundation model 范式  ☐ 物理/数学  ☐ 已建立的成熟范式（image generation 等）

**句首挂钩词**:
- *Our key idea is that...*
- *Our main insight is that...*
- *We argue that...*
- *Inspired by [analogy], we propose that...*
- *Drawing on [field], we observe that...*

**段落（英文，2-4 句）**:
```
[第 1 句: 类比 / 灵感来源（如有）]
[第 2 句: nugget 的直接陈述（必须能一句话复述）]
[可选第 3 句: 这个 nugget 如何关联回 Gap]
```

**自检**: ☐ Nugget 能用一句话复述 ☐ Nugget 不是 contribution（"+15% gain" 不是 nugget） ☐ 不是把方法当 nugget

---

## ¶4 · Approach（250-400 词，1-2 段）

**这段的 message（中文一句话）**: ___________________________________________

**句首挂钩词**:
- *To this end, we propose [Method], a [type] that [does Y].*
- *Building on this insight, we introduce [Method].*
- *Following this principle, we design [Method] with [N] key components: ...*

**段落（英文）**:
```
[第 1 句: "We propose X" — 一句话定义 X 是什么]
[第 2-4 句: 列 2-3 个 key design decisions，每条配 "This enables / avoids / addresses" 一句]
[可选: 一句 input/output 说明，让外行 reviewer 也能 follow]
[可选: 一张 teaser figure 的 in-text 引用]
```

**自检**: 
- ☐ 每个 design choice 都连回前面提到的具体问题
- ☐ 不超过 3 个 design choices（多于 3 个就拆段或简化）
- ☐ 没写成 method section 缩水版（应该是概念级，不是细节级）

---

## ¶5 · Evidence（150-300 词，1 段）

**这段的 message（中文一句话）**: ___________________________________________

**句首挂钩词**:
- *We evaluate [Method] on [N] benchmarks across [setting]...*
- *Across [N] tasks and [M] embodiments, [Method] achieves...*
- *Our experiments show that [Method] [outperforms / enables / scales]...*

**段落（英文）**:
```
[第 1 句: 评测概括（多少 task / benchmark / embodiment）]
[第 2-3 句: 至少 2 个具体数字（百分比 / 时长 / sample efficiency）]
[第 4 句: 至少 1 个生活化任务 / 真实场景描述]
[可选第 5 句: "first to demonstrate" 类宣称]
```

**自检**:
- ☐ 至少一个具体百分比或时长
- ☐ 至少一个 specific baseline 名字
- ☐ 至少一个具体任务名（laundry folding / espresso / cleaning kitchen 而非 "manipulation tasks"）
- ☐ 不超过 5 个数字（reviewer 记不住）

---

## ¶6 · Contributions（100-200 词）

**形式选择**:
☐ Bullet list (3-5 条) — 适合 method / benchmark paper
☐ Narrative 段落 — 适合 conceptual / system paper
☐ Capability bullets — 适合 emergent capability paper

### Bullet 模式

```
We summarize our contributions as follows:
- We [verb] [X], which [refutable claim] (§Y, Table Z).
- We [verb] [X], showing that [refutable finding] (§Y).
- We [verb] [X], reducing/improving [metric] by [Z%] over [baseline] (§Y, Table Z).
```

### Narrative 模式

```
Our central contribution is [X], together with [Y]. We provide a detailed empirical evaluation
of [Z capabilities]. To our knowledge, our work is the first to demonstrate [W].
```

**自检（每条 contribution 都要过）**:
- ☐ 可证伪（能想象一个具体实验拒绝它）
- ☐ 带 forward reference (§X 或 Table Y)
- ☐ 不与其他 contribution 重叠 / 嵌套
- ☐ 用 "We propose / introduce / present" 而非 "We are the first to think about"

---

## 全局自检（写完一遍后跑一次）

把每段第一句抽出来，连成一段：

```
¶1 第一句: ____________________________
¶2 第一句: ____________________________
¶3 第一句: ____________________________
¶4 第一句: ____________________________
¶5 第一句: ____________________________
¶6 第一句: ____________________________
```

读这段连起来的"骨架文字"。它能独立讲完整 story 吗？  ☐ 能  ☐ 不能 → 重写不能的 topic sentence

---

## 排版纪律

- 每段 ≤ 4 行（编译后）。超过就拆。
- 不要让 Contributions 跨页（强制留在第一页）。
- Figure 1 的 in-text reference 必须在 ¶3 或 ¶4 出现一次（"see Figure 1" / "as illustrated in Fig. 1"）。
- §2 Related Work 不能从第一页开始。
