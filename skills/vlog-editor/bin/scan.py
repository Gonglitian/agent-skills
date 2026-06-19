#!/usr/bin/env python3
"""B-roll content selector — turn a long continuous take into a decision surface.

Following the video-use principle ("text + on-demand visuals, no frame-dumping"):
instead of detecting shot boundaries (useless on continuous footage), we sample
the take on a grid and let the agent *see* it, then pick the best windows.

Outputs:
  work/scan/<name>_sheetNN.jpg  contact sheet(s), each thumbnail labelled with
                                its source timestamp (so the agent can cite exact
                                in/out points)
  work/scan/<name>.json         {duration, interval, frozen_intervals, sheets}
                                frozen_intervals = static/dead segments to avoid.

Usage: python3 bin/scan.py footage_real/hawaii.mp4 [--interval 3] [--cols 6]
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys

ROOT = os.getcwd()  # resolve work/ relative to where the user runs (portable as a skill)
SCAN_DIR = os.path.join(ROOT, "work", "scan")
FFMPEG = os.environ.get(
    "FFMPEG",
    "/opt/homebrew/Caskroom/miniconda/base/envs/whisper/bin/ffmpeg",
)
FONT = "/System/Library/Fonts/Supplemental/Futura.ttc"


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out.strip())


def contact_sheets(path, name, interval, cols, thumb_w):
    """One tall sheet per <=rows_cap rows; timestamp burned per thumbnail."""
    dur = duration(path)
    n = max(1, int(math.ceil(dur / interval)))
    rows_cap = 10
    per_sheet = cols * rows_cap
    n_sheets = int(math.ceil(n / per_sheet))
    rows = int(math.ceil(min(n, per_sheet) / cols))
    label = (f"drawtext=fontfile='{FONT}':text='%{{eif\\:t\\:d}}s':"
             f"fontcolor=yellow:fontsize=20:x=6:y=6:"
             f"box=1:boxcolor=black@0.6:boxborderw=4")
    vf = (f"fps=1/{interval},scale={thumb_w}:-1,{label},"
          f"tile={cols}x{rows}:margin=4:padding=3:color=black")
    out_tmpl = os.path.join(SCAN_DIR, f"{name}_sheet%02d.jpg")
    subprocess.run(
        [FFMPEG, "-y", "-nostdin", "-loglevel", "error", "-i", path,
         "-vf", vf, "-frames:v", str(n_sheets),
         "-start_number", "0", out_tmpl], check=True)
    return dur, n, [os.path.join(SCAN_DIR, f"{name}_sheet{i:02d}.jpg")
                    for i in range(n_sheets)]


def freeze_intervals(path):
    """ffmpeg freezedetect -> list of static/dead segments (camera not moving)."""
    r = subprocess.run(
        [FFMPEG, "-nostdin", "-i", path, "-vf", "freezedetect=n=-55dB:d=1.5",
         "-map", "0:v:0", "-an", "-f", "null", "-"],
        capture_output=True, text=True)
    frozen, cur = [], {}
    for line in r.stderr.splitlines():
        m = re.search(r"freeze_start: ([\d.]+)", line)
        if m:
            cur = {"start": round(float(m.group(1)), 2)}
        m = re.search(r"freeze_end: ([\d.]+)", line)
        if m and cur:
            cur["end"] = round(float(m.group(1)), 2)
            frozen.append(cur)
            cur = {}
    return frozen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--interval", type=float, default=3.0)
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--thumb-w", type=int, default=320)
    a = ap.parse_args()
    os.makedirs(SCAN_DIR, exist_ok=True)
    name = os.path.splitext(os.path.basename(a.video))[0]
    dur, n, sheets = contact_sheets(a.video, name, a.interval, a.cols, a.thumb_w)
    frozen = freeze_intervals(a.video)
    meta = {"video": a.video, "duration": round(dur, 2), "interval": a.interval,
            "n_samples": n, "cols": a.cols, "sheets": sheets,
            "frozen_intervals": frozen}
    with open(os.path.join(SCAN_DIR, f"{name}.json"), "w") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
    print(f"[scan] {name}: {dur:.0f}s, {n} samples @ {a.interval}s, "
          f"{len(sheets)} sheet(s), {len(frozen)} frozen segment(s)")
    for s in sheets:
        print("   ", s)
    if frozen:
        print("   frozen:", frozen)


if __name__ == "__main__":
    main()
