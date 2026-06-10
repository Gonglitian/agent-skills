# Building a Domain Wiki

The goal is a small, trustworthy, indexed corpus — not an exhaustive dump. A focused wiki of 50 well-sourced entries beats 5000 scraped paragraphs, because in a long loop the agent must find the *right* entry fast and trust it without re-deriving it.

## Step 1 — Pick sources and set the cutoff

List the **authoritative** sources for the domain — the ones a domain expert would actually cite:

- Primary specs / official docs.
- Source code and merged PRs/commits (often the only place real behavior is documented).
- Papers / benchmark results.
- Hard-won internal notes.

Write them into `meta.yaml` with a `refresh_cutoff` date. Everything in the corpus is "current as of" that date; it's what lets the agent know when an entry might be stale. Prefer a few high-signal sources over many low-signal ones.

## Step 2 — Extract atomic entries

Go through each source and turn it into small entries under `entries/`, one fact/pattern/pitfall/reference each. For every entry, capture:

- The claim **in your own words** (synthesis).
- A **verbatim quote** that backs it (`>` blockquote).
- `source_ref` (exact URL/commit/file:line) and `source_date`.
- A `confidence` you'd defend.

Copy [`../assets/entry.template.md`](../assets/entry.template.md) per entry. Resist the urge to write essays — if an entry is getting long, it's probably two entries.

**Tip:** this extraction parallelizes well. If you have subagents, fan out — one source (or one section) per agent, each returning entries in the schema — then dedup. But keep a human/curator pass: provenance and confidence are exactly the fields an over-eager extractor fakes.

## Step 3 — Tag on multiple axes

For each entry set `type`, `tags`, `source`, and — when it addresses a concrete problem — `symptom`. The test: imagine three different future moments when you'd want this entry, and make sure each of those searches would surface it. See the axes discussion in [`schema.md`](schema.md).

## Step 4 — Verify and check freshness

Run the checker from the wiki root:

```bash
python3 scripts/wiki_check.py            # validate schema + provenance, list stale entries
python3 scripts/wiki_check.py --strict   # exit non-zero on any problem (for pre-commit / CI)
```

It flags: missing required fields, entries with no verbatim quote (unsupported claims), bad `source_date`, duplicate `id`s, and entries older than `freshness_window_days` past `refresh_cutoff`. Fix or re-verify what it surfaces. Re-run periodically as the domain moves; advancing the corpus is just bumping `refresh_cutoff` and re-checking the entries the source has since changed.

## Keeping it honest over time

- When upstream changes, add a new entry and mark the old one `supersedes`-d — don't silently rewrite history; you may want to know what *used* to be true.
- A `low`-confidence entry is a to-do: verify it up to `high`, or delete it. Don't let unverified leads accumulate and get treated as fact.
- The wiki is an input to the engineering-loop, not a place to record task-specific results — those belong in the task workspace (`candidates.jsonl`, `benchmark.csv`). Keep the wiki reusable across tasks.
