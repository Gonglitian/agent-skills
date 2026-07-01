# Style preset · Physical Intelligence 风格 (retro-computing terminal-vibe paper diagram)

A reusable prompt block for generating Physical Intelligence (π / pi-zero) 系列论文配图风格的架构图与数据流图：高度结构化、ultra-flat、模型整体走 retro-computing / typewriter 路线，**全 monospace 小写、parchment 背景、capsule + trapezoid 几何、纯黑细描边 + 黑色虚线连接**。Paste into your `prompt` (usually after a one-line description of the figure's content), or feed wholesale when you want the look itself.

## When to use

Trigger on user phrases like：
- "Physical Intelligence 风格"、"PI 风格"、"π 风格"、"pi-zero 风格"、"physical-intelligence-style figure"
- "retro-computing diagram"、"monospace paper figure"、"typewriter-style architecture diagram"、"terminal-vibe schematic"
- 用户明确希望奶油/米白背景 + monospace 全小写标签 + 粉蓝粉绿 capsule + 梯形视觉编码器 + 黑细线描边
- 与 UniVLA 风格的判别：UniVLA = pastel macaron + 手写 italic + 纯白；Physical Intelligence = parchment off-white + monospace 小写 + 全黑细描边

## How to use

1. Write a 1–3 sentence description of what the figure shows (modules, tokens, data flow, stages, real-photo thumbnails 用什么场景).
2. Append the **STYLE BLOCK** below verbatim.
3. Recommended `--size 16:9` for system overview, `21:9` for pre-train ‖ post-train 横向对比, `1:1` for teaser/cyclical-process。

```bash
STYLE=$(sed -n '/^<<<STYLE/,/^STYLE>>>/p' \
  ~/.claude/skills/wuyin-gpt-image-2/prompt_styles/physical_intelligence.md \
  | sed '1d;$d')

python3 ~/.claude/skills/wuyin-gpt-image-2/generate.py \
  "<your figure description>. $STYLE" \
  --size 16:9 -o figure.png
```

Or just inline-paste the STYLE BLOCK section into your prompt string.

## STYLE BLOCK (paste verbatim)

<<<STYLE
Render in **Physical Intelligence style** — a highly structured, ultra-flat academic paper architecture / data-flow diagram in the visual language of Physical Intelligence (π / pi-zero) papers. Aesthetic: a unique blend of modern flat-design minimalism and a distinct retro-computing / typewriter vibe. **Strictly no 3D, no gradients, no drop shadows, no glow.** Visually dense but rigorously organized — engineering-focused, slightly raw, terminal-like elegance.

BACKGROUND & PALETTE — never pure white. Background is a very pale warm off-white / ivory / extremely light cream (parchment-like). All colored blocks are **solid flat pastels**, each with a **1px thin crisp dark-grey or black border** that does the heavy lifting for separation. Low color contrast, high border contrast.
- Main backbone (VLM / base model): soft powder blue / pale cerulean.
- Specialized / action modules: pale sage green / muted light olive.
- Text & instruction nodes: pale dusty pink, pale soft yellow, light neutral grey.
- Container / grouping backgrounds: very light warm beige / tan.
- Block-arrow accents (only in cyclical high-level diagrams): pastel blue / yellow / green / pink chevron blocks.

TYPOGRAPHY — **strictly monospace / typewriter font for ALL text** (Courier, Fira Code, Roboto Mono, JetBrains Mono vibe). **Predominantly lowercase** — module labels, descriptions, data types ("language subtasks", "action expert", "value function") almost entirely lowercase. **No italics.** Uniform, mechanical, terminal-like. Math/variables kept simple in the same monospace font (e.g., `a_t`, `a_{t+1}`, `q_t`, numbers like `-1.7`, `1.25` inside small pills).

GEOMETRY & SHAPES —
- Main processing blocks: elongated **perfect capsule / pill** (rectangles with fully semi-circular ends).
- Vision encoders: **flat-topped trapezoids** (truncated pyramids) placed below the main backbone, pointing upward into it.
- Tokens / internal representations: rows of **smaller horizontal capsules** uniformly spaced inside the large blue backbone capsule.
- Data nodes (text prompts, discretized actions, metadata): simple rounded rectangles.
- Containers: large rectangles with very slight rounded corners, filled pale beige, grouping datasets / task lists / robot types.
- Grouping brackets: large, thin, **black curly brackets `{` `}`** to bundle multiple inputs or outputs visually.

LINES, ARROWS, FLOW —
- Connectors: thin, crisp, **solid black or dark grey**. **No colored lines.**
- Arrowheads: simple solid black triangles or minimalist "V" shapes.
- Dashed lines: used extensively for secondary data flow, conditioning, noise injection, alignment across boundaries. Feedback loops drawn as U-shaped dashed arrows.
- Block-arrow exception: in high-level cyclical / lifecycle diagrams only, use large thick blocky chevron arrows in pastel blue / yellow / green / pink, arranged in a circle.

ILLUSTRATION & MULTIMEDIA —
- **Real photographic thumbnails** are a signature: small square / slightly rectangular photos of robotic arms manipulating objects in kitchens, labs, household scenes — placed directly inside the pale beige container boxes.
- Icons: extremely simple flat vector icons only (e.g., a minimalist globe with grid lines = internet data). No 3D clip art, no detailed illustration.

LAYOUT —
- **Grid-like rigidity**: orthogonal, dominated by horizontal and vertical alignments. Inputs on bottom, backbone in middle, outputs on top — or pre-training on the left ‖ post-training on the right, divided by a **thick dashed vertical line**.
- Strong parallelism and symmetry across rows / columns. No diagonal flourishes.

OVERALL VIBE — Physical Intelligence retro-modern paper diagram, ultra-flat, parchment ivory background (NOT white), powder-blue capsule backbones, sage-green action capsules, pale-beige container boxes housing real robot photos, flat-topped trapezoid vision encoders, monospace all-lowercase labels, thin solid + dashed black connectors with V arrowheads, large black curly-bracket groupings, engineering-terminal aesthetic, rigid grid alignment.
STYLE>>>

## Tips

- 关键字"physical intelligence" / "π" 出现在生成模型可能触发与 LLM 项目无关的内容；可在描述里替换为 "robotic foundation model" + 你自己的方法名。
- 想强调 "pre-training ‖ post-training" 双栏布局，明确写 "left column: pre-training stage; right column: post-training stage; thick vertical dashed divider in the middle"。
- 保留 monospace + lowercase 是这个风格的灵魂；如果生成图出现 italic / 大写 / 衬线字体，立即追加 negative-cue: "no italic, no serif font, no title case, all lowercase monospace only"。
- 真实机器人小图想要更多/更少时直接说 "place 6 photo thumbnails inside the beige container" 控制密度。
- 如果背景跑成纯白，强化一句："warm cream parchment background, NOT pure white"。
