# Vec-db 安装与配置指南

Vec-db 是基于 LanceDB 的本地论文向量数据库，包含 60K+ 顶会论文，支持语义搜索。

## 前提条件

- Node.js >= 18
- npm / npx

## 检查现有安装

```bash
# 检查默认路径
cd /home/vla-reasoning/proj/litian-research/vec-db && npx tsx src/cli.ts status

# 输出示例：
# === Vec-DB Status ===
# Papers in DB: 63381
# Tables: papers
# Available index files: 32
```

## 如果需要重新构建

```bash
cd <vec-db-path>

# 安装依赖
npm install

# 查看可用索引文件
ls data/indices/

# 构建索引（将论文导入 LanceDB）
npx tsx src/cli.ts index

# 验证
npx tsx src/cli.ts status
```

## 使用方法

### 语义搜索

```bash
cd <vec-db-path>
npx tsx src/cli.ts search "your query here" --top 15
```

### 搜索技巧

- **使用英文查询**：嵌入模型是英文的，中文查询效果较差
- **多角度查询**：同一个话题用 5-8 个不同角度的查询
- **分数阈值**：score > 0.25 有参考价值，> 0.35 高度相关
- **并行查询**：多个查询可以并行执行（多个 Bash 调用）

### 输出格式

搜索结果包含：
- `title`：论文标题
- `venue`：会议/期刊名
- `year`：发表年份
- `abstract`：摘要
- `score`：相关度分数

**注意**：结果不包含 arXiv ID，需要额外通过 WebSearch 或 Semantic Scholar 查找。

## 收录的会议

截至当前版本，vec-db 收录以下会议的论文：

- **AI 顶会**：ICLR, ICML, NeurIPS (2023-2026)
- **CV 顶会**：CVPR, ECCV, ICCV (2023-2025)
- **机器人**：CoRL, RSS, ICRA, IROS (2023-2025)
- 其他：AAAI, WACV 等

运行 `npx tsx src/cli.ts status` 可查看完整列表。
