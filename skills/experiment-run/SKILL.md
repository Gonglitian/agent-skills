---
name: experiment-run
description: Execute experiments from EXPERIMENT_TRACKER.md produced by experiment-plan. For each TODO run: launch training/eval, monitor via gpu-train-monitor, auto-diagnose failures via train-debug, collect results, update tracker. Bridges the gap between planning (experiment-plan) and reporting (experiment_report). Use when user says "跑实验", "run experiments", "执行实验", "按照 plan 跑", or has an EXPERIMENT_TRACKER.md ready to execute.
---

# Experiment Run: Execute the Plan

Read EXPERIMENT_TRACKER.md → execute runs in order → update with results. **Delegates monitoring to gpu-train-monitor, debugging to train-debug.**

## Pipeline

```
refine-logs/EXPERIMENT_TRACKER.md
  │
  ├─ P0: Load tracker, verify environment
  ├─ P1: Execute runs stage-by-stage (M0→M1→M2→M3→M4)
  │     ├─ Launch training/eval script
  │     ├─ Monitor → gpu-train-monitor
  │     └─ On failure → train-debug (Peng Sida 十问)
  ├─ P2: Collect results, update tracker
  └─ Output: updated EXPERIMENT_TRACKER.md + results/
```

## Parameters

Parse from `$ARGUMENTS`:
- **Positional**: path to EXPERIMENT_TRACKER.md (default: `refine-logs/EXPERIMENT_TRACKER.md`)
- `--stage <M0-M4>` — run only specific stage (default: all TODO)
- `--dry-run` — validate scripts without executing
- `--gpu <N>` — GPU device(s) to use (default: 0)

## P0: Load & Verify

```bash
# Read tracker, extract TODO runs sorted by stage
# Verify each run has a launchable script
# Check: GPU available, data paths exist, model checkpoints accessible
# If W&B configured (CLAUDE.md), verify API key + project
```

Gate: all MUST-RUN scripts are launchable → proceed.

## P1: Execute Stage by Stage

For each stage M0→M4, for each TODO run in that stage:

### 1a: Launch

```bash
# Example: python train.py --config configs/exp_001.yaml --seed 42
# Capture PID, log file path, W&B run URL
```

### 1b: Monitor → **gpu-train-monitor** (if available)

```bash
# Watch: GPU util, loss curve, memory. Alert if: loss diverges, OOM, GPU idle > 5min
```

### 1c: Decision Gate (from EXPERIMENT_PLAN.md)

| Stage | Gate | Action on Fail |
|-------|------|---------------|
| M0 | Loss decreases | Fix pipeline, re-run |
| M1 | Match published ±σ | Debug baseline implementation |
| M2 | Claim holds | → train-debug (Peng Sida 十问) |
| M3 | No bloat | Accept or remove component |
| M4 | All MUST-RUN done | Move to experiment_report |

### 1d: On Failure → **train-debug**

If a run doesn't pass its gate, invoke train-debug with the run's log file. Apply fixes, mark run as BLOCKED with diagnosis, continue to next run.

## P2: Collect & Update

For each completed run:
```bash
# Extract: final metrics, best checkpoint path, W&B URL
# Update EXPERIMENT_TRACKER.md: TODO → DONE, fill Result column
# Save detailed logs to results/<run_id>/
```

Failed runs: TODO → BLOCKED, fill Notes with diagnosis + suggested fix.

## Output

```
refine-logs/
├── EXPERIMENT_TRACKER.md     ← Updated (TODO→DONE/BLOCKED)
└── results/
    ├── R001/                  ← Logs, checkpoints, metrics JSON
    ├── R002/
    └── ...
```

## Stage Gates Reference

| Stage | Must Pass | Tolerance |
|-------|-----------|-----------|
| M0 | Pipeline runs, loss decreases, no NaN | Zero tolerance for bugs |
| M1 | Reproduced baselines match published | ±1 std from reported |
| M2 | Main claim: ours > baseline by target margin | Statistical significance |
| M3 | Ablation −component < full method | Clear gap |
| M4 | All MUST-RUN complete | — |

## Key Rules

1. **Stage order is strict.** Don't run M2 before M1 passes.
2. **One run at a time per GPU.** Don't oversubscribe.
3. **Log everything.** Every run gets a timestamped log file.
4. **Gate before proceeding.** Don't launch M3 if M2 failed.
5. **Update tracker immediately.** Don't batch — status goes stale.
6. **On failure, diagnose before re-running.** Blind re-runs waste GPU-hours.

## Calls

- gpu-train-monitor (P1b)
- train-debug (P1d)
- Reads: refine-logs/EXPERIMENT_TRACKER.md (from experiment-plan)

## Called by

experiment-plan → experiment-run (YOU ARE HERE) → experiment_report → paper-write
