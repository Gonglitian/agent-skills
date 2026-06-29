# Experiment Domain Guide

## Embodied AI / VLA / Robot Manipulation

### Simulation Evaluation
- Simulator + version: Isaac Sim / MuJoCo / LIBERO / CALVIN / RLBench
- Task distribution: single-task / multi-task / language-conditioned / generalization
- Domain randomization: lighting, textures, object positions, camera poses
- Success rate: binary (task-complete) or progressive (subtask progress)
- Episode budget: 100-1000 depending on variance

### Real-Robot Evaluation
- Platform + sensor suite
- Trials per task: ≥20
- Object/scene variation: ≥3-5
- Failure taxonomy: perception / planning / execution error
- Video recording: side-by-side baseline comparison

### Sim-to-Real Gap
- Train in sim → evaluate zero-shot on real
- Compare sim vs real on matched tasks
- Domain randomization ablation: which randomization helps transfer?

### Compute Realism
- VLA training: 100-1000+ GPU-hours — budget honestly
- Multi-GPU: DDP / FSDP strategy

## Peng Sida 十问 (When Experiments Fail)

1. Data pipeline correct? No leakage? Preprocessing consistent?
2. Metric implementation matches definition?
3. Gradient flow: vanishing/exploding?
4. Hyperparameter sensitivity: wider range tried?
5. Baseline strength: properly tuned, not sandbagged?
6. Implementation bugs: dimension mismatch? off-by-one? wrong loss reduction?
7. Statistical significance: enough seeds? variance too high?
8. Task difficulty: benchmark saturated? impossibly hard?
9. Overfitting: train >> eval?
10. Core hypothesis: fundamentally wrong?

Document which questions were checked and findings.
