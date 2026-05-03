# 6 段黄金骨架 · The Golden Skeleton

> 来源: 提炼自 OpenVLA / π0 / π0.5 / π*0.6 / π0.7 / MemoryVLA / RoboMME / MEM / Fast-WAM / DiT4DiT 共 10 篇 famous VLA / robot-learning 论文 introduction 的逐段拆解；与 Widom 5-段、Black 12-问、SPJ single-ping、Tokekar 5-Qs、Black GPS 节律 完全相容。

每段都有：
- **Message**：这段必须传达的唯一信息
- **Goal**：reviewer 读完这段会形成什么认知 / 情绪
- **字数**：经验区间（1500 词 intro 为基线）
- **常见错误**
- **真实 paper 实例**（截取一句 topic + 一句 punch）

---

## 段 1 · Hook（开篇钩子）

- **Message**: 这个领域有一个被广泛认可的承诺 / 愿景 / 普世原则；它如此重要，以至于 anyone in robotics 都该关心。
- **Goal**: reviewer 读完后觉得 "这是我领域的关键问题，我愿意继续读"。
- **字数**: 150–250 词，2–4 句。
- **形式**: 4 选 1 — 见 `hook_strategies.md`：
  - **Vision-driven**: 领域终极愿景 + 现状之间的张力（OpenVLA / π0.5 / Fast-WAM）
  - **Human-analogy**: 用人类能力作锚点（π0 / π0.5 / MEM / MemoryVLA）
  - **Foundation-model-analogy**: 用 LLM/VLM 的成功 mirror 自己领域（π0.7 / DiT4DiT / OpenVLA）
  - **Epigraph**: 文学引文 + 直接命题（π*0.6: Heinlein; π0.7: Tennyson）
- **常见错误**:
  - ❌ 上来就 "Recently, with the development of deep learning, X has attracted increasing attention..." → reviewer 立刻 disengage
  - ❌ Hook 是一句简单陈述事实而非 vision/tension
  - ❌ 把 contribution 偷渡到 hook（"In this paper, we propose..."第一句出现）
- **真实实例**:
  - π0: *"Artificial intelligence systems come in all shapes and sizes... However, the axis along which human intelligence most outpaces machine intelligence is versatility."* — vision + tension
  - π0.5: *"Open-world generalization represents one of the biggest open problems in physical intelligence: embodied systems... only truly become useful when they can leave the lab and handle the diverse situations and unexpected events that occur in the real world."*
  - MemoryVLA: *"Vision-Language-Action (VLA) models, powered by large-scale cross-embodiment robotic datasets and pretrained Vision-Language Models, have achieved remarkable progress in robotic manipulation. However, mainstream VLA models such as OpenVLA and π₀ rely solely on the current observation, thereby overlooking temporal dependencies and performing poorly on long-horizon temporal manipulation tasks."*

---

## 段 2 · Gap（指出现有方法做不到的具体事）

- **Message**: 当前 SOTA 在追求 Hook 描述的愿景时遭遇了一个**具体的、可被指认的**瓶颈；不是泛泛而谈"还需要更好"。
- **Goal**: reviewer 读完后觉得 "这个 gap 真实存在 / 我也注意到了 / 这是个值得做的问题"。
- **字数**: 200–350 词，3–5 句。
- **必备元素**:
  1. 现状概括（"Recent VLA models have advanced by..."）
  2. **具体短板**（不是 "limited"，是 "they rely solely on the current observation, performing poorly on long-horizon tasks"）
  3. 短板带来的**下游后果**（"this leads to..."）
  4. 可选: 列 1–2 个失败的修复尝试 + 它们为何失败（→ 给 reviewer "你已经想过 obvious solutions 了" 的信号）
- **常见错误**:
  - ❌ Gap 太抽象（"existing methods are limited"）→ 等于没说
  - ❌ Gap 是 strawman（描述了一个根本没人做过的方法的局限）
  - ❌ Related work paragraph 伪装成 gap → reviewer 觉得是 background dump
- **关键锚词**: *However / Yet / Unfortunately / Nevertheless / Despite this / While ... promising,*
- **真实实例**:
  - OpenVLA: *"there are two key reasons preventing the widespread use of existing VLAs: 1) current models are closed... and 2) existing works do not provide best practices for deploying and adapting VLAs to new robots."* — 编号清楚，每条都可证伪
  - Fast-WAM: *"Most existing WAMs follow an imagine-then-execute paradigm, incurring substantial test-time latency due to iterative video denoising. More fundamentally, it remains unclear whether explicit future imagination is actually necessary for strong action performance."* — 一个 practical gap + 一个 conceptual gap
  - MemoryVLA: *"A naive strategy is to concatenate consecutive frames as input to the VLM. However, it faces two critical limitations: (1) The quadratic complexity... (2) Sequential frame inputs are misaligned with the model's single-frame robotic pretraining distribution."* — 把"为什么 obvious solution 不行"明白说出来

---

## 段 3 · Insight (the nugget)（关键洞察）

- **Message**: 我们看到了一个**别人没看到、或没说穿**的关键转折；这个洞察让 Gap 变得可解。
- **Goal**: reviewer 读完后想 "啊，原来可以这么看 / 这角度有意思"。这是论文 10 年后唯一被记住的东西（SPJ single ping）。
- **字数**: 100–250 词，1 段，2–4 句。
- **形式**:
  - 类比 / 灵感来源（人脑 / LLM / 物理 / cognitive science / foundation model 训练范式）
  - 一句直接陈述（"Our key idea is that ..."、"The main insight is that ..."、"We argue that ..."）
- **必备**: 一句话能复述。如果你写不出一句话能复述的 nugget，这篇 paper 还不该开始写。
- **常见错误**:
  - ❌ Nugget = contribution（"we achieve 16% gain"不是 nugget，是 result）
  - ❌ Nugget 藏在 Approach 段里 → reviewer 看不到 single ping
  - ❌ 缺失（很多 incremental paper 都缺这段，被 reviewer 评为"engineering 而非 research"）
- **真实实例**:
  - MEM: *"our main insight is that an effective memory architecture for long-horizon robotic control should combine multiple modalities to capture these different levels of abstraction."* — 一句话 nugget
  - MemoryVLA: *"Research in cognitive science demonstrates that humans handle manipulation tasks through a dual-memory system... Drawing on cognitive science insights, the authors propose MemoryVLA"* — analogy → nugget
  - Fast-WAM: *"do WAMs need to imagine future observations at test time, or do they benefit primarily from learning to model them during training? Our key idea is to decouple the video prediction objective used in WAM training from explicit future generation at inference time."* — 提一个尖锐问题再回答
  - π0.7: *"the cornerstone of generalist capabilities ... has proven elusive in the domain of physical intelligence"* + later "annotating the data with detailed context annotations that contain not only information about what to do but also how to do it"

---

## 段 4 · Approach（方法概述 + design rationale）

- **Message**: 我们如何把 Insight 变成具体方法；**每个 design choice 都对应解决前面提到的某个具体问题**。
- **Goal**: reviewer 读完后觉得 "方法和 gap / insight 严格闭环；不是堆砌组件"。
- **字数**: 250–400 词，1–2 段。
- **结构**:
  - "We propose / introduce / present X, a [type] that [does Y]." — 一句话定义
  - 列 2–3 个 key design decisions，每条配 rationale (*"This enables...", "This avoids..."*)
  - 必要时加一句 input/output 描述（让没读过你领域的 reviewer 也能 follow）
- **常见错误**:
  - ❌ 写成 method section 的浓缩版（讲细节而非概念）
  - ❌ 列 design choices 但不连回前面的 gap（"我们用 attention" 但没说为什么）
  - ❌ 一段塞 5 个 component → reviewer 跟丢
- **真实实例**:
  - π0: *"To incorporate diverse data sources, we begin by utilizing a pre-trained vision-language model (VLM) to import Internet-scale experience. ... we use an action chunking architecture with flow matching (a variant of diffusion) to represent complex continuous action distributions. This enables our model to control robots at frequencies of up to 50 Hz for dexterous tasks such as laundry folding."* — 每个 choice 配 rationale + 直接给一个 impressive 用例
  - DiT4DiT: *"Unlike prior methods built on visual-language autoregressive backbones, our framework adopts a bidirectional Video Diffusion Transformer (DiT). During denoising, we extract compact latent features from future-frame generation and use them to condition action learning, so the policy is grounded in the generative visual dynamics that govern physical interaction."* — contrast with prior 加强 design rationale
  - MemoryVLA: 三步 (retrieve / fuse / consolidate)，每步配一句话作用 — 用编号让结构更显眼

---

## 段 5 · Evidence（实验 highlight）

- **Message**: 我们的方法**真的**解决了前面提的问题；用最具体的数字 + 最 impressive 的任务 / setting。
- **Goal**: reviewer 读完后觉得 "数字硬，setting 难；不是 toy"。
- **字数**: 150–300 词，1 段。
- **结构**:
  - 1 句话总评（"We evaluate X on Y benchmarks and find ..."）
  - 2–3 个具体数字 / 对比（"X% gain over Y", "Z hours of espresso making"）
  - 一句"first to demonstrate" / "for the first time" 类强宣称（如果合理）
- **常见错误**:
  - ❌ 含糊的相对量（"significant improvement"）→ 写"+14.6 points over CogACT"
  - ❌ 只有 simulation 数字，real-world 一笔带过
  - ❌ 强调小细节数字（"trained for 80k steps"）而非 reviewer 在意的 outcome
- **关键锚词**: *We evaluate / Across / Our experiments show that / Notably / In particular / First*
- **真实实例**:
  - OpenVLA: *"OpenVLA outperforms the 55B-parameter RT-2-X model... by 16.5% absolute success rate across 29 evaluation tasks."* — 具体数字 + 具体 baseline + 具体 task 数
  - π0.5: *"perform long-horizon manipulation skills 10 to 15 minutes in length, cleaning an entire kitchen or bedroom"* — 用时长直觉化 task 难度
  - π*0.6 (Recap): *"thirteen hours of espresso making, over two hours of novel laundry folding in new homes without interruption, and factory box assembly using real packaging"* — 三个生活化场景，让 reviewer 直觉到 robustness
  - MemoryVLA: *"71.9% and 72.7% success rates on Bridge and Fractal suites, surpassing CogACT by 14.6 and 4.6 points"*
  - π0.7: 4 个 bullet point 子能力，每个 bullet 都是一句"我们能做 X 而别人做不到"

---

## 段 6 · Contributions（可证伪 + 带跳转）

- **Message**: 把整篇贡献用 3–5 条**可证伪、互不重叠**的句子封装。
- **Goal**: reviewer 在写 review 时直接 copy 这段当作"strengths"列表。
- **字数**: 100–200 词，3–5 个 bullet 或一段 narrative。
- **必备**:
  - 每条 *refutable*（描述一个能被实验拒绝的 claim）— SPJ 标准
  - 每条 *forward reference*（带 §X / Table X / Figure X 跳转）
  - 内部不重叠（贡献 1 ≠ 贡献 2 的子集）
- **形式选择**:
  - **Bullet list**（OpenVLA 后期版本、MemoryVLA、Fast-WAM、RoboMME）— 适合 system / benchmark paper
  - **Narrative 段落**（π0、π0.5）— 适合 conceptual paper, 一段话讲完贡献
  - **Bullet of capabilities**（π0.7）— 强调 emergent / 多面能力的 paper
- **常见错误**:
  - ❌ "We propose a novel X."（不可证伪）→ 改"X reduces Y by Z% on dataset W"
  - ❌ Contribution 之间嵌套（"我们提出 X" + "X 的某个组件 Y" + "X 的另一组件 Z" → 应合并为 1 条 + ablation）
  - ❌ 没有 forward reference → reviewer 找不到证据章节
  - ❌ 太长（>5 条）→ reviewer 看不下；专注 3 条最重要的
- **真实实例**:
  - MemoryVLA: 三个 bullet — 框架贡献 / 模块设计贡献 / 实验贡献，每条都可证伪
  - Fast-WAM: 三个 bullet — 提出问题 / 提出 Fast-WAM 架构 / 通过 controlled comparison 给出经验答案
  - π0.5: *"Our central contribution is a system for training a highly generalizable VLA, π0.5, together with a proof of concept that generalization can emerge from this model when it is trained on appropriately diverse data."* + 紧跟一句 "first to demonstrate..." — narrative 形式

---

## 段间过渡：节律锚词

> Black: *"This rhythm of problem-solution-problem-solution is the clearest way to convey a scientific story in discoverable pieces."*

| 段间 | 锚词候选 | 作用 |
|------|---------|------|
| Hook → Gap | *However / Yet / Despite this progress / Nevertheless* | 引入张力 |
| Gap → Insight | *We observe that / We argue that / Our key idea is / Inspired by [analogy]* | 翻转视角 |
| Insight → Approach | *To this end / Building on this insight / Following this principle* | 把抽象变具体 |
| Approach → Evidence | *We evaluate / Our experiments show / Across X benchmarks* | 进入实证 |
| Evidence → Contributions | *In summary / Our contributions are / We summarize our contributions as follows* | 收尾 |

---

## 视觉化：6 段如何对应到 page-1 layout

```
+-------------------------------------------+
| Title + authors + email                    |
+-------------------------------------------+
| Abstract (Mad-Libs 形式)                    |
+-------------------------------------------+
| §1 Introduction                            |
|   ¶1 Hook         ────────┐                |
|   ¶2 Gap          ────────┤                |
|                           ├─ 第一栏        |
|   [Figure 1: Teaser ──→]──┘                |
|                                            |
|   ¶3 Insight      ────────┐                |
|   ¶4 Approach     ────────┤  第二栏        |
|   ¶5 Evidence     ────────┘                |
|   ¶6 Contributions                         |
+-------------------------------------------+
```

**关键纪律**:
- Figure 1 (teaser) 必须在第一页**右上**或**左上**，与 ¶3 Insight 对齐：reviewer 视线第一次移开文字时落在 teaser 上。
- ¶6 Contributions 跨页时，**永远不要让 contribution list 在第二页开始** — 强制保留在第一页底部。
- §2 Related Work 不能在第一页（SPJ rule）。如果会议传统要求（如 robotics 把 related work 放第 2 节），让 §2 从第 2 页开始。

---

## 用法

写 / 改 introduction 时，按以下顺序：
1. 复制 `templates/intro_skeleton.md`，每段填入"这段我要传递的 Message"。
2. 对照本文每段的 "Message / Goal / 必备 / 锚词 / 实例"，把每段 Message 扩展成 4-6 句。
3. 跑 `references/checklist.md` 25 项。
4. 把 6 段的 topic sentence 抽出来连成一段，看是否能独立讲完整 story。
