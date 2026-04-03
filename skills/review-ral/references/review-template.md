# RA-L Review Output Template

Use this exact structure for the English review output (`review_en.md`).
All fields must be filled. Character limits are hard — PaperCept will reject if exceeded.

---

## Assessment / Evaluation Section

```
Paper contribution:        [Exceptional / Major / Minor / Questionable / None]
Technical quality:         [Excellent / Good / Fair / Poor]
Originality:               [Excellent / Good / Fair / Poor]
Thoroughness of results:   [Excellent / Good / Fair / Poor]
Clarity of presentation:   [Excellent / Good / Fair / Poor]
Adequacy of citation:      [Excellent / Good / Fair / Poor]
Relevance to field:        [Excellent / Good / Fair / Poor]
```

### Justification for Each Score

For each score, write 1-2 sentences explaining the rating. This is for the reviewer's
own reference and for the Chinese notes — it does not go into PaperCept directly, but
informs the Comments to Author.

---

## Recommendation Section

```
Overall Recommendation:    [Accept / Revise and resubmit / Reject / Unsuitable due to scope]
Wish to see revision:      [Yes / No]
Reviewer confidence:       [Very confident / Confident / Fairly confident / Not very confident / No confidence]
Multimedia attachment:     [Yes / No]
Multimedia justification:  [Brief comment, e.g., "The video clearly demonstrates real-time performance."]
Best paper award:          [Yes / No]
```

---

## Confidential Comments to the Editorial Staff

**Hard limit: 2000 characters (about 33 lines)**

These comments are NOT sent to authors. Use this section for:
- Your honest assessment of the paper's significance
- Any concerns about ethics, dual submission, or plagiarism
- Context for your recommendation that you don't want authors to see
- How confident you are in your assessment and why

Template:
```
This paper presents [brief description]. 

[Your honest assessment — is this a borderline case? Are you uncertain about something?]

[Any flags: plagiarism concerns, overlap with known work, ethical issues, etc.]

[Recommendation context: e.g., "I recommend revise-and-resubmit because the core idea has
merit but the experimental evaluation has significant gaps that need to be addressed."]

Confidence note: [Why you rated your confidence the way you did]
```

---

## Comments to the Author

**Hard limit: 10000 characters (about 166 lines)**

This is the main review that authors will read. Structure it as follows:

```
## Summary

[2-3 sentence summary of what the paper does. This shows you understood the paper.]

## Major Contribution Assessment

[Evaluate the claimed contributions. Are they genuine? How significant are they relative
to the current state of the art? Cite specific related work for comparison.]

## Strengths

[List genuine strengths. Be specific — "strong experimental results" is useless,
"outperforms all baselines on KITTI 2015 by >1% EPE while being 3x faster" is useful.]

S1. [Strength 1 — with specific evidence]
S2. [Strength 2 — with specific evidence]
S3. [Strength 3 — with specific evidence]

## Weaknesses

[List weaknesses from most to least critical. Each weakness should be specific and
actionable — tell the authors exactly what's wrong and how to fix it.]

W1. [Critical weakness — with specific evidence and suggested fix]
W2. [Major weakness — with specific evidence and suggested fix]
W3. [Minor weakness — with specific evidence and suggested fix]
...

## Technical Accuracy

[Address any technical concerns: mathematical errors, flawed reasoning, incorrect
claims, missing proofs, etc. Point to specific equations, theorems, or arguments.]

## Adequacy of Citations

[Are important related works cited? List any missing references with full citation info.
Note if the paper over-cites or self-cites excessively.]

Missing references:
- [Author et al., "Title", Venue Year] — relevant because [reason]
- ...

## Minor Issues

[Presentation issues, typos, unclear figures, etc. Be specific: "Figure 3 is too small
to read the axis labels" not "some figures are hard to read".]

- Page X, Line Y: [issue]
- Figure Z: [issue]
- Table W: [issue]
- ...

## Questions for the Authors

[Specific questions that would help clarify the paper. These should probe the key
uncertainties in your assessment.]

Q1. [Question about methodology/results/claims]
Q2. [Question about experimental design]
Q3. [Question about generalizability]

## Multimedia Assessment (if applicable)

[If the paper has a video or other multimedia attachment, evaluate: Is it consistent
with paper content? Does it enhance quality? Technical quality of the video?]
```

---

## Chinese Analysis Notes Template (review_cn.md)

```markdown
# 审稿分析笔记

## 论文基本信息
- 标题: 
- 提交编号: 
- 审稿截止日期: 

## 一句话评价
[用中文写对论文的核心判断]

## 评分理由详析

| 维度 | 评分 | 理由 |
|------|------|------|
| Paper contribution | | |
| Technical quality | | |
| Originality | | |
| Thoroughness of results | | |
| Clarity of presentation | | |
| Adequacy of citation | | |
| Relevance to field | | |

## 核心优点
1. 
2. 
3. 

## 核心问题
1. [致命问题 — 影响核心结论的]
2. [主要问题 — 需要补充实验或修改的]
3. [次要问题 — 可以改进但不影响结论的]

## 与相关工作对比

| 方法 | 年份 | 会议 | 关键指标 | 与本文的关系 |
|------|------|------|----------|-------------|
| | | | | |

## 领域判断
- 这个方向目前的热度和趋势:
- 本文在领域中的定位:
- 是否值得录用的核心理由:

## 审稿策略
[选择 Accept/Revise/Reject 的核心逻辑，以及对 AE 的建议]
```
