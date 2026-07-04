# Agent Skills Collection

A comprehensive collection of **46 Claude Code skills** for ML research workflows, covering the full research cycle from literature survey to experiment management.

## Installation

```bash
# Install all skills
npx skills add Gonglitian/agent-skills

# Install specific skill
npx skills add Gonglitian/agent-skills --skill read-paper
```

## Skills Overview

### Research & Literature (研究调研)

| Skill | Description |
|-------|-------------|
| **[comprehensive-survey](https://github.com/Gonglitian/agent-skills/tree/main/skills/comprehensive-survey)** | Full-spectrum survey: 6 academic sources + 5 social platforms → parallel subagents → structured report with concept glossary |
| **[topic_survey](https://github.com/Gonglitian/agent-skills/tree/main/skills/topic_survey)** | Interactive field survey: explore sub-topics guided by user, produce a structured literature review / reading list |
| **[read-paper](https://github.com/Gonglitian/agent-skills/tree/main/skills/read-paper)** | Deep-read papers with VLM figure analysis, parallel subagents, and structured 12-section notes |
| **[gap-to-method](https://github.com/Gonglitian/agent-skills/tree/main/skills/gap-to-method)** | Multi-dimensional literature matrix → Gap discovery → Evidence-based method proposal |
| **[idea_refinery](https://github.com/Gonglitian/agent-skills/tree/main/skills/idea_refinery)** | Iteratively refine research ideas through survey, validation, and branching exploration |
| **[paper_related_works](https://github.com/Gonglitian/agent-skills/tree/main/skills/paper_related_works)** | Build predecessor/successor citation maps for any paper |
| **[create_skill_with_paper](https://github.com/Gonglitian/agent-skills/tree/main/skills/create_skill_with_paper)** | Turn academic papers into reusable skill reference cards |
| **[paper-intro-writing](https://github.com/Gonglitian/agent-skills/tree/main/skills/paper-intro-writing)** | Write reviewer-grade paper Introductions: 6-段黄金骨架 + 10 篇 VLA/robot-learning 顶会 paper 拆解 + Mad-Libs 填空模板 + 25 项自检表 |
| **[research-refine](https://github.com/Gonglitian/agent-skills/tree/main/skills/research-refine)** | Turn a vague direction into a problem-anchored, elegant method plan via iterative GPT-5.4 review |
| **[experiment-plan](https://github.com/Gonglitian/agent-skills/tree/main/skills/experiment-plan)** | Turn a refined proposal into a claim-driven experiment roadmap: ablation matrix, eval protocol, run order, compute budget |
| **[review-ral](https://github.com/Gonglitian/agent-skills/tree/main/skills/review-ral)** | IEEE RA-L paper review assistant: read PDF → multi-source related-work search → parallel deep-read → full bilingual review with scores |
| **[multi-platform-search](https://github.com/Gonglitian/agent-skills/tree/main/skills/multi-platform-search)** | Cross-platform info gathering from Xiaohongshu, Bilibili, Zhihu, and X/Twitter simultaneously |
| **[notion-paper-table](https://github.com/Gonglitian/agent-skills/tree/main/skills/notion-paper-table)** | Build a structured literature survey database in Notion with paper metadata |
| **[paper-discovery-sources](https://github.com/Gonglitian/agent-skills/tree/main/skills/paper-discovery-sources)** | Shared 3-source paper-discovery reference (vec-db / Semantic Scholar / AlphaXiv) loaded by other skills — not user-invokable |
| **[arxiv-deepdive](https://github.com/Gonglitian/agent-skills/tree/main/skills/arxiv-deepdive)** | Code-grounded paper deep-dive: arXiv PDF + official repo shallow-clone (fetch.sh, size-capped) → 01_highlevel (core idea) + 02_technical (training/inference details pinned to file:line, runnable commands, repro pitfalls); flags paper-vs-code mismatches, batch fan-out with INDEX.md |

### Paper Knowledge Base (论文知识库)

| Skill | Description |
|-------|-------------|
| **[omnibox-search](https://github.com/Gonglitian/agent-skills/tree/main/skills/omnibox-search)** | Semantic search over 965 paper reports + 353 video transcripts: full-report chunk index (29k+, bge-m3 + sqlite-vec) → top-k with hit section + note path, topic/受控 tag filters (expects local OmniBox KB at ~/proj/omnibox) |
| **[omnibox-sync](https://github.com/Gonglitian/agent-skills/tree/main/skills/omnibox-sync)** | Token-minimal incremental sync of an OmniBox (小黑) public share: metadata-only diff (id + updated_at) vs persistent snapshot → fetch content for delta only → JSON + MD delta files (new / changed / removed) — ingestion stage feeding arxiv-deepdive |
| **[omnibox-video](https://github.com/Gonglitian/agent-skills/tree/main/skills/omnibox-video)** | Video 预阅读 pipeline: OmniBox share 里的 B站/小红书 videos → audio download (yt-dlp + XHS-Downloader signed API) → faster-whisper GPU transcription → mine spoken arXiv papers (ASR name correction) → dedupe vs existing KB → arxiv-deepdive reports + INDEX; chains omnibox-sync + audio-transcribe + arxiv-deepdive |

### Experiment Management (实验管理)

| Skill | Description |
|-------|-------------|
| **[auto_experiment](https://github.com/Gonglitian/agent-skills/tree/main/skills/auto_experiment)** | Full experiment lifecycle: workspace setup → iterative experiment loop → final report |
| **[experiment_report](https://github.com/Gonglitian/agent-skills/tree/main/skills/experiment_report)** | Structured experiment reports with results-first format and W&B integration |
| **[gpu-train-monitor](https://github.com/Gonglitian/agent-skills/tree/main/skills/gpu-train-monitor)** | Multi-GPU training monitoring: GPU stats, loss tracking, throughput analysis |
| **[checkGPUStatus](https://github.com/Gonglitian/agent-skills/tree/main/skills/checkGPUStatus)** | SSH GPU 巡检 across 4 remote servers (2 Slurm: HPCC/BCC + 2 direct: TASL-LabServer/TASL-7): per-GPU VRAM & util via nvidia-smi; for Slurm — my jobs, account GrpTRES quota with running/queued-job accounting, all-node free GPUs by model → "how many GPUs I can actually request now" (edit SERVERS list for other hosts) |
| **[train-debug](https://github.com/Gonglitian/agent-skills/tree/main/skills/train-debug)** | Systematic training diagnosis: OOM, NaN gradients, loss plateau, multi-GPU issues |
| **[data-pipeline-check](https://github.com/Gonglitian/agent-skills/tree/main/skills/data-pipeline-check)** | Dataset validation, schema checks, quality metrics, and compatibility verification |
| **[weights-and-biases](https://github.com/Gonglitian/agent-skills/tree/main/skills/weights-and-biases)** | Track ML experiments with W&B: auto-logging, real-time visualization, hyperparameter sweeps, model registry |
| **[evidence-report](https://github.com/Gonglitian/agent-skills/tree/main/skills/evidence-report)** | KDA measurement layer: Measure → Diagnose → Plan, never guess — immutable profile/\<run\>/ dirs + aggregate.py (mean±stddev, baseline delta) + 5 analysis dimensions + signal→cause→fix playbook → 2–4 recommendations ranked by evidence × impact |

### Engineering (代码工程)

| Skill | Description |
|-------|-------------|
| **[project-init](https://github.com/Gonglitian/agent-skills/tree/main/skills/project-init)** | Initialize research projects: conda env, CLAUDE.md, git, data path organization |
| **[setup-dev-env-ubuntu](https://github.com/Gonglitian/agent-skills/tree/main/skills/setup-dev-env-ubuntu)** | Bootstrap a fresh Ubuntu machine: zsh + oh-my-zsh + fzf, Ghostty, Edge, VSCode, Miniconda, Claude Code + claude-hud, gh auth, Snipaste, WeChat, fcitx, Tailscale |
| **[tmux-workspace](https://github.com/Gonglitian/agent-skills/tree/main/skills/tmux-workspace)** | Generate tmuxinator configs for multi-project terminal workspaces |
| **[ucr_hpcc_cluster](https://github.com/Gonglitian/agent-skills/tree/main/skills/ucr_hpcc_cluster)** | Work with the UCR HPCC cluster: connecting, job submission, software management, data storage |
| **[ghostty-cjk-input-debug](https://github.com/Gonglitian/agent-skills/tree/main/skills/ghostty-cjk-input-debug)** | Diagnose and fix CJK input-method issues in Ghostty terminal on Linux (snap + fcitx5 + GTK4) |
| **[kda](https://github.com/Gonglitian/agent-skills/tree/main/skills/kda)** | KDA (Kernel Design Agents) orchestration entry point: engineering-loop (control) + domain-wiki (knowledge) + evidence-report (measurement) → Task Contract → correctness-first → evidence-guided optimization → per-regime specialization → promotion, with anti-reward-hacking guards |
| **[engineering-loop](https://github.com/Gonglitian/agent-skills/tree/main/skills/engineering-loop)** | KDA-style long-horizon optimization harness: task contract → draft/plan → one-candidate-at-a-time iterate → promote; immutable baseline + candidates.jsonl DAG (helper script) + benchmark.csv + 3-phase search + anti-reward-hacking guards |
| **[domain-wiki](https://github.com/Gonglitian/agent-skills/tree/main/skills/domain-wiki)** | Provenance-tracked domain knowledge base: sources → atomic entries (verbatim quote + source_ref + date + confidence) → 4-axis query (tag/type/source/symptom) + staleness check via 2 stdlib-only scripts; knowledge layer of the KDA loop |

### Meta (元技能)

| Skill | Description |
|-------|-------------|
| **[skill-creator](https://github.com/Gonglitian/agent-skills/tree/main/skills/skill-creator)** | Create new skills, run evals, benchmark variance, optimize descriptions for triggering accuracy |
| **[find-skills](https://github.com/Gonglitian/agent-skills/tree/main/skills/find-skills)** | Discover and install skills from the open agent-skills ecosystem (skills.sh) |
| **[planning-with-files](https://github.com/Gonglitian/agent-skills/tree/main/skills/planning-with-files)** | Manus-style file-based planning (task_plan.md / findings.md / progress.md) for complex multi-step tasks |
| **[long-horizon-spec](https://github.com/Gonglitian/agent-skills/tree/main/skills/long-horizon-spec)** | 协作式 Plan Mode for long tasks: refine intent → read-only exploration → multi-round AskUserQuestion interview → runnable acceptance checks → SPEC.md hard gate (user must approve) → pick autonomy engine (/goal, Stop hook, Dynamic Workflow, or engineering-loop handoff) + adversarial final review |

### Domain-Specific (领域专用)

| Skill | Description |
|-------|-------------|
| **[isaaclab-dev](https://github.com/Gonglitian/agent-skills/tree/main/skills/isaaclab-dev)** | Isaac Lab robot simulation development reference manual |
| **[isaaclab-async-pipeline-dev](https://github.com/Gonglitian/agent-skills/tree/main/skills/isaaclab-async-pipeline-dev)** | Async data generation pipeline for Isaac Lab |
| **[image-gen](https://github.com/Gonglitian/agent-skills/tree/main/skills/image-gen)** | Unified image generation / edit / compose. Two user-selected backends: `nano` (official Google Gemini "Nano Banana" — fast ~3-10s, cheap, lite/nb2/pro tiers, 1K/2K/4K) and `gpt` (速创API GPT-Image-2 — stronger realism/fine text, async submit→poll). Four style presets usable on either backend (UniVLA / Physical Intelligence / Fast-WAM paper figures + BlueBook 蓝皮书 science-popular infographic), auto-attaching STYLE text block + curated reference images (catbox-cached for gpt, local-inline for nano) |
| **[marp-slide](https://github.com/Gonglitian/agent-skills/tree/main/skills/marp-slide)** | Create professional Marp presentation slides with 7 themes, custom layouts, and auto quality improvements |
| **[paper-talk-deck](https://github.com/Gonglitian/agent-skills/tree/main/skills/paper-talk-deck)** | Turn a set of papers into one continuous Slidev HTML 串讲: per-paper section (motivation → method diagram from original figure + Mermaid redraw → core code with line-by-line focus/magic-move pinned to file:line → results) + cross-paper compare; reuses omnibox-search / arxiv-deepdive / read-paper / drawio for material; exports PDF/PPTX → Google Slides |
| **[slidev-academic-deck](https://github.com/Gonglitian/agent-skills/tree/main/skills/slidev-academic-deck)** | Style + quality layer for research Slidev decks: academic style guide, HTML/CSS flow diagrams (reliable over SVG `<text>`), asset pipeline (paper-figure crops, GIF vs looping MP4, ffmpeg/pdftoppm recipes), Slidev-52 build gotchas, and clean `export --format png` screenshot QA |
| **[audio-transcribe](https://github.com/Gonglitian/agent-skills/tree/main/skills/audio-transcribe)** | Transcribe audio/video to text: faster-whisper large-v3 with parallel CUDA scheduling + mlx-whisper counterpart for Apple Silicon (Metal), plus a context-aware LLM polish pass (auto-triggered, timestamp-preserving) |

### Obsidian (笔记系统)

| Skill | Description |
|-------|-------------|
| **[obsidian-markdown](https://github.com/Gonglitian/agent-skills/tree/main/skills/obsidian-markdown)** | Obsidian Flavored Markdown authoring: wikilinks + embeds (notes/images/PDF/audio/search) + 13 callout types + YAML properties + tags/comments/Mermaid/LaTeX, with 3 syntax reference sheets |
| **[obsidian-bases](https://github.com/Gonglitian/agent-skills/tree/main/skills/obsidian-bases)** | Author Obsidian Bases (.base YAML): 4 view types (table/cards/list/map) + filters/formulas/groupBy/summaries, with Duration-math gotchas, YAML quoting rules, and a full functions reference (Date/String/Number/List/File/RegExp) |
| **[obsidian-cli](https://github.com/Gonglitian/agent-skills/tree/main/skills/obsidian-cli)** | Drive a live Obsidian vault via the `obsidian` CLI: notes / search / daily / tasks / properties / tags / backlinks + plugin-dev loop (reload → dev:errors → screenshot/DOM → console) with in-app JS eval and mobile emulation |

## Research Workflow

These skills support the full research cycle:

```
idea_refinery → gap-to-method → project-init → auto_experiment → experiment_report
     ↑              ↑                                  ↑
comprehensive-survey read-paper                gpu-train-monitor
                                               train-debug
                                               data-pipeline-check
```

And the local paper knowledge-base pipeline:

```
omnibox-sync ─→ arxiv-deepdive ─→ omnibox-search
omnibox-video ↗   (01_highlevel + 02_technical)   (bge-m3 + sqlite-vec semantic search)
```

## License

MIT
