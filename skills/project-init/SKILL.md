---
name: project-init
description: Initialize a new research project with conda environment, CLAUDE.md, git setup, data/checkpoint path organization, and planning files. Trigger when user starts a new project, says "新项目", "初始化", "project init", "/init", "搭建环境", "新建项目", "配置环境", "setup environment", or clones a new repo and needs conda + paths + CLAUDE.md setup.
---

# Research Project Initializer

Set up a new research project with all standard infrastructure.

## When Triggered

- User clones a new repository
- User says "初始化项目", "新项目", "/init"
- User starts working in an unfamiliar codebase

## Execution Steps

### Step 1: Environment Survey

```bash
# Check server resources
hostname
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader
df -h /data1 /data2 2>/dev/null
conda env list
```

Determine:
- Available GPUs and their assignment across projects
- Storage paths (prefer /data1 or /data2 for data/checkpoints)
- Existing conda environments that might be reusable

### Step 2: Conda Environment Setup

```bash
# Create project-specific environment
conda create -n <project_name> python=<version> -y
conda activate <project_name>

# Install requirements if present
pip install -r requirements.txt  # or setup.py / pyproject.toml
```

**Ask user for:**
- Python version requirement
- Key dependencies (PyTorch version, CUDA version)
- Whether to reuse an existing environment

### Step 3: Directory Structure

Create standard project organization:

```
<project_root>/
├── CLAUDE.md           # AI assistant guide
├── data/               # symlink to /data{1,2}/<user>/<project>/data
├── checkpoints/        # symlink to /data{1,2}/<user>/<project>/ckpt
├── logs/               # training logs
├── docs/               # documentation
│   └── pipeline.md     # data/training pipeline description
├── scripts/            # utility scripts
├── papers/             # reference papers
└── outputs/            # experiment outputs
```

```bash
# Create data symlinks to data disk
DATA_BASE="/data1/vla-reasoning/<project_name>"
mkdir -p "$DATA_BASE"/{data,ckpt,outputs}

ln -sf "$DATA_BASE/data" ./data
ln -sf "$DATA_BASE/ckpt" ./checkpoints
ln -sf "$DATA_BASE/outputs" ./outputs

mkdir -p logs docs scripts papers
```

### Step 4: Git Setup

```bash
# If not already a git repo
git init
git checkout -b <user>/dev  # or main

# Create .gitignore
cat > .gitignore << 'EOF'
# Data and models (stored on data disk)
data/
checkpoints/
outputs/
*.hdf5
*.h5
*.pkl
*.npy
*.npz
*.pt
*.pth
*.ckpt
*.safetensors

# Environment
.venv/
__pycache__/
*.pyc
*.egg-info/

# Logs
logs/
wandb/
*.log
nohup.out

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
EOF
```

### Step 5: Generate CLAUDE.md

Analyze the codebase and generate a comprehensive CLAUDE.md:

```markdown
# <Project Name>

## Overview
[Brief project description based on README/code analysis]

## Environment
- **Conda env**: `<env_name>`
- **Python**: X.X
- **Key deps**: PyTorch X.X, transformers X.X, etc.
- **Activate**: `conda activate <env_name>`

## Key Paths
- **Code**: /home/vla-reasoning/proj/<project>
- **Data**: /data1/vla-reasoning/<project>/data
- **Checkpoints**: /data1/vla-reasoning/<project>/ckpt
- **Logs**: ./logs/

## Common Commands
```bash
# Training
python train.py --config configs/default.yaml

# Evaluation
python eval.py --checkpoint <path>
```

## Code Structure
[Key files and their purposes]

## Notes
[Any important conventions, gotchas, or decisions]
```

### Step 6: Planning Files (Optional)

If user wants project planning:

```bash
# Create planning-with-files structure
mkdir -p docs
cat > docs/task_plan.md << 'EOF'
# Task Plan

## Goals
- [ ] Goal 1
- [ ] Goal 2

## Current Phase
Phase 1: Setup and Exploration

## Next Steps
1. ...
EOF
```

### Step 7: Summary

Output a concise summary:

```markdown
## 项目初始化完成 ✓

| 项目 | 配置 |
|------|------|
| 项目名 | <name> |
| Conda 环境 | <env_name> (Python X.X) |
| 数据路径 | /data1/vla-reasoning/<project>/data |
| Checkpoint 路径 | /data1/vla-reasoning/<project>/ckpt |
| Git 分支 | <user>/dev |
| GPU 分配 | [建议: GPU X-Y] |

### 下一步建议
1. 阅读代码结构，理解 pipeline
2. 下载所需数据集
3. 运行 baseline 实验
```

## Key Rules

1. **Always use data disk** for large files (/data1 or /data2, NOT home directory)
2. **Symlink, don't copy** - create symlinks from project to data disk
3. **One conda env per project** - avoid environment conflicts
4. **Git ignore data** - never commit large files
5. **Chinese summary** - output in Chinese with English technical terms
6. **Ask before acting** - confirm environment name, Python version, GPU assignment with user
