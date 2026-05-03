# 10 篇 Famous Paper Introduction · 逐篇拆解 + 横向共性

> 数据集: 10 篇 2024–2026 年 VLA / robot-learning 顶会 / 顶刊投稿。原文存于 `raw_introductions.md`。
> 拆解方法: 把每篇 Introduction 对位到 6 段黄金骨架（Hook / Gap / Insight / Approach / Evidence / Contributions），并标注每段的修辞 / 节奏特征。

---

## 0. 论文清单

| Tag | 标题 | arXiv | 年份 | 类型 |
|-----|------|-------|------|------|
| **OpenVLA** | An Open-Source Vision-Language-Action Model | [2406.09246](https://arxiv.org/abs/2406.09246) | 2024 | 系统/开源 |
| **π0** | π₀: A Vision-Language-Action Flow Model for General Robot Control | [2410.24164](https://arxiv.org/abs/2410.24164) | 2024 | 概念/foundation |
| **π0.5** | π₀.₅: a VLA with Open-World Generalization | [2504.16054](https://arxiv.org/abs/2504.16054) | 2025 | 系统/co-training |
| **MemoryVLA** | Perceptual-Cognitive Memory in VLA | [2508.19236](https://arxiv.org/abs/2508.19236) | 2025 | 方法/memory |
| **MEM** | Multi-Scale Embodied Memory for VLA | [2603.03596](https://arxiv.org/abs/2603.03596) | 2026 | 方法/memory |
| **π*0.6** | a VLA That Learns From Experience | [2511.14759](https://arxiv.org/abs/2511.14759) | 2025 | 方法/RL |
| **DiT4DiT** | Jointly Modeling Video Dynamics and Actions | [2603.10448](https://arxiv.org/abs/2603.10448) | 2026 | 方法/architecture |
| **Fast-WAM** | Do WAMs Need Test-time Future Imagination? | [2603.16666](https://arxiv.org/abs/2603.16666) | 2026 | 方法/科学问题 |
| **RoboMME** | Benchmarking Memory for Robotic Generalist Policies | [2603.04639](https://arxiv.org/abs/2603.04639) | 2026 | benchmark |
| **π0.7** | a Steerable Generalist Robotic Foundation Model | [2604.15483](https://arxiv.org/abs/2604.15483) | 2026 | 系统/foundation |

---

## 1. 逐篇 6 段对位拆解

### 1.1 OpenVLA — "open the closed VLA"

| 段 | 内容 | 修辞策略 |
|---|------|--------|
| Hook | "A key weakness of learned policies for robotic manipulation is their inability to generalize..." | 反向 hook：直接把领域痛点讲清楚 |
| Gap | "Yet beyond robotics, existing foundation models for vision and language ... are capable of these types of generalization" + 后段 "two key reasons preventing the widespread use of existing VLAs: 1) closed, 2) no fine-tuning best practices" | 用 "closed vs open" 的政治化框架 |
| Insight | "robotics needs open-source, generalist VLAs that support effective fine-tuning" | 不是技术 insight，是 community insight |
| Approach | "OpenVLA, a 7B-parameter open-source VLA... fine-tuned on 970k trajectories from Open-X..." | 数字密集 + 直接给规模 |
| Evidence | "outperforms 55B RT-2-X by 16.5% absolute success rate across 29 evaluation tasks... 7× fewer parameters... LoRA + quantization on consumer GPUs" | 三层证据：performance / efficiency / accessibility |
| Contributions | 自然语言段落，非 bullet | 系统 paper 风格 |

**特殊技巧**: 用 "open vs closed" 的张力替代典型 technical gap。这给了 paper 一个 community-level positioning，让审稿人从"是否值得发表"角度容易给 accept。

---

### 1.2 π0 — "robot foundation model 第一次像样的范式"

| 段 | 内容 | 修辞策略 |
|---|------|--------|
| Hook | "AI systems come in all shapes and sizes... However, the axis along which human intelligence most outpaces machine intelligence is versatility" | 哲学性 hook：用 "human vs machine" 的 axis |
| Gap | "Flexible and general-purpose models that can be tasked to perform a variety of robot behaviors have tremendous practical ramifications, but they may also offer solutions to some of the toughest challenges facing robot learning today" | 把 gap 包装成 *opportunity* 而非 *limitation* |
| Insight | "developing such generalist robot policies involves a number of major challenges. First... Second... Third..." | 把"难题清单"作为 nugget — 我们能解决这三个 |
| Approach | "we present a prototype model and learning framework, which we call π₀... pre-trained VLM + cross-embodiment training + flow matching action expert" | 三个 design decision + 每个配 rationale |
| Evidence | "10,000 hours of robot data ... laundry folding, clearing a table, putting dishes in microwave, stacking eggs, assembling a box, bagging groceries" | 用 6 个生活化任务列表替代百分比 |
| Contributions | "novel generalist robot policy architecture based on VLM pre-training and flow matching, and an empirical investigation of pre-training/post-training recipes" | narrative 段落，强调 conceptual contribution |

**特殊技巧**: 整篇 introduction 没有写一个数字百分比。完全用任务名（laundry folding）和能力描述（50 Hz）建立读者直觉。这是 PI 系列的标志写法。

---

### 1.3 π0.5 — "open-world generalization"

| 段 | 内容 | 修辞策略 |
|---|------|--------|
| Hook | "Open-world generalization represents one of the biggest open problems in physical intelligence" | 直接断言领域核心问题 |
| Gap | "the diversity of situations ... requires more than just scale: we need to design training recipes" + 一个 mobile-cleaning 例子展开层次 | 把 gap 用一个具体的 task 例子（mobile robot 进入新厨房）走读一遍，让 reviewer 看到挑战的层次 |
| Insight | "A person can draw on a lifetime of experience... Analogously, we might hypothesize that generalizable robotic learning systems must be able to transfer experience and knowledge from a variety of information sources." | 人类类比 → nugget |
| Approach | "we propose to include a range of different data sources to create the π0.5 model... 97.6% of training examples do NOT come from mobile manipulators" | 反直觉数字（97.6% ≠ target task）作为 design statement |
| Evidence | "perform long-horizon manipulation skills 10 to 15 minutes in length, cleaning an entire kitchen or bedroom" | 用时长直觉化任务难度 |
| Contributions | "Our work is the first to demonstrate an end-to-end learning-enabled robotic system that can perform long-horizon and dexterous manipulation skills in entirely new homes" | "first to demonstrate" 强宣称 |

**特殊技巧**: §2 (Gap) 用一段中等长度的具体 example walkthrough（mobile robot 进入新厨房需要哪几层能力），把抽象的 generalization 变成具体的认知挑战。这是 PI 系列另一个标志写法。

---

### 1.4 π*0.6 (Recap) — RL for VLA

| 段 | 内容 | 修辞策略 |
|---|------|--------|
| Hook | Heinlein 文学引文 + "Humans acquire new skills through repeated practice, eventually achieving mastery" | epigraph 钩子（ICLR 强偏好） |
| Gap | "While reinforcement learning principles have been established for decades, implementing them in scalable robotic systems presents significant challenges: designing stable RL methods for large models, managing heterogeneous data, and establishing real-world RL training" | 三个具体子 gap |
| Insight | "leveraging not just demonstration data, but also autonomously collected experiential data" | 直接陈述 nugget |
| Approach | "Recap... combines demonstrations, autonomous experience, and expert interventions... offline RL pre-training, then additional training on deployment-collected data" | 时序流程化的 approach |
| Evidence | "thirteen hours of espresso making, over two hours of novel laundry folding in new homes without interruption, and factory box assembly" | 时长 + 真实场景 |
| Contributions | "results demonstrate, for the first time, that a general-purpose RL recipe ... significantly improves both robustness and throughput" | "first" + 双指标 |

**特殊技巧**: 用 epigraph 创造 literary tone。这是 PI 系列在 GR1.5+ 时代的特色 — 把 paper 从纯技术报告升级为 manifesto。

---

### 1.5 π0.7 — "compositional generalization through context"

| 段 | 内容 | 修辞策略 |
|---|------|--------|
| Hook | Tennyson 引文 ("I am a part of all that I have met") + "Foundation models operate on a principle that generalist capabilities emerge from training on large and diverse datasets" | epigraph + LLM 类比 |
| Gap | "this compositional generalization represents arguably the cornerstone of generalist capabilities, but it has proven elusive in the domain of physical intelligence" | "elusive" 是高级词，给 reviewer 一种"我们承认这很难"的认知 |
| Insight | "annotating the data with detailed context annotations that contain not only information about what to do but also how to do it" | 一句话 nugget |
| Approach | "detailed language labels, strategy metadata, and multimodal information such as subgoal images" + 整段说明 prompt expansion 在 image generation 的先例 | 跨域类比（image generation prompt expansion）强化 design choice |
| Evidence | 4 个粗体 bullet（Out-of-the-box / Instruction / Cross-embodiment / Compositional） | bullet 强调 emergent / 多面能力 |
| Contributions | 嵌入在 evidence bullet 里 + 末段 "strong synergy between diverse datasets and detailed contexts" | 不写传统 contribution list，把 capabilities 当 contributions |

**特殊技巧**: 用 image generation 的 prompt expansion 作为已建立的成熟先例 — 这种"跨域类比"特别有 sell power 因为它把 reviewer 拉到一个 "yes, this is a known good approach" 的舒适区。

---

### 1.6 MemoryVLA — cognitive science → memory bank

| 段 | 内容 | 修辞策略 |
|---|------|--------|
| Hook | "VLA models... have achieved remarkable progress... However, mainstream VLA models such as OpenVLA and π₀ rely solely on the current observation, thereby overlooking temporal dependencies" | 直接对标具体竞品（OpenVLA / π0），让 reviewer 立刻定位 |
| Gap | "Push Buttons tasks exhibit almost no visual difference before and after pushing... non-Markovian nature... A naive strategy is to concatenate consecutive frames... However, it faces two critical limitations: (1) quadratic complexity, (2) misalignment with single-frame pretraining distribution" | 用一个**具体例子**（Push Buttons）让 gap 直观 + 给出 obvious solution + 解释为什么不行 |
| Insight | "humans handle manipulation tasks through a dual-memory system... working memory + episodic memory (verbatim + gist)" | cognitive science 类比 → nugget |
| Approach | "we propose MemoryVLA... PCMB stores both low-level perceptual details and high-level cognitive semantics... retrieval, fusion, consolidation" | 三步流程对应 cognitive science 类比的三个组件 |
| Evidence | "71.9%, 72.7%, 96.5%, 41.2% on SimplerEnv-Bridge, Fractal, LIBERO-5, Mikasa-Robo... +14.6 on Bridge ... +26 on long-horizon real-world" | 全数字密集 |
| Contributions | 三个 bullet：framework / module design / SOTA | 经典 method paper 的 3-bullet |

**特殊技巧**: §2 (Gap) 用 "Push Buttons" 这个具体场景作 visual hook — 配合 Figure 1 让 reviewer 5 秒内理解为什么需要 memory。这是用 *example-first* 原则的标杆。

---

### 1.7 MEM — multi-scale memory

| 段 | 内容 | 修辞策略 |
|---|------|--------|
| Hook | "Efficiently and effectively endowing robotic policies with memory requires multiple levels of abstraction" | 直接断言 |
| Gap | 走读两个具体例子（occlusion handling 和 cooking ingredient tracking） + "the representation required for long- and short-term memory is likely to be very different" | 两个具体例子 + 一句概括 |
| Insight | "An effective memory architecture for robot policies should use multiple modalities to represent memories at these different levels of abstraction. ... For short-horizon, dense image-based memory; for long-horizon, language-based representation" | nugget = "different time scales need different modalities" |
| Approach | "we introduce MEM... combines two key ingredients: (1) video encoder for short-horizon dense memory, (2) language-based memory mechanism for long-horizon" | 两组件，每组件配 rationale |
| Evidence | "we integrate it into the π₀.₆ model... long-horizon tasks like cleaning up a whole kitchen or preparing a grilled cheese sandwich, which require keeping track of memories for up to fifteen minutes" | 时长 + 任务描述 |
| Contributions | 一段 narrative summary | 简洁 |

**特殊技巧**: 用 "cooking" 和 "occlusion" 两个生活化例子让 reviewer 立刻理解为什么 memory 必须分层。Hook → Gap → Insight 三段都围绕这两个例子展开 — running example throughout。

---

### 1.8 Fast-WAM — 一个尖锐的科学问题

| 段 | 内容 | 修辞策略 |
|---|------|--------|
| Hook | "Building general-purpose embodied agents requires policies that can not only map visual observations to actions, but also reason about how the physical world evolves under interaction" | 直接陈述领域 vision |
| Gap | "Most existing WAMs follow an imagine-then-execute paradigm, incurring substantial test-time latency... More fundamentally, it remains unclear whether explicit future imagination is actually necessary for strong action performance" | 一个 practical gap (latency) + 一个 conceptual gap (necessity unknown) |
| Insight | "we revisit this design choice and ask a simple question: do WAMs need to imagine future observations at test time, or do they benefit primarily from learning to model them during training? Our key idea is to decouple the video prediction objective..." | 把整篇 paper 包装成"一个被忽视的科学问题" — 这是顶级 sell |
| Approach | "Fast-WAM... preserves video co-training during training but skips future prediction at test time... MoT architecture with shared attention" + 整段实验 design 解释 controlled comparison | 把 architecture 和 controlled experiment design 放一起 |
| Evidence | "190 ms latency, over 4× faster... competitive with imagine-then-execute variants while removing video co-training causes a much larger performance drop" | 双指标：speed + necessity |
| Contributions | 三 bullet：identify question / architecture / controlled finding | "我们的贡献是回答了一个之前被忽视的问题" |

**特殊技巧**: 整篇 introduction 围绕**一个尖锐的二元问题**展开（"need imagination at test time?" Y/N）。这种 framing 让 paper 看起来像一个科学发现而非 engineering work，特别有 sell power。

---

### 1.9 DiT4DiT — video generation 作为 backbone

| 段 | 内容 | 修辞策略 |
|---|------|--------|
| Hook | "VLA models have demonstrated remarkable capabilities... Yet most existing VLA systems inherit backbones pretrained primarily on static image-text data, leaving spatiotemporal structure and physical dynamics to be learned only during downstream policy training. In parallel, video generation models have emerged as a promising alternative" | 双线 hook：VLA 缺什么 + VGM 有什么 |
| Gap | "Recent works have begun exploring this direction, typically by using video models to synthesize additional training data or by extracting latent representations to train inverse dynamics models. While encouraging, these approaches are often multi-stage rather than end-to-end" | 直接 cite 已有尝试 + 指出他们是 multi-stage |
| Insight | "We first examine whether video generation can serve as an effective proxy objective for policy learning. ... we find that video generation is a highly effective unsupervised pre-training signal" | 把 nugget 包装成"一个被验证的发现" |
| Approach | "DiT4DiT, a unified end-to-end Video-Action Model with a dual-DiT architecture... extract compact latent features from future-frame generation... dual flow-matching objective with decoupled timesteps" | 多个 design choice 列出 + 每个配 rationale |
| Evidence | "98.6% on LIBERO and 50.8% on RoboCasa-GR1... Unitree G1 deployments... improves sample efficiency by over 10× and accelerates convergence by up to 7×... robust zero-shot generalization" | 数字密集 + 多 setting |
| Contributions | 写在 abstract 里，introduction 不再列；介绍直接进 §2 | 紧凑 |

**特殊技巧**: §1 用 "two parallel lines" 修辞（VLA 这边缺 X，VGM 那边有 X），暗示自己 paper 是必然的"桥接"。

---

### 1.10 RoboMME — benchmark paper

| 段 | 内容 | 修辞策略 |
|---|------|--------|
| Hook | "Open-world robotic manipulation often requires reasoning over history... return books, wipe a table, fold laundry after observing a human demonstration" | 三个生活化例子让 motivation 直觉化 |
| Gap | "MemoryBench is the first benchmark to explicitly evaluate spatial memory, but it contains only three near-solved tasks. MIKASA-Robo introduces several history-dependent tasks, yet they remain short-horizon and lack sufficient high-quality demonstrations" | 直接 cite 现有 benchmark 并指其不足 — benchmark paper 必须做的事 |
| Insight | "Drawing inspiration from cognitive theories of human memory, RoboMME categorizes memory into four cognitive dimensions: temporal / spatial / object / procedural" | nugget = 四维分类法本身 |
| Approach | "16 tasks ... 1,600 demonstrations ... 770k timesteps ... 14 memory-augmented VLA variants based on π₀.₅ backbone... three integration mechanisms: memory-as-context / memory-as-modulator / memory-as-expert" | benchmark + ablation 双轨 |
| Evidence | "no single memory representation or integration strategy consistently performs well across all tasks ... symbolic memory excels at counting; perceptual memory is critical for time-sensitive and motion-centric behaviors" | 一个 surprising finding（"no single design dominates"）作为 sell |
| Contributions | 隐式：建立第一个综合 framework | 自然语言收尾 |

**特殊技巧**: benchmark paper 的 Insight 是 *分类法 (taxonomy)* 本身，而非新算法。RoboMME 把 4D 分类作为 nugget — 这是 benchmark paper 的标准做法（参考 BIG-Bench、MMLU 等）。

---

## 2. 横向共性提炼（10 篇都遵守的 N 条规律）

### 共性 1：开篇绝不直接讲 method

10/10 都从领域 vision / 普世原则 / 人类类比 / 政治痛点 ("closed") 开始。**没有一篇** 第一句就 "In this paper, we propose..."。

### 共性 2：Gap 段一定具体到能被指认

10/10 都不写 "limited" / "challenging"，而是 ：
- 列编号子 gap (OpenVLA, π0, π*0.6)
- 给具体失败例子 (MemoryVLA: Push Buttons, MEM: occlusion + cooking)
- 直接 cite 竞品并指其短板 (MemoryVLA, RoboMME, DiT4DiT)
- 提"obvious solution"并解释为何不行 (MemoryVLA, Fast-WAM)

### 共性 3：Insight 段必有一句"可一句话复述的 nugget"

10/10 都有 "Our key idea is..." / "Our main insight is..." / "We argue that..." / "Drawing on X, we propose Y" 形式的句子。

### 共性 4：类比 / 灵感锚点高度集中

| 锚点 | 出现 |
|------|------|
| 人类能力 | π0, π0.5, π*0.6, MEM, MemoryVLA, RoboMME |
| LLM / Foundation model 范式 | π0.7, OpenVLA, DiT4DiT |
| Cognitive science | MemoryVLA, RoboMME |
| Video generation 范式 | DiT4DiT |
| 文学引文 | π*0.6 (Heinlein), π0.7 (Tennyson) |

→ 选一个 anchor 而不是堆砌；让 reviewer 把你的 paper 挂到他已知的 mental model。

### 共性 5：Approach 段每个 design choice 都连回 Gap

10/10 都用 "This enables..." / "This avoids..." / "This addresses..." 句模把 design 连回前面提到的具体问题。

### 共性 6：Evidence 段用具体数字 + 具体任务名

10/10 都给：
- 至少一个百分比 (XX% gain) 或时长 (15 minutes / 13 hours)
- 至少一个具体任务名 (laundry folding / espresso making / cleaning a kitchen)
- 至少一个具体 baseline 名 (RT-2-X / CogACT / GR00T)

### 共性 7：长度高度收敛在 1000-1700 词

| Paper | 词数（估算）|
|-------|----|
| OpenVLA | ~900 |
| π0 | ~1100 |
| π0.5 | ~1300 |
| π*0.6 | ~600 |
| π0.7 | ~1000 |
| MemoryVLA | ~1000 |
| MEM | ~700 |
| Fast-WAM | ~1100 |
| DiT4DiT | ~1100 |
| RoboMME | ~1000 |

→ **1000 词左右是甜区**，超过 1500 就开始失去 reviewer 注意力。

### 共性 8：5-7 段是最常见的段数

不是 4，也不是 8。5-7 段正好足够走完 Hook → Gap → Insight → Approach → Evidence → Contributions 而不冗余。

### 共性 9："first to demonstrate" 高频出现

7/10 在 Evidence 或 Contributions 里有 "first to demonstrate" / "for the first time" / "to our knowledge, our work is the first" 类强宣称。这是 reviewer 直接 copy 到 "Strengths" 的 phrase。

### 共性 10：Contribution 段不一定 bullet，但一定可证伪

- Bullet 风：MemoryVLA, Fast-WAM, π0.7
- Narrative 风：π0, π0.5, π*0.6, OpenVLA, MEM, RoboMME, DiT4DiT
- 选哪种取决于 contribution 数量和类型，但**每条都必须可证伪**。

---

## 3. 跨派别风格差异（不要混搭）

### Style A · Physical Intelligence 系（π0 / π0.5 / π*0.6 / π0.7）

特征：
- Epigraph 文学引文（π*0.6, π0.7）
- 长段落、人类类比、time-scale 描述（"15 minutes", "13 hours"）
- 不堆砌百分比；强调能力 / 任务难度
- 带哲学色彩的 hook ("Open-world generalization is one of the biggest open problems...")

适合：foundation model paper、capability paper、demo-driven paper。

### Style B · 学院派 method paper（MemoryVLA / DiT4DiT / Fast-WAM）

特征：
- 直接对标具体竞品 (OpenVLA, π0)
- 数字密集（百分比 / latency / sample efficiency）
- Cognitive science 或科学问题作 anchor
- 三 bullet contribution

适合：method paper、新模块 paper、SOTA-driven paper。

### Style C · Benchmark paper（RoboMME）

特征：
- 走读多个生活化例子作 hook
- 直接 cite 现有 benchmark 列其不足
- Taxonomy 本身作为 nugget
- 强调"systematic" / "comprehensive"

适合：benchmark / evaluation framework paper。

### Style D · 系统/开源 paper（OpenVLA）

特征：
- 政治化 framing ("closed vs open")
- 强调 community impact / accessibility
- 数字 + 资源开放清单作 contribution

适合：开源 release、tool paper。

**关键纪律**: 选一种 style 写到底，不要混搭。混搭的 introduction 让 reviewer 找不到你 paper 的 identity。

---

## 4. 选哪种 style 决策树

```
你的 paper 是什么类型？
├─ Foundation / capability demonstration ─────→ Style A (PI 系)
├─ 新方法 / 新模块 / SOTA on benchmark ───────→ Style B (学院派)
├─ Benchmark / evaluation framework ──────────→ Style C
└─ 开源 / 系统 / tool ────────────────────────→ Style D
```

如果不确定，**默认走 Style B**（学院派 method paper 风格）— 它最能被 reviewer 快速 scan。
