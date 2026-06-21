#!/usr/bin/env python3
"""Perception layer for SPEECH: emit word-level timestamps the agent can read.

Backends, tried in order (so it runs on any machine):
  1. mlx_whisper     — Apple Silicon, fastest (MLX). Default model turbo.
  2. faster_whisper  — cross-platform (CTranslate2, CPU or CUDA). Fallback.

Unified output: {language, text, backend, segments:[{start,end,text,
words:[{word,start,end}]}]}.

Usage: python3 bin/transcribe.py narration.wav > work/transcript.json
Env:   WHISPER_MODEL overrides the model id.
"""
import json
import os
import sys

MLX_MODEL = os.environ.get("WHISPER_MODEL", "mlx-community/whisper-large-v3-turbo")
FW_MODEL = os.environ.get("WHISPER_MODEL", "large-v3")


def via_mlx(audio):
    import mlx_whisper
    r = mlx_whisper.transcribe(audio, path_or_hf_repo=MLX_MODEL,
                               word_timestamps=True)
    segs = []
    for s in r.get("segments", []):
        segs.append({
            "start": round(s["start"], 3), "end": round(s["end"], 3),
            "text": s["text"].strip(),
            "words": [{"word": w["word"], "start": round(w["start"], 3),
                       "end": round(w["end"], 3)} for w in s.get("words", [])],
        })
    return {"backend": "mlx_whisper", "language": r.get("language"),
            "text": r.get("text", "").strip(), "segments": segs}


def via_faster(audio):
    from faster_whisper import WhisperModel
    model = WhisperModel(FW_MODEL, device="auto", compute_type="auto")
    segments, info = model.transcribe(audio, word_timestamps=True)
    segs = []
    for s in segments:
        segs.append({
            "start": round(s.start, 3), "end": round(s.end, 3),
            "text": s.text.strip(),
            "words": [{"word": w.word, "start": round(w.start, 3),
                       "end": round(w.end, 3)} for w in (s.words or [])],
        })
    return {"backend": "faster_whisper", "language": info.language,
            "text": " ".join(s["text"] for s in segs), "segments": segs}


def main():
    audio = sys.argv[1]
    try:
        import mlx_whisper  # noqa: F401
        out = via_mlx(audio)
    except ImportError:
        try:
            import faster_whisper  # noqa: F401
            out = via_faster(audio)
        except ImportError:
            sys.exit("No whisper backend found. Install one:\n"
                     "  Apple Silicon : pip install mlx-whisper\n"
                     "  cross-platform: pip install faster-whisper")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    n = sum(len(s["words"]) for s in out["segments"])
    print(f"[transcribe] backend={out['backend']} lang={out['language']} "
          f"{len(out['segments'])} segments, {n} words", file=sys.stderr)


if __name__ == "__main__":
    main()
