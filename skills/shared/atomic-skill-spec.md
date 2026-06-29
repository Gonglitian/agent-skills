# Atomic Skill Interface Specification

Every atomic skill (does one thing, called by orchestrators) MUST follow this contract.
Orchestration skills SHOULD follow it where applicable.

## 1. Naming

| Rule | Example |
|------|---------|
| `name:` = lowercase, hyphenated, verb-noun | `paper-read`, `litian-academic-search` |
| Directory = same as name | `skills/paper-read/` |
| `description:` = what it does + exact trigger phrases | Must include both Chinese and English triggers |

## 2. Argument Parsing

All arguments come from `$ARGUMENTS` (a single string). Parse in this order:

```
/litian-academic-search "QUERY" --sources a,b,c --k 10 --year 2024-
                         ^^^^^^    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                         positional (topic/query)   named flags
```

### Positional argument (REQUIRED)

The first un-flagged token(s) before any `--flag`. This is the primary input (topic, arxiv ID, file path, etc.).

### Named flags (OPTIONAL, standardized)

| Flag | Type | Meaning | Used by |
|------|------|---------|---------|
| `--sources <list>` | comma-sep | Which data sources | litian-academic-search |
| `--k <N>` | int | Max results | all search skills |
| `--year <YYYY->` | string | Year filter | search skills |
| `--topic <tag>` | string | OmniBox topic filter | OmniBox-related |
| `--output <dir>` | path | Override output directory | all |
| `--no-<feature>` | flag | Disable default feature | paper-read (`--no-ingest`, `--no-repo`) |
| `--force` | flag | Skip cache/dedup checks | paper-read |
| `--light` | flag | Fast/minimal mode | paper-read |
| `--deep` | flag | Full/deep mode | litian-academic-search |

**Rules:**
- All flags have `--double-dash` prefix
- Boolean flags default OFF, enabled by presence
- `--no-<feature>` disables a default-ON feature
- Unknown flags: silently ignore (don't error)

### Flag parsing pattern (copy into each atomic skill)

```
Parse $ARGUMENTS:
  positional = everything before first --flag
  --sources <list>  → SOURCES
  --k <N>           → TOP_K
  --year <YYYY->    → YEAR_FILTER
  --output <dir>    → OUTPUT_DIR
  --force           → FORCE=true
  --light           → LIGHT=true
  --no-<feature>    → FEATURE=false
```

## 3. Output Contract

### Output directory

Default: skill-specific subdirectory under the project root or `$ARGUMENTS --output`.

| Skill | Default output |
|-------|---------------|
| paper-read | Writes to `~/proj/omnibox/papers/<topic>/<arxiv>_<slug>/` |
| research-refine | `refine-logs/` |
| experiment-plan | `refine-logs/` |
| paper-write | `paper/` |
| comprehensive-survey | `<user-specified>/` |

### Output format

Every skill that produces structured data MUST support `--json` for machine consumption:

```
/litian-academic-search "query" --json
→ [{"title": "...", "arxiv_id": "...", ...}, ...]
```

Human-readable output is the default. `--json` is for orchestrators.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success, results produced |
| 1 | Input error (bad args, missing required input) |
| 2 | Source unavailable (graceful degradation — some sources skipped) |
| 3 | All sources failed (nothing to return) |

## 4. Graceful Degradation

Every external dependency must fail gracefully:

```
if source_A_available:
    results += source_A(query)
else:
    log("source_A unavailable, skipping")
    # Continue with remaining sources

if no_sources_contributed:
    exit 3  # All sources failed
```

**Never**: crash because one API is down, one file is missing, or one conda env is broken.

## 5. Calling Another Skill (orchestrator contract)

When an orchestration skill calls an atomic skill:

```
Invoke: /paper-read <arxiv_id> --topic <t> --light
Expect:  papers written to OmniBox path
Verify:  check exit code 0, check output files exist
Fallback: if exit ≠ 0, log warning, continue with next paper
```

**Rule**: orchestrators NEVER reimplement what an atomic skill does. They ONLY:
1. Parse user input → determine which atomics to call
2. Call atomics in sequence/parallel
3. Pass results between atomics via files (not in-memory)
4. Report progress to user

## 6. Documentation Requirements

Every atomic skill's SKILL.md must include:

```markdown
## Input
- **Positional**: <what it is, required/optional>
- **Flags**: <list all supported --flags>

## Output
- **Files written**: <paths, format>
- **Exit codes**: <0/1/2/3 meanings>

## Called by
- <list of orchestration skills that call this>

## Calls
- <list of other atomics this skill calls, if any>
```

## 7. Verification Checklist

Before marking a skill as "ready", verify:

- [ ] Accepts arguments per §2 (positional + named flags)
- [ ] Supports `--json` if producing structured output (per §3)
- [ ] All external deps fail gracefully (per §4)
- [ ] Orchestrator contract documented: input → output → exit codes (per §5-6)
- [ ] Tested with at least one real input end-to-end
