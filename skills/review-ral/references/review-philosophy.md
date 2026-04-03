# Review Philosophy: How to Write Sharp, Incisive Reviews

The goal is not to find fault for its own sake, but to see what others miss. A great review
helps the authors improve their work AND helps the editor make the right decision. Generic
reviews ("the experiments are insufficient") are useless. Specific reviews ("Table 2 omits
comparison with Method X which achieves 0.5px lower EPE on the same benchmark") are valuable.

---

## The Reviewer's Mindset

Think of yourself as a **friendly but rigorous expert** who genuinely wants to help:
- If the paper is good, help the authors make it great
- If the paper has flaws, explain exactly what they are and how to fix them
- If the paper is fundamentally flawed, be clear about why so the authors don't waste time on minor revisions

You are NOT trying to:
- Show off your knowledge
- Reject papers to reduce competition
- Write a template review that could apply to any paper
- Be harsh for the sake of being harsh

---

## 10 Angles for Finding Non-Obvious Issues

These are the "刁钻见解" (sharp insights) that separate expert reviews from generic ones.
Not every angle applies to every paper — pick the ones that are relevant.

### 1. Question the Problem Formulation

Before checking if the solution works, ask: **is the problem well-defined?**
- Is the problem statement actually what practitioners need?
- Are the evaluation metrics aligned with the real objective?
- Is there a simpler formulation that the authors overlooked?

Example: A paper claims "real-time" performance but defines real-time as >15 FPS. 
For autonomous driving stereo matching, real-time typically means >30 FPS at full resolution.
This reframing changes whether the paper's contribution is meaningful.

### 2. Check the Baseline Fairness

This is the most common source of inflated results. Look for:
- **Stale baselines** — comparing against methods from 3+ years ago when newer ones exist
- **Unfair training** — did all methods use the same training data, augmentation, schedule?
- **Re-implementation vs. original** — did they re-implement baselines (possibly poorly) or use official code?
- **Hardware differences** — comparing FPS numbers across different GPUs is meaningless
- **Missing baselines** — is there an obvious method they didn't compare against?

Red flag: If a paper only compares against methods it beats, and excludes methods that would beat it.

### 3. Scrutinize the Ablation Study

A good ablation isolates each contribution. Common issues:
- **Additive-only ablation** — they only show "base → +A → +A+B → +A+B+C" but never test B or C alone. 
  This doesn't tell you if B or C independently contribute.
- **Missing the obvious baseline** — what if you just use a bigger/smaller backbone instead of their fancy module?
- **Ablation on easy data only** — ablation on one dataset but the main results are on another
- **Marginal improvements** — if removing a complex module only drops 0.1%, is it worth the complexity?

### 4. Look for Statistical Significance Issues

- **No variance reporting** — single run results are unreliable. Random seed variance can be >1% on many benchmarks.
- **Tiny improvements** — 0.02% improvement is likely noise, not signal
- **Leaderboard numbers** — if they claim SOTA on a leaderboard, check if the leaderboard has been updated since submission
- **Train/test overlap** — have they verified no contamination?

### 5. Examine Failure Cases and Limitations

Honest papers discuss where their method fails. If a paper doesn't:
- What are the known hard cases for this problem? Do they address them?
- What happens at distribution shift (different datasets, domains)?
- What are the computational limits (resolution, batch size, memory)?
- If they claim generalization, do they actually test it?

### 6. Check Figure and Table Integrity

- **Qualitative cherry-picking** — are the shown examples the best cases? Request random sampling.
- **Scale manipulation** — are axis scales chosen to exaggerate differences?
- **Missing error bars** — especially in bar charts comparing methods
- **Inconsistent numbers** — do numbers in the text match the tables? Do the tables match the figures?
- **Resolution and readability** — can you actually read the figures at print size?

### 7. Assess Computational Efficiency Claims

Efficiency claims are often misleading:
- **FLOPs vs. actual latency** — FLOPs don't account for memory bandwidth, parallelism, etc.
- **Parameter count vs. speed** — a model with fewer parameters can be slower if it's sequential
- **Batch size effects** — some methods are only fast at batch size 1
- **Pre-processing/post-processing** — is total pipeline time reported, or just model inference?
- **Hardware-specific optimizations** — TensorRT/ONNX optimized vs. naive PyTorch isn't a fair comparison

### 8. Evaluate Novelty Depth

There's a spectrum from "completely new paradigm" to "just tuned hyperparameters":
- **Architecture novelty** — is the new module fundamentally different from existing ones, or just a rearrangement?
- **Loss function novelty** — is the new loss actually different in behavior, or mathematically equivalent to existing ones?
- **Pipeline novelty** — is the contribution in the method itself, or just in how existing pieces are combined?
- **Concurrent work** — has similar work appeared on arXiv within months? (Not the authors' fault, but affects novelty)

### 9. Question Generalizability Claims

Authors often overclaim generalizability:
- **Tested on N=2 datasets** — that's not "generalizable", that's "works on two datasets"
- **Domain gap** — training on synthetic, testing on real, without domain adaptation analysis
- **Scale effects** — does it work at different resolutions, speeds, noise levels?
- **Edge cases** — textureless regions, occlusions, thin structures, reflective surfaces

### 10. Look for Presentation Red Flags

These often signal deeper issues:
- **Vague language** — "our method significantly outperforms" without numbers
- **Passive voice to hide agency** — "it was found that" — by whom? how?
- **Overstated claims** — "first to", "novel", "state-of-the-art" without strong evidence
- **Missing details** — hyperparameters, training schedule, data preprocessing, hardware specs
- **Inconsistent notation** — symbols meaning different things in different sections

---

## Calibrating Your Recommendation

### Accept
- Clear, significant contribution to the field
- Sound methodology with thorough evaluation
- Well-written and well-organized
- Minor issues only (typos, presentation tweaks)

### Revise and Resubmit
- Core idea has merit but execution needs work
- Missing important experiments or comparisons
- Presentation issues that obscure the contribution
- Overclaiming that needs to be toned down
- The paper COULD be acceptable with specific, addressable changes

### Reject
- Fundamental methodological flaws
- No clear contribution beyond existing work
- Severely incomplete evaluation
- Results don't support the claims
- The issues are too deep to fix in one revision cycle

### Unsuitable due to scope
- Not about robotics or automation
- Better suited for a different venue (pure CV → CVPR, pure ML → NeurIPS)

---

## Common Traps to Avoid

1. **Don't reject for ambition.** A paper that tries something bold and partially succeeds is 
   more valuable than a paper that makes a trivial contribution perfectly.

2. **Don't demand impossible experiments.** If you suggest an additional experiment, make sure 
   it's actually feasible within the 8-page limit and reasonable compute budget.

3. **Don't confuse "not in my style" with "wrong".** Different research traditions have different
   norms. Focus on correctness and contribution, not stylistic preferences.

4. **Don't penalize honest limitations.** If the authors acknowledge a limitation, that's a 
   sign of scientific maturity, not a weakness.

5. **Don't over-index on novelty.** A solid engineering contribution with thorough evaluation
   can be more useful to the community than a "novel" method with sloppy experiments.

6. **Don't be swayed by flashy results alone.** SOTA numbers mean little if the evaluation
   is unfair or the improvement is within noise.
