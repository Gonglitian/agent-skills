#!/usr/bin/env python3
"""Self-eval: measure a rendered cut and surface evidence for the agent.

Following video-use's self-evaluation step. Produces:
  - automated checks: duration vs EDL, video/audio streams, black frames
    (outside the intended end fade), audio clipping / too-quiet
  - a QC contact sheet at every segment midpoint + the final frame, so the
    agent can VISUALLY confirm titles/captions/grade before showing the user
  - a JSON verdict with PASS / WARN + reasons

The re-render loop itself is agent-driven: read the verdict + sheet, and if
something is wrong, fix edl.json and re-run assemble.py.

Usage: python3 bin/qc.py output/real_travel_diary.mp4 --edl edl_real.json
"""
import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _env

ROOT = os.getcwd()  # resolve work/ relative to where the user runs (portable as a skill)
QC_DIR = os.path.join(ROOT, "work", "qc")
FFMPEG = _env.ffmpeg()
FONT = _env.font()


def probe(path):
    out = subprocess.run(
        [_env.ffprobe(), "-v", "error", "-of", "json",
         "-show_format", "-show_streams", path],
        capture_output=True, text=True).stdout
    d = json.loads(out)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    return {
        "w": int(v["width"]), "h": int(v["height"]),
        "fps": round(eval(v["r_frame_rate"]), 2),
        "dur": round(float(d["format"]["duration"]), 2),
        "has_audio": a is not None,
    }


def segment_midpoints(edl):
    """Final-timeline midpoint of each segment (mode-aware) + the end time."""
    durs = [s["dur"] for s in edl["segments"]]
    cut = (edl.get("xfade_transition") == "cut"
           or edl.get("xfade_duration", 0) == 0)
    xf = 0 if cut else edl.get("xfade_duration", 0)
    starts, t = [], 0.0
    for i, d in enumerate(durs):
        starts.append(t)
        t += d - (xf if i < len(durs) - 1 else 0)
    mids = [round(s + durs[i] / 2, 2) for i, s in enumerate(starts)]
    total = round(sum(durs) - xf * (len(durs) - 1), 2)
    return mids, total


def black_intervals(path):
    r = subprocess.run(
        [FFMPEG, "-nostdin", "-i", path, "-vf",
         "blackdetect=d=0.1:pic_th=0.95", "-an", "-f", "null", "-"],
        capture_output=True, text=True)
    out = []
    for line in r.stderr.splitlines():
        m = re.search(r"black_start:([\d.]+) black_end:([\d.]+)", line)
        if m:
            out.append((round(float(m.group(1)), 2), round(float(m.group(2)), 2)))
    return out


def audio_levels(path):
    r = subprocess.run(
        [FFMPEG, "-nostdin", "-i", path, "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True)
    mean = mx = None
    for line in r.stderr.splitlines():
        m = re.search(r"mean_volume: ([\-\d.]+) dB", line)
        if m:
            mean = float(m.group(1))
        m = re.search(r"max_volume: ([\-\d.]+) dB", line)
        if m:
            mx = float(m.group(1))
    return mean, mx


def qc_sheet(path, name, times):
    os.makedirs(QC_DIR, exist_ok=True)
    # extract one labelled frame per time, then tile
    frames = []
    for i, t in enumerate(times):
        f = os.path.join(QC_DIR, f"{name}_f{i:02d}.jpg")
        subprocess.run(
            [FFMPEG, "-y", "-nostdin", "-loglevel", "error", "-ss", str(t),
             "-i", path, "-frames:v", "1",
             "-vf", (f"scale=460:-1,drawtext=fontfile='{FONT}':text='{t}s':"
                     f"fontcolor=yellow:fontsize=22:x=6:y=6:box=1:"
                     f"boxcolor=black@0.6:boxborderw=5"), f], check=True)
        frames.append(f)
    sheet = os.path.join(QC_DIR, f"{name}_qcsheet.jpg")
    cols = min(3, len(frames))
    rows = (len(frames) + cols - 1) // cols
    inp = []
    for f in frames:
        inp += ["-i", f]
    fc = "".join(f"[{i}:v]" for i in range(len(frames)))
    fc += f"xstack=inputs={len(frames)}:layout="
    layout = []
    for i in range(len(frames)):
        c, r = i % cols, i // cols
        x = "0" if c == 0 else "+".join(["w0"] * c)
        y = "0" if r == 0 else "+".join(["h0"] * r)
        layout.append(f"{x}_{y}")
    fc += "|".join(layout)
    # xstack needs equal sizes; frames already same scale width, pad heights
    subprocess.run([FFMPEG, "-y", "-nostdin", "-loglevel", "error"] + inp +
                   ["-filter_complex", fc + ":fill=black", "-frames:v", "1",
                    sheet], check=True)
    for f in frames:
        os.remove(f)
    return sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--edl")
    a = ap.parse_args()
    name = os.path.splitext(os.path.basename(a.video))[0]
    info = probe(a.video)
    issues = []

    edl = json.load(open(a.edl)) if a.edl else None
    if edl:
        mids, total = segment_midpoints(edl)
        if abs(info["dur"] - total) > 0.5:
            issues.append(f"duration {info['dur']}s != expected {total}s")
        end_fade = edl.get("end_fade_to_black", 0)
        times = mids + [round(info["dur"] - 0.05, 2)]
    else:
        end_fade = 1.0
        times = [round(info["dur"] * f, 2) for f in
                 (0.1, 0.3, 0.5, 0.7, 0.9)]

    if not info["has_audio"]:
        issues.append("no audio stream")
    # black frames outside the intended end fade
    for s, e in black_intervals(a.video):
        if s < info["dur"] - end_fade - 0.3:
            issues.append(f"unexpected black {s}-{e}s")
    mean, mx = audio_levels(a.video)
    if mx is not None and mx > -0.3:
        issues.append(f"audio near clipping (max {mx} dB)")
    if mean is not None and mean < -35:
        issues.append(f"audio very quiet (mean {mean} dB)")

    sheet = qc_sheet(a.video, name, times)
    verdict = "PASS" if not issues else "WARN"
    report = {"video": a.video, "verdict": verdict, "info": info,
              "audio_mean_db": mean, "audio_max_db": mx,
              "issues": issues, "qc_sheet": sheet, "checked_times": times}
    with open(os.path.join(QC_DIR, f"{name}_report.json"), "w") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    print(f"[qc] {name}: {verdict}  "
          f"{info['w']}x{info['h']} {info['fps']}fps {info['dur']}s "
          f"audio(mean={mean},max={mx})")
    for i in issues:
        print("   ⚠ ", i)
    print("   sheet:", sheet)
    sys.exit(0 if verdict == "PASS" else 2)


if __name__ == "__main__":
    main()
