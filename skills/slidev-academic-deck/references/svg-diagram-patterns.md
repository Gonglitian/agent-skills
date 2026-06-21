# SVG Diagram Patterns for Slidev

Use inline SVG when diagram geometry matters. It gives the agent more reliable control than Mermaid for precise academic diagrams and more reproducibility than screenshots or generated images.

## Decision Rules

- Use **inline SVG** for framework diagrams, control loops, robot learning pipelines, evaluation loops, architecture blocks, and any diagram with important arrows.
- Use **HTML/CSS** for text-heavy grids, comparison tables, small cards, and callout panels.
- Use **Mermaid** only for simple flows where exact spacing and arrow endpoints are not critical.
- Use **draw.io** when the user needs an editable standalone diagram artifact.
- Use **bitmap image generation** only for illustrative scenes, textures, icons, or conceptual art. Do not use it for text-heavy diagrams.

## ⚠️ SVG `<text>` vs HTML flow — prefer HTML for text-in-boxes diagrams

SVG `<text>` font-size is **unreliable in Slidev**: the `font-size` presentation attribute gets overridden by the framework CSS reset, so labels render 2–3× oversized and overlap while the boxes look empty (geometry is fine, only the type explodes — see `slidev-gotchas.md` #2).

Therefore, for the most common academic diagram — **labelled boxes connected by arrows** (pipelines, control loops, framework blocks) — build it as **HTML/CSS flow**, not SVG. Reserve inline SVG for cases that are mostly *arrow geometry* with little embedded text.

Reusable flow primitives (put in `style.css`):

```css
.flow   { display:flex; align-items:center; justify-content:center; gap:0.45rem; flex-wrap:nowrap; }
.fbox   { border:1px solid #d8dee2; border-radius:6px; padding:0.45rem 0.6rem; font-size:0.8rem;
          text-align:center; line-height:1.25; font-family:Georgia, serif; background:#fcfdfe; }
.fbox small  { display:block; color:#647985; font-size:0.68rem; font-style:italic; }
.fbox.b { background:#e7eefc; border-color:#3a6ea5; color:#22405f; }   /* blue / RL head   */
.fbox.t { background:#eaf2f6; border-color:#2f6f8f; color:#1d4a5e; }   /* teal / process   */
.fbox.o { background:#fdf0e3; border-color:#e07b2a; color:#8a4d16; }   /* orange / robot   */
.fbox.g { background:#f1f3f4; border-color:#9aa7ad; color:#444; }      /* gray / world     */
.farrow { color:#4d6b78; font-size:1.25rem; font-weight:700; line-height:1; }
.farrow small { display:block; font-size:0.62rem; font-weight:400; font-style:italic; color:#647985; }
.loopbar{ border:1px dashed #8fb0bf; border-radius:6px; background:#eef6fa; color:#2f6f8f;
          font-size:0.8rem; text-align:center; padding:0.4rem 0.6rem; }   /* "↺ closed loop" bar */
```

```html
<div class="flow mt-5">
  <div class="fbox o">measure d<sub>t</sub></div>
  <div class="farrow">→</div>
  <div class="fbox t">tolerance &amp; mapping</div>
  <div class="farrow">→<small>pref p</small></div>
  <div class="fbox b">Meta-Policy π<sup>M</sup></div>
  <div class="farrow">→</div>
  <div class="fbox g">Robot + Target</div>
</div>
<div class="loopbar mt-3">↺ <b>Closed loop</b>: re-measure each step, no retraining</div>
```

This renders identically in `dev`, PNG/PDF/PPTX export, and across Slidev versions. Use `<sub>`/`<sup>` for `d_t`, `v_x`, `π^M`; `<b>` for emphasis (markdown `**` will not render inside these `<div>`s).

When you genuinely need SVG below (precise arrow endpoints, layered geometry):

## Geometry Rules

- Define a fixed `viewBox`, commonly `0 0 1120 520` or similar.
- Use explicit `x`, `y`, `width`, and `height` for every node.
- Align related boxes by exact centers:
  - `centerX = x + width / 2`
  - `centerY = y + height / 2`
- For a vertical relationship, set the same `centerX`.
- For a horizontal relationship, set the same `centerY`.
- Draw connectors behind nodes. Put connector elements before box elements in SVG order.
- Stop connector endpoints just outside box boundaries when arrowheads would otherwise overlap fills.

## Arrow Rules

- Prefer straight `<line>` or orthogonal `<polyline>` connectors.
- Avoid cubic Bezier paths (`C ...`) for normal connector arrows. Curve endpoints are easy to misplace and often look broken in screenshots.
- Use a single marker definition per diagram unless styles differ.
- Give marker ids unique names if multiple SVGs appear on the same slide.
- Keep arrowheads large enough to be visible but small enough not to collide with nodes.

Example marker:

```html
<defs>
  <marker id="arrow-main" viewBox="0 0 10 10" refX="8" refY="5"
          markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#586f7c" />
  </marker>
</defs>
```

Example connector:

```html
<polyline points="260,160 420,160 420,245 560,245"
          fill="none"
          stroke="#586f7c"
          stroke-width="3"
          marker-end="url(#arrow-main)" />
```

## Text Rules

- Prefer regular HTML text outside SVG when the text must wrap naturally.
- If SVG text is needed, use short labels only.
- Avoid `baseline-shift` for equations or complex annotations in SVG. Use separate `<text>` elements or Slidev/KaTeX outside the SVG.
- Check screenshots for text overflow inside boxes. SVG text does not wrap by default.

## QA Rules

For every SVG diagram:
- Verify all intended arrows are present.
- Verify arrowheads touch the intended destination and do not float, clip, or point into empty space.
- Verify no connector crosses through important labels.
- Verify aligned boxes actually share the same center coordinate.
- Replace curves with straight or orthogonal routes if screenshots show endpoint artifacts.
