# 投稿前 Introduction 自检清单（25 项）

> 用法: 写完 / 改完 introduction 后逐项过。任何 ❌ 都要返工对应段落，**不接受"差不多就行"**。
> 推荐顺序: 先全部跑过一遍打 ✓/❌，再统一返工 ❌ 项。
> 这份 checklist 是从 SKILL.md 工作流里抽出来的"质量门"，应当在 T-1 周和 T-1 天各跑一次。

---

## A. 结构（6 项）

- [ ] **1. 6 段骨架对位完整**：Hook / Gap / Insight / Approach / Evidence / Contributions 每段都能识别（即便段数是 5 或 7，每段功能必须明确）。
- [ ] **2. ¶1 Hook 不出现 method 名**：方法名 first appearance 在 ¶3 或 ¶4。
- [ ] **3. ¶2 Gap 不是 related work dump**：直接对话 2-3 篇 prior work；不评述领域 5 年历史。
- [ ] **4. ¶3 Insight 有一句话 nugget**：用 "Our key idea is..." / "We argue that..." / "Inspired by..." 形式。能一句中文一句英文复述。
- [ ] **5. ¶6 Contributions 可证伪 + 带 forward reference**：每条都能想象一个具体实验拒绝它，且配 §X / Table Y / Fig Z 跳转。
- [ ] **6. §2 Related Work 不在第一页**：会议传统允许的话（如 robotics）也要让 §2 从第 2 页开始。

---

## B. Story / 节奏（4 项）

- [ ] **7. Topic sentence 抽出能讲完整 story**：把每段第一句抽出来连成一段，独立读能讲清 paper 在做什么。
- [ ] **8. 锚词节律完整**：找到这些过渡词的位置 — *However / Yet*（Hook → Gap）、*Inspired by / Our key idea*（Gap → Insight）、*To this end*（Insight → Approach）、*We evaluate*（Approach → Evidence）、*In summary*（Evidence → Contributions）。任何缺失都会让节奏断。
- [ ] **9. Goal-Problem-Solution 节律可识别**：每段内部都能看到 "我们要做 X / X 难 / 我们的解 / 这解又带来子问题 / 我们的子解" 的微节律（Black GPS 递归）。
- [ ] **10. 段间过渡句承担工作**：每段最后一句要么承上（"Despite this progress, ..."）要么启下（"To address these challenges, we propose ..."）。不是孤立陈述。

---

## C. 内容质量（5 项）

- [ ] **11. Gap 是具体的，不是 "limited"**：至少有一个具体例子、具体竞品名、或编号子 gap。
- [ ] **12. Insight 不等于 contribution**：nugget 是"原来 problem 可以这么看"；contribution 是"+15% gain"。两者不能混。
- [ ] **13. 每个 design choice 连回 gap**：¶4 Approach 段每条 design 都用 "This enables / addresses / avoids" 句模显式连回 ¶2 提到的某个具体问题。
- [ ] **14. Evidence 段含具体数字 + 具体任务名 + 具体 baseline**：至少各一个。例: "+14.6 over CogACT on Bridge" 而非 "significant improvement"。
- [ ] **15. 至少一句"first to demonstrate"或同等强宣称**（如果合理）：reviewer 直接 copy 到 "Strengths"。

---

## D. Page-1 视觉 / 排版（4 项）

- [ ] **16. Figure 1 (teaser) 在第一页且 ≠ 架构图**：是 5 秒说明书（输入→nugget→输出）。
- [ ] **17. Figure 1 有 in-text reference**：在 ¶3 或 ¶4 出现 "see Figure 1" / "as illustrated in Fig. 1"。
- [ ] **18. Contributions 不跨页**：完整保留在第一页底部。如果会跨页，缩短 ¶2 或合并 contribution 条。
- [ ] **19. 第一页没有 Related Work**：见 ¶6。

---

## E. 语言 / ESL（3 项）

- [ ] **20. 没有 "Recently, with the rapid development of..." 套话开头**。
- [ ] **21. 没有引用作主语**："*[Smith 2020] proposes...*" 全部改写为 "*Smith et al. (2020) propose...*" 或 "*Prior work proposes X [Smith 2020].*"
- [ ] **22. Self-grep 清单过关**：grep `recently | thus | hence | moreover | furthermore | besides | we believe | we think | many | a lot of | various | significant`，每次出现都审视是否承担 work。85% 应当删除。

---

## F. 全局（3 项）

- [ ] **23. 总长 800-1500 词**：少于 800 信息密度不够；多于 1500 reviewer 失去耐心。
- [ ] **24. 朗读一遍无卡顿**：用 macOS `say` 或 TTS 读一遍，标注卡顿位置；这些位置要么句太长要么节奏怪。
- [ ] **25. 找一个非项目内 labmate 读完后能复述 nugget**：如果他/她答不出 "this paper's key idea is X"，¶3 Insight 没写好。

---

## 评分

- ≥ 23/25：可以投。剩余几项小修。
- 18-22/25：introduction 还有结构 / 节奏问题；至少再迭代一轮。
- < 18/25：introduction 没准备好；回去用 `templates/pre_writing_form.md` 重答 13 问。

---

## T-1 周 vs T-1 天 的不同侧重

**T-1 周**: 重点跑 A / B / C 三组（共 15 项）— 这些需要时间返工。

**T-1 天**: 重点跑 D / E / F 三组（共 10 项）— 这些是 polish + 视觉修。
