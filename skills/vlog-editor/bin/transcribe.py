#!/usr/bin/env python3
"""Perception layer for SPEECH: run mlx_whisper and emit word-level timestamps.

This is how the agent "hears" dialogue: the model returns text + precise
(start,end) for every word, which we turn into burned-in captions.

Usage: python3 bin/transcribe.py narration/voiceover.wav > work/transcript.json
"""
import json
import sys

import mlx_whisper

MODEL = "mlx-community/whisper-large-v3-turbo"


def main():
    audio = sys.argv[1]
    r = mlx_whisper.transcribe(
        audio,
        path_or_hf_repo=MODEL,
        word_timestamps=True,
    )
    # keep only what captioning needs
    segs = []
    for s in r.get("segments", []):
        segs.append({
            "start": round(s["start"], 3),
            "end": round(s["end"], 3),
            "text": s["text"].strip(),
            "words": [
                {"word": w["word"], "start": round(w["start"], 3),
                 "end": round(w["end"], 3)}
                for w in s.get("words", [])
            ],
        })
    out = {"language": r.get("language"), "text": r.get("text", "").strip(),
           "segments": segs}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    n_words = sum(len(s["words"]) for s in segs)
    print(f"[transcribe] {len(segs)} segments, {n_words} words, "
          f"lang={out['language']}", file=sys.stderr)


if __name__ == "__main__":
    main()
