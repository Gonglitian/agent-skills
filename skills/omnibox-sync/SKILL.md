---
name: omnibox-sync
description: >-
  增量拉取一个 OmniBox（小黑 / omnibox.pro/s/<token>）公开分享里"自上次以来新增或变更"的保存内容（链接/文档/文件），做最小 token 的 DIFF：
  先只拉元数据比对 id + updated_at，只对 delta 拉正文，并维护一份持久化快照（全局 ~/.claude/omnibox-sync/<token>.json）。
  Use PROACTIVELY whenever the user wants to check / pull / sync NEW or updated items from an OmniBox share, or says
  "OmniBox 又更新了", "小黑里加了新内容", "拉一下新增的保存", "看看 OmniBox 有什么新东西", "增量同步 OmniBox",
  "omnibox 的 diff", "omnibox.pro/s/ 新增", "sync omnibox", "pull new omnibox links", "what's new in my omnibox share"。
  本 skill 单一职责：只产出"增量"（new/changed 的结构化清单 + 正文），不做下游分类/arXiv 解析/报告——那些另起（如 arxiv-deepdive）。
---

# omnibox-sync：OmniBox 分享的增量 DIFF 拉取

OmniBox（小黑）的一个公开分享是一棵随时间增长的资源树。每次想"看看又加了什么"时，全量重拉 1000+ 条既慢又费 token。这个 skill 用 **快照 + DIFF** 只取增量：**元数据先比对，正文只拉 delta**。

**单一职责**：只负责把"新增 / 变更"的条目拉出来、落成结构化文件、更新快照。**不做**分类、不做 arXiv 解析、不写技术报告——那些是下游的事（比如对新论文跑 `arxiv-deepdive`），按需另起。

## 为什么这样最省 token

OmniBox 的 API 分两层：
- **列子节点**（`/children`）：返回 id / name / url / type / created_at / **updated_at**，**不含正文** —— 便宜。
- **取单个资源**（`/resources/{id}`）：返回 `content`（解析后的正文）+ `tags` —— 贵。

所以：先用列接口拿到当前全树的元数据，和快照里的「已见 id + updated_at」比对，**只对新增和变更的那几条**调用取资源接口。1221 条里只新增 85 条时，正文调用就只有 85 次，而非 1221 次。

## 用法

核心是自带脚本，已封装好上述逻辑：

```bash
python3 <skill_dir>/scripts/ob_diff.py --token <share_token> [--out-dir <dir>]
```

- `--token`：分享 slug，即 `omnibox.pro/s/<token>` 里的 `<token>`（如 `FdTOBfmV2D`）。
- `--root`：根资源 id，**可省**（脚本自动从 `/api/v1/shares/<token>` 元数据发现）。
- `--snapshot`：快照路径，**默认全局** `~/.claude/omnibox-sync/<token>.json`（跨 /tmp 清理存活，按 share 分文件）。一般不用传。
- `--out-dir`：delta 文件输出目录，默认当前目录。
- `--no-changed`：只看新增、忽略 updated_at 变更（默认会**追踪变更并重拉**其正文）。
- `--seed-from-children <file>`：**仅当快照不存在时**用一份旧的 children 元数据 dump（`[{id, updated_at}, ...]`）初始化快照，从而首跑就只报真实增量、不把存量当新增。
- `--base`：API 根，默认 `https://www.omnibox.pro`（自部署实例改这里）。

### 产物
写到 `--out-dir`：
- `omnibox_delta_<token>_<stamp>.json`：结构化，含 `new[]` / `changed[]`（均带 `content`+`tags`）/ `removed[]` + `counts`。
- `omnibox_delta_<token>_<stamp>.md`：人读摘要表（类型 / 标题 / 链接 / 标签 / 正文字数）。

脚本末尾打印 `DELTA_NEW=.. DELTA_CHANGED=.. DELTA_REMOVED=..`，便于程序判断。**delta 为 0 也是成功**（说明没更新）。

## 语义与边界

- **快照即"已见全集"**：每次跑完，快照被刷新为"当前全树的 id+updated_at"。所以 DIFF 永远是"相对上次同步"的增量。
- **变更检测靠 `updated_at`**：默认 new + changed 都重拉正文（用户编辑过的旧条目也会被重新抓取）。
- **删除只记录不处理**：快照有、当前无的 id 列进 `removed`，不做动作。
- **首次同步（无快照、无 seed）= 全量**：这是对的——第一次必须把整棵树读一遍建立基线；之后才增量。要避免把已处理的存量当新增，用 `--seed-from-children` 喂一份历史元数据 dump。
- **嵌套文件夹**：脚本会对 `has_children` 的节点递归，递归只花元数据调用，仍便宜。本类分享多为扁平（根下直接挂全部）。
- **鉴权**：公开分享免鉴权；私有分享本 API 取不到。

## 典型场景

**Input:** 用户说"OmniBox 又加了新东西，拉一下增量"，分享是 `omnibox.pro/s/FdTOBfmV2D`
**Output:** 运行 `ob_diff.py --token FdTOBfmV2D`，得到 `omnibox_delta_FdTOBfmV2D_<stamp>.{json,md}`（只含新增/变更项及其正文），快照同步更新。随后若用户想进一步处理这些新内容（分类、对新 arXiv 论文出报告），再各自调用对应流程。
