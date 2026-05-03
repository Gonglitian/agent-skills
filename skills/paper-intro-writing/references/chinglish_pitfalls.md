# Chinglish Pitfalls in Introduction Writing

> 来源: Sida Peng 论文写作模板 + MLNLP-World/Paper-Writing-Tips + LARG pre-writing form 30 条 + 10 篇 famous paper 反向比对。
> 母语 reviewer 不是刻意针对你的语言；他们只是在阅读疲劳下把"读不顺"解读为"思考不清"。Tokekar: *"If the reviewer is unsure about what you did, they may make the most uncharitable interpretation."*

---

## 等级 1 · 句子结构层（高频且毁印象分）

### 1.1 引用作主语

- ❌ *"[Smith 2020] proposes a new method..."*
- ✅ *"Smith et al. (2020) propose a new method..."*
- ✅ *"Prior work proposes X [Smith 2020]."*

理由: 引用是"标注"，不是"句子的 actor"。

### 1.2 Comma splice（逗号连接两个独立句）

- ❌ *"Existing methods are limited, they cannot generalize to new objects."*
- ✅ *"Existing methods are limited; they cannot generalize to new objects."*
- ✅ *"Existing methods are limited, and they cannot generalize to new objects."*
- ✅ *"Existing methods are limited. They cannot generalize to new objects."*

### 1.3 主谓数不一致

- ❌ *"A series of works has shown that..."* (✗ 和 ✓ 都常见，看上下文)
- ✅ *"A series of works have shown that..."* (works 复数时)
- ❌ *"The set of approaches are limited."* (set 单数)
- ✅ *"The set of approaches is limited."*

### 1.4 The vs. a vs. 无冠词

| 场景 | 选 |
|------|---|
| 第一次提到的具体物 | *a / an* |
| 已提到，再次指代 | *the* |
| 类指（"狗会叫"）| *无冠词* 或 *the dog* |
| 抽象名词（generalization, robustness）| 通常无冠词 |
| 唯一对象（the world / the field）| *the* |

- ❌ *"We propose new method that ..."*
- ✅ *"We propose a new method that ..."*
- ❌ *"VLA model has shown promise."* (类指但单数)
- ✅ *"VLA models have shown promise."*

---

## 等级 2 · 词汇层（reviewer 一眼看出非母语）

### 2.1 过量使用结构副词

- *Thus / Hence / Moreover / Furthermore / Therefore / Besides* — **85% 可删**
- 留下来的必须承担**真正的逻辑过渡**作用，不是装饰
- 替代策略：用更具体的连接词
  - *Thus* → *As a result* / *Consequently* / *In particular*
  - *Moreover* → *In addition* / *Furthermore* (但都谨慎用)
  - *Besides* → 几乎永远删

### 2.2 "We believe / We think / Should / Want to"

LARG 规则: *"Don't comment on what we 'believe'. Instead use words such as 'expect' or 'hypothesize'."*

- ❌ *"We believe our method works because..."*
- ✅ *"We hypothesize that our method works because..."*
- ✅ *"We argue that..."*
- ❌ *"This should improve performance."*
- ✅ *"This is expected to improve performance under [condition]."*
- ❌ *"We wanted to test whether..."*
- ✅ *"We test whether..."*

### 2.3 "Showing / Demonstrating" vs. "Evaluating"

LARG: *"Instead of talking about 'showing' or 'demonstrating' an effect, talk about 'evaluating' a hypothesis. We're doing science, not trying to sell a product."*

- ❌ *"We show our method's effectiveness."*
- ✅ *"We evaluate whether our method [refutable claim]."*

### 2.4 "Significant / Significantly" 滥用

中文 PhD 偏爱 *significant*，但它在统计语境有专义。日常 hype 用 *substantial / notable / sizeable*。

- ❌ *"We achieve significant improvement."*
- ✅ *"We achieve a +14.6 point improvement over CogACT."* (用具体数字)
- ✅ *"We achieve a substantial improvement (+14.6 points)."* (实在要副词)

### 2.5 Respectively 用错位置

- ❌ *"Respectively, X gets 90% and Y gets 80%."*
- ✅ *"X and Y achieve 90% and 80%, respectively."*

### 2.6 与具体名词搭配的弱动词

- ❌ *"do experiments"* → ✅ *conduct experiments*
- ❌ *"make a comparison"* → ✅ *compare X and Y*
- ❌ *"have improvement"* → ✅ *improve / yield gains*
- ❌ *"get better result"* → ✅ *outperform / surpass*

---

## 等级 3 · 段落 / 修辞层

### 3.1 Topic sentence 缺失

每段第一句必须告诉 reviewer 这段在说什么（Sida Peng 规则）。

- ❌ 段落开头: *"Recently, with the rapid development of vision-language models, a lot of works have ..."* (没有 message，只有时间和趋势)
- ✅ *"VLA models suffer from temporal blindness: they treat each step as Markovian when manipulation tasks are not."* (有具体 claim)

### 3.2 "Recently / In recent years / With the rapid development of"

- ❌ *"Recently, with the rapid development of deep learning, X has attracted increasing attention."*
- 这是 ESL 引论第一句最高频套话，reviewer 一眼判定 "low signal"
- ✅ 用具体的领域 vision 或 problem 直接开篇（见 `hook_strategies.md`）

### 3.3 段落内部不只讲一个 message

Sida Peng: *"一段文字只讲一个 Message。"*

- 如果你的段落里出现了 "On the other hand" / "另一方面" 类转折，先停下来：是不是该拆成两段？

### 3.4 写"我做了什么"而非"我发现了什么"

Ernst: *"Do not write your paper as a chronological narrative of all the things that you tried."*

- ❌ *"We first tried using attention. Then we found it didn't work, so we used flow matching..."*
- ✅ *"We use flow matching to represent continuous action distributions, enabling 50 Hz control."*

---

## 等级 4 · Introduction-specific Pitfalls

### 4.1 Related work 在第一页

SPJ rule: *"This related work section is like a sandbar between your reader and your key idea."*

- ❌ Introduction 第二段开始 cite 5+ 论文 review 整个领域历史
- ✅ Introduction 只 cite 直接对话的 2-3 篇关键 prior work（在 Gap 段）

### 4.2 Contribution 不可证伪

- ❌ *"We propose a novel attention mechanism for VLA."* (无法证伪)
- ✅ *"Our attention mechanism reduces KV cache by 4× at iso-perplexity on LIBERO-long."*

### 4.3 没有 forward reference

- ❌ *"We achieve state-of-the-art on multiple benchmarks."*
- ✅ *"We achieve 96.5% on LIBERO and 71.9% on Bridge (§4.2, Table 2)."*

### 4.4 Method name 出现在第一句

- ❌ ¶1 第一句: *"In this paper, we present X, a novel ..."*
- ✅ ¶1 是 Hook（vision / problem），方法名 first appears in ¶3 (Insight) 或 ¶4 (Approach)。

### 4.5 用 "many / a lot / various" 代替具体数字

- ❌ *"Many existing methods suffer from..."*
- ✅ *"Recent VLA models such as OpenVLA, π0, and CogACT all rely on single-frame inputs."*

---

## Self-grep 清单（写完 introduction 后过一遍）

把这些词在你 introduction 里 grep 一下，看每个是否承担 work：

```
Recently | In recent years | With the rapid development of
Thus | Hence | Moreover | Furthermore | Besides
We believe | We think | should | want to
significant | significantly
many | a lot of | various | several existing
[XX 2024]  ← 检查是否引用作主语
```

如果某个词出现 > 3 次，强制每次重新审视：是结构作用，还是装饰？

---

## 母语者 review 时高频指出的 5 条（统计自实际 reviewer comments）

1. *"The introduction reads more like a literature review than a motivation."*  
   → 修复: 把 related work 移到 §2；¶2 Gap 只对话 2-3 篇直接 prior。
2. *"It's unclear what's novel."*  
   → 修复: ¶3 Insight 段的 nugget 写得不够明显。加 "Our key idea is..." 一句。
3. *"The contributions are vague."*  
   → 修复: 每条 contribution refutable + forward reference。
4. *"The connection between the motivation and the method is weak."*  
   → 修复: ¶4 Approach 每个 design choice 用 "This addresses [Gap 段提到的具体问题]" 显式连回。
5. *"Some sentences are hard to parse."*  
   → 修复: 删 hedge 词、删冗余副词、改主动语态、把 24+ 词的句子拆成两句。

---

## 推荐工具

- **Grammarly** + **LanguageTool**：句子级
- **[Academic-Writing-Check](https://github.com/devd/Academic-Writing-Check)**：weasel words / passive voice
- **TTS 朗读**：投稿前用 macOS *say* 或 Google TTS 读 introduction 一遍。机械朗读暴露节奏怪的句子（Eisner 风）。
- **Labmate review**：找一个非中文母语 labmate 读你的 introduction，问他 "after reading, what do you think this paper is about?" 如果他答不出 nugget，你的 ¶3 没写好。
