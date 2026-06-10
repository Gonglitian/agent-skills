---
name: domain-wiki
description: Build and query a structured, provenance-tracked, freshness-aware knowledge base for any specialized domain, so an agent can pull real, citeable engineering knowledge into a long task instead of relying on parametric memory. Use this when work depends on hard-won domain details that the model is likely to get subtly wrong or out-of-date — APIs, library internals, hardware/architecture features, protocol specs, regulations, prior PRs/commits, paper results — and when you want every retrieved claim to carry a source, a date, and a confidence so it can be trusted and re-checked. Trigger it to scaffold a new knowledge base ("build a wiki of X", "index these sources"), to query one mid-task ("what does the corpus say about Y"), or whenever a long optimization/research loop keeps guessing at domain facts. Pairs with the engineering-loop and evidence-report skills.
---

# Domain Wiki

A reusable pattern for giving an agent **retrievable, provenance-tracked domain knowledge** instead of relying on what the model happens to remember. It generalizes KernelWiki: any deep domain (GPU kernels, a compiler's IR, a payments API, a regulatory regime, a research subfield) has knowledge that lives in PRs, source, specs, papers, and docs — knowledge a model will confabulate or get out-of-date on. A domain wiki organizes that knowledge into a small, indexed, citeable corpus the agent queries on demand, pulling in *only* the entries relevant to the current sub-problem.

## When to use this

- A long task keeps hinging on facts the model is likely to get subtly wrong or stale.
- You want every retrieved claim to carry a **source + date + confidence**, so it can be trusted and re-verified.
- The same domain knowledge will be reused across many tasks/sessions — worth curating once.

Two modes: **build** a wiki for a new domain, or **query** an existing one.

## Core principles (what makes this better than raw search)

1. **Provenance on every entry.** Each fact records where it came from (URL/commit/file + a date) and ideally a verbatim quote. A claim you can't trace is a claim you can't trust in a long loop.
2. **A knowledge cutoff.** The whole corpus declares "current as of <date>." Fast-moving domains go stale; the cutoff tells the agent when to distrust an entry and re-check upstream.
3. **Confidence, not false certainty.** Entries are tagged `high` / `medium` / `low`. A `low`-confidence entry is a lead to verify, not a fact to build on.
4. **Multi-axis indexing.** The same corpus is reachable by source, by problem/symptom, by technique, and by concept — because mid-task you rarely know which axis you'll search on.
5. **Pull only what's relevant.** Optimizing component A? Read A's entries. Stuck on symptom B? Read B's entries. Don't load the whole corpus into context.

## Query an existing wiki

From the wiki root (where `entries/` lives):

```bash
python3 scripts/wiki_query.py "how to avoid double-spend on retried charges"   # natural-language text search
python3 scripts/wiki_query.py --tag idempotency --type pattern
python3 scripts/wiki_query.py --source stripe-docs --limit 20
python3 scripts/wiki_query.py --symptom duplicate-charge --compact
python3 scripts/wiki_query.py --id pattern-idempotency-keys --show          # fetch one entry in full
python3 scripts/wiki_query.py --stale                                       # entries older than the cutoff window
```

Filters compose: `--tag`, `--type`, `--source`, `--symptom`, `--confidence`, `--limit`, `--compact`, `--show`, `--id`. The script is stdlib-only and parses the entry frontmatter directly — no dependencies. See [`references/querying.md`](references/querying.md) for the full flag list and output formats.

## Build a wiki for a new domain

Read [`references/building.md`](references/building.md) — it walks the four steps end to end. In short:

1. **Pick sources & set the cutoff.** List the authoritative sources (repos, docs, specs, papers) and record a `refresh-cutoff` date in `meta.yaml`.
2. **Extract entries.** Turn each source into small markdown entries under `entries/`, one fact/pattern/reference each, using the schema in [`references/schema.md`](references/schema.md) (copy [`assets/entry.template.md`](assets/entry.template.md)). Capture a verbatim quote + source URL/commit + date for provenance.
3. **Tag on multiple axes.** Give each entry `type`, `tags`, `source`, and (where relevant) `symptom` so it's findable by problem and by technique, not just by source.
4. **Verify & check freshness.** Run `scripts/wiki_check.py` to validate the schema, flag entries with no provenance, and list entries past the cutoff window that need re-checking.

## Entry anatomy

Each entry is a markdown file with YAML frontmatter (full spec in [`references/schema.md`](references/schema.md)):

```markdown
---
id: pattern-idempotency-keys
title: Use idempotency keys to make charge retries safe
type: pattern              # pattern | reference | pitfall | concept | result
tags: [idempotency, retries, payments]
source: stripe-docs
source_ref: https://stripe.com/docs/api/idempotent_requests
source_date: 2026-03-01
confidence: high           # high | medium | low
symptom: duplicate-charge  # optional: the problem this addresses
---

One-paragraph synthesis in your own words.

> Verbatim quote from the source that backs the claim.

Notes, caveats, links to related entries by id: see also [[pattern-webhook-dedup]].
```

## Directory layout

```
my-domain-wiki/
  meta.yaml                # domain name, refresh-cutoff date, source list
  entries/                 # one markdown file per fact/pattern/reference
    pattern-idempotency-keys.md
    pitfall-...md
  scripts/
    wiki_query.py          # search & fetch (provided)
    wiki_check.py          # schema + provenance + freshness validation (provided)
```

> Note: the two scripts ship inside this skill's `scripts/` directory. When you scaffold a new wiki, copy them into the wiki root (or call them by absolute path). They are dependency-free.

## Reference files

- [`references/building.md`](references/building.md) — the four-step build process in detail.
- [`references/schema.md`](references/schema.md) — entry frontmatter spec, types, and indexing axes.
- [`references/querying.md`](references/querying.md) — every query flag and output format.
