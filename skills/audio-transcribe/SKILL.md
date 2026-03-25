---
name: audio-transcribe
description: "Transcribe audio files to text using faster-whisper with smart parallel GPU processing. Trigger when user says '转录', '音频转文字', 'transcribe', '语音识别', '听写', '把这个音频转成文字', '帮我转录一下', 'speech to text', or provides audio/video files (mp3, m4a, wav, mp4) and wants text output. Also trigger when user mentions extracting text from B站 videos, podcast episodes, or meeting recordings."
---

# Audio Transcription Pipeline

Transcribe audio/video files to text using faster-whisper large-v3 with smart parallel GPU scheduling.

## When to Use

- User provides audio files and wants text output
- User wants to transcribe B站 videos, podcasts, meetings, lectures
- User mentions speech-to-text, 语音识别, or 转录
- After downloading audio from Bilibili or other platforms

## Environment

- **Conda env**: `whisper` (Python 3.11)
- **Model**: faster-whisper large-v3 (fp16, 2.9GB VRAM)
- **GPU**: RTX 6000 Ada × 8 (any free GPU, ~4.5GB per instance)
- **Speed**: 60-105x real-time (81 min audio → ~46 seconds)
- **Script**: `/home/vla-reasoning/proj/research_tracker/transcribe.py`

## Usage

### Single File
```bash
conda run -n whisper python /home/vla-reasoning/proj/research_tracker/transcribe.py \
  "audio_file.m4a"
```

### With Language and Domain Terms
```bash
conda run -n whisper python /home/vla-reasoning/proj/research_tracker/transcribe.py \
  "audio_file.m4a" \
  --language zh \
  --context "VLA,具身智能,世界模型,机器人" \
  --output-dir /data1/vla-reasoning/social_crawler/transcripts/
```

### Multiple Files (Smart Parallel)
```bash
conda run -n whisper python /home/vla-reasoning/proj/research_tracker/transcribe.py \
  /path/to/audio_dir/ \
  --gpus 0,1,2,3,4 \
  --language zh
```

The script automatically:
- Classifies files as "short" (<10min) or "long" (>=10min)
- Long files → distributed across multiple GPUs in parallel
- Short files → single GPU sequential (avoids model reload overhead)
- Performance: 7 hours of audio transcribed in under 2 minutes

### From Bilibili Videos (Full Pipeline)
```bash
# Step 1: Extract audio
cd /home/vla-reasoning/proj/research_tracker/social_tools/MediaCrawler
source venv/bin/activate
./bili_audio_extract.sh from_json 10

# Step 2: Batch transcribe
conda run -n whisper python /home/vla-reasoning/proj/research_tracker/transcribe.py \
  /data1/vla-reasoning/social_crawler/bili/audio/ \
  --gpus 0,1,2,3,4 --language zh \
  --output-dir /data1/vla-reasoning/social_crawler/transcripts/batch
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--model` | large-v3 | Model size (tiny/base/small/medium/large-v3) |
| `--language` | auto | Language code (zh/en/ja...), auto-detect if omitted |
| `--gpus` | 0,1,2,3,4 | GPU IDs for parallel, comma-separated |
| `--compute-type` | float16 | Precision (float16/int8) |
| `--batch-size` | 8 | Batch size per GPU |
| `--context` | none | Domain terms, comma-separated. Injected as initial_prompt to bias recognition toward these terms |
| `--output-dir` | auto | Output directory |

## Context Prompt Tips

The `--context` parameter feeds terms into Whisper's initial_prompt, biasing it toward correct spelling of domain-specific words. Keep it under 200 tokens. Group related terms together:

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
| `*_transcript.txt` | Plain text | Timestamped text `[MM:SS-MM:SS] content` with metadata header |
| `*_transcript.json` | JSON | Structured segments with start/end times, confidence scores |
| `*_transcript.srt` | SRT subtitle | Standard subtitle format, importable into video editors |

For batch runs, an additional `batch_summary_*.json` is generated with timing stats for all files.

## Post-Processing with LLM

After transcription, optionally polish the output with an LLM agent:
- Fix domain terminology (e.g., "face solubility" → "phase solubility")
- Remove Whisper hallucinations ("Thank you for watching")
- Add topic section headers
- Standardize formatting

To do this, ask Claude to read the transcript and produce a `*_final.txt` version.

## Data Path Management

```
/data1/vla-reasoning/social_crawler/transcripts/
├── models/faster-whisper-large-v3 → (2.9GB symlink)
├── batch/              ← Batch transcription results
│   ├── *_transcript.txt
│   ├── *_transcript.json
│   ├── *_transcript.srt
│   └── batch_summary_*.json
├── bili/               ← B站 specific transcripts
└── *_final.txt         ← LLM-polished versions
```

## Performance Reference

| Scenario | Files | Total Audio | Wall Time | Speed |
|----------|-------|-------------|-----------|-------|
| Single file, 1 GPU | 1 | 81.5 min | 46s | 105x |
| 5 files, 5 GPUs | 5 | 97.2 min | 56s | 104x |
| 12 files, 5 GPUs (smart) | 12 | 415.8 min | 106s | 236x |
