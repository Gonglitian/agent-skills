---
name: legacy-omnibox-search
description: >-
  在 OmniBox 论文知识库(~/proj/omnibox/papers,965 篇中文工程报告)里做语义检索。**索引的是两份报告(01_highlevel + 02_technical)的全文内容**(分块嵌入,29k+ chunk),不止摘要——所以连"技术报告深处某个训练细节/架构选择/代码片段"都搜得到,并会告诉你命中是哪篇的哪一节。
  底层 SiliconFlow bge-m3 + 本地 sqlite-vec,支持按 topic / 受控 tag 过滤。(注:索引的是我们写的报告,非 PDF 原文。)
  Use PROACTIVELY whenever the user (or you) needs to find papers in this corpus by MEANING rather than exact keywords —
  triggers: "OmniBox 里有哪些关于…的论文", "知识库里找…", "相关工作有哪些", "find papers about…", "search my paper KB",
  "哪些工作做了… (in the omnibox corpus)", "给我 X 方向的论文清单"。
  返回 top-k {相关度, arxiv, 短名, topic, tags, 一句话摘要, 笔记路径},拿到路径后可直接 Read 全文报告。
---

# omnibox-search:OmniBox 论文库语义检索

965 篇论文的笔记在 `~/proj/omnibox/papers/<topic>/<arxiv>_<slug>/{01_highlevel.md,02_technical.md}`,每篇有结构化 frontmatter(arxiv/title/aliases/topic/tags/summary/related)。本 skill 让你按**语义**而非关键词检索。

## 检索(主入口)

```bash
conda run -n ml python ~/proj/omnibox/index/search.py "你的研究问题" [--topic <topic>] [--tag <facet/value>] [-k 8] [--json]
```

- 例:`search.py "test-time 记忆与检索增强的具身智能体" -k 8`
- 过滤:`--topic VLA`(主题子串匹配)、`--tag method/diffusion`(受控 tag 精确匹配)
- 来源:库里**同时含论文报告和 353 个视频(B站/小红书)转写**。默认混排;`--only paper` 或 `--only video` 限定来源。视频结果带 `kind=video`、标题、原始 url。
- `--json` 输出结构化结果便于程序消费。

返回每条:`相关度(0-1)`、`arxiv`、`短名`、`topic`、`year`、`tags`、`一句话 summary`、**`命中节(report/section)+ 片段`**、`hl 笔记路径`。**典型用法:先 search 命中 3-8 篇 → 看命中节定位 → 再 Read 命中论文的 `01_highlevel.md`(高层)或 `02_technical.md`(复现级细节)。**

## 其它索引方式(不需要 embedding)

- **按主题浏览**:`~/proj/omnibox/papers/<topic>/_MOC.md`(每主题地图,分组+一句话+双链);总入口 `INDEX.md`。
- **轻量全量索引**(可整体载入,~43k tokens):`papers/catalog_slim.jsonl`,每行 `{arxiv,short,topic,tags}`。
- **完整目录**:`papers/catalog.jsonl`,每行含 summary/paths(较大,按需 grep 而非整体载入)。
- **按 tag 过滤**:`grep '"tags":.*method/flow-matching' papers/catalog.jsonl`。受控 tag 词表见 `~/proj/omnibox/index/canonical.json`(8 分面:topic/method/task/capability/embodiment/modality/data/model,共 162 个)。

## 维护(`~/proj/omnibox/index/`)

- **增量更新(日常用这个)**:`conda run -n ml python update_index.py` —— 内容哈希比对,只对**新增/改动**的论文重嵌入,几秒搞定。删除的论文自动清理。
- **全量重建(很少用)**:`conda run -n ml python build_index.py`(读 frontmatter→两份报告全文分块→bge-m3 嵌入→重写 papers.db,~29k chunk,SiliconFlow 限流时 ~25min)。⚠️ 全量重建会清空视频 → 之后**必须再跑** `add_videos.py`。
- **视频转写入库**:`conda run -n ml python add_videos.py`(可重复运行,先清旧视频行再灌)。
- 依赖:conda env `ml`(`sqlite-vec`、`urllib`);SiliconFlow key 在 `~/.siliconflow_key`(模型 `BAAI/bge-m3`,1024 维,批量≤32)。
- Obsidian 动态视图:`papers/Papers.base`(4 个视图:全部按主题/有官方代码/2025后/卡片墙)。
