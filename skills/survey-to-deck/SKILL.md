---
name: survey-to-deck
description: >-
  端到端"调研一个方向 → 深读论文 → 每篇产两份报告 → 入 OmniBox 向量语义索引 → 做成 Slidev 串讲 deck"的总编排(meta)skill。
  它本身不重新实现任何一步,而是把四个已有 skill 串成一条流水线并用 Workflow 并行 fan-out:
  ① 发现(comprehensive-survey / 用户直接给清单)→ ② 去重 → ③ 每篇一个 agent 跑 arxiv-deepdive 写 01_highlevel + 02_technical(带 frontmatter)→
  ④ update_index.py 增量入库 + search.py 验证 → ⑤ paper-talk-deck 出 deck。
  Use PROACTIVELY whenever the user wants the WHOLE pipeline from a topic/paper-list to a knowledge-base + presentation — triggers:
  "调研 <方向> 然后读论文出报告入库再做 deck", "把这批 paper 跑全套:deep-read 进 omnibox + re-index + 出一个 deck",
  "深入读一两百篇 paper、每篇 high-level + technical 报告、入向量库、做 slides", "走一遍我那条调研流水线",
  "research a topic end to end: deep-read papers, two reports each, ingest to my KB, build a slide deck",
  "survey to deck", "from topic to slides", 或用户给一个主题/一组 arXiv 清单并期望"读 → 报告 → 入库 → deck"一条龙。
  若用户只想要其中一步(只深读出报告→arxiv-deepdive;只入库/同步→omnibox-sync;只做 deck→paper-talk-deck;只检索→comprehensive-survey),用对应单 skill,本 skill 专做"串起全程"的编排。
---

# survey-to-deck:从一个方向到一份可讲的 deck(总编排)

把"调研 → 深读 → 双报告 → 向量入库 → Slidev deck"五个阶段**串成一条自动流水线**。本 skill 是**胶水/编排层**——每一步的真正逻辑在各自的子 skill 里,这里只负责接力、传参、并行 fan-out、跨阶段的去重与验证。核心交付链:

```
[主题 / arXiv 清单]
   └►① 发现   comprehensive-survey ─► 候选 {arxiv_id,title}
        └►② 去重 KB  (find papers/ 已有的跳过)
             └►③ 深读·双报告  Workflow fan-out: 一篇一 agent 跑 arxiv-deepdive
                  │   写 papers/<topic>/<id>_<slug>/{01_highlevel.md,02_technical.md}(必须带 frontmatter)
                  └►④ 入库   update_index.py (增量) ─► search.py 验证
                       └►⑤ deck   paper-talk-deck ─► slides.md (npm run dev)
```

**语料与索引都在本机 Mac** `~/proj/omnibox/`(`papers/` 语料 + `index/` 索引)。报告默认中文。

## 何时用 / 不用

- **用**:用户要"一条龙"——给个方向或一组论文,期望最终拿到「入库的知识 + 一份能讲的 deck」。
- **不用(走单 skill)**:只检索→`comprehensive-survey`;只深读出报告→`arxiv-deepdive`;只把报告嵌入索引/同步→`omnibox-sync`/`update_index.py`;只做 deck→`paper-talk-deck`;只在库里查→`omnibox-search`。

## 默认口味(本机用户偏好,除非用户当场另说)

- **中文**报告 + 中文 deck。
- **全自动**跑(无"候选清单审批"检查点)——除非用户要先审清单。
- **已在库的精确 arXiv id 跳过不重读**(去重见 ②)。
- **deck 一个方向一份**(多主题→多 deck),不强行合并;每份 14 篇上下精选代码级串讲。
- latent-memory 这类口味偏好(聚焦决策/序列/具身、剔纯 RAG)是**项目级**约定,不是本 skill 的默认——开跑前若主题模糊就用 AskUserQuestion 确认范围/篇数/分几份 deck。

---

## 阶段 0:确认范围(开跑前)

把输入归一成两种之一:
- **给了主题**(如"驾驶世界模型"):走完整 ①→⑤。
- **给了清单**(arXiv 链接/ID/标题):跳过 ①,直接 ②→⑤。只给标题的先 WebSearch 补 arXiv id。

确认这几点(用户没说就用默认,模糊就一次性问清):**目标篇数量级**(几十?一两百?)、**分几份 deck**(按主题)、**要不要候选审批检查点**、**deck 每份精选多少篇**。Ultracode 下倾向直接按默认全自动跑,把不确定项一次问完。

## 阶段 ①:发现候选(给了清单则跳过)

调 `comprehensive-survey`（其内部搜索已统一由 `/litian-academic-search` 完成——7 源并行、自动去重、S2 限流自动处理）。

产出:候选 `{arxiv_id, title, one_liner, topic}` 列表。多主题就给每篇打上 `topic`(对应 canonical 的 topic 分面,见下)。

## 阶段 ②:对 KB 去重

```bash
# 对每个候选 id 查库里是否已有(已有则跳过深读)
find ~/proj/omnibox/papers -maxdepth 2 -type d -name "<id>_*"
```
或用脚本一把过滤:`bash ~/.claude/skills/survey-to-deck/scripts/dedup.sh <id1> <id2> ...`(打印 NEW / SKIP)。
已有 topic 目录见 `~/proj/omnibox/index/canonical.json` 的 `topic` 分面(如 `topic/world-model`、`topic/autonomous-driving`、`topic/memory`、`topic/vla`...)。**新主题**要先往 `canonical.json` 的 `topic` 数组里加一项(否则报告 tag 用不了该 topic)。

## 阶段 ③:深读 + 双报告(Workflow 并行 fan-out)

这是流水线的重心。**一篇论文 = 一个 subagent**,每个 agent 自洽走完 arxiv-deepdive 的流程(下 PDF→找官方 repo 浅克隆→读 PDF 含附录 + repo 关键文件→写两份中文报告)。

**编排步骤:**
1. 把去重后的新论文写成一个 manifest JSON(一条一篇):`{arxiv_id, title, topic_dir, slug, one_liner}`。约定放 `~/proj/omnibox/papers/_DEEPREAD_manifest.json`(第二波用 `_manifest2.json`)。`slug` = 论文主名小写连字符化;`topic_dir` = 不带 `topic/` 前缀的目录名(如 `world-model`)。
2. 用 `assets/ingest-workflow.template.js` 起 Workflow。传 `args = { manifest: "<上面的路径>", count: <篇数> }`。每个 agent 用下标自取 manifest 条目(prompt 不必塞全表)。
3. ⚠️ **报告必须带 YAML frontmatter**(否则 `update_index.py` 读不进、tag 也进不了受控词表)。每篇 `01_highlevel.md` 顶部需有:
   `arxiv / title / aliases / type(highlevel|technical) / topic / year / authors / affiliations / repo / has_repo / tags / related / summary`。
   - `tags` **只能取自** `~/proj/omnibox/index/canonical.json` 的受控词表(分面:`topic/ method/ task/ embodiment/ capability/ data/ modality/ model/ benchmark`)。模板已把"先 `cat canonical.json` 选合法 tag"写进 agent 指令。常见踩坑:`method/nerf`→`model/nerf`、`modality/lidar`→`modality/point-cloud`、`method/lora`→`topic/lora`。
   - `summary` 里**别用 ASCII 双引号**(会断 YAML 字符串)——用「中文引号」。
4. 子 skill 细节(PDF 回退 export.arxiv.org、>800MB repo 读完即删、写完删 paper.pdf 省盘、诚实标注无官方 repo / 训练码未开源)全在 `arxiv-deepdive` 的 SKILL.md,模板已浓缩进 agent prompt;有疑问回看那篇。

并行约束:Workflow 并发上限 ~14,生命周期上限 1000 agent。大批量(>100)直接 `parallel` 全丢进去,超出的会排队。

## 阶段 ④:入向量索引(增量)+ 验证

```bash
# 增量嵌入:内容哈希,只对新增/改动的报告重嵌入
conda run -n ml python ~/proj/omnibox/index/update_index.py

# 验证:能检索到刚入库的内容
conda run -n ml python ~/proj/omnibox/index/search.py "<刚入库主题的查询>" -k 8
```
- 环境:conda env `ml` + SiliconFlow key `~/.siliconflow_key`(模型 bge-m3,1024 维,batch≤32)。
- ⚠️ **别跑 `build_index.py`**(全量重建会清空视频,得再 `add_videos.py`)。日常只用增量的 `update_index.py`。
- 首次对一个全新库跑 update_index 是 baseline(只记哈希、不嵌入);之后再跑才真正嵌入新增/改动——批量入库后跑一次即可。

## 阶段 ⑤:做 Slidev deck

调 `paper-talk-deck`,一个方向一份(按用户口味)。**协同点**:报告已经在 OmniBox 里,deck 的"取素材"步会先 `omnibox-search` 命中现成 `02_technical.md`(代码/file:line/超参)和 `01_highlevel.md`(动机/idea),**不必重读论文**——这正是先入库再做 deck 的价值。

paper-talk-deck 自带脚手架与语法手册,这里只记**当前 Slidev 版本的硬约束**(否则白忙):
- 脚手架已默认 `@slidev/cli ^52.16.0`（**52.x = Slidev 当前主版本**，已去掉 `0.` 前缀，不是 `0.52`；别误降到 `0.x`，旧 deck 在 `0.4x/0.5x` 的要升上来）。配套 `@slidev/theme-seriph ^0.25.0`。
- **Slidev 52 引 public 图必须用运行时绑定** `<img :src="'/<id>/fig.png'">`,**不能** `<img src="/...">`(rolldown 的 import-guard 会让 dev/build 全 500)。
- 全量 PNG 导出默认 per-page 超时:`slidev export --format png --timeout 120000`。
- 导出默认连 3030 端口的 dev server——多 deck 同跑会**串线**;导出前先杀 dev server 或用唯一端口。
- 对比表行多会竖直溢出:scoped `<style>` 缩 `font-size`/`padding` 解决(模板里有写法)。

## 收尾:回报 + 更新记忆

- 回报:深读了几篇(新增 vs 跳过)、库从 N→M、各 topic 现存量、deck 在哪几份/怎么 `npm run dev`、有无"某篇无官方 repo / S2 限流手动补"这类注记。
- **更新记忆**:把这次产出写进/更新 `project` 记忆(篇数、库规模变化、新建 topic、deck 路径+端口、踩的坑),并在 `MEMORY.md` 加/改一行。可参考既有 [[wm-ad-memory-survey-2026-06]]。

## 资源

- `assets/ingest-workflow.template.js` — 阶段③的 Workflow 脚本(Mac 路径 + frontmatter 强制 + canonical tag 约束 + StructuredOutput schema)。把它当 `script` 传给 Workflow 工具,配 `args={manifest,count}`;或复制改 prompt。
- `scripts/dedup.sh` — 阶段②去重:批量打印每个 arXiv id 是 NEW 还是 SKIP(库里已有)。
- 子 skill(每步的真实逻辑):`comprehensive-survey`(发现)· `arxiv-deepdive`(深读双报告)· `omnibox-search`/`omnibox-sync`(库内检索/同步)· `paper-talk-deck`(deck)。
- 记忆:[[omnibox-ingest-pipeline]](②③④ 的触发词与命令细节)· [[wm-ad-memory-survey-2026-06]](一次完整跑的实例与坑)。
