# Slidev Deck QA Checklist

Use this before telling the user a Slidev deck is ready.

## Build

- Run `npm run build` — and run it **early**, before authoring many slides, as a version/bundler probe.
- Treat Slidev/Vite build failures as blockers.
- Slidev ≥ 52 (Rolldown): a build error `Import "/media/…" resolves outside of Vite server.fs.allow` means public assets referenced by absolute URL. Add a `vite.config.ts` (`server.fs.strict:false` + `assetsInclude`) — see `slidev-gotchas.md` #3. `dev`/`export` can pass while `build` fails, so don't skip the build.
- Warnings from dependencies may be non-blocking, but record them if they are new or visual output may be affected.

## Server

- Start or reuse the local Slidev dev server.
- If port `3030` is busy, identify whether it is the current deck. Use another port only when needed.
- Give the user the local URL when the deck is meant to be tried interactively.

## Screenshot Coverage

Capture and inspect:
- Every changed slide.
- Every slide with SVG, Mermaid, or complex HTML diagrams.
- Every slide with formulas or math in HTML.
- Every slide with bottom callouts, dense text, or tables.
- Cover and final slide if style was changed globally.

**Preferred — clean print-mode export.** Render every slide with no dev-server chrome:

```bash
npx slidev export slides.md --format png --output /tmp/slidev-check
```

This gives one clean PNG per slide (`1.png`, `2.png`, …). Use it for full-deck QA. The dev-server capture helper can overlay Slidev's slide-list / nav panel onto the page, which looks like clipped content (false alarm) — so reach for the helper only for quick single-slide checks, not whole-deck review:

```bash
node /Users/glt/.claude/skills/slidev-academic-deck/scripts/capture_slidev_pages.mjs \
  --url http://localhost:3030 \
  --pages 1,3,4,7,10 \
  --out /tmp/slidev-check
```

If Playwright waits on fonts indefinitely, run with:

```bash
PW_TEST_SCREENSHOT_NO_FONTS_READY=1 node /Users/glt/.claude/skills/slidev-academic-deck/scripts/capture_slidev_pages.mjs \
  --url http://localhost:3030 \
  --pages 1,3,4,7,10 \
  --out /tmp/slidev-check
```

## Visual Checks

- No clipped content at slide edges.
- No bottom callout is pushed outside the slide.
- No text overlaps diagrams, formulas, or other text.
- No raw math syntax appears where rendered math is expected.
- Arrowheads are visible and connected to the intended node.
- Orthogonal arrows have clean turns and do not cross labels unnecessarily.
- Related nodes are aligned when the relation implies a shared row or column.
- Tables fit without tiny text.
- Slide controls or browser overlays are not mistaken for slide content.
- Emphasis renders: no literal `**` / `*` visible — markdown bold does **not** work inside raw `<div>` blocks (use `<b>`; see `slidev-gotchas.md` #1).
- SVG `<text>` labels are not oversized/overlapping (font-size override; prefer HTML flow — `slidev-gotchas.md` #2).
- Media slides: the GIF/video **first frame** is representative (exports show only frame 0; #4).

## Common Fixes

- If an arrow curve endpoint looks broken, replace it with a straight line or orthogonal polyline.
- If a bottom callout is clipped, reduce vertical density or split the slide.
- If a diagram is crowded, enlarge the SVG viewBox or reduce labels before shrinking all text.
- If math inside HTML does not render, move it to Markdown math or use Slidev-supported syntax outside raw HTML.
- If external fonts cause inconsistent screenshots, set `fonts.provider: none`.
- If SVG diagram text is huge/overlapping, rebuild it as an HTML/CSS flow diagram (`svg-diagram-patterns.md` → HTML flow).
- If `**bold**` shows literally or unbolded inside a `<div>`, switch to `<b>`.
- If `npm run build` fails on `/media` or `/figs` imports, add the `vite.config.ts` from `slidev-gotchas.md` #3.
