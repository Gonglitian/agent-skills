# Agent Skills Collection

A comprehensive collection of **33 Claude Code skills** for ML research workflows, covering the full research cycle from literature survey to experiment management.

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

### Experiment Management (实验管理)

| Skill | Description |
|-------|-------------|
| **[auto_experiment](https://github.com/Gonglitian/agent-skills/tree/main/skills/auto_experiment)** | Full experiment lifecycle: workspace setup → iterative experiment loop → final report |
| **[experiment_report](https://github.com/Gonglitian/agent-skills/tree/main/skills/experiment_report)** | Structured experiment reports with results-first format and W&B integration |
| **[gpu-train-monitor](https://github.com/Gonglitian/agent-skills/tree/main/skills/gpu-train-monitor)** | Multi-GPU training monitoring: GPU stats, loss tracking, throughput analysis |
| **[train-debug](https://github.com/Gonglitian/agent-skills/tree/main/skills/train-debug)** | Systematic training diagnosis: OOM, NaN gradients, loss plateau, multi-GPU issues |
| **[data-pipeline-check](https://github.com/Gonglitian/agent-skills/tree/main/skills/data-pipeline-check)** | Dataset validation, schema checks, quality metrics, and compatibility verification |

### Engineering (代码工程)

| Skill | Description |
|-------|-------------|
| **[project-init](https://github.com/Gonglitian/agent-skills/tree/main/skills/project-init)** | Initialize research projects: conda env, CLAUDE.md, git, data path organization |
| **[setup-dev-env-ubuntu](https://github.com/Gonglitian/agent-skills/tree/main/skills/setup-dev-env-ubuntu)** | Bootstrap a fresh Ubuntu machine: zsh + oh-my-zsh + fzf, Ghostty, Edge, VSCode, Miniconda, Claude Code + claude-hud, gh auth, Snipaste, WeChat, fcitx, Tailscale |
| **[tmux-workspace](https://github.com/Gonglitian/agent-skills/tree/main/skills/tmux-workspace)** | Generate tmuxinator configs for multi-project terminal workspaces |

### Meta (元技能)

| Skill | Description |
|-------|-------------|
| **[skill-creator](https://github.com/Gonglitian/agent-skills/tree/main/skills/skill-creator)** | Create new skills, run evals, benchmark variance, optimize descriptions for triggering accuracy |
| **[find-skills](https://github.com/Gonglitian/agent-skills/tree/main/skills/find-skills)** | Discover and install skills from the open agent-skills ecosystem (skills.sh) |

### Domain-Specific (领域专用)

| Skill | Description |
|-------|-------------|
| **[isaaclab-dev](https://github.com/Gonglitian/agent-skills/tree/main/skills/isaaclab-dev)** | Isaac Lab robot simulation development reference manual |
| **[isaaclab-async-pipeline-dev](https://github.com/Gonglitian/agent-skills/tree/main/skills/isaaclab-async-pipeline-dev)** | Async data generation pipeline for Isaac Lab |
| **[wuyin-gpt-image-2](https://github.com/Gonglitian/agent-skills/tree/main/skills/wuyin-gpt-image-2)** | GPT-Image-2 text-to-image / image edit via 速创API (api.wuyinkeji.com): async submit → poll → download, with 3 paper-figure style presets (UniVLA / Physical Intelligence / Fast-WAM), each shipping curated reference images auto-uploaded to catbox and reused as `urls` for high-fidelity style-mimic |

## Research Workflow

These skills support the full research cycle:

```
idea_refinery → gap-to-method → project-init → auto_experiment → experiment_report
     ↑              ↑                                  ↑
comprehensive-survey read-paper                gpu-train-monitor
                                               train-debug
                                               data-pipeline-check
```

## License

MIT
