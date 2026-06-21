# Slidev Academic Style Guide

Use this reference when the user asks for a research, paper-talk, robotics, AI, or academic lecture deck in Slidev, especially when matching the local reference style.

## Visual Profile

- Tone: academic lecture, research seminar, paper presentation.
- Page feel: mostly white slides with generous margins; optional dark technical cover or section separators.
- Typography: serif display headings, restrained sans/serif body depending on the Slidev theme; no decorative type.
- Palette: white paper background, black or near-black body text, muted gray-blue headings, pale yellow note/citation callouts, restrained gray rules.
- Density: one major claim per slide; diagrams or equations carry explanation; bullets stay short.
- Imagery: use real screenshots, paper figures, simulator captures, or precise SVG diagrams. Avoid marketing-style hero imagery.

## Slide Types

Cover:
- May use a dark simulator-grid or technical canvas.
- Title is the first-viewport signal.
- Keep metadata small and aligned; avoid card-style hero panels.

Section divider:
- Large centered title.
- Minimal subtitle or no subtitle.
- Use one accent rule or small label, not decorative backgrounds.

Content slide:
- Clear heading near the top-left.
- Body content uses a two-column or single-column academic layout.
- Formulas and diagrams should have breathing room and not fight for the same center.

Diagram slide:
- Diagram gets a stable frame and explicit coordinates.
- Text labels should be large enough for presentation, but not oversized relative to boxes.
- Captions or takeaways stay outside the diagram unless part of the visual grammar.

Callout slide:
- Pale yellow callouts work well for quotes, constraints, and key observations.
- Always leave visible bottom padding; callouts at the bottom are common clipping risks.

## CSS Conventions

Keep deck-wide styling in `style.css`. Prefer reusable classes such as:

```css
:root {
  --paper: #ffffff;
  --ink: #151515;
  --muted: #647985;
  --rule: #d8dee2;
  --note: #fff8e8;
  --note-line: #f2c94c;
}

.slidev-layout {
  background: var(--paper);
  color: var(--ink);
}

.slidev-layout h1 {
  color: var(--muted);
  font-family: Georgia, "Times New Roman", serif;
  font-weight: 500;
  letter-spacing: 0;
}

.note-box {
  background: var(--note);
  border-left: 6px solid var(--note-line);
  padding: 0.75rem 1rem;
}
```

## Layout Rules

- Do not rely on viewport-scaled font sizes.
- Do not use nested cards.
- Do not make operational or research slides look like landing pages.
- Avoid one-note palettes dominated by a single saturated hue.
- Keep bottom callouts at least 24 px from the slide edge in screenshots.
- Use stable dimensions for diagrams, grids, counters, and panels so text changes do not shift layout.

## Slidev Defaults

In deck frontmatter, prefer:

```yaml
theme: seriph
fonts:
  provider: none
```

Use local/system fonts unless the deck explicitly needs a bundled font asset.
