# Mad-Libs Introduction（整段填空版）

> 改编自 Michael Black 的 Mad-Libs Abstract（textbooks/03_writing.md §4.2），扩展到 Introduction 全段。
> 用法: 把 `[方括号]` 全部替换。锚词 (Unfortunately / In contrast / However / Therefore / We) 一律保留 — 它们是结构。

---

## 标准版（method paper）

```
[Field/task] plays a central role in [domain A] and underpins applications such as [domain B].
Recent work has approached this problem by [paradigm/family of methods], achieving impressive
results in [setting]. **However**, all of these approaches share a fundamental limitation:
[concrete limitation]. In particular, [specific failure example or scenario], where [the limitation
manifests in observable behavior].

A natural workaround is to [obvious-solution]. **Yet**, this strategy fails for two reasons:
(1) [reason 1, with mechanism]; and (2) [reason 2, with mechanism]. As a result, [downstream
problem] remains an open challenge.

**Inspired by** [analogy / cognitive-science / foundation-model / human-experience], we observe
that [key insight in one sentence — this is your nugget]. **Our key idea is** to [one-sentence
restatement of nugget operationalized as a design principle].

**To this end, we propose** [Method-name], a [type-of-system] that [does X]. [Method-name]
consists of [N] key components: (i) [component 1], which [purpose 1]; (ii) [component 2], which
[purpose 2]; and (iii) [component 3], which [purpose 3]. Together, these components enable
[capability X] without [trade-off Y] (see Figure 1).

**We evaluate** [Method-name] on [N] benchmarks spanning [scope], including [benchmark 1],
[benchmark 2], and [N real-world tasks on M robots]. [Method-name] achieves [headline number,
e.g., 96.5% on LIBERO], outperforming [baseline] by [+X points] on [hardest benchmark].
**Notably**, on [most-impressive scenario, e.g., long-horizon tasks], [Method-name] reaches
[secondary number], a +[Y points] improvement over the prior state of the art. **To our
knowledge, this is the first** [strong claim].

**We summarize our contributions as follows:**
- We propose [Method-name], a [conceptual contribution] that addresses [main gap] (§3).
- We design [specific module/algorithm], which [refutable mechanism claim] (§3.X, Fig. Y).
- We demonstrate, through extensive evaluation on [scope], that [Method-name] achieves
  [refutable empirical claim], including [+X points on benchmark 1] and [+Y points on benchmark 2]
  (§4, Table Z).
```

---

## Foundation / capability paper 版（PI 系风格）

```
[Epigraph: 文学引文，1-2 行]
— [Author], *[Source]*

[Capability X] represents one of the biggest open problems in [field]: [systems / agents / robots]
only truly become [useful / general / robust] when they can [target capability]. Learning-based
systems offer a path to [enabling X], particularly with recent advances that have enabled
[scalable learning systems / foundation models] in domains ranging from [domain 1] to [domain 2].
**However**, [the diversity / complexity / variability] of [target setting] requires more than
just [scale / data / compute]: [we need to design X that does Y].

[A person / human / expert] can [solve target task] by drawing on [a richer source of information].
**Analogously**, we hypothesize that [systems should also] [transfer / compose / leverage] [variety
of information]. Some of these sources are [direct experience], some require [transfer from neighbor
domains], and some represent [entirely different modalities such as Z]. The heterogeneity of these
sources presents a major obstacle, but [recent advances in [VLA / LLM / foundation-model paradigm]]
provide us with a toolkit that makes this possible: [framework property].

**In this paper**, we leverage this observation to design [system / framework / model] that
[utilizes heterogeneous sources / generalizes broadly]. Building on [prior backbone], we propose
[Method-name] ("[pronunciation guide]"), which can [target capability] even in [most-extreme
test setting, e.g., entirely new homes]. [Method-name] draws on experience from [N sources]: ...
The overwhelming majority of training examples (e.g., [X% during training phase]) do not come
from [target task / target embodiment], but from [other sources]. **Nonetheless**, [Method-name]
is able to [target task] in [extreme test setting], performing [most-impressive specific task]
that span [time-scale, e.g., 10–15 minutes].

The design of [Method-name] follows a [adjective] hierarchical architecture: we first [stage 1],
and then [stage 2]. At runtime, ... [3-5 sentences explaining design rationale tied back to the
heterogeneity / generalization theme].

**Our central contribution is** a system for training a highly [adjective] [system class],
[Method-name], together with a proof of concept that [target capability] can emerge from this
model when it is trained on [appropriately-described data]. We provide a detailed empirical
evaluation of both [Method-name]'s [main capability] and the relevance of different [design
ingredients]. **To our knowledge, our work is the first to demonstrate** [strong claim].
```

---

## Benchmark paper 版

```
[Target task] often requires [reasoning over X / capability Y]. For instance, [household robot
example 1], [example 2], or [example 3]. In such scenarios, relying solely on [naive baseline] is
insufficient. Effective [task] depends on the ability to [target capability], which we broadly
refer to as [concept Z].

Prior work incorporates [Z] into [target system] through [N] main representations: (1) [type 1],
which [property 1]; (2) [type 2], which [property 2]; and (3) [type 3], which [property 3]. While
demonstrating the importance of [Z], these methods rely on different [backbones / protocols],
making it unclear which [design] generalizes across tasks. Progress is further limited by the
absence of benchmarks that capture [target requirements]. [Benchmark X] is the first to evaluate
[narrow aspect], but [limitation]. [Benchmark Y] [property], yet [limitation]. **Consequently**,
existing benchmarks neither [criterion 1] nor [criterion 2].

To address these limitations, we present **[Benchmark-name]**: a [scope adjective] [type of
benchmark] designed for [explicit purpose]. Drawing inspiration from [theoretical framework, e.g.,
cognitive theories of memory], [Benchmark-name] categorizes [Z] into [N] [cognitive / functional]
dimensions: (1) [dim 1] for [purpose]; (2) [dim 2] for [purpose]; ...

Building on [Benchmark-name], we develop a family of [N] [variants / models] based on the
[backbone] backbone to systematically study how different [design axes] influence [target metric]. ...

**Interestingly**, our experiments show that [surprising finding, e.g., no single design dominates].
Instead, [task-dependent finding]: [design A] excels at [task family 1], while [design B] is
critical for [task family 2]. ... Together, these results establish [contribution claim].
```

---

## 锚词速查表（不要省略！这些是结构而不是修辞）

| 位置 | 锚词 | 中文心智 |
|------|------|---------|
| Hook 末尾 → Gap 开头 | **However / Yet / Despite this** | 转折，引出问题 |
| Gap 内部第二个问题 | **Moreover / In addition / Furthermore** | 加码 gap 严重性 |
| Gap → Insight | **Inspired by / Drawing on / We observe / Our key idea is** | 翻转视角 |
| Insight → Approach | **To this end / Building on / Following this** | 把抽象变具体 |
| Approach 内部并列 design | **First / Second / Third / In particular** | 列举 |
| Approach → Evidence | **We evaluate / Our experiments / Across** | 进入实证 |
| Evidence 内最强项 | **Notably / In particular / Most importantly** | 高亮 |
| Evidence → Contributions | **In summary / We summarize our contributions / Our central contribution is** | 收尾 |

**反模式**: 用 *Furthermore / Moreover / Thus* 在每段开头作填充。这些词如果不承担结构作用，必须删。

---

## 用完后做这件事

把你填好的 Mad-Libs 草稿读一遍，**删掉所有锚词**，再读一遍。如果删掉锚词后段落仍能讲清 story，说明锚词只在装饰；保留它们但意识到它们应该承担结构作用。

如果删掉锚词后段落跳跃或不连贯，**保留锚词** — 它们正在做结构性工作。
