# OCR Environment Setup (macOS Apple Silicon)

Complete setup guide for LightOnOCR-2-1B + llama.cpp. Estimated time: ~10 minutes + download.

## Step 1: Install llama.cpp

```bash
brew install llama.cpp
```

This gives you `/opt/homebrew/bin/llama-mtmd-cli` with Metal GPU support built-in.

## Step 2: Download the model

```bash
# Create conda env (one-time)
conda create -n ocr python=3.12 -y
conda run -n ocr pip install huggingface_hub

# Download model files (~1.16GB total)
mkdir -p ~/proj/ocr-models
cd ~/proj/ocr-models

conda run -n ocr python3 -c "
from huggingface_hub import hf_hub_download
hf_hub_download('wangjazz/LightOnOCR-2-1B-gguf', 'LightOnOCR-2-1B-Q4_K_M.gguf', local_dir='.')
hf_hub_download('wangjazz/LightOnOCR-2-1B-gguf', 'LightOnOCR-2-1B-mmproj-f16.gguf', local_dir='.')
print('Done!')
"
```

Files:
- `LightOnOCR-2-1B-Q4_K_M.gguf` — 378MB (quantized model)
- `LightOnOCR-2-1B-mmproj-f16.gguf` — 781MB (vision encoder projection)

## Step 3: Install the wrapper script

```bash
cp ~/.claude/skills/ocr/scripts/ocr ~/.local/bin/ocr
chmod +x ~/.local/bin/ocr
```

## Step 4: Verify

```bash
ocr --help
# Should show usage info
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `llama-mtmd-cli: command not found` | `brew install llama.cpp` |
| Model not found error | `ls ~/proj/ocr-models/*.gguf` — re-download if missing |
| Out of memory (OOM) | Close other apps; Q4_K_M needs ~2GB VRAM |
| `huggingface_hub` not found | `conda run -n ocr pip install huggingface_hub` |
| Permission denied on `ocr` | `chmod +x ~/.local/bin/ocr` |
