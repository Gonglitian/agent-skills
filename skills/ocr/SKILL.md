---
name: ocr
description: Local OCR via LightOnOCR-2-1B + llama.cpp on macOS (Apple Silicon). Use this skill whenever the user wants to extract text from images, convert screenshots to Markdown, OCR documents, or batch-process images to text. Triggers on: OCR, 图片转文字, 截图转Markdown, extract text from image, 识别图片文字, 批量OCR. The tool is ~6s per image on M4 Metal GPU, outputs clean Markdown. Already installed at ~/proj/ocr-models/ and ~/.local/bin/ocr.
---

# Local OCR — LightOnOCR-2-1B via llama.cpp (macOS Metal GPU)

Zero-dependency image-to-Markdown OCR. Already deployed on this machine.

## Quick reference

```bash
ocr <image>              # Single image → stdout
ocr <image> -o out.md    # Single image → file
ocr <dir>                # Batch: all images in dir → dir/*.md
```

## Environment

| Component | Path |
|-----------|------|
| llama.cpp | `/opt/homebrew/bin/llama-mtmd-cli` (brew, arm64) |
| Model GGUF | `~/proj/ocr-models/LightOnOCR-2-1B-Q4_K_M.gguf` (378MB) |
| Vision encoder | `~/proj/ocr-models/LightOnOCR-2-1B-mmproj-f16.gguf` (781MB) |
| Wrapper script | `~/.local/bin/ocr` |
| Conda env | `ocr` (python=3.12, `huggingface_hub` for model downloads) |

**Model:** [wangjazz/LightOnOCR-2-1B-gguf](https://huggingface.co/wangjazz/LightOnOCR-2-1B-gguf) — 1B params, Q4_K_M quantization, 228 tok/s on M4 Max, excellent Chinese + English, tables/receipts/math support.

## Usage patterns

### When the user gives you image paths

Just run `ocr <path>` and read the Markdown output. For multiple images, run them in parallel:

```bash
ocr img1.jpg -o img1.md &
ocr img2.jpg -o img2.md &
wait
```

### When the user gives you a directory of images

```bash
ocr /path/to/dir
# Creates /path/to/dir/*.md for each .jpg/.png/.webp
```

### When you need to adjust quality

```bash
OCR_TEMP=0.0 ocr image.jpg          # Lower temperature = stricter
OCR_MAX_TOKENS=4000 ocr image.jpg   # Longer output for dense pages
```

### When the user asks about OCR setup

They already have llama.cpp via brew, the model in `~/proj/ocr-models/`, and the `ocr` script in PATH. If anything is missing, see `references/setup.md` for the full installation guide.

## Limitations

- **~6 seconds per image** on this M4 Mac (Metal GPU, 16GB RAM)
- **Image quality matters**: blurry screenshots → degraded output; clean screenshots → near-perfect
- **Memory**: ~2GB VRAM during inference (Q4_K_M quantized)
- **Multi-page PDF**: not directly supported — extract pages to images first, then batch OCR
