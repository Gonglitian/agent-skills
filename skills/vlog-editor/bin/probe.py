#!/usr/bin/env python3
"""Probe all footage and emit clean JSON metadata.

Usage: python3 bin/probe.py footage/*.mp4 > work/probe.json
The understanding layer: gives the editorial brain exact specs to plan around.
"""
import json
import subprocess
import sys
from fractions import Fraction


def probe_one(path: str) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-of", "json",
         "-show_format", "-show_streams", path],
        capture_output=True, text=True, check=True,
    ).stdout
    meta = json.loads(out)
    v = next(s for s in meta["streams"] if s["codec_type"] == "video")
    a = next((s for s in meta["streams"] if s["codec_type"] == "audio"), None)
    fps = float(Fraction(v.get("avg_frame_rate") or v["r_frame_rate"]))
    w, h = int(v["width"]), int(v["height"])
    return {
        "path": path,
        "width": w,
        "height": h,
        "orientation": "portrait" if h > w else "landscape",
        "fps": round(fps, 3),
        "duration": round(float(meta["format"]["duration"]), 3),
        "vcodec": v["codec_name"],
        "has_audio": a is not None,
        "acodec": a["codec_name"] if a else None,
    }


def main():
    clips = [probe_one(p) for p in sys.argv[1:]]
    print(json.dumps(clips, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
