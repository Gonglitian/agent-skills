# 6 类段落 Archetype · 句模库

> 6 类对应 `golden_skeleton.md` 的 6 段。每类给 3-5 个真实 paper 的句模 + 多个填空变体。
> 用法: 写每段时翻到对应 archetype，挑一个最贴合你 paper 类型的句模，**改写**成你的内容（不要逐字照抄 — 那是 plagiarism）。

---

## Archetype 1 · Hook 段句模

### 1A · "Field's biggest open problem"

```
[Capability X] represents one of the biggest open problems in [field]: [target system class]
only truly become [adjective] when they can [target capability].
```

来源: π0.5

### 1B · "Tension between machine and human"

```
[AI/ML systems] come in all shapes and sizes, from [example A] to [example B]. However, the
axis along which [target capability] most outpaces [machine version] is [property]: the ability
to [task description].
```

来源: π0

### 1C · "Practical mandate"

```
In order for [target system] to be useful, they must [requirement A], outside [current limitation].
While [recent advances] have demonstrated impressive results for [property], it remains an open
question how far such [systems] can [goal].
```

来源: π0.5 abstract first sentence

### 1D · "Dual-line setup"

```
[Domain A] models have demonstrated remarkable capabilities across [tasks]. Yet most existing
[systems] inherit [limitation X], leaving [property] to be learned only during [stage Y]. In
parallel, [Domain B] models have emerged as a promising alternative.
```

来源: DiT4DiT

### 1E · "Closed-vs-open" framing

```
A key weakness of [current generation of methods] is their inability to [property]. While [adjacent
field] foundation models such as [examples] are capable of [property], reproducing this scale of
[setup] for [our domain] is still an open challenge.
```

来源: OpenVLA

### 1F · "Epigraph + direct"

```
> [Epigraph quote, 1-2 lines]
> [Author], *[Source]*

[Direct first sentence connecting to paper's thesis].
```

来源: π*0.6, π0.7

---

## Archetype 2 · Gap 段句模

### 2A · "Numbered limitations"

```
However, there are [N] key reasons preventing the widespread use of [existing approach]:
1) [concrete limitation 1]; and 2) [concrete limitation 2].
```

来源: OpenVLA

### 2B · "Naive solution rebuttal"

```
A naive strategy is to [obvious solution]. However, it faces [N] critical limitations:
(1) [concrete limitation 1, with mechanism]; (2) [concrete limitation 2, with mechanism].
```

来源: MemoryVLA

### 2C · "Direct competitor critique"

```
Most existing [systems] follow [paradigm], incurring [practical issue X]. More fundamentally,
it remains unclear whether [conceptual question Y] is actually necessary for [target outcome].
```

来源: Fast-WAM

### 2D · "Visual / scenario walk-through"

```
For instance, [household / lab / driving scenario] requires [capability]. As shown in Figure 1(a),
[specific task / observation] exhibits [counterintuitive property], making it difficult to [naive
approach]. This highlights [the underlying conceptual gap].
```

来源: MemoryVLA

### 2E · "Existing benchmarks fall short"

```
[Benchmark X] is the first [benchmark type] to evaluate [aspect], but [limitation]. [Benchmark Y]
introduces [property], yet [limitation]. Consequently, existing benchmarks neither [criterion 1]
nor [criterion 2].
```

来源: RoboMME

### 2F · "Recent attempts but multi-stage"

```
Recent works have begun exploring [direction], typically by [approach 1] or [approach 2]. While
encouraging, these approaches are often [structural limitation], making [downstream issue] indirect
and leaving open [the central question of how to ...].
```

来源: DiT4DiT

---

## Archetype 3 · Insight 段句模

### 3A · "Key idea declarative"

```
Our key idea is to [decouple / combine / reformulate] [X] from [Y]. Concretely, we [operationalize
this as a design principle].
```

来源: Fast-WAM

### 3B · "Insight from analogy"

```
Cognitive science suggests that humans rely on [mechanism A] for [purpose 1], while [mechanism B]
for [purpose 2]. Inspired by these mechanisms, we propose [Method] that [bridges the analogy to
the technical design].
```

来源: MemoryVLA

### 3C · "Main insight as thesis"

```
In this work, our main insight is that [target capability] should [property]. [Justification in
one sentence].
```

来源: MEM

### 3D · "Question-driven insight"

```
In this paper, we revisit this design choice and ask a simple question: [pointed binary question]?
Our key idea is [the operational answer].
```

来源: Fast-WAM

### 3E · "Cross-domain analogy"

```
[Detailed prompts / mechanism X] improving [target metric] has precedent in other fields—[image
generation / NLP] models utilize [analogous technique] for high-quality outputs. However, in
[our domain], [the simple translation is not enough — additional consideration].
```

来源: π0.7

---

## Archetype 4 · Approach 段句模

### 4A · "We propose X with N components"

```
To this end, we propose [Method-name], a [type-of-system] that [does target capability].
[Method-name] consists of [N] key components: (i) [component 1], which [purpose 1 + rationale];
(ii) [component 2], which [purpose 2 + rationale]; and (iii) [component 3], which [purpose 3 +
rationale]. Together, these enable [capability X] (see Figure 1).
```

来源: 通用，多篇

### 4B · "Hierarchical / staged"

```
The design of [Method-name] follows a simple hierarchical architecture: we first [stage 1], and
then [stage 2]. At runtime, [the model first does X, then Y]. This simple architecture provides
[both A and B], where [low-level capability] benefits from [data source 1], while [high-level
capability] benefits from [data source 2].
```

来源: π0.5

### 4C · "Building on prior + key change"

```
Building on [prior method], we propose to [key modification], creating [Method-name]. Unlike
[prior method] which [limitation X], [Method-name] [novel property].
```

来源: π0.5

### 4D · "Two-ingredients minimalism"

```
[Method-name] combines two key ingredients: First, we use [ingredient 1] to [purpose]. Second,
we introduce [ingredient 2] in which [policy property]. This [minimalist] design can not only
[main capability], but also enables [secondary capability].
```

来源: MEM

---

## Archetype 5 · Evidence 段句模

### 5A · "Multi-benchmark headline"

```
We evaluate [Method-name] across [N] benchmarks spanning [scope]. On [benchmark 1], [Method-name]
achieves [headline number 1]; on [benchmark 2], [headline number 2]; and on [N real-world tasks]
across [M robots], it reaches [number 3], outperforming [strongest baseline] by [+X points].
```

来源: MemoryVLA, DiT4DiT

### 5B · "Time-scale impressiveness"

```
[Method-name] performs long-horizon [task class] [N to M minutes] in length, [accomplishing
specific household / dexterous task] in entirely new [setting].
```

来源: π0.5, MEM

### 5C · "Latency / efficiency centric"

```
[Method-name] runs in real time with [N ms] latency, over [M×] faster than [comparison family].
Additionally, [Method-name] improves [secondary metric] by [over X×].
```

来源: Fast-WAM, DiT4DiT

### 5D · "Capability bullets"

```
- **Out-of-the-box performance:** [Method] reliably executes [task class] without [task-specific
  post-training] across various environments.
- **[Capability 2]:** [Method] [property]
- **[Capability 3]:** [Method] [property]
```

来源: π0.7

### 5E · "First to demonstrate"

```
To our knowledge, our work is the first to demonstrate [strong claim that frames the field-shaping
result, e.g., an end-to-end learning-enabled robotic system that can perform long-horizon tasks
in entirely new homes].
```

来源: π0.5, π*0.6

---

## Archetype 6 · Contributions 段句模

### 6A · "Bullet, refutable + forward-ref"

```
We summarize our contributions as follows:
- We propose [Method-name], a [type] that [conceptual contribution] (§3).
- We design [specific module/algorithm], which [refutable mechanism claim] (§3.X, Fig. Y).
- We demonstrate, through extensive evaluation on [scope], that [Method-name] achieves
  [refutable empirical claim], outperforming [baseline] by [+X points] (§4, Table Z).
```

来源: MemoryVLA, Fast-WAM

### 6B · "Narrative + first-claim"

```
Our central contribution is a [system / framework] for [target capability], [Method-name],
together with a proof of concept that [emergent property] can emerge from this model when
trained on [appropriate data]. We provide a detailed empirical evaluation of both [Method-name]'s
[main capability] and the relevance of different [design ingredients]. To our knowledge, our work
is the first to demonstrate [strong claim].
```

来源: π0.5

### 6C · "Three-layer (architecture + module + experiment)"

```
The contributions of our work consist of:
1) A novel [architecture / framework] based on [foundation 1] and [foundation 2].
2) An empirical investigation of [recipe / training strategy / design space] for such [class of
   systems].
3) A comprehensive evaluation [scope description], demonstrating [refutable improvements].
```

来源: π0

---

## 句模使用纪律

### 1. 不要逐字照抄
即使是已发表 paper，逐字抄是 plagiarism。改写到你能用一句中文复述并自己重新写一遍英文。

### 2. 选风格一致的句模
不要在 ¶1 用 PI 风（epigraph），¶4 用学院风（数字密集），¶6 又回到 PI 风。Reviewer 会觉得 paper identity 模糊。参考 `case_studies.md` §3 (Style A/B/C/D) 选一种贯穿到底。

### 3. 句模是脚手架，不是终点
填完一遍后，**删掉所有句模痕迹**：把 "Our key idea is" 这种"过明显"的开头改成更自然的过渡（如果信息已经传达）。

### 4. 优先用与你 paper 同 style 的实例
你的 paper 是 method paper 就重点参考 MemoryVLA / Fast-WAM / DiT4DiT 的句模；是 benchmark 就 RoboMME；是 system / capability 就 π0 系。
