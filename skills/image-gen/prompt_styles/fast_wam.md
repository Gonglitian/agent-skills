# Style preset · Fast-WAM 风格 (CVPR / ICLR vector-graphics paper schematic)

A reusable prompt block for generating Fast-WAM-style 论文配图：highly professional, crisp, modern standard vector-graphics 学术架构图，典型 CVPR / ICLR 风。**纯白背景 + 白底灰描边模块 + 语义色编码（淡绿/淡蓝/芥末黄）+ 标准 sans-serif + LaTeX 下标 + 梯形 encoder + rounded-square token + attention 矩阵 grid + 左架构 ‖ 右矩阵 split layout**。

## When to use

Trigger on user phrases like：
- "Fast-WAM 风格"、"fast wam 风格"、"fastwam 风"、"fast-wam-style figure"
- "CVPR 风格图"、"ICLR 风格图"、"vector-graphics paper diagram"、"标准矢量学术图"
- 用户希望生成带 attention mask / 矩阵网格 / split layout 的方法图，强调 crisp、professional、purely geometric
- 与 UniVLA / Physical Intelligence 风格的判别：
  - **UniVLA** = pastel macaron + 手写 italic + 纯白 + capsule，柔和友好
  - **Physical Intelligence** = parchment 米白底 + monospace 全小写 + 黑细描边 + 复古打字机
  - **Fast-WAM** = 纯白背景 + 标准 sans-serif + 灰描边 + 矩阵 grid + 严格几何对齐，最"客观工程感"

## How to use

1. Write a 1–3 sentence description of what the figure shows (modules, tokens, attention masks, video stacks, side-by-side panels)。
2. Append the **STYLE BLOCK** below verbatim。
3. Recommended `--size 16:9` for 单栏 split layout（左架构 / 右矩阵），`21:9` for 三栏（input ‖ architecture ‖ matrix），`3:2` for 半页方法图。

```bash
STYLE=$(sed -n '/^<<<STYLE/,/^STYLE>>>/p' \
  ~/.claude/skills/wuyin-gpt-image-2/prompt_styles/fast_wam.md \
  | sed '1d;$d')

python3 ~/.claude/skills/wuyin-gpt-image-2/generate.py \
  "<your figure description>. $STYLE" \
  --size 16:9 -o figure.png
```

Or just inline-paste the STYLE BLOCK section into your prompt string.

## STYLE BLOCK (paste verbatim)

<<<STYLE
Render in **Fast-WAM style** — a highly professional, crisp, clean standard vector-graphics academic paper diagram in the visual language of top-tier computer vision / machine learning conferences (CVPR / ICLR). Aesthetic: highly structured, modern, objective. **No hand-drawn elements, no vintage textures, no gradients, no 3D, no drop shadows.** Precise geometric shapes, strict orthogonal alignment, functional color-coding only. Pure white background.

BACKGROUND & PALETTE — pure white (#FFFFFF) background.
- Core processing modules: **white fill with a clean medium-grey solid border** (no color fill on the module itself).
- Semantic color coding (solid but soft, applied only to tokens / matrix cells / abstract plots):
  - Text / language input → pale muted green (pale sage / mint).
  - Vision / video / spatial data → clear light blue (sky blue).
  - Action / temporal / control data → mustard / golden yellow.
- Grid / matrix cells: blue and mustard-yellow squares mixed with white empty squares; **all cells share thin grey borders**.

TYPOGRAPHY — standard modern highly-legible sans-serif (Arial / Helvetica / Roboto / standard LaTeX sans-serif vibe). Standard sentence case or title case — **no forced lowercase, no italic-handwriting, no monospace**. Math notation: standard LaTeX with simple subscripts (`$f_0$`, `$f_1$`, `$f_h$`, `$a_1$`, `$a_h$`), variables placed **perfectly centered** inside their geometric tokens.

GEOMETRY & SHAPES —
- Encoders / decoders: **symmetrical trapezoids** — wider at the bottom, narrower at the top (or mirrored for decoders).
- Main processing modules (DiT, Transformer blocks, etc.): standard **rounded rectangles** with moderate corner radius (NOT fully-rounded pill / capsule).
- Data tokens / variables: **perfect squares with slightly rounded corners** (squovals), uniform size, uniformly aligned.
- Attention masks / matrices (signature element): perfect **grid layouts of small squares** representing attention/mask patterns; some cells filled blue or mustard-yellow per the semantic mapping, others left white, illustrating structured attention patterns. Each cell has a thin grey border.
- Groupings: large bounding boxes with rounded corners, outlined in **dashed grey** lines, used to encapsulate core joint-training or shared architectures.

LINES, ARROWS, FLOW —
- Main connections: thin, crisp, **solid black** lines with standard simple solid black triangular arrowheads.
- Secondary / internal flow: thin **dashed grey** lines with curved or sweeping paths for information flow, noise injection (use a small `⊕` symbol), or alignment cues.
- Cross-attention edges: explicitly labeled straight lines with the text "cross-attn" placed directly on or just above the arrow.

ILLUSTRATION & MULTIMEDIA —
- Photographic thumbnails: small real photos (e.g., robotic manipulation tasks). When representing "Video" or "Future Frames", **stack the photos in an overlapping offset stack** to simulate a temporal sequence.
- Abstract data plots: simple **smooth golden-yellow curved line graphs without axes** to abstractly represent continuous data such as action chunks / trajectories.
- Icons: minimal flat vector only when needed; never decorative.

LAYOUT —
- **Split layout is a hallmark**: side-by-side or partitioned, e.g., the complex network architecture sits on the left while a corresponding theoretical visualization (training-vs-inference attention matrices, mask grids) is neatly stacked on the right.
- **Absolute precision in alignment** — tokens line up perfectly with modules above/below them; columns share x-coordinates; rows share y-coordinates. No diagonal flourishes, no free-floating elements.

OVERALL VIBE — Fast-WAM CVPR/ICLR vector-graphics paper schematic, pure white background, white-fill modules with grey borders, pale-sage / sky-blue / mustard-yellow semantic color coding, trapezoidal encoders, rounded-rectangle transformer blocks, squoval tokens, attention-mask grid matrices, overlapping photo stacks for video, smooth yellow curve plots for trajectories, thin solid black + curved dashed grey arrows, split left-architecture / right-matrix layout, precise grid alignment, clean vector lines, no gradients, no 3D, no hand-drawn flair.
STYLE>>>

## Tips

- 想突出 attention-mask 网格效果，描述里要明确给出网格规格："a 12×12 attention mask grid in the right panel, with blue cells in the upper-left triangle and mustard cells along the diagonal, white empty cells elsewhere"。GPT-Image-2 对结构化网格的服从度比纯抽象描述高很多。
- 避免被模型加上彩色填充：再强化一句 "modules have white fill, ONLY tokens and matrix cells carry color"。
- 想要 video stack 更明显："4 overlapping photo thumbnails offset by 8px each, rotated 0°"。
- 想要左右对照感更强："vertical thin grey divider line splits the figure into a left architecture panel and a right attention-matrix panel"。
- 如果跑出手绘 / italic / 米白底，加 negative-cue: "no hand-drawn lines, no italic, no cream/ivory background — pure white only, sans-serif only"。
