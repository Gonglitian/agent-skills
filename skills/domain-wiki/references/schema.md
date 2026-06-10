# Entry Schema

Each entry is one markdown file in `entries/` with YAML frontmatter followed by a markdown body. One entry = one fact, pattern, pitfall, concept, or reference. Keep them small and atomic — small entries are easier to retrieve precisely and easier to re-verify when they go stale.

## Frontmatter fields

| Field | Required | Values | Purpose |
|---|---|---|---|
| `id` | yes | kebab-case, unique | Stable handle; used by `--id`, `--show`, and `[[id]]` cross-links. Prefix with type, e.g. `pattern-…`, `pitfall-…`. |
| `title` | yes | one line | Human-readable summary. |
| `type` | yes | `pattern` \| `reference` \| `pitfall` \| `concept` \| `result` | The axis "what kind of knowledge is this." |
| `tags` | yes | list | Free-form technique/topic tags. The main discovery axis. |
| `source` | yes | short id | Which source this came from (matches a key in `meta.yaml` sources). |
| `source_ref` | yes | URL / commit / file:line | Exact provenance pointer. |
| `source_date` | yes | `YYYY-MM-DD` | When the source said this. Drives freshness. |
| `confidence` | yes | `high` \| `medium` \| `low` | How much to trust it. `low` = a lead to verify. |
| `symptom` | no | short id | The problem/observable this entry addresses — the "by-problem" axis. |
| `supersedes` | no | id | Marks an older entry this one replaces. |

## Type meanings

- **`pattern`** — a reusable way to do something well ("use idempotency keys for retries", "rewrite scalar score path to tensor-core").
- **`pitfall`** — a known trap and how to avoid it ("comparisons with NaN return false, so a NaN-only output passes a naive validator").
- **`reference`** — a concrete prior implementation/PR/spec section worth pointing at ("vLLM PR #X implements paged loads via TMA").
- **`concept`** — background a reader needs to understand the others ("what TMEM is and why it changes accumulation").
- **`result`** — a measured fact / benchmark / paper finding ("approach Y gave 4.5× on workload Z").

## Indexing axes — why more than one

Mid-task you don't know in advance how you'll look for a fact. You might search:

- **by source** (`--source`) — "what did the official docs / this repo say?"
- **by problem/symptom** (`--symptom`) — "I'm seeing duplicate charges / low occupancy / a stale read."
- **by technique/topic** (`--tag`) — "idempotency", "tensor-core", "rate-limiting".
- **by type** (`--type`) — "show me the known pitfalls", "show me prior implementations."

Tag generously on all relevant axes. An entry that's only findable by the source it came from is nearly invisible when you're searching by the problem you actually have.

## Body conventions

- First paragraph: the claim **in your own words** (a synthesis, not a copy).
- A `>` blockquote: the **verbatim** supporting quote from the source. This is what makes the entry checkable — `wiki_check.py` flags entries that assert without a quote.
- Cross-link related entries by id with `[[other-id]]`.

## `meta.yaml`

```yaml
domain: payments-integration
refresh_cutoff: 2026-04-27      # corpus is "current as of" this date
freshness_window_days: 180      # entries older than this are flagged --stale
sources:
  stripe-docs:   { kind: docs,  ref: https://stripe.com/docs }
  internal-repo: { kind: repo,  ref: git@…:payments.git }
```
