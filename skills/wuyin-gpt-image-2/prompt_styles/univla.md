# Style preset · UniVLA 风格 (NeurIPS / CoRL / RSS / ICRA paper figure)

UniVLA-style 论文配图视觉语言：modern soft flat illustration（flat-but-soft），pastel macaron 配色 + 严格语义色映射 + capsule 主模块 + 手写感 italic 标签 + LaTeX 数学 + 极简单色机械臂线稿 + ">>>>>" chevron 数据流。Paste into your `prompt` (usually after a one-line description of the figure's content), or feed wholesale when you want the look itself.

## When to use

Trigger on user phrases like：
- "UniVLA 风格"、"用 UniVLA 风格画"、"UniVLA-style figure"、"univla 风"
- "画一张论文配图"、"NeurIPS / CoRL / RSS / ICRA 风格的方法图"、"科研架构图"、"模型结构图"
- "academic paper figure"、"conference paper figure"、"method overview diagram"、"architecture diagram (paper style)"
- "soft flat illustration"、"flat-but-soft"、"pastel macaron palette"、"hand-drawn italic labels"
- whenever the user asks for a model/pipeline/architecture diagram and explicitly wants paper-quality, not a generic infographic

## How to use

1. Write a 1–3 sentence description of what the figure shows (modules, tokens, data flow, stages).
2. Append the **STYLE BLOCK** below verbatim.
3. Recommended `--size 16:9` for full-width figures, `3:2` for half-page, `1:1` for teaser/icon.

```bash
python3 ~/.claude/skills/wuyin-gpt-image-2/generate.py \
  "<your figure description>. $(cat ~/.claude/skills/wuyin-gpt-image-2/prompt_styles/univla.md | sed -n '/^<<<STYLE/,/^STYLE>>>/p' | sed '1d;$d')" \
  --size 16:9 -o figure.png
```

Or just inline-paste the STYLE BLOCK section into your prompt string.

## STYLE BLOCK (paste verbatim)

<<<STYLE
Render in **UniVLA style** — a meticulously composed academic paper figure illustration in the visual language of top-tier machine learning and robotics conferences (NeurIPS / CoRL / RSS / ICRA), matching the look of the UniVLA paper figures. Aesthetic: clean, professional, **modern soft flat illustration (flat-but-soft)** — high information density with friendly, elegant visual comfort. Nordic minimalism + elegant hand-painted accents, highly structured and logical, generous whitespace on a **pure white background**.

COLOR PALETTE — low-saturation lightened pastel/macaron, intentionally whitened so colors look translucent rather than solid. Each fill has a 1px slightly-darker same-tone border. Strict semantic mapping:
- Soft baby blue (~#B8D4E8): visual input / observation tokens, image-frame borders, vision-module bases.
- Gentle mint green (~#C5E0C9): baseline or task-irrelevant action tokens.
- Cream / vanilla yellow (~#F5D88B): text & instruction tokens, tokenizer / base-model bases.
- Coral pink / light brick red (~#E8A89B): task-centric or latent action tokens.
- Soft lavender: action-decoder / processing-mainframe bases.
- Warm rice grey: encoder/decoder base layers and stage labels.

TYPOGRAPHY — all labels in **hand-drawn-feel italic** (vibe of Caveat / Patrick Hand / Kalam), elegant research-paper tone with subtle brush-like line variation, never rigid or mechanical. Text color matches its semantic mapping. Hierarchy:
- Main module headings: bolder, larger italic (e.g., "Main Processor Module").
- Sub-labels: smaller italic (e.g., "Encoder", "Decoder", "Supervise").
- Math notation: standard LaTeX italic (e.g., $O_t$, $a_{TI}$, $\in \mathbb{R}^{k\times d}$).
- Special tokens like "<ACT_C>" or "Actions": small, red.

SHAPES & GEOMETRY — soft and rounded throughout.
- Main modules: large capsule / slim pill-shaped rounded rectangles, corner radius ≈ 50% of height.
- Tokens: small rounded squares in sequences, 3–4px corner radius, uniform small spacing.
- Action quantization markers: equilateral triangles (solid = active, outline = pending).
- Groupings: grey dashed rounded rectangles to delimit stages / logical zones (e.g., "Quantization Zone").
- Multi-stage transition: a vertical fine dashed line splits columns (Stage A ‖ Stage B), with one elegant flow arrow between them.
- Connections: minimal thin arrows in light blue or light grey for data flow. Special transitions use repeating chevrons ">>>>>" as a paper-figure motif. Attention-style edges labeled "Q" and "KV" with matching text + line color.

ILLUSTRATION ELEMENTS —
- Robotic mechanisms: minimalist single-color (black / dark grey) thin-line art, no fills or shadows, Noun-Project vibe; multiple variants may sit side-by-side.
- Observation thumbnails: real photos (operational-dataset style), shrunk small, encased in rounded frame (~8px radius) with a 2–3px light-blue border, integrated flush into the flat layout.
- Icons: flat-but-soft, two-color (line + light fill) — camera, document, images, etc.
- Frozen parameters: a small cartoon snowflake emoji (blue-toned) sits next to the module.

LAYOUT — logical, hierarchical, multi-layered.
- Overall flow: top-down and left-to-right. Inputs top, processing center, outputs bottom.
- Multi-stage: side-by-side columns with a dashed vertical divider.
- Vertical stacking: Input Tokens → Processing Module → Output Actions, with clear arrows.
- Whitespace: generous around every module and token sequence — light, uncrowded, breathable.

OVERALL VIBE — UniVLA-style modern academic paper figure, NeurIPS/CoRL/RSS aesthetic, soft pastel macaron palette, all-italic hand-drawn labels, LaTeX math, capsule modules, rounded-square token grids, minimalist line-art robot arms, rounded-corner photo thumbnails with light-blue borders, dashed grouping rectangles, ">>>>>" chevron flows, snowflake-frozen markers, top-down multi-stage composition, pure white background, friendly and elegant.
STYLE>>>

## Tips

- Keep the figure-content description **specific** (name modules, list tokens, say which arrows go where) — the style block alone is not a figure.
- For text rendering inside the figure (LaTeX, labels), state the exact strings in quotes; GPT-Image-2 honors them well.
- If the result feels too "infographic" / too saturated, add: "less saturated, more whitened pastel, thinner borders, more whitespace".
- For dense figures use `--size 16:9` or `21:9`; small icons / teasers use `1:1`.
