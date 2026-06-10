# Querying a Domain Wiki

Run from the wiki root (the directory containing `entries/` and `meta.yaml`). `wiki_query.py` is stdlib-only.

## Flags

| Flag | Effect |
|---|---|
| `"free text"` (positional) | Full-text search over title + body + tags. Ranked by match count. |
| `--tag T` | Entries tagged `T` (repeatable; AND semantics). |
| `--type T` | Filter by `type` (`pattern`/`reference`/`pitfall`/`concept`/`result`). |
| `--source S` | Filter by `source`. |
| `--symptom S` | Filter by `symptom` (the "by-problem" axis). |
| `--confidence C` | Minimum confidence (`high` shows only high; `medium` shows medium+high). |
| `--limit N` | Cap results (default 10). |
| `--compact` | One line per hit (id + title + confidence + source). |
| `--id ID` / `--show` | Fetch a single entry; `--show` prints the full body. |
| `--stale` | List entries whose `source_date` is older than `freshness_window_days` past the cutoff — re-verify these. |

Filters compose. Text search + `--tag` + `--confidence high` is a common combination: "find the trustworthy entries about X."

## Output

Default (ranked list):
```
pattern-idempotency-keys  [high]  (stripe-docs, 2026-03-01)
  Use idempotency keys to make charge retries safe
  → symptom: duplicate-charge   tags: idempotency, retries, payments
```

`--compact`:
```
pattern-idempotency-keys  [high]  Use idempotency keys to make charge retries safe  (stripe-docs)
```

`--show` prints frontmatter + full body including the verbatim quote, so you can cite it.

## How to use results in a loop

1. **Read confidence and date before trusting.** A `low`-confidence or stale entry is a lead to verify against the live source, not a fact to build on.
2. **Cite the entry** when you act on it — its `source_ref` is the provenance you'd want if the decision is later questioned.
3. **Search by the problem you have**, not only by where you think the answer lives. If `--symptom` and `--tag` come up empty, fall back to free-text, then consider that the wiki has a gap — which is itself signal (add an entry once you solve it).
4. **When the wiki is silent or stale on something load-bearing**, that's the cue to go read the live source and add/refresh an entry — exactly the "supplement new references when returns flatten" behavior from KDA.
