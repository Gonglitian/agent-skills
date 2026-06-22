---
theme: seriph
fonts:
  provider: none
title: Deck Title
class: cover
---

<!-- COVER. `class: cover` (above) applies the dark cover style from style.css.
     Inside raw <div> blocks use <b>/<i>, NOT markdown ** _ (gotcha #1). -->

# Deck Title

## One-line subtitle / thesis

<div class="sub">secondary line</div>
<div class="meta">venue · author · date</div>

---

# Slide with a flow diagram

<!-- Labelled boxes + arrows = HTML/CSS flow (NOT SVG <text>, gotcha #2).
     Box accents: .b blue  .t teal  .o orange  .g gray/frozen  .gn green/gain
     .rd red/anti  .vl violet/loss  | add .big or .dash as needed. -->

<div class="flow mt-6">
  <div class="fbox o">input<small>caption</small></div>
  <div class="farrow">→</div>
  <div class="fbox t">process</div>
  <div class="farrow">→<small>label</small></div>
  <div class="fbox b">module<sub>t</sub></div>
  <div class="farrow gn">→</div>
  <div class="fbox gn big">output</div>
</div>

<div class="loopbar mt-3">↺ <b>closed loop</b>: re-run each step</div>

<div class="note-box mt-5">Key takeaway in a pale-yellow callout. Use <b>bold</b> for emphasis.</div>

---

# Comparison slide (VS)

<div class="vs mt-6">
  <div class="panel">
    <h3 style="color:var(--c-rd)">Approach A</h3>
    <div class="flow"><div class="fbox rd">weak path</div></div>
    <div class="cap">why it falls short</div>
  </div>
  <div class="mid">vs</div>
  <div class="panel" style="border-color:var(--c-gn)">
    <h3 style="color:var(--c-gn)">Approach B (ours)</h3>
    <div class="flow"><div class="fbox gn">strong path</div></div>
    <div class="cap">why it wins</div>
  </div>
</div>

<div class="def-box mt-6"><b>Definition / claim</b> goes in a blue def-box.
Chips: <span class="chip good">+5 pts</span> <span class="chip bad">fails</span> <span class="chip info">note</span></div>

---

# Two-column content

<div class="cols2 mt-3">
  <div class="panel"><h3>Left</h3>
    <ul class="tight"><li>short bullet</li><li>formula <span class="kbd">L = a + b</span></li></ul>
  </div>
  <div class="panel"><h3>Right</h3>
    <ul class="tight"><li>short bullet</li><li>short bullet</li></ul>
  </div>
</div>
