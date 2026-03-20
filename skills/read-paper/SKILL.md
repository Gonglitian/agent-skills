---
name: read-paper
description: "Deep-read an academic paper (PDF or arXiv ID) and produce a structured markdown note with figure analysis. Use this skill whenever the user wants to read, summarize, or take notes on a research paper — including phrases like '读一下这篇论文', 'summarize this paper', 'read paper 2401.xxxxx', '论文笔记', 'paper notes', or any mention of reading/analyzing an arXiv paper or PDF. Also trigger when the user provides a paper ID or PDF path and expects a detailed summary. This skill handles the full pipeline: text segmentation, figure extraction via VLM, cross-analysis, and final note assembly."
---

# Read Paper — 论文深度阅读 Pipeline

你是一个学术论文深度阅读助手。给定一篇论文（PDF 路径或 arXiv ID），你会执行一个完整的阅读 pipeline，产出一份结构化的 markdown 笔记，包含文本总结、图片分析和交叉验证。

## Pipeline 总览

```
输入: PDF 路径 / arXiv ID
  │
  ├─ Phase 1 (主代理): 定位 PDF → 提取图片 + 获取全文 + 长度检测
  │   └─ split_paper.py → strategy: "standard" | "dynamic"
  │
  ├─ Phase 2+3 (并行扇出): ★ 核心加速点
  │   ├── Bash(background): describe_figures.py (VLM API)
  │   │
  │   ├── [standard: 短论文 < 12k words] 固定 2 subagent
  │   │   ├── Subagent A: 头部提炼 + Research Intelligence + Sec 0-4
  │   │   └── Subagent B: Sec 5-11
  │   │
  │   └── [dynamic: 长论文 ≥ 12k words] 1+N subagent
  │       ├── Overview Subagent: overview.md → TL;DR, Claims, Roadmap, Research Intelligence, Sec 0,2,3
  │       ├── Chunk 0 Subagent: chunk_0.md → 相关 sections
  │       ├── Chunk 1 Subagent: chunk_1.md → 相关 sections
  │       └── ... (N chunks, 每个 ~6k words)
  │
  └─ Phase 4 (主代理): 汇总所有结果 → 交叉融合 → 组装最终笔记
```

**关键原则**：文本分析与图片 VLM 完全独立，必须并行。VLM 耗时最长（60-90s），在此期间文本分析同步进行。

## 文件路径约定

```
papers/notes/<paper_id>/
├── note.md                     # 最终笔记
├── figures/                    # 提取的图片
├── chunks/                     # [仅 dynamic] 分片文件
│   ├── overview.md
│   ├── chunk_0.md
│   └── ...
└── figure_descriptions.json    # VLM 图片描述
```

`<paper_id>` 从 PDF 文件名或 arXiv ID 提取（如 `2602.13932`）。

---

## Phase 1: 准备工作（主代理）

### 1.1 定位论文

- **本地 PDF 路径**：直接使用
- **arXiv ID**（如 `2602.17049`）：
  1. 检查本地：`papers/raw/<id>.pdf` 或 `papers/raw/MMDD/<id>.pdf` 或 `papers/raw/<id>.md`
  2. 若无本地文件，用 `arxiv-mcp-server` 的 `download_paper` + `read_paper` 获取
  3. 若需 PDF（图片提取），下载：`curl -L -o /tmp/<id>.pdf https://arxiv.org/pdf/<id>`

### 1.2 并行：提取图片 + 获取全文

在同一个 tool call 中并行发起：

```
并行 ①: Bash → mkdir -p + extract_figures.py (几秒)
并行 ②: Read → 论文全文
```

图片提取：
```bash
mkdir -p papers/notes/<paper_id>/figures && \
uv run <skill-dir>/scripts/extract_figures.py <pdf_path> \
  --output-dir papers/notes/<paper_id>/figures \
  --min-size 150
```

### 1.3 长度检测与分片

全文获取后，运行分片脚本判断策略：

```bash
uv run <skill-dir>/scripts/split_paper.py <paper_text_path> \
  --output-dir papers/notes/<paper_id>/chunks \
  --target-words 6000 \
  --threshold 12000
```

脚本输出 JSON：
- `strategy: "standard"` → 短论文，使用固定 2 subagent
- `strategy: "dynamic"` → 长论文，已生成 `overview.md` + `chunk_0.md` ... `chunk_N.md`

`<skill-dir>` = 本 skill 所在目录。

---

## Phase 2+3: 并行扇出

Phase 1 完成后，根据 strategy 在**同一条消息**中并行发起所有操作。

### 操作 1 — VLM 图片描述（始终执行，Bash background）

```bash
# run_in_background: true
uv run <skill-dir>/scripts/describe_figures.py \
  papers/notes/<paper_id>/figures \
  --output papers/notes/<paper_id>/figure_descriptions.json \
  --model Qwen/Qwen2.5-VL-72B-Instruct \
  --max-figures 12
```

### 模式 A: Standard（短论文 < 12k words）

与 VLM 同时发起 2 个 subagent（均 run_in_background: true）：

**Subagent A（头部 + Sec 0-4）**：
```
Agent tool, subagent_type: "general-purpose", run_in_background: true
prompt: |
  你是论文阅读助手。请基于以下论文全文，完成两项任务：

  任务 1 — 头部提炼区：
  生成 TL;DR（一句话）、Claims & Evidence 表格（作者核心声称 + 实证数据 + 强度评估）、
  Academic Roadmap（前置工作 → 本文 → 后续方向）、
  Research Intelligence 块：
    - Claims: 2-4 条简洁声称（≤50字/条，仅声称不含证据）
    - Insights: 2-3 条技术洞见（WHY it works / WHAT is novel）
    - Direction: 一个短语描述研究方向（≤15词）
    - Milestones: [Prior] 前置关键工作 + [This] 本文里程碑意义（共 2-5 条）
  格式详见 references/note-template.md 中 "Research Intelligence" 部分。

  任务 2 — 模板 Section 0-4：
  - Section 0: 元信息（作者、机构、关键词）
  - Section 1: 关键图示（最重要 3 张图的文字描述，图片嵌入由主代理完成）
  - Section 2: 论文背景（逻辑链，箭头串联）
  - Section 3: 核心思想与贡献
  - Section 4: 方法概述

  要求：忠实原文，缺失标注"未提及"，保留量化数据原始数字。
  输出纯 markdown 文本，无需文件操作。

  论文全文路径: <paper_text_path>
```

**Subagent B（Sec 5-11）**：
```
Agent tool, subagent_type: "general-purpose", run_in_background: true
prompt: |
  你是论文阅读助手。请基于以下论文全文，完成模板 Section 5-11：

  - Section 5: 数据（来源、模态、规模、数据集名称，表格形式）
  - Section 6: 模型架构（组件表格）
  - Section 7: 其他关键组件
  - Section 8: 训练范式
  - Section 9: 机器人平台 / 实验平台（非机器人论文改为"实验平台"）
  - Section 10: 实验摘要（通用设置 + 逐项实验，含量化数据）
  - Section 11: 备注（关键洞见、局限性、未来工作）

  要求：忠实原文，缺失标注"未提及"，保留量化数据原始数字。
  输出纯 markdown 文本，无需文件操作。

  论文全文路径: <paper_text_path>
```

### 模式 B: Dynamic（长论文 ≥ 12k words）

与 VLM 同时发起 1 + N 个 subagent（均 run_in_background: true）：

**Overview Subagent（全局提炼）**：
```
Agent tool, subagent_type: "general-purpose", run_in_background: true
prompt: |
  你是论文阅读助手。这是一篇长论文，你收到的是摘要+引言+结论的提取文本。
  请完成以下任务：

  1. 头部提炼区：
     - TL;DR（一句话）
     - Claims & Evidence 表格（作者核心声称 + 实证数据 + 强度评估）
     - Academic Roadmap（前置工作 → 本文 → 后续方向）
     - Research Intelligence 块（Claims 简洁版、Insights、Direction、Milestones）
       格式详见 references/note-template.md 中 "Research Intelligence" 部分。

  2. 模板 Section：
     - Section 0: 元信息（作者、机构、关键词）
     - Section 2: 论文背景（逻辑链，箭头串联）
     - Section 3: 核心思想与贡献

  要求：忠实原文，缺失标注"未提及"，保留量化数据原始数字。
  输出纯 markdown，无需文件操作。

  论文概览文本路径: <overview_path>
```

**Chunk i Subagent（每个 chunk 一个）**：
```
Agent tool, subagent_type: "general-purpose", run_in_background: true
prompt: |
  你是论文阅读助手。这是一篇长论文的第 {i+1}/{N} 段（共 {N} 段）。

  请阅读这段内容，根据以下模板 section 列表，输出该段涵盖的所有相关 section。
  仅输出有内容的 section，跳过不相关的。用 ## N. Section名称 作为标题格式。

  完整模板 Section (0-11)：
  - 0: 元信息（作者、机构、关键词）
  - 1: 关键图示（文字描述该段中提到的重要图表）
  - 2: 论文背景
  - 3: 核心思想与贡献
  - 4: 方法概述（Pipeline / 算法步骤）
  - 5: 数据（来源、模态、规模，表格形式）
  - 6: 模型架构（组件表格）
  - 7: 其他关键组件
  - 8: 训练范式
  - 9: 机器人平台 / 实验平台
  - 10: 实验摘要（设置 + 逐项实验 + 量化数据）
  - 11: 备注（关键洞见、局限性、未来工作）

  该段的标题列表: {headings}

  要求：忠实原文，缺失标注"未提及"，保留量化数据原始数字。
  输出纯 markdown，无需文件操作。

  论文段落路径: <chunk_i_path>
```

**动态并行规则**：
- 所有 subagent + VLM bash 在同一条消息中一起发出
- Claude Code 建议 3-5 个并行 subagent 为宜；若 chunk 数 > 4，可将相邻小 chunk 合并给同一 subagent
- 总 subagent 数 = 1 (overview) + min(N_chunks, 4)

### 等待策略

所有操作启动后，等待全部完成：
- VLM：通过 TaskOutput 获取 background bash 结果
- Subagents：Agent tool 自动返回

---

## Phase 2 详细要求

### 头部提炼格式

```markdown
# <论文标题>

> **TL;DR**: <一句话概括>

## Claims & Evidence
| 作者声称 (Claim) | 实证支撑 (Evidence) | 强度 |
|---|---|---|
| <claim 1> | <具体数据/实验> | 强/中/弱 |

## Academic Roadmap
> <前置工作 A> → <前置工作 B> → **本文** → <可能的后续方向>

## Research Intelligence

**Claims:**
- <简洁声称1，≤50字>
- <简洁声称2>

**Insights:**
- <技术洞见1>
- <技术洞见2>

**Direction:** <研究方向短语>

**Milestones:**
- [Prior] <WorkName Year>: <一句话成就>
- [This] <本文的里程碑意义>

---
```

强度标准：**强** = 充分对比+消融；**中** = 有实验但缺某些对照；**弱** = 仅定性分析

### 模板 Section

详见 `references/note-template.md`，共 12 个 section（0-11）。

**核心要求**：忠实原文、缺失标注"未提及"、保留量化数据原始数字。

---

## Phase 3 详细要求（VLM 脚本自动完成）

`describe_figures.py` 自动处理：
1. 扫描 figures 目录，按文件大小排序取 top N（默认 12）
2. 逐张发送到 SiliconFlow VLM API（base64 webp，OpenAI 兼容协议）
3. 输出 JSON：filename, path, description（类型/内容/关键信息/位置推测）

API key 来源：环境变量 `SILICONFLOW_API_KEY`。

---

## Phase 4: 交叉融合 + 最终组装（主代理）

### 4.1 汇总结果

**Standard 模式**：
- Subagent A → 头部提炼 + Research Intelligence + Sec 0-4
- Subagent B → Sec 5-11

**Dynamic 模式**：
- Overview Subagent → 头部提炼 + Research Intelligence + Sec 0, 2, 3
- Chunk Subagents → 各自产出的 sections（可能有重叠）
- **合并规则**：同一 section 有多个 chunk 贡献时，按 chunk 顺序拼接内容，去重

### 4.2 交叉分析

读取 `figure_descriptions.json`，将 VLM 图片描述与文本总结交叉验证：

- 文本中提到的 figure 是否与图片描述一致
- 图片中展示但文本遗漏的信息 → 补充到对应 section
- 实验数据图的数字与文本不一致 → 在 Remarks 注明

### 4.3 组装最终笔记

写入 `papers/notes/<paper_id>/note.md`：

```
1. 头部提炼区（TL;DR + Claims & Evidence + Academic Roadmap + Research Intelligence）
2. ---
3. 模板 Section 0-11（合并所有 subagent 输出）
4. Section 1 中嵌入实际图片
5. 其他 section 适当位置插入对应图片
```

**图片嵌入使用相对路径**：
```markdown
![Figure 1 — 系统架构](./figures/fig_p2_0.png)
```

根据 VLM 描述中的"论文位置推测"将图片插入最相关的 section。

### 4.4 最终检查

- 所有图片路径有效（相对于 note.md）
- 没有空 section（要么有内容，要么标注"未提及"）
- 头部提炼区完整
- [Dynamic] 所有 chunk 的内容已合并，无遗漏

---

## 关键原则

1. **准确优先**：宁可说"未提及"也不编造
2. **数据保留**：量化结果保留原始数字
3. **图文互证**：文字和图片互相验证，不一致时在 Remarks 注明
4. **并行优先**：Phase 2+3 必须并行，不要串行等待
5. **动态适应**：长论文自动分片，短论文用固定方案，无需用户干预
6. **适应性**：模板中"机器人平台"对非机器人论文改为"实验平台"

---

## 性能预期

| 场景 | 文本分析 | VLM | 组装 | 总耗时 |
|------|---------|-----|------|--------|
| 短论文 (standard) | ~40s (2 agents) | ~70s | ~20s | **~90s** |
| 长论文 (dynamic, 5 chunks) | ~60s (6 agents) | ~70s | ~30s | **~100s** |
| 长论文 串行假设 | ~150s | ~70s | ~30s | ~250s |

Dynamic 模式对长论文可节省 ~60% 耗时，同时避免单个 agent 上下文溢出。
