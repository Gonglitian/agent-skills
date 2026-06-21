# Slidev Gotchas (rendering & build traps)

Hard-won failures that cost a QA round each. Check these proactively — they do **not** show up in `npm run build` errors except where noted, only in screenshots.

## 1. Markdown `**bold**` / `*italic*` does not render inside raw HTML blocks

Inside a raw block-level HTML element (`<div>…</div>`, `<td>…`, callout boxes) with **no blank line** after the opening tag, markdown-it treats the content as raw HTML and passes it through — so `**text**` shows literally or just unbolded.

- **Symptom:** a word you wrapped in `**…**` (e.g. a key term in a `<div class="note-box">`) is not bold; nearby spans look inconsistent.
- **Fix:** inside any raw HTML container, use `<b>…</b>` / `<i>…</i>` (or `<strong>`/`<em>`), never `**`/`_`.
- Markdown `**` is fine only in true markdown context (a blank line separates it from any surrounding HTML tag). When in doubt in HTML-heavy academic slides, default to `<b>`.

## 2. SVG `<text>` font-size is unreliable in Slidev → oversized, overlapping labels

The `font-size="14"` *presentation attribute* on `<svg><text>` gets overridden by the framework's CSS reset, so labels render 2–3× too large and overlap; boxes look empty. Geometry (x/y) is correct, only the type explodes.

- **Fix (preferred):** for any "boxes + text + arrows" diagram, build it as **HTML/CSS flow** (flex `<div>`s + Unicode arrows), not SVG `<text>`. See `svg-diagram-patterns.md` → "HTML flow diagrams".
- **Fix (if SVG is required):** set size via inline style — `style="font-size:14px"` — not the attribute.
- Reserve SVG for precise *arrow geometry* with little or no embedded text.

## 3. Slidev ≥ 52 (Rolldown) breaks on public assets referenced by absolute URL

`<img src="/media/x.gif">` / `<video src="/media/x.mp4">` (files in `public/`) make `npm run build` fail with:

```
RolldownError: [slidev] Import "/media/x.gif" … resolves outside of Vite server.fs.allow
```

`dev` and `slidev export` still work — only the static `build` fails. Add a `vite.config.ts` at the deck root:

```ts
import { defineConfig } from 'vite'
export default defineConfig({
  server: { fs: { strict: false, allow: ['.'] } },
  assetsInclude: ['**/*.gif', '**/*.mp4'],
})
```

(Slidev 0.5x did not need this. Run `npm run build` once **early** to detect which regime you're in.)

## 4. `<video>` and GIFs export as a single still frame

`slidev export --format pdf|png|pptx` renders each `<video>`/GIF as its **first frame** (videos with no poster may be blank). Animation is lost in any exported artifact; only the live dev server animates.

- Make the **first frame representative** (trim/crop so frame 0 is meaningful — e.g. crop a title bar or transition off the front of a clip).
- Prefer `<video autoplay loop muted playsinline>` for footage so it loops in the live deck.

## 5. Run `npm run build` early as a version probe

The Slidev major version is invisible from `slides.md`. A jump (e.g. `^0.50` resolved to 0.50 vs. `latest` = 52.x) changes the bundler and asset rules (see #3). Build once before authoring many slides so a version/bundler break surfaces immediately, not at delivery.

## 6. Delivery formats — know what survives

- **Live dev / built `dist/`** — the only form where GIF/MP4 animate. Use for Zoom (share the browser window; enable "optimize for video clip").
- **PDF** (`--format pdf`) — static, media shown as first frame; best offline fallback.
- **PPTX** (`--format pptx`) → import to Google Slides: each slide becomes a **full-slide bitmap** — not editable, GIF/video static. Fine for static sharing; re-insert GIFs manually if they must animate.
