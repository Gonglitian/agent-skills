#!/usr/bin/env python3
"""Transcribe audio/video with faster-whisper (single-file or batch w/ smart parallel GPUs)."""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

AUDIO_EXTS = {".mp3", ".m4a", ".wav", ".flac", ".ogg", ".opus", ".mp4", ".mkv", ".webm", ".mov"}
SHORT_THRESHOLD_SEC = 600.0


def fmt_ts(sec: float) -> str:
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec - 60 * (h * 60 + m)
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def fmt_mmss(sec: float) -> str:
    sec = max(0, int(sec))
    return f"{sec // 60:02d}:{sec % 60:02d}"


def probe_duration(path: Path) -> float | None:
    try:
        import av  # bundled with faster-whisper via PyAV
        with av.open(str(path)) as container:
            if container.duration:
                return float(container.duration) / 1_000_000.0
    except Exception:
        pass
    return None


def transcribe_one(
    audio_path: str,
    output_dir: str,
    model_name: str,
    compute_type: str,
    language: str | None,
    context: str | None,
    beam_size: int,
    batch_size: int,
    gpu_id: int,
    model=None,
    skip_existing: bool = True,
    device: str = "cuda",
) -> dict:
    if device == "cuda":
        os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    from faster_whisper import WhisperModel

    p = Path(audio_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = p.stem
    txt_path = out_dir / f"{stem}_transcript.txt"
    json_path = out_dir / f"{stem}_transcript.json"
    srt_path = out_dir / f"{stem}_transcript.srt"

    if skip_existing and txt_path.exists() and json_path.exists() and srt_path.exists():
        return dict(file=str(p), gpu=gpu_id, duration_s=0.0, load_s=0.0,
                    inference_s=0.0, n_segments=0, txt=str(txt_path), skipped=True)

    t0 = time.time()
    if model is None:
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
    t_load = time.time() - t0

    t1 = time.time()
    try:
        segments_iter, info = model.transcribe(
            str(p),
            language=language,
            beam_size=beam_size,
            initial_prompt=context,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        segments = []
        for seg in segments_iter:
            segments.append(
                dict(
                    id=seg.id,
                    start=seg.start,
                    end=seg.end,
                    text=seg.text.strip(),
                    avg_logprob=getattr(seg, "avg_logprob", None),
                )
            )
    except Exception as e:
        # One unreadable/corrupt file must not kill the whole batch.
        return dict(file=str(p), gpu=gpu_id, duration_s=0.0, load_s=t_load,
                    inference_s=time.time() - t1, n_segments=0, txt=str(txt_path),
                    error=f"{type(e).__name__}: {e}")
    t_inf = time.time() - t1

    with txt_path.open("w", encoding="utf-8") as f:
        f.write(f"# {p.name}\n")
        f.write(f"# language={info.language}  prob={info.language_probability:.3f}  "
                f"duration={info.duration:.1f}s  model={model_name}  gpu={gpu_id}\n\n")
        for s in segments:
            f.write(f"[{fmt_mmss(s['start'])}-{fmt_mmss(s['end'])}] {s['text']}\n")

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(
            dict(
                file=str(p),
                language=info.language,
                language_probability=info.language_probability,
                duration=info.duration,
                model=model_name,
                compute_type=compute_type,
                segments=segments,
            ),
            f, ensure_ascii=False, indent=2,
        )

    with srt_path.open("w", encoding="utf-8") as f:
        for i, s in enumerate(segments, 1):
            f.write(f"{i}\n{fmt_ts(s['start'])} --> {fmt_ts(s['end'])}\n{s['text']}\n\n")

    return dict(
        file=str(p),
        gpu=gpu_id,
        duration_s=float(info.duration),
        load_s=t_load,
        inference_s=t_inf,
        n_segments=len(segments),
        txt=str(txt_path),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Audio file or directory")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--language", default=None)
    ap.add_argument("--gpus", default="0", help="Comma-separated GPU IDs")
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"],
                    help="cuda (default) or cpu. On cpu, float16 is auto-coerced to int8.")
    ap.add_argument("--compute-type", default="float16", choices=["float16", "int8", "int8_float16"])
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--beam-size", type=int, default=5)
    ap.add_argument("--context", default=None)
    ap.add_argument("--output-dir", default=None)
    args = ap.parse_args()

    # CPU cannot do float16 in CTranslate2 — coerce to int8.
    if args.device == "cpu" and args.compute_type in ("float16", "int8_float16"):
        print(f"[transcribe] device=cpu: coercing compute_type {args.compute_type} -> int8")
        args.compute_type = "int8"

    in_path = Path(args.input)
    if in_path.is_file():
        files = [in_path]
    else:
        files = sorted(p for p in in_path.rglob("*") if p.suffix.lower() in AUDIO_EXTS)
    if not files:
        print(f"No audio found in {in_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.output_dir) if args.output_dir else (
        in_path.parent / "transcripts" if in_path.is_file() else in_path / "transcripts"
    )
    gpus = [int(g) for g in args.gpus.split(",") if g.strip() != ""]

    print(f"[transcribe] {len(files)} file(s), gpus={gpus}, model={args.model}, "
          f"compute={args.compute_type}, out={out_dir}")

    longs, shorts = [], []
    for f in files:
        d = probe_duration(f)
        (longs if (d or 0) >= SHORT_THRESHOLD_SEC else shorts).append((f, d))
    print(f"[transcribe] long(>={SHORT_THRESHOLD_SEC/60:.0f}min)={len(longs)}  short={len(shorts)}")

    results = []
    t0 = time.time()

    # Long files: parallel across GPUs
    if longs and len(gpus) > 1:
        with ProcessPoolExecutor(max_workers=len(gpus), mp_context=mp.get_context("spawn")) as ex:
            futs = {}
            for i, (f, _d) in enumerate(longs):
                g = gpus[i % len(gpus)]
                futs[ex.submit(
                    transcribe_one, str(f), str(out_dir), args.model, args.compute_type,
                    args.language, args.context, args.beam_size, args.batch_size, g,
                    device=args.device,
                )] = f
            for fut in as_completed(futs):
                r = fut.result()
                results.append(r)
                print(f"[done] {Path(r['file']).name}  {r['duration_s']:.0f}s audio / "
                      f"{r['inference_s']:.1f}s infer  gpu={r['gpu']}")
    else:
        for f, _d in longs:
            r = transcribe_one(str(f), str(out_dir), args.model, args.compute_type,
                               args.language, args.context, args.beam_size, args.batch_size, gpus[0],
                               device=args.device)
            results.append(r)
            print(f"[done] {Path(r['file']).name}  {r['duration_s']:.0f}s / {r['inference_s']:.1f}s")

    # Short files: sequential on gpus[0] with ONE model load reused across files
    if shorts:
        if args.device == "cuda":
            os.environ["CUDA_VISIBLE_DEVICES"] = str(gpus[0])
        from faster_whisper import WhisperModel
        t_load0 = time.time()
        shared_model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)
        print(f"[model] loaded {args.model} on {args.device}:{gpus[0]} in {time.time()-t_load0:.1f}s — reusing across {len(shorts)} short file(s)")
        for f, _d in shorts:
            r = transcribe_one(str(f), str(out_dir), args.model, args.compute_type,
                               args.language, args.context, args.beam_size, args.batch_size,
                               gpus[0], model=shared_model, device=args.device)
            results.append(r)
            tag = "fail" if r.get("error") else ("skip" if r.get("skipped") else "done")
            extra = f"  ERR={r['error']}" if r.get("error") else f"  {r['duration_s']:.0f}s / {r['inference_s']:.1f}s"
            print(f"[{tag}] {Path(r['file']).name}{extra}")

    wall = time.time() - t0
    total_audio = sum(r["duration_s"] for r in results)
    speed = total_audio / wall if wall > 0 else 0
    summary = dict(wall_s=wall, total_audio_s=total_audio, speed=speed, results=results)
    summary_path = out_dir / f"batch_summary_{int(time.time())}.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"[transcribe] wall={wall:.1f}s  audio={total_audio:.0f}s  speed={speed:.1f}x realtime")
    print(f"[transcribe] summary -> {summary_path}")


if __name__ == "__main__":
    main()
