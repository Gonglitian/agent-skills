# The Task Contract

The contract is the single most important artifact in the loop. It is written **before** any code and it is what a long-running agent re-reads to avoid drifting. A vague contract ("make it faster") produces a vague, meandering search. A sharp contract makes every later decision — keep, revise, reject, stop — mechanical.

Fill every field. If a field is genuinely not applicable, write "n/a" and say why — don't leave it blank.

## Fields

### Objective
The user-facing goal in one or two sentences. What does success look like *to the person who asked*? Not "optimize the kernel" but "reduce p50 latency of the top-k indexer on the official trace while passing all official correctness checks."

### Inputs and outputs
The exact shapes/types/ranges the implementation must accept and produce. For search-heavy tasks, note the **distribution** of inputs, not just one example — the real workload is rarely a single fixed shape, and a candidate that wins on the average case can lose badly on a regime you didn't measure.

### Correctness requirements
What must be true of any candidate's output. Tolerances (absolute/relative error), invariants, and explicitly **what counts as invalid** (NaN, Inf, empty, wrong dtype). Be precise here: an under-specified correctness bar is exactly what lets a degenerate candidate pass. See `integrity-guards.md`.

### Validation command
The exact command that *proves* a candidate is correct. It should be runnable, deterministic, and — wherever possible — the **official / pre-existing harness**, not one you wrote. Reusing the authoritative validator removes the temptation (and the risk) of a home-grown checker that quietly omits a check.

### Performance / quality target + Evaluation command
The measurable thing you are optimizing (latency, throughput, accuracy, cost, token count, …) and the exact command that measures it. Often different from the validation command. State the target as a number or a comparison ("≥ 1.0× baseline on every workload, ≥ X× mean").

### Allowed approaches / constraints
Languages, libraries, APIs, hardware, deployment limits, dependencies you may or may not introduce. This bounds the search space so the agent doesn't wander into approaches that can never ship.

### Immutable baseline + provenance
What you are comparing against, and where it came from (commit hash, file path, upstream release, command). **This never changes during the task.** Write down how to reproduce the baseline number from scratch. If you can't reproduce it, you don't have a baseline yet — fix that before iterating.

### Promotion criteria
The precise condition under which a candidate replaces the current best. Example: "passes the official validator on all N workloads AND mean evaluation metric strictly better than the current promoted candidate AND no individual workload regresses below baseline." This is your stop condition too.

## Template

See [`../assets/task-contract.template.md`](../assets/task-contract.template.md). Copy it into the task workspace as `docs/contract.md` and fill it in. Re-read it at the start of every working session and whenever you feel the search losing direction.
