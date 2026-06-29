export const meta = {
  name: 'survey-deepread-ingest',
  description: 'One agent per paper: fetch PDF + official repo, read both, write 01_highlevel.md + 02_technical.md (WITH frontmatter) into the Mac OmniBox corpus',
  phases: [{ title: 'DeepRead', detail: 'fan-out arxiv-deepdive per paper; reports land in ~/proj/omnibox/papers' }],
}

// ── Inputs (pass via the Workflow tool's `args`) ───────────────────────────────
//   args = { manifest: "/Users/glt/proj/omnibox/papers/_DEEPREAD_manifest.json", count: 152 }
// Each manifest entry: { arxiv_id, title, topic_dir, slug, one_liner }
//   topic_dir = directory name WITHOUT the "topic/" prefix (e.g. "world-model", "memory")
//   slug      = paper main-name lowercased & hyphenated
// Agents self-load their entry by index → keeps both the script and each prompt tiny.
const MANIFEST = args.manifest
const COUNT = args.count
const BASE = '/Users/glt/proj/omnibox/papers'                 // ⚠️ Mac corpus — NOT /home/glt/...
const VOCAB = '/Users/glt/proj/omnibox/index/canonical.json'  // controlled tag vocabulary

const SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['arxiv_id', 'slug', 'pdf_ok', 'repo_status', 'reports_written', 'frontmatter_ok', 'tags', 'notes'],
  properties: {
    arxiv_id: { type: 'string' },
    slug: { type: 'string' },
    pdf_ok: { type: 'boolean' },
    repo_url: { type: ['string', 'null'] },
    repo_status: { type: 'string', enum: ['cloned', 'cloned_then_removed_large', 'no_official_repo', 'clone_failed', 'too_large_skipped'] },
    reports_written: { type: 'boolean' },          // both 01_highlevel.md AND 02_technical.md written
    frontmatter_ok: { type: 'boolean' },           // 01_highlevel.md has the required YAML frontmatter
    tags: { type: 'array', items: { type: 'string' } }, // tags chosen, all from canonical.json
    notes: { type: 'string' },
  },
}

log(`DeepRead: ${COUNT} papers → ${BASE} (manifest ${MANIFEST})`)
phase('DeepRead')

const idx = Array.from({ length: COUNT }, (_, i) => i)

const out = await parallel(idx.map((i) => () =>
  agent(
`You produce a deep, code-grounded engineer study of ONE paper using BOTH the PDF and the official repo, then write TWO Chinese reports into the OmniBox corpus so they can be vector-indexed. Follow the arxiv-deepdive skill.

STEP 0 — load your assignment (do this first, in Bash):
  python3 -c "import json;print(json.dumps(json.load(open('${MANIFEST}'))[${i}],ensure_ascii=False))"
This prints {arxiv_id,title,topic_dir,slug,one_liner}. Use those below. TARGET DIR = ${BASE}/<topic_dir>/<arxiv_id>_<slug>/

STEPS (Bash, Read, WebSearch, WebFetch):
1. mkdir -p the TARGET DIR.
2. PDF → <dir>/paper.pdf:
   curl -L --retry 3 --retry-delay 5 -A "Mozilla/5.0" -o <dir>/paper.pdf "https://arxiv.org/pdf/<arxiv_id>"
   verify it begins with %PDF and is >50KB; if not, retry https://export.arxiv.org/pdf/<arxiv_id>. Set pdf_ok.
3. Find the OFFICIAL repo (authors' own — WebSearch '<title> github', arXiv abstract, project page), NOT a reimplementation. None → repo_status=no_official_repo.
4. If a repo exists, shallow+blobless clone:
   GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --filter=blob:none <url> <dir>/repo ; du -sm <dir>/repo
   - clone fails → repo_status=clone_failed (read files online via WebFetch instead)
   - size > 800MB → after reading what you need, rm -rf <dir>/repo, write the URL into <dir>/REPO_URL.txt, repo_status=cloned_then_removed_large
   - else keep it, repo_status=cloned
5. READ: the whole PDF (use the pages param, INCLUDING the appendix — hyperparams/algorithms live there) + repo README, configs, and key model/training/inference source files. Ground numbers in file:line / config keys.
6. Pick TAGS — read the controlled vocabulary first and choose ONLY from it:
     cat ${VOCAB}
   Facets: topic/ method/ task/ embodiment/ capability/ data/ modality/ model/ benchmark. If your paper's topic isn't present, use the closest existing tag (do NOT invent new vocab here). Return the tags you used.
7. Write TWO Chinese markdown reports.

   <dir>/01_highlevel.md — MUST START with this exact YAML frontmatter block (required for indexing; omitting it means the paper is NOT indexed):
   ---
   arxiv: "<arxiv_id>"
   title: "<英文标题>"
   aliases: ["<方法简称/别名>"]
   type: highlevel
   topic: "<topic_dir>"
   year: <出版年, 整数>
   authors: ["..."]
   affiliations: ["..."]
   repo: "<repo url 或空字符串>"
   has_repo: <true|false>
   tags: ["topic/...", "method/...", ...]   # 全部取自 canonical.json
   related: []
   summary: "<一两句中文定位。绝不要用 ASCII 双引号 \\" —— 用「中文引号」代替,否则 YAML 断裂>"
   ---
   然后正文(高层叙述,少公式): 一句话定位; 解决的问题/动机; 核心idea/关键洞察(直觉); 主要贡献(bullet); 与已有工作区别; 适用场景与局限.

   <dir>/02_technical.md — frontmatter 同上但 type: technical;正文面向工程师、详细不遗漏: 整体架构(模块/数据流/张量形状); 训练细节(数据集与预处理/损失公式+代码位置/优化器/lr/调度/batch/步数/硬件与时长/trick/超参表,尽量具体数值并标来源); 推理细节(流程/动作解码采样/chunk/频率/延迟/部署); 代码层面(仓库结构/关键文件函数/配置入口/实际可跑的训练与评测命令/依赖环境与版本坑); 复现要点与坑. 诚实标注: 无官方repo / 只放推理没放训练 / 论文与代码不一致 / 用了内部数据无法严格复现.
8. After BOTH files exist,省盘: rm -f <dir>/paper.pdf (仅当两份报告都已写好且非空时).

CRITICAL: end by calling the StructuredOutput tool with arxiv_id, slug, pdf_ok, repo_status, repo_url, reports_written=true, frontmatter_ok=true, the tags array, and notes. Do not end your turn without it.`,
    { schema: SCHEMA, label: `p${i}`, phase: 'DeepRead', agentType: 'general-purpose' }
  )
))

const r = out.filter(Boolean)
log(`Done ${r.length}/${COUNT}: pdf_ok=${r.filter(x => x.pdf_ok).length} reports=${r.filter(x => x.reports_written).length} frontmatter=${r.filter(x => x.frontmatter_ok).length}`)
return { results: r, total: COUNT, written: r.filter(x => x.reports_written).length }
