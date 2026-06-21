#!/usr/bin/env python3
"""Render layer: turn an EDL into a finished film with FFmpeg.

Two-pass, robust & debuggable:
  Pass 1  normalize each segment -> work/segments/segNN.mp4
          (uniform 1920x1080@fps, SAR 1, color grade, captions baked in;
           portrait clips get a blurred-background pillarbox)
  Pass 2  xfade the segments into one timeline, lay the music bed,
          fade to black, encode with VideoToolbox.

Usage:  python3 bin/assemble.py edl.json
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _env

# Paths in the EDL (clips, output) and the work/ dir are resolved relative to
# the CURRENT WORKING DIRECTORY, so the script is portable: run it from any
# project folder (e.g. when installed as a skill under ~/.claude/skills/).
ROOT = os.getcwd()
SEG_DIR = os.path.join(ROOT, "work", "segments")

# Auto-detected drawtext-capable ffmpeg (override via $FFMPEG). The Homebrew
# build often lacks libfreetype; _env prefers one that has drawtext.
FFMPEG = _env.ffmpeg()


def run(cmd):
    cmd = [FFMPEG if a == "ffmpeg" else a for a in cmd]
    print("  $ ffmpeg", " ".join(a if " " not in a else f'"{a}"' for a in cmd[1:]) [:240], "...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG ERROR:\n", r.stderr[-2500:], file=sys.stderr)
        raise SystemExit(1)
    return r


def caption_drawtext(text, font, dur, fontsize=52, y="h-162"):
    """A lower-third caption that fades in/out.

    Legibility is bulletproofed for ANY background: a real black glyph
    outline (borderw) + drop shadow + a semi-opaque box. White text with
    only a faint box vanishes over bright footage (e.g. a sunlit road);
    the outline is what makes it readable on bright and dark alike.
    """
    fin, fout = 0.6, 0.6
    appear, vanish = 0.7, dur - 0.5
    alpha = (
        f"if(lt(t,{appear}),0,"
        f"if(lt(t,{appear+fin}),(t-{appear})/{fin},"
        f"if(lt(t,{vanish-fout}),1,"
        f"if(lt(t,{vanish}),({vanish}-t)/{fout},0))))"
    )
    safe = text.replace(":", "\\:").replace("'", "")
    return (
        f"drawtext=fontfile='{font}':text='{safe}':fontcolor=white:"
        f"fontsize={fontsize}:x=(w-text_w)/2:y={y}:"
        f"borderw=4:bordercolor=black@0.9:"
        f"shadowcolor=black@0.75:shadowx=2:shadowy=2:"
        f"box=1:boxcolor=black@0.42:boxborderw=26:"
        f"alpha='{alpha}'"
    )


def title_drawtext(text, subtitle, font, t_in, hold):
    """Big centered hero title + subtitle, fades in then out."""
    fin, fout = 0.9, 0.9
    a = (
        f"if(lt(t,{t_in}),0,"
        f"if(lt(t,{t_in+fin}),(t-{t_in})/{fin},"
        f"if(lt(t,{hold-fout}),1,"
        f"if(lt(t,{hold}),({hold}-t)/{fout},0))))"
    )
    title = (
        f"drawtext=fontfile='{font}':text='{text}':fontcolor=white:"
        f"fontsize=120:x=(w-text_w)/2:y=(h-text_h)/2-30:"
        f"borderw=3:bordercolor=black@0.55:"
        f"shadowcolor=black@0.55:shadowx=2:shadowy=3:alpha='{a}'"
    )
    sub = (
        f"drawtext=fontfile='{font}':text='{subtitle}':fontcolor=white:"
        f"fontsize=34:x=(w-text_w)/2:y=(h/2)+70:"
        f"borderw=2:bordercolor=black@0.5:"
        f"shadowcolor=black@0.55:shadowx=1:shadowy=2:alpha='{a}'"
    )
    return title + "," + sub


def build_segment_vf(seg, edl):
    W, H, fps = edl["width"], edl["height"], edl["fps"]
    # CRITICAL: -ss after -i keeps the source PTS, so a clip trimmed at in=20s
    # would start at t≈20. Time-based filters (drawtext alpha fades) assume the
    # segment starts at t=0, so reset PTS first or captions silently vanish.
    reset = "setpts=PTS-STARTPTS"
    if seg.get("portrait"):
        base = (
            f"{reset},split=2[a][b];"
            f"[b]scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},boxblur=26:3[bg];"
            f"[a]scale=-2:{H}[fg];"
            f"[bg][fg]overlay=(W-w)/2:0,setsar=1,fps={fps}"
        )
    else:
        base = (
            f"{reset},scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"setsar=1,fps={fps}"
        )
    chain = base + "," + edl["grade"]
    # optional Ken-Burns slow push-in. Applied to the picture only (before
    # captions, so text stays put). `on` is the per-segment output frame index,
    # so zoom starts at 1.0 each segment and resets at every hard cut -> the
    # reset reads as a subtle "punch" on the beat.
    if edl.get("kenburns"):
        zmax = edl.get("kenburns_max", 1.06)
        frames = max(1, int(round(seg["dur"] * fps)))
        zrate = round((zmax - 1.0) / frames, 7)
        chain += (
            f",zoompan=z='min(1.0+{zrate}*on,{zmax})':d=1:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={fps}"
        )
    overlays = []
    if seg.get("role") == "open" and edl.get("title"):
        t = edl["title"]
        overlays.append(title_drawtext(t["text"], t["subtitle"], edl["font"],
                                       t["in"], t["hold_until"]))
    if seg.get("caption"):
        overlays.append(caption_drawtext(seg["caption"], edl["font"], seg["dur"]))
    if overlays:
        chain += "," + ",".join(overlays)
    chain += ",format=yuv420p"
    return chain


def pass1(edl):
    os.makedirs(SEG_DIR, exist_ok=True)
    seg_files = []
    for i, seg in enumerate(edl["segments"]):
        out = os.path.join(SEG_DIR, f"seg{i:02d}.mp4")
        vf = build_segment_vf(seg, edl)
        print(f"[pass1] segment {i}: {os.path.basename(seg['clip'])} "
              f"in={seg['in']} dur={seg['dur']} "
              f"{'(portrait fill)' if seg.get('portrait') else ''}")
        run([
            "ffmpeg", "-y", "-nostdin",
            # -ss BEFORE -i: input seeking is frame-accurate in modern ffmpeg
            # AND resets the segment timeline to t=0, which the drawtext alpha
            # fades depend on. (-ss after -i keeps source PTS, e.g. t=20+, so
            # the fade window 0..dur never matches and captions never appear.)
            "-ss", str(seg["in"]),
            "-i", os.path.join(ROOT, seg["clip"]),
            "-t", str(seg["dur"]),
            "-vf", vf, "-an",
            "-c:v", "libx264", "-crf", "16", "-preset", "medium",
            "-pix_fmt", "yuv420p", "-r", str(edl["fps"]),
            out,
        ])
        seg_files.append(out)
    return seg_files


def pass2(edl, seg_files):
    durs = [s["dur"] for s in edl["segments"]]
    inputs = []
    for f in seg_files:
        inputs += ["-i", f]
    fc = []
    # Two timeline modes:
    #   cut   -> hard cuts (concat). Total = sum of durations. Cuts land exactly
    #            where each segment ends, so beat-aligned durations => on-beat.
    #   xfade -> crossfade chain. Each transition eats `xfade` seconds of overlap.
    cut_mode = (edl.get("xfade_transition") == "cut"
                or edl.get("xfade_duration", 0) == 0)
    if cut_mode:
        cat_in = "".join(f"[{i}:v]" for i in range(len(seg_files)))
        fc.append(f"{cat_in}concat=n={len(seg_files)}:v=1:a=0[vcat]")
        prev = "[vcat]"
        total = round(sum(durs), 3)
    else:
        xfade = edl["xfade_duration"]
        prev = "[0:v]"
        combined = durs[0]
        for i in range(1, len(seg_files)):
            offset = round(combined - xfade, 3)
            label = f"[vx{i}]"
            fc.append(
                f"{prev}[{i}:v]xfade=transition={edl['xfade_transition']}:"
                f"duration={xfade}:offset={offset}{label}"
            )
            prev = label
            combined = round(combined + durs[i] - xfade, 3)
        total = combined
    # final video fade to black
    efb = edl.get("end_fade_to_black", 0)
    vlabel = prev
    if efb:
        fc.append(f"{prev}fade=t=out:st={round(total-efb,3)}:d={efb}[vout]")
        vlabel = "[vout]"
    # music bed
    m = edl["music"]
    mi = len(seg_files)
    inputs += ["-ss", str(m["start"]), "-t", str(round(total, 3)),
               "-i", os.path.join(ROOT, m["path"])]
    gain = m.get("gain_db", 0)
    afilter = (
        f"[{mi}:a]volume={gain}dB,"
        f"afade=t=in:st=0:d={m['fade_in']},"
        f"afade=t=out:st={round(total-m['fade_out'],3)}:d={m['fade_out']}[aout]"
    )
    fc.append(afilter)
    filter_complex = ";".join(fc)

    out = os.path.join(ROOT, edl["output"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    mode = "hard-cut" if cut_mode else "xfade"
    print(f"[pass2] {mode} {len(seg_files)} segments -> {total:.2f}s, "
          f"music bed, fade-to-black, encode")
    cmd = ["ffmpeg", "-y", "-nostdin"] + inputs + [
        "-filter_complex", filter_complex,
        "-map", vlabel, "-map", "[aout]",
        *_env.video_encoder_args("12M"),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart",
        out,
    ]
    run(cmd)
    return out, total


def main():
    edl_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "edl.json")
    with open(edl_path) as fh:
        edl = json.load(fh)
    edl["font"] = _env.resolve_font(edl.get("font"))  # portable font
    print(f"== Assembling '{edl_path}' ==")
    seg_files = pass1(edl)
    out, total = pass2(edl, seg_files)
    print(f"\n✅ Done: {out}  (~{total:.1f}s)")


if __name__ == "__main__":
    main()
