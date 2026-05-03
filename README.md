# Agent Skills Collection

A comprehensive collection of Claude Code skills for ML research workflows, covering the full research cycle from literature survey to experiment management.

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
| **research-survey** | Deep literature survey: vec-db semantic search + web search + parallel subagent reading → structured report |
| **read-paper** | Deep-read papers with VLM figure analysis, parallel subagents, and structured 12-section notes |
| **gap-to-method** | Multi-dimensional literature matrix → Gap discovery → Evidence-based method proposal |
| **idea_refinery** | Iteratively refine research ideas through survey, validation, and branching exploration |
| **paper_related_works** | Build predecessor/successor citation maps for any paper |
| **create_skill_with_paper** | Turn academic papers into reusable skill reference cards |
| **paper-intro-writing** | Write reviewer-grade paper Introductions: 6-段黄金骨架 + 10 篇 VLA/robot-learning 顶会 paper 拆解 + Mad-Libs 填空模板 + 25 项自检表 |

### Experiment Management (实验管理)

| Skill | Description |
|-------|-------------|
| **auto_experiment** | Full experiment lifecycle: workspace setup → iterative experiment loop → final report |
| **experiment_report** | Structured experiment reports with results-first format and W&B integration |
| **gpu-train-monitor** | Multi-GPU training monitoring: GPU stats, loss tracking, throughput analysis |
| **train-debug** | Systematic training diagnosis: OOM, NaN gradients, loss plateau, multi-GPU issues |
| **data-pipeline-check** | Dataset validation, schema checks, quality metrics, and compatibility verification |

### Engineering (代码工程)

| Skill | Description |
|-------|-------------|
| **project-init** | Initialize research projects: conda env, CLAUDE.md, git, data path organization |
| **setup-dev-env-ubuntu** | Bootstrap a fresh Ubuntu machine: zsh + oh-my-zsh + fzf, Ghostty, Edge, VSCode, Miniconda, Claude Code + claude-hud, gh auth, Snipaste, WeChat, fcitx, Tailscale |
| **git-pushing** | One-click git add → conventional commit → push |
| **review-pr** | PR code review with CONTRIBUTING.md compliance checking |
| **tmux-workspace** | Generate tmuxinator configs for multi-project terminal workspaces |

### Meta (元技能)

| Skill | Description |
|-------|-------------|
| **skill-creator** | Create new skills, run evals, benchmark variance, optimize descriptions for triggering accuracy |
| **find-skills** | Discover and install skills from the open agent-skills ecosystem (skills.sh) |

### Domain-Specific (领域专用)

| Skill | Description |
|-------|-------------|
| **isaaclab-dev** | Isaac Lab robot simulation development reference manual |
| **isaaclab-async-pipeline-dev** | Async data generation pipeline for Isaac Lab |
| **wuyin-gpt-image-2** | GPT-Image-2 text-to-image / image edit via 速创API (api.wuyinkeji.com): async submit → poll → download, with 3 paper-figure style presets (UniVLA / Physical Intelligence / Fast-WAM), each shipping curated reference images auto-uploaded to catbox and reused as `urls` for high-fidelity style-mimic |

### Paper Knowledge Base (论文知识库)

Pre-built reference cards for key papers:

| Skill | Paper |
|-------|-------|
| paper_rob__openpi | Physical Intelligence VLA (pi0, pi0-FAST, pi0.5) |
| paper_rob__any3d_vla | Any3D-VLA: 3D Point Cloud VLA |
| paper_rob__3d_diffusion_policy | 3D Diffusion Policy |
| paper_rob__robocasa | RoboCasa simulation |
| paper_rob__ibrl | IBRL |
| paper_rob__idp3 | iDP3 |
| paper_rob__resfit | ResFit |
| paper_rob__rdd | RDD |
| paper_rob__bpp | BPP |
| paper_rl__dqc | Decoupled Q-Chunking |
| paper_rl__qc | Q-Chunking |
| paper_3d__concerto | Concerto 3D encoder |
| paper_3d__utonia | Utonia 3D generation |

## Research Workflow

These skills support the full research cycle:

```
idea_refinery → gap-to-method → project-init → auto_experiment → experiment_report
     ↑              ↑                                  ↑
research-survey  read-paper                    gpu-train-monitor
                                               train-debug
                                               data-pipeline-check
```

## License

MIT
