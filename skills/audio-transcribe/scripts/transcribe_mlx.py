#!/usr/bin/env python3
"""Mac-native audio/video transcription via mlx-whisper (Apple Silicon / Metal GPU).

This is the macOS counterpart of the server's faster-whisper(CUDA) pipeline.
On Apple Silicon there is no CUDA and CTranslate2 has no Metal backend, so we use
Apple's MLX framework instead — it runs Whisper on the GPU through Metal.

Usage:
    python transcribe_mlx.py <file_or_dir> [options]

    # single file
    python transcribe_mlx.py talk.m4a
    # a whole folder (all common audio/video), skip already-done
    python transcribe_mlx.py ~/proj/omnibox/video/audio --out ./transcripts
    # bigger / more accurate model, force language
    python transcribe_mlx.py talk.mp4 --model large-v3 --language zh

Options:
    --model       turbo | large-v3 | large-v3-q4 | <hf repo>   (default: turbo)
    --out DIR     output directory (default: alongside each input file)
    --formats     comma list of json,txt,srt   (default: json,txt)
    --language    force language code (e.g. zh, en); default = auto-detect
    --overwrite   re-transcribe even if outputs already exist

Models are HuggingFace MLX repos, auto-downloaded & cached on first use:
    turbo       -> mlx-community/whisper-large-v3-turbo   (~1.6GB, ~12x realtime on M4, best default)
    large-v3    -> mlx-community/whisper-large-v3-mlx     (highest accuracy, slower)
    large-v3-q4 -> mlx-community/whisper-large-v3-mlx-4bit(lowest memory)

Env: conda env `whisper` (python 3.11) with `mlx-whisper` + `ffmpeg` installed.
"""
import argparse, json, os, sys, time, glob

MODEL_ALIASES = {
    "turbo": "mlx-community/whisper-large-v3-turbo",
    "large-v3": "mlx-community/whisper-large-v3-mlx",
    "large-v3-q4": "mlx-community/whisper-large-v3-mlx-4bit",
}
AUDIO_EXTS = {".mp3", ".m4a", ".wav", ".flac", ".aac", ".ogg", ".opus",
              ".mp4", ".mov", ".mkv", ".webm", ".aiff", ".aif"}


def fmt_srt_time(t):
    h = int(t // 3600); t -= h * 3600
    m = int(t // 60); t -= m * 60
    s = int(t); ms = int(round((t - s) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_outputs(res, stem, outdir, formats):
    base = os.path.join(outdir, stem)
    paths = []
    if "json" in formats:
        p = base + ".json"
        json.dump(res, open(p, "w"), ensure_ascii=False, indent=1)
        paths.append(p)
    if "txt" in formats:
        p = base + ".txt"
        open(p, "w").write(res["text"].strip() + "\n")
        paths.append(p)
    if "srt" in formats:
        p = base + ".srt"
        with open(p, "w") as f:
            for i, seg in enumerate(res.get("segments", []), 1):
                f.write(f"{i}\n{fmt_srt_time(seg['start'])} --> "
                        f"{fmt_srt_time(seg['end'])}\n{seg['text'].strip()}\n\n")
        paths.append(p)
    return paths


def gather_inputs(target):
    if os.path.isdir(target):
        files = [p for p in sorted(glob.glob(os.path.join(target, "*")))
                 if os.path.splitext(p)[1].lower() in AUDIO_EXTS]
        return files
    return [target]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="audio/video file or a directory of them")
    ap.add_argument("--model", default="turbo")
    ap.add_argument("--out", default=None)
    ap.add_argument("--formats", default="json,txt")
    ap.add_argument("--language", default=None)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    import mlx_whisper
    import mlx.core as mx
    print(f"[mlx-whisper] device = {mx.default_device()}", file=sys.stderr)

    repo = MODEL_ALIASES.get(args.model, args.model)
    formats = [f.strip() for f in args.formats.split(",") if f.strip()]
    files = gather_inputs(args.target)
    if not files:
        sys.exit(f"no audio/video files found at {args.target}")

    kw = {}
    if args.language:
        kw["language"] = args.language

    print(f"[mlx-whisper] model={repo}  files={len(files)}", file=sys.stderr)
    total_audio = total_wall = 0.0
    for i, fp in enumerate(files, 1):
        stem = os.path.splitext(os.path.basename(fp))[0]
        outdir = args.out or os.path.dirname(os.path.abspath(fp))
        os.makedirs(outdir, exist_ok=True)
        done = os.path.join(outdir, stem + ".json")
        if os.path.exists(done) and not args.overwrite:
            print(f"[{i}/{len(files)}] skip (done): {stem}", file=sys.stderr)
            continue
        t0 = time.time()
        try:
            res = mlx_whisper.transcribe(fp, path_or_hf_repo=repo, **kw)
        except Exception as e:
            print(f"[{i}/{len(files)}] FAIL {stem}: {e}", file=sys.stderr)
            continue
        dt = time.time() - t0
        dur = res.get("segments", [{}])[-1].get("end", 0.0) if res.get("segments") else 0.0
        total_audio += dur; total_wall += dt
        paths = write_outputs(res, stem, outdir, formats)
        rtf = (dur / dt) if dt else 0
        print(f"[{i}/{len(files)}] {stem}  lang={res.get('language')}  "
              f"{dur:.0f}s audio / {dt:.1f}s  ({rtf:.1f}x)  -> {', '.join(os.path.basename(p) for p in paths)}",
              file=sys.stderr)

    if total_wall:
        print(f"[done] {total_audio:.0f}s audio in {total_wall:.0f}s  "
              f"=> {total_audio/total_wall:.1f}x realtime overall", file=sys.stderr)


if __name__ == "__main__":
    main()
