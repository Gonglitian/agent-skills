# Pre-Writing Form for Introduction · 动笔前 13 问

> 改编自 LARG/Stone Lab 的 Pre-writing Form (10 问) + Michael Black 12-Q pre-check + Tokekar 5-Qs，专门聚焦 Introduction。
> **建议节点**: T-4 周（投稿前一个月）逐字回答，发给导师。导师审完后再开始写 introduction。

---

## 使用说明

- 用**中文**作答（让自己思考清楚），最后再翻成英文。
- 每题答案 **2-5 句话**；写不出来说明这题还没想清楚，别糊弄。
- 写完所有 13 题后，把 **Q5 (nugget) + Q9 (contributions) + Q10 (impressive task) + Q12 (single takeaway)** 四题的答案抽出来，看这 4 句话连起来能否独立讲完整篇 paper 的 story。

---

## 13 问

### Q1. **这篇 paper 解决什么 problem？**
*只描述 problem，不要包含 solution。试着把 "problem" 写成"现状的什么是 broken 的 / 不够的"。*

中文回答:
________________________________________________________________________________

### Q2. **目标读者是谁？哪个 sub-community 会对这工作感兴趣？**
*具体到能想象 reviewer 名单的程度。"VLA researchers" 太宽；"VLA researchers working on long-horizon manipulation" 才对。*

中文回答:
________________________________________________________________________________

### Q3. **现有方法在 Q1 这个 problem 上的具体局限是什么？为什么这些 obvious solutions 不够？**
*列 2-3 个具体方法 + 每个的具体局限。如果回答里有 "limited" / "challenging" / "expensive" 等抽象词，refine 到具体机制。*

中文回答:
________________________________________________________________________________

### Q4. **你的 Hypothesis 是什么？**
*Black 12-问中的 "My hypothesis is..."。即使最终不写进 paper，也要写出来。Hypothesis ≠ method；hypothesis 是你对 problem 本质的判断。*

中文回答:
________________________________________________________________________________

### Q5. **★ Nugget — 你这篇 paper 的 single ping 是什么？**
*用一句话写。如果写不出一句话，这篇 paper 还不该开始写 introduction。Nugget 不是 "我们用了 X 模块"，是 "我们看到 problem 可以这么看 / 这么转化"。*

中文（一句话）:
________________________________________________________________________________

英文（一句话，将出现在 Insight 段）:
________________________________________________________________________________

### Q6. **类比 / 灵感来源是什么？为什么这个 anchor 自然？**
*4 选 1 + 一句解释: ☐ 人类能力  ☐ Cognitive science  ☐ LLM/Foundation model 范式  ☐ 其他成熟范式（image gen / web data / RL）。如果都不合适，跳过。*

中文回答:
________________________________________________________________________________

### Q7. **方法是什么？关键 design choices 有哪些？**
*列 2-3 个 design decisions，每个写一句 rationale（"我们这么设计是因为 ...，否则会 ..."）。这些将进 Approach 段。*

中文回答:
________________________________________________________________________________

### Q8. **Teaser Figure（Fig. 1）会画成什么样？**
*画在草稿纸上，描述给同事 5 秒讲清。Fig. 1 必须在 introduction 第 3-4 段出现 in-text reference。*

中文描述（输入 → 中间 nugget → 输出）:
________________________________________________________________________________

### Q9. **★ 主 contributions 是什么？（3-5 条，每条可证伪）**
*每条用 "We [verb] [X], showing that [refutable claim], (§Y / Table Z)" 的形式写。SPJ refutable rule。*

1. ___________________________________________________________________________
2. ___________________________________________________________________________
3. ___________________________________________________________________________

### Q10. **★ 你最 impressive 的实验数字 / 任务是什么？**
*选 1-2 个能放进 Evidence 段的"硬数字"或"具体场景"。例: "+14.6 over CogACT on Bridge"，"15-minute kitchen cleaning"，"190 ms latency, 4× faster"。*

中文（含具体数字 / 任务名）:
________________________________________________________________________________

### Q11. **现有最相关的 prior work 是哪 2-3 个？他们错在哪 / 缺什么？**
*只列与本 paper 直接对话的工作。Related work 大部头不在这一节，留给 §2。*

1. ___________________________________________________________________________
2. ___________________________________________________________________________
3. ___________________________________________________________________________

### Q12. **★ 如果 reviewer 只记得这篇 paper 一件事，你希望是什么？**
*用一句话写。这必须 ≈ Q5 nugget + Q10 most impressive。如果两者无法浓缩成一句，paper 的 single ping 还没收敛。*

中文（一句话）:
________________________________________________________________________________

### Q13. **限制 / 不足是什么？怎么 frame 这些以让 reviewer 不变成 attack？**
*老实承认限制是技术展示，不是示弱。每条限制配一句 "we mitigate by X / we leave for future work because Y"。*

中文回答:
________________________________________________________________________________

---

## 核对：4 句 story 测试

把 Q5、Q9 第一条、Q10、Q12 的答案抽出来，连成 4 句：

```
[Q5 nugget]: __________________________________________
[Q9.1 main contribution]: __________________________________________
[Q10 most impressive evidence]: __________________________________________
[Q12 single takeaway]: __________________________________________
```

读这 4 句连起来。reviewer 看完只能记住这 4 句的话，他知道你 paper 在做什么吗？

☐ 是 → 可以开始写 introduction
☐ 否 → 回去 refine Q5 / Q9 / Q12

---

## 提交给导师时的格式

```
To: [导师]
Subject: [Paper Codename] Pre-writing form (T-4 weeks)

[导师姓]，

附上下次投稿的 pre-writing form。如果你只想看 4 句话版本：

[Q5 nugget]
[Q9.1 main contribution]
[Q10 most impressive evidence]
[Q12 single takeaway]

完整 13 问回答见下文。希望听你的反馈，特别是 Q3 (gap 是否真实)、Q5 (nugget 是否清晰)、
Q9 (contributions 是否互不重叠且可证伪)。

谢谢，
[你]

---

[完整 13 问回答附在下方]
```

---

## 框架引用

> *"I'd like everyone to have the sentence 'My hypothesis is…' even if we do not include it in the paper."* — Michael Black

> *"When reading this, I am looking at it as if I were a reviewer. Please answer the questions as if they are being read by someone who is not previously familiar with your work."* — LARG/PeARL pre-writing form
