---
name: slidev-academic-deck
description: Use this skill whenever the user wants to create, restyle, or polish a research or academic Slidev deck; asks to reproduce a reference slide style in Slidev; or needs clear diagrams with reliable arrows in Slidev. Pair it with paper-talk-deck or survey-to-deck when those skills generate paper/survey content, and use this skill for the visual system and diagram construction.
---

# Slidev Academic Deck

## Overview

This skill is a Slidev style layer for research decks. It helps Codex fit a reference slide style, choose robust diagram primitives, and implement the deck in Slidev. After building, hand the deck off to the user for manual review (no screenshot QA).

It does not replace paper discovery or paper-reading workflows. Use `paper-talk-deck` or `survey-to-deck` for content pipelines, then apply this skill to make the deck visually coherent and presentation-ready.

## Workflow

1. **Inspect the target style**
   - Read the existing Slidev project or provided screenshots.
   - If screenshots/images are available, inspect them visually and describe typography, palette, spacing, density, diagram language, and recurring slide types.
   - Load `references/style-guide.md` when building or matching the academic reference style.

2. **Set up the Slidev surface — scaffold from skill assets, do NOT hand-write boilerplate**
   - **Scaffold first**: `bash <skill-dir>/scaffold.sh <target_dir> [--install]`. This copies ready-to-use, version-pinned files so you never rewrite them by hand:
     - `assets/package.json` — Slidev pinned to the current major `52.x` (`@slidev/cli ^52.16.0` + `@slidev/theme-seriph ^0.25.0`). Slidev dropped the `0.` prefix — `52.x` **is** the latest major, *not* `0.52`; never "correct" it down to a `0.x` range.
     - `assets/vite.config.ts` — the Slidev-≥52 fix so `public/` assets (`/figs…` `/media…`) build (gotcha #3).
     - `assets/style.css` — academic base + **flow-diagram primitives** (`.flow/.fbox/.farrow` with accent variants `.b/.t/.o/.g/.gn/.rd/.vl`) + `.chip`/`.panel`/`.vs`/`.note-box`/`.def-box`, and `fonts.provider: none` baked into the template. Edit/extend it; don't recreate from scratch.
     - `assets/slides.template.md` → `slides.md` — a working starter (cover + flow diagram + VS + callout) that already demonstrates the primitives. **Edit this**, don't start from a blank file.
     `scaffold.sh` overwrites only `package.json`/`vite.config.ts` and never clobbers an existing `slides.md`/`style.css`, so it is safe to re-run.
   - Then **author by editing `slides.md`**; keep any extra styling in `style.css`. Inside raw `<div>` blocks use `<b>`, not `**` (gotcha #1). Use inline SVG only for precise arrow geometry (see step 3).
   - Run `npm run build` **once early** as a version/bundler probe (the `vite.config.ts` is already in place from the scaffold).

   When the deck needs real media (paper figures, simulator GIFs, footage), load `references/asset-pipeline.md` for crop/GIF/MP4 recipes and the `materials/` + `public/{figs,media}` layout.

3. **Choose drawing primitives deliberately**
   - For **labelled boxes connected by arrows** (pipelines, control loops, framework blocks) — the most common academic diagram — build an **HTML/CSS flow** (flex `<div>`s + Unicode arrows), NOT SVG. SVG `<text>` font-size is overridden in Slidev and renders oversized/overlapping (gotcha #2). Use the `.flow/.fbox/.farrow` template in `references/svg-diagram-patterns.md`.
   - Use inline SVG only when you mainly need exact arrow geometry with little embedded text.
   - Prefer straight lines and orthogonal polylines for arrows.
   - Avoid Bezier curves for connector arrows unless the user specifically wants curved diagrams.
   - Use Mermaid only for simple, rough flowcharts where exact visual polish is less important.
   - Load `references/svg-diagram-patterns.md` before implementing nontrivial diagrams.

4. **Implement slides with fixed geometry where needed**
   - Give boards, diagrams, and dense panels stable dimensions with `viewBox`, grid tracks, aspect ratios, and explicit x/y positions.
   - Align related boxes by shared centers or shared columns. Compute centers explicitly instead of eyeballing them.
   - Keep academic slides sparse: short claims, formulas, compact bullets, and a small number of visual anchors.

5. **Build and hand off for manual review**
   - Build with `npm run build` (or start the dev server) to confirm the deck compiles cleanly.
   - Give the user the preview link (dev-server URL, e.g. `http://localhost:3030`) and let them review manually. Do NOT run screenshot-based QA.

## Resources

- `scaffold.sh`: one-shot deck scaffolder — copies `assets/*` into a target dir. **Use this instead of hand-writing** `package.json` / `vite.config.ts` / `style.css` / `slides.md`.
- `assets/`: copy-ready templates — `package.json` (pinned 52.x), `vite.config.ts` (build fix), `style.css` (academic base + flow-diagram primitives + chips/panels/VS/callouts), `slides.template.md` (starter deck). The `.flow/.fbox/.farrow` examples in `references/svg-diagram-patterns.md` are already shipped in `assets/style.css`.
- `references/style-guide.md`: academic Slidev style profile and CSS conventions.
- `references/svg-diagram-patterns.md`: diagram primitives — when to use HTML/CSS flow vs SVG, reliable arrows.
- `references/slidev-gotchas.md`: rendering/build traps (bold-in-`<div>`, SVG text font-size, Slidev-52 public-asset build error).
- `references/asset-pipeline.md`: figure crops, GIF/MP4 prep, ffmpeg/pdftoppm recipes, directory layout.
