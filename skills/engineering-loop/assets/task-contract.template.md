# Task Contract — <task name>

> Fill every field before writing any code. Re-read at the start of every session.

## Objective
<one or two sentences: what success looks like to the person who asked>

## Inputs and outputs
- Inputs: <shapes / types / ranges>
- Input distribution: <not just one example — the real spread of workloads>
- Outputs: <shapes / types / invariants>

## Correctness requirements
- Tolerances: <abs / rel error>
- Invariants: <what must always hold>
- Invalid output = <NaN / Inf / empty / wrong dtype / ...>  ← explicit

## Validation command  (proves correctness — prefer the official harness)
```
<command>
```

## Performance / quality target
- Metric: <latency / throughput / accuracy / cost / ...>
- Target: <number or comparison, e.g. "≥1.0× baseline on every workload, ≥X× mean">

## Evaluation command  (measures the target)
```
<command>
```

## Allowed approaches / constraints
<languages, libraries, APIs, hardware, dependency limits>

## Immutable baseline + provenance
- Baseline: <what it is>
- Provenance: <commit / file / upstream release / command>
- Reproduce baseline number:
```
<command>
```
- Baseline measurement: <number, conditions>   ← this never changes during the task

## Promotion criteria  (when a candidate replaces current best — also the stop condition)
<precise condition, e.g. "passes official validator on all N workloads AND mean metric strictly better than current best AND no workload regresses below baseline">
