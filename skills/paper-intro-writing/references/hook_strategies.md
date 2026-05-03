# 4 类开篇 Hook · Archetypes

> Hook = ¶1。它的工作只有一个：让 reviewer 决定继续读 ¶2。
> 风格选择由 paper 类型决定 — 见 `case_studies.md` §3 (Style A/B/C/D)。

---

## 类型 1 · Vision-Driven Hook

**心智**: "这个领域有一个公认的终极目标，但现状离它很远。"

**适合**: foundation paper、capability paper、open-world paper。

**句模**:
- *X represents one of the biggest open problems in [field]: [systems/agents] only truly become [useful adjective] when they can [target capability].*
- *Building [target system class] requires [capability A] and [capability B]; recent advances have begun to [progress] but [missing piece].*
- *In order for [agents] to [achieve goal], they must [requirement], outside [current limitation].*

**真实实例**:
- π0.5: *"Open-world generalization represents one of the biggest open problems in physical intelligence: embodied systems such as robotic arms, humanoids, and autonomous vehicles only truly become useful when they can leave the lab and handle the diverse situations and unexpected events that occur in the real world."*
- Fast-WAM: *"Building general-purpose embodied agents requires policies that can not only map visual observations to actions, but also reason about how the physical world evolves under interaction."*
- π*0.6: *"In order for robots to be useful, they must perform practically relevant tasks in the real world, outside of the lab."*

**陷阱**:
- ❌ Vision 太宽（"AI is changing the world"）
- ❌ Vision 不连接到本 paper 后面的 specific gap
- ❌ Vision 段写成 abstract 复述

---

## 类型 2 · Human-Analogy Hook

**心智**: "看，人能轻松做这事；机器为什么不行？"

**适合**: cognitive-inspired method paper、memory paper、generalization paper、learning-paradigm paper。

**句模**:
- *[Humans / experts / a person] can [target capability] by drawing on [richer source]. [Analogously], we hypothesize that [systems should] [transfer/compose/leverage] [variety].*
- *Cognitive science suggests that humans rely on [mechanism A] for [purpose 1], while [mechanism B] for [purpose 2]. Inspired by these mechanisms, we propose [Method].*
- *[Humans / a person] acquire new skills through [process], eventually achieving [outcome]. Similarly, [systems], though flexible for [property], require [process] to achieve [outcome].*

**真实实例**:
- π0: *"the axis along which human intelligence most outpaces machine intelligence is versatility: the ability to solve diverse tasks situated in varied physical environments..."*
- π0.5: *"A person can draw on a lifetime of experience to synthesize appropriate solutions to each of these challenges. Not all of this experience is firsthand, and not all of it comes from rote practice..."*
- π*0.6: *"Humans acquire new skills through repeated practice, eventually achieving mastery. Similarly, general-purpose robotic foundation models like VLA models, though flexible for task specification through prompts, require practice to achieve mastery."*
- MemoryVLA: *"Research in cognitive science demonstrates that humans handle manipulation tasks through a dual-memory system... working memory + episodic memory."*
- MEM: *"the robot's memory must represent past events at multiple levels of granularity: from long-term memory that captures abstracted semantic concepts (e.g., a robot cooking dinner should remember which stages of the recipe are already done) to short-term memory..."*

**陷阱**:
- ❌ 类比太松（"Humans can do X, so machines should too" 不带具体机制）
- ❌ 类比与 method 设计不对位（说人脑有 A/B/C，但方法只对应 A）
- ❌ 把类比写成科普，占据太多 word budget

---

## 类型 3 · Foundation-Model-Analogy Hook

**心智**: "LLM/VLM/image-gen 这条路证明了 [paradigm]，我们要在 robot/embodied 这边做同样的事。"

**适合**: scaling paper、cross-domain transfer paper、新 backbone paper。

**句模**:
- *[LLMs / Foundation models] operate on a principle that [generalist capabilities emerge from training on large and diverse datasets]. [Capability] represents arguably the cornerstone of [generalist capabilities], but it has proven elusive in [our domain].*
- *Existing foundation models for [vision / language] such as [X / Y / Z] are capable of [these types of generalization], stemming from [their pretraining data].*
- *Detailed [prompts / context] improving foundation model performance has precedent in other fields—[image and video generation models utilize prompt expansion for high-quality outputs].*
- *In parallel to [our domain], [adjacent domain] models have emerged as a promising alternative: by [property], they learn [rich priors].*

**真实实例**:
- π0.7: *"Foundation models operate on a principle that generalist capabilities emerge from training on large and diverse datasets. Large language models exemplify this through fact recall, semantic knowledge composition, problem-solving requiring unexpected connections."*
- OpenVLA: *"existing foundation models for vision and language such as CLIP, SigLIP, and Llama 2 are capable of these types of generalization and more, stemming from the priors captured by their Internet-scale pretraining datasets."*
- DiT4DiT: *"In parallel, video generation models (VGMs) have emerged as a promising alternative: by synthesizing temporally coherent and physically plausible futures video frames, they learn rich motion priors..."*

**陷阱**:
- ❌ 把 LLM 成功直接套到 robotics 而不论证迁移性
- ❌ 类比层级太抽象（"LLM 用了 transformer，所以我们也用 transformer"）
- ❌ 让 reviewer 觉得本 paper 的 contribution 只是 "搬一搬 trick"

---

## 类型 4 · Epigraph + Direct-Statement Hook

**心智**: 一句文学引文（设氛围）+ 一句直接断言（落地）。把 paper 升格为 manifesto。

**适合**: PI 系风格、ICLR/NeurIPS oral candidate、conceptual paper、综述性 capability paper。

**句模**:
```
> [Epigraph quote, 1-2 行]
> 
> [Author], *[Source]*

[Direct statement that connects the epigraph to the paper's central argument].
```

**真实实例**:
- π*0.6: 
  > *"It's amazing what you can learn if you're not afraid to try."*  
  > Robert A. Heinlein, *Have Space Suit–Will Travel*
  
  + "Humans acquire new skills through repeated practice, eventually achieving mastery..."
- π0.7:
  > *"I am a part of all that I have met."*  
  > Alfred, Lord Tennyson, *Ulysses*
  
  + "Foundation models operate on a principle that generalist capabilities emerge from..."

**陷阱**:
- ❌ 引文与 paper 主题关联牵强 → reviewer 觉得装腔作势
- ❌ 引文段落 + 紧跟的解释段加起来过长 → 占了 hook 段全部预算
- ❌ 在 method paper（Style B）使用 → 与 paper 类型不匹配会显得不严肃

**保险做法**: 选一篇你最尊敬的 PI 系 paper 作为 reference；如果你的 paper 是同类，就大胆用；如果是 method paper，谨慎用。

---

## 选择决策树

```
你的 paper 主要 selling point 是什么？
├─ 一种新的 generalist 能力 / open-world capability  ─→ Type 1 (Vision)
├─ 一个新的 inductive bias / 灵感来源                  ─→ Type 2 (Human-analogy)
├─ 把另一个领域成熟的 paradigm 引入                    ─→ Type 3 (Foundation-model-analogy)
├─ Foundation paper / capability demo / manifesto       ─→ Type 4 (Epigraph)
└─ 不确定                                              ─→ Type 1（最安全）
```

---

## 把 Hook 写好的 3 个 micro-tips

1. **第一句不要超过 25 词**。reviewer 视线在第一行停留时间最长；长句让他疲劳。
2. **第一段不要出现你 paper 的方法名**。方法名进 Insight / Approach 段。Hook 段只有 vision / problem。
3. **Hook 末尾必须留一个张力**（"Yet" / "However" / "Despite this"），让 reviewer 自然进入 ¶2 Gap。
