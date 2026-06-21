---
name: slidev-academic-deck
description: Use this skill whenever the user wants to create, restyle, polish, or quality-check a research or academic Slidev deck; asks to reproduce a reference slide style in Slidev; reports clipped/overlapping slide content; asks for screenshot-based slide QA; or needs clear diagrams with reliable arrows in Slidev. Pair it with paper-talk-deck or survey-to-deck when those skills generate paper/survey content, and use this skill for visual system, diagram construction, and QA.
---

# Slidev Academic Deck

## Overview

This skill is a Slidev style and quality layer for research decks. It helps Codex fit a reference slide style, choose robust diagram primitives, implement the deck in Slidev, and verify layout by screenshots rather than source inspection alone.

It does not replace paper discovery or paper-reading workflows. Use `paper-talk-deck` or `survey-to-deck` for content pipelines, then apply this skill to make the deck visually coherent and presentation-ready.

## Workflow

1. **Inspect the target style**
   - Read the existing Slidev project or provided screenshots.
   - If screenshots/images are available, inspect them visually and describe typography, palette, spacing, density, diagram language, and recurring slide types.
   - Load `references/style-guide.md` when building or matching the academic reference style.

2. **Set up the Slidev surface**
   - **Pin Slidev to the current major `52.x`** (`@slidev/cli ^52.16.0` + `@slidev/theme-seriph ^0.25.0`). Slidev dropped the `0.` prefix — `52.x` **is** the latest major (52.16.0), *not* `0.52`; never "correct" it down to a `0.x` range, and update any deck still on `0.4x/0.5x`. ≥52 also kills the stray `.autocomplete-list` (Goto.vue) panel that otherwise overlays screenshots during QA.
   - Prefer standard Slidev markdown plus scoped HTML/CSS; use inline SVG only for precise arrow geometry (see step 3).
   - Keep project-level styling in `style.css`; avoid scattering one-off layout rules unless the slide truly needs custom geometry.
   - Disable remote font fetching unless the project already depends on it: set `fonts.provider: none` in Slidev frontmatter.
   - Run `npm run build` **once early** as a version/bundler probe. On Slidev ≥ 52, add the `vite.config.ts` from `references/slidev-gotchas.md` #3 so `public/` assets referenced by `/media…` `/figs…` build. Inside raw `<div>` blocks use `<b>`, not `**` (gotcha #1).

   When the deck needs real media (paper figures, simulator GIFs, footage), load `references/asset-pipeline.md` for crop/GIF/MP4 recipes and the `materials/` + `public/{figs,media}` layout.

3. **Choose drawing primitives deliberately**
   - For **labelled boxes connected by arrows** (pipelines, control loops, framework blocks) — the most common academic diagram — build an **HTML/CSS flow** (flex `<div>`s + Unicode arrows), NOT SVG. SVG `<text>` font-size is overridden in Slidev and renders oversized/overlapping (gotcha #2). Use the `.flow/.fbox/.farrow` template in `references/svg-diagram-patterns.md`.
   - Use inline SVG only when you mainly need exact arrow geometry with little embedded text.
   - Prefer straight lines and orthogonal polylines for arrows.
   - Avoid Bezier curves for connector arrows unless the user specifically wants curved diagrams and screenshots confirm the endpoints are clean.
   - Use Mermaid only for simple, rough flowcharts where exact visual polish is less important.
   - Load `references/svg-diagram-patterns.md` before implementing nontrivial diagrams.

4. **Implement slides with fixed geometry where needed**
   - Give boards, diagrams, and dense panels stable dimensions with `viewBox`, grid tracks, aspect ratios, and explicit x/y positions.
   - Align related boxes by shared centers or shared columns. Compute centers explicitly instead of eyeballing them.
   - Keep academic slides sparse: short claims, formulas, compact bullets, and a small number of visual anchors.

5. **Run screenshot QA and iterate**
   - Build the deck with `npm run build`.
   - Render clean per-slide PNGs with `npx slidev export slides.md --format png --output /tmp/slidev-check` (print-mode, no dev-server chrome). Prefer this for full-deck QA over the dev-server capture helper, which can overlay the slide-list panel and fake a clipping bug.
   - Inspect screenshots visually for clipping, overlap, raw math / literal `**`, oversized SVG text, missing arrows, broken arrowheads, and bottom-margin issues. On media slides, confirm the GIF/video first frame is representative (exports show only frame 0).
   - Load `references/qa-checklist.md` before final verification.

## Resources

- `references/style-guide.md`: academic Slidev style profile and CSS conventions.
- `references/svg-diagram-patterns.md`: diagram primitives — when to use HTML/CSS flow vs SVG, reliable arrows.
- `references/slidev-gotchas.md`: rendering/build traps (bold-in-`<div>`, SVG text font-size, Slidev-52 public-asset build error, export shows media first frame).
- `references/asset-pipeline.md`: figure crops, GIF/MP4 prep, ffmpeg/pdftoppm recipes, directory layout.
- `references/qa-checklist.md`: screenshot and build QA checklist (prefers clean `export --format png`).
- `scripts/capture_slidev_pages.mjs`: Playwright screenshot helper for quick single-slide checks.

## Capture Helper

From a Slidev deck directory with Playwright installed:

```bash
node /Users/glt/.claude/skills/slidev-academic-deck/scripts/capture_slidev_pages.mjs \
  --url http://localhost:3030 \
  --pages 3,4,7,10 \
  --out /tmp/slidev-check
```

If the project uses `playwright-chromium` instead of `playwright`, run it from that project so Node can resolve the local package.
