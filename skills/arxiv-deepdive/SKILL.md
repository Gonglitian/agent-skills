---
name: arxiv-deepdive
description: >-
  从一个 arXiv 链接 / arXiv ID / 论文标题出发，把论文 PDF 与其官方代码仓库一起作为上下文深读，产出两份面向工程师的报告：
  ① 01_highlevel.md（High-Level 叙述 / 核心 idea）和 ② 02_technical.md（工程技术深挖：架构、训练细节、推理细节、代码层面、复现要点）。
  与"做 Obsidian 论文笔记"不同，这个 skill 强调**结合官方代码**、面向**复现/工程落地**、且把训练超参与推理流程坐实到 file:line。
  Use PROACTIVELY whenever the user wants a deep, code-grounded engineering/reproduction report of a paper — triggers include
  "技术报告", "工程报告", "深挖这篇", "结合代码读", "把 repo 克隆下来一起读", "复现方案", "训练/推理细节", "engineer report",
  "technical deep dive", "reproduce this paper", "read paper with its code", "high-level + technical report",
  或用户给出 arXiv 链接/ID 并要求"详细的技术性总结/不要遗漏技术细节/能照着复现"。也适用于批量给一组 arXiv 论文生成此类报告。
  若用户只想要轻量阅读笔记 / Obsidian 双链笔记，用 robotics-paper-reading；若要审稿用 review-ral；本 skill 专做代码级工程深挖报告。
---

# arxiv-deepdive：论文 + 代码 → 两份工程报告

把一篇论文读"透"——不只读 PDF，而是把**官方代码仓库**也拉下来当上下文，这样训练细节、推理流程、超参数、张量形状这些"论文正文常常含糊、代码里才有真相"的东西才能坐实。最终产出两份中文报告：一份讲清楚 **为什么/核心 idea**（给快速理解的人看），一份讲清楚 **怎么实现/怎么复现**（给要动手的工程师看）。

## 何时用

用户给了一个 arXiv 链接 / arXiv ID / 论文标题（或一批），并希望得到**详细、可复现、结合代码**的技术报告。典型说法见 frontmatter description。一次处理一篇；处理一批时，对每篇独立走一遍本流程（可并行 fan-out，每篇一个 agent）。

## 输入与产物

**输入**：一个 arXiv 标识（`https://arxiv.org/abs/2406.09246`、`2406.09246`、或论文标题）。若只给标题，先用 WebSearch / arXiv 找到 arXiv ID。

**产物**：一个目录（默认 `./<arxiv_id>_<slug>/`，`slug` = 论文主名小写连字符化；若用户指定了 vault/项目目录就放那里），内含：

```
<arxiv_id>_<slug>/
├── paper.pdf            # 论文原文（读完、两份报告写好后删除以省盘，见步骤 5）
├── repo/                # 官方代码（浅克隆；超大仓库读完即删，见下）
│   └── REPO_URL.txt     # 若 repo 没保留/没克隆成功，这里留 URL
├── 01_highlevel.md      # High-Level 叙述报告
└── 02_technical.md      # 工程技术深挖报告
```

报告**默认中文**（本机用户偏好中文）；用户要英文就写英文。

## 流程

### 1. 建目录、定位 arXiv ID
确定 `arxiv_id`（去掉版本号如 `v3`）与 `slug`，建好目标目录。

### 2. 下 PDF + 找并克隆官方 repo（用 `scripts/fetch.sh`）
先确定官方仓库 URL：用 WebSearch（`<title> github code`）、看 arXiv abstract 页、或论文 project page。**务必是作者自己发布的官方实现**，不是第三方复现（第三方仅可作为"无官方 repo 时的复现入口"提及）。

然后用本 skill 自带脚本一步搞定下载与克隆：
```bash
bash <skill_dir>/scripts/fetch.sh <arxiv_id> <target_dir> [repo_url] [max_repo_mb=800]
```
脚本会：下载 `paper.pdf`（`arxiv.org/pdf` 失败自动回退 `export.arxiv.org`，校验 `%PDF` 且 >50KB）；浅克隆 repo（`--depth 1 --filter=blob:none` + `GIT_LFS_SKIP_SMUDGE=1`，跳过权重/LFS 大文件）；并按体积分流——
- `REPO_OK <mb>`：保留。
- `REPO_LARGE <mb>`（>max）：先留着供你读，**读完关键文件后 `rm -rf <dir>/repo`**，URL 已存入 `REPO_URL.txt`。这是为了控制磁盘——超大仓库（带数据/资产）不值得长期占盘。
- `REPO_CLONE_FAILED` / `NO_REPO`：无 repo，用 WebFetch 在线读 GitHub 上的 README/关键脚本，或仅据论文写。

arXiv 偶尔 429 限流；脚本已带重试，必要时稍等再试。

### 3. 把论文 + 代码读进上下文
- **读 PDF**：用 Read 工具读 `paper.pdf`（用 `pages` 参数通读全文，**包括附录**——超参表、训练配置、算法伪代码常在附录）。
- **读代码**：优先读这些"出真相"的文件：`README`、模型/策略定义、训练脚本（`train*.py`）、配置（`*.yaml`/`config*`）、推理/评测脚本、`requirements.txt`/环境文件。目标是把架构、损失、超参、数据管线、训练/评测命令坐实。

### 4. 写两份报告
按下面的模板写。两份都要，写到目标目录。

### 5. 收尾
若 repo 是 `REPO_LARGE`，此时删除 `repo/`（已读完）。**确认两份报告（`01_highlevel.md`、`02_technical.md`）都已写好且内容完整后，删除 `paper.pdf` 以节省存储**——PDF 只是读取阶段的中间产物，报告产出后不再保留；日后若需原文，凭目录名里的 arXiv id 用 `scripts/fetch.sh` 几秒即可重新下载。删除前务必先核验两份报告确实在位且非空，避免误删未读的 PDF。简要回报：PDF 是否拿到并已按规清理、repo 状态、两份报告路径、以及任何"无官方 repo / 训练码未开源 / 论文与代码不一致"的重要注记。

---

## 报告模板

### `01_highlevel.md` — High-Level 叙述报告
讲清楚"是什么、为什么、凭什么"，**故事/直觉层面**，尽量少公式。建议结构：

```markdown
# <标题> — 高层叙述报告

> arXiv: <id> · 项目页/代码: <links> · 机构/作者: <...>

## 一句话定位
（这篇工作到底是什么、解决谁的问题）

## 解决的问题 / 动机
（当时的痛点、为什么重要、自然的机会在哪）

## 核心 idea / 关键洞察
（直觉层面把方法讲透；它"聪明"在哪一两点上）

## 主要贡献
- ...（bullet）

## 与已有工作的区别 / 它的位置
（对比 RT-2 / Octo / 同类基线，差异与定位）

## 适用场景与局限
```

### `02_technical.md` — 工程技术深挖报告
面向要动手的工程师，**详细、不遗漏技术细节，能照着复现**。所有引用尽量给到 `repo/路径::函数` 或 `配置键` 或具体数值。建议结构：

```markdown
# <标题> 技术深挖报告（面向工程师）

> 论文 arXiv:<id> + 官方仓库 <url>；引用尽量给到文件路径/配置键/数值。

## 0. 一图速览（数据流）
（用 ASCII 画出输入→各模块→输出的数据流与关键张量形状）

## 1. 整体架构
（模块分解；每个模块的输入输出张量形状；关键 trick；对应代码文件/类/函数）

## 2. 训练细节
- 数据集与预处理（来源、规模、清洗/采样规则、配比）
- 损失函数（公式 + 代码位置）
- 优化器 / 学习率 / 调度 / batch size / 训练步数或 epoch
- 硬件与时长
- 关键 trick；完整超参表（尽量给具体数值，来自论文与代码，标注来源）

## 3. 推理细节
（推理流程；动作解码 / 采样方式；chunk / horizon；频率 / 延迟；部署注意点）

## 4. 代码层面
- 仓库结构（关键目录与文件一览表）
- 关键文件与函数（做什么、怎么连起来）
- 配置入口；**实际可跑的训练与评测命令**（从 repo 提取）
- 依赖与环境（版本 pin、坑）

## 5. 复现要点与坑
（结合 code 与论文，列出复现时最容易踩的点）
```

---

## 质量准则（让报告"可信、可复现"）

这些是把报告从"看着像样"提升到"真能用"的关键，背后的逻辑是：**工程师最怕被论文的乐观叙述误导**，所以坐实与诚实最重要。

- **坐实到代码**：超参、张量形状、损失、命令尽量引用 `文件:行` 或配置键，而不是泛泛复述论文。论文正文常省略的数值，去代码/配置里挖。
- **诚实标注边界**：很常见的情况——官方 repo **只放了推理/评测，没放训练代码**，或训练用了**内部数据/算力**无法严格复现，或是**纯 benchmark/数据集**没有模型训练。务必在报告里明确写出来，并说明哪些数字来自论文、哪些来自代码。这比假装能复现有价值得多。
- **主动指出论文 vs 代码的不一致**：例如论文说某层 18 个 head、repo 配置是 8；论文公式用 L=8 帧、默认 config 是 2。这类差异对复现是致命的，发现就记下来。
- **无官方 repo 时**：明确说明（查过 arXiv abstract / project page / GitHub 搜索都没有），给出最接近的第三方复现作为入口，技术报告基于论文正文 + 附录撰写并注明"实现细节待官方放码核对"。
- **未来日期的 arXiv ID 是正常的**：有些 id 看起来"在未来"（如 2026 年的），只要 PDF/repo 能正常拉到就照常处理，不要因此跳过。

## 批量处理

给一组论文时，对每篇独立走本流程。若有并行能力（subagent / workflow fan-out），一篇一个 agent 并发，每个 agent 拿到 `{arxiv_id, title, target_dir}` 后自洽完成"下 PDF + 找/克隆 repo + 读 + 写两份报告"，返回简短状态（pdf 是否 ok、repo 状态、是否写了两份报告、注记）。处理完可生成一个 `INDEX.md` 总索引（按主题分组，每行：arXiv 链接 / repo 状态 / 两份报告链接 / 一句话定位），方便回查。批量时注意磁盘（超大 repo 用 `REPO_LARGE` 读完即删策略）。
