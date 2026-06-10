---
name: audio-transcribe
description: "Transcribe audio files to text using faster-whisper with smart parallel GPU processing. Trigger when user says '转录', '音频转文字', 'transcribe', '语音识别', '听写', '把这个音频转成文字', '帮我转录一下', 'speech to text', or provides audio/video files (mp3, m4a, wav, mp4) and wants text output. Also trigger when user mentions extracting text from B站 videos, podcast episodes, or meeting recordings."
---

# Audio Transcription Pipeline

Transcribe audio/video files to text using faster-whisper large-v3 with smart parallel GPU scheduling.

## Prerequisites & Installation

### 1. Conda Environment

```bash
conda create -n whisper python=3.11 -y
conda run -n whisper pip install faster-whisper
```

**Required model** (~2.9GB, auto-downloads on first use):
- `Systran/faster-whisper-large-v3` from HuggingFace Hub
- Cached at `~/.cache/huggingface/hub/` (or wherever HF_HOME points)

### 2. System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **GPU** | Any NVIDIA GPU with ≥5GB VRAM | RTX 3090+ / RTX 6000 Ada |
| **CUDA** | 12.x | 12.4+ |
| **cuDNN** | 9.x | 9+ |
| **Python** | 3.9 | 3.11 |
| **ffmpeg** | Not required (PyAV bundles it) | System ffmpeg for yt-dlp |

VRAM per model instance:
- large-v3 fp16: **~4.5 GB**
- large-v3 int8: **~3 GB**
- distil-large-v3 fp16: **~2.4 GB**

### 3. Transcription Script

Save the `transcribe.py` script to your project. The script supports:
- Single file and batch transcription
- Smart parallel GPU scheduling (long files parallel, short files serial)
- Domain terminology injection via `--context`
- Multiple output formats (txt, json, srt)

### 4. yt-dlp (for extracting audio from videos)

```bash
conda run -n whisper pip install yt-dlp
# Also needs system ffmpeg for audio conversion:
# Ubuntu: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

### 5. Data Directory Setup

```bash
DATA_BASE="/data1/$USER/social_crawler"  # adjust to your setup
mkdir -p $DATA_BASE/transcripts/{batch,models}

# Optional: symlink model cache for path management
ln -sf ~/.cache/huggingface/hub/models--Systran--faster-whisper-large-v3 \
       $DATA_BASE/transcripts/models/faster-whisper-large-v3
```

### 6. Verify Installation

```bash
# Quick test: transcribe 10 seconds of silence (should load model and return empty)
conda run -n whisper python -c "
from faster_whisper import WhisperModel
import os; os.environ['CUDA_VISIBLE_DEVICES']='0'
m = WhisperModel('large-v3', device='cuda', compute_type='float16')
print('Model loaded OK. VRAM ~4.5GB allocated.')
"
```

---

## Usage

### Single File
```bash
conda run -n whisper python transcribe.py "audio.m4a"
```

### With Language and Domain Terms
```bash
conda run -n whisper python transcribe.py "audio.m4a" \
  --language zh \
  --context "VLA,具身智能,世界模型,机器人" \
  --output-dir /data1/$USER/social_crawler/transcripts/
```

### Multiple Files (Smart Parallel)
```bash
conda run -n whisper python transcribe.py /path/to/audio_dir/ \
  --gpus 0,1,2,3,4 --language zh
```

The script automatically:
- Classifies files as "short" (<10min) or "long" (≥10min)
- Long files → distributed across multiple GPUs in parallel
- Short files → single GPU sequential (avoids model reload overhead)

### From Bilibili Videos (Full Pipeline)
```bash
# Step 1: Extract audio (needs yt-dlp + ffmpeg)
cd <MediaCrawler_path>
source venv/bin/activate
./bili_audio_extract.sh from_json 10

# Step 2: Batch transcribe all audio
conda run -n whisper python transcribe.py \
  /data1/$USER/social_crawler/bili/audio/ \
  --gpus 0,1,2,3,4 --language zh \
  --output-dir /data1/$USER/social_crawler/transcripts/batch
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--model` | large-v3 | Model size (tiny/base/small/medium/large-v3/distil-large-v3) |
| `--language` | auto | Language code (zh/en/ja...), auto-detect if omitted |
| `--gpus` | 0,1,2,3,4 | GPU IDs for parallel, comma-separated |
| `--compute-type` | float16 | Precision (float16/int8) — int8 saves ~35% VRAM |
| `--batch-size` | 8 | Inference batch size per GPU |
| `--beam-size` | 5 | Beam search width |
| `--context` | none | Domain terms injected as initial_prompt (max ~200 tokens) |
| `--output-dir` | auto | Output directory |

## Context Prompt Tips

The `--context` parameter biases Whisper toward correct domain terminology. Group related terms:

```bash
# Pharmaceutical research
--context "rapamycin,cyclodextrin,HP-β-CD,IND,FDA,bioanalytical,pharmacology"

# Robotics/AI
--context "VLA,具身智能,世界模型,LIBERO,Isaac Lab,LoRA,MoE"

# General Chinese tech
--context "爬虫,Python,API,数据采集,反爬虫,robots.txt"
```

## Output Files

Each audio file produces three outputs:

| File | Format | Content |
|------|--------|---------|
| `*_transcript.txt` | Plain text | Timestamped `[MM:SS-MM:SS] content` with metadata header |
| `*_transcript.json` | JSON | Structured segments with start/end, confidence |
| `*_transcript.srt` | SRT subtitle | Standard subtitle, importable into video editors |

Batch runs also produce `batch_summary_*.json` with timing stats.

## Post-Processing with LLM (context-aware polish)

After transcription, Claude should polish the raw `*_transcript.txt` into a `*_final.txt` **inline in the current session** (or via a dispatched subagent for long files). Do NOT shell out to `claude -p` or build a polish CLI — run the pass directly.

### When to run the polish

Trigger automatically when any of the following apply to a just-produced transcript:
- `language_probability < 0.95` in the metadata header (suggests rough ASR)
- The user supplied a `--context` to `transcribe.py` (they care about domain terms)
- The user explicitly asks ("润色一下", "polish", "clean up", "fix the transcript")

When unsure, surface the offer instead of running silently — polishing takes real tokens.

### Execution routing

| Transcript size | Approach |
|---|---|
| ≤ 200 segments (≈ ≤15 min audio) | Read + rewrite inline with Edit/Write |
| > 200 segments OR > ~6k tokens of text | Dispatch a `general-purpose` Agent with the rules below, run in the foreground so you can verify output, and have it write `*_final.txt` directly |
| Batch of many files | Dispatch one Agent per file in parallel (single message, multiple tool calls) |

### Polish rules (give these to yourself or the subagent verbatim)

```
You are editing a raw ASR transcript. Fix obvious errors ONLY. Never add content.

HARD RULES:
1. Preserve every `[MM:SS-MM:SS]` timestamp line-by-line. Do not merge or split segments. Do not reorder.
2. Preserve the metadata header (lines starting with `#`) unchanged. Append one line:
   `# polished_by=<model>  context=<domain terms used>`
3. Only these edits are allowed:
   a. Homophone / near-homophone ASR errors that context makes unambiguous
      (e.g., zh: "正与以前" → "正余弦"; en: "face solubility" → "phase solubility").
   b. Domain terms in the provided context list — snap misspellings to the canonical form.
   c. Remove stock Whisper hallucinations inserted into unrelated audio
      ("Thank you for watching", "请订阅我的频道", "字幕由...提供", repeated tail phrases
       on silence). If the phrase plausibly belongs to the content, LEAVE IT.
   d. Fix punctuation / spacing if it improves readability. No paraphrasing.
4. If a segment is already correct, output it character-for-character unchanged.
5. When in doubt, prefer the original. Under-editing is safer than over-editing.
6. Do NOT add summaries, section headers, speaker labels, or commentary.

INPUT: the raw transcript text (header + timestamped lines).
OUTPUT: the same file, polished per the rules above. Nothing else.

Domain context: <paste the --context value, or extract domain hints from the audio title>
```

### After polishing — always report the diff

After writing `*_final.txt`, run `diff` against the raw `*_transcript.txt` and summarize the changes to the user in 3-5 bullets (e.g., "fixed 正与以前 → 正余弦 at 03:13; removed 1 'thank you for watching' hallucination at end"). This keeps the edit auditable — the user can reject specific changes.

### What polish does NOT do

- No section headers, no TL;DR, no reorganization — that's a separate summarization step.
- No translation.
- No speaker diarization — Whisper doesn't produce speaker IDs, the polish pass won't fabricate them.

## Data Path Management

```
<data_base>/transcripts/
├── models/faster-whisper-large-v3 → (2.9GB symlink)
├── batch/              ← Batch results
│   ├── *_transcript.txt
│   ├── *_transcript.json
│   ├── *_transcript.srt
│   ├── batch_summary_*.json
│   └── *_final.txt     ← Claude-polished versions (see Post-Processing section)
└── bili/               ← B站 specific transcripts
```

## Performance Reference

| Scenario | Files | Total Audio | Wall Time | Speed |
|----------|-------|-------------|-----------|-------|
| Single file, 1 GPU | 1 | 81.5 min | 46s | 105x real-time |
| 5 files, 5 GPUs | 5 | 97 min | 56s | 104x |
| 12 files, 5 GPUs (smart) | 12 | 416 min | 106s | **236x real-time** |

*Benchmarked on RTX 6000 Ada (49GB), large-v3 fp16, batch_size=8*

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `CUDA out of memory` | GPU occupied | Use `--gpus` to select free GPUs; or use `--compute-type int8` |
| Model download slow | Large file (2.9GB) | Set `HF_TOKEN` for faster auth download |
| "Thank you for watching" in output | Whisper hallucination on silence | Use `--context` to bias; run Post-Processing polish step |
| Polish pass adds content not in source | Over-zealous LLM | Tighten the HARD RULES prompt; re-run with "under-edit" emphasis; reject and keep raw |
| Polish pass drops timestamps / merges segments | LLM ignored format rule | Re-run with smaller chunks; pass one segment block at a time |
| Poor Chinese recognition | Wrong model | Use `large-v3` (not tiny/base); set `--language zh` |
| Parallel slower than serial | All files short (<10min) | Model load overhead dominates; use single GPU for short files |
