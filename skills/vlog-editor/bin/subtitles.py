#!/usr/bin/env python3
"""Turn a whisper transcript (word timestamps) into a styled .ass subtitle.

Styles:
  karaoke  each word highlights (color fill) exactly as it is spoken — the
           modern vlog / CapCut look. Uses ASS \\kf and per-word onset timing.
  plain    whole phrase shown white, fades in/out.

Burn in with:  ffmpeg -i video -vf "ass=work/captions.ass" out.mp4

Usage: python3 bin/subtitles.py work/transcript.json work/captions.ass [--style karaoke] [--font Futura]
"""
import argparse
import json


def ass_time(t):
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{size},&H004AD2FF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0.6,0,1,4,1,2,160,160,120,1

[Events]
Format: Layer, Start, End, Style, MarginL, MarginR, Effect, Name, Text
"""


def chunk_segments(segs, max_words=7):
    """Split long segments into <=max_words caption chunks for readability."""
    for s in segs:
        words = s.get("words") or [{"word": s["text"], "start": s["start"],
                                    "end": s["end"]}]
        for i in range(0, len(words), max_words):
            grp = words[i:i + max_words]
            yield {"start": grp[0]["start"], "end": grp[-1]["end"], "words": grp}


def build(transcript, style, font):
    lines = [HEADER.format(font=font, size=58)]
    chunks = list(chunk_segments(transcript["segments"]))
    for ch in chunks:
        start, end = ch["start"], ch["end"]
        words = ch["words"]
        if style == "karaoke":
            parts = []
            for j, w in enumerate(words):
                nxt = words[j + 1]["start"] if j + 1 < len(words) else w["end"]
                cs = max(1, int(round((nxt - w["start"]) * 100)))  # onset-based
                wt = w["word"].strip()
                if j == 0:                       # drop leading punctuation
                    wt = wt.lstrip(" ,.;:!?-—")
                parts.append(f"{{\\kf{cs}}}{wt} ")
            text = "{\\fad(120,80)}" + "".join(parts).strip()
        else:
            toks = [w["word"].strip() for w in words]
            toks[0] = toks[0].lstrip(" ,.;:!?-—")
            text = "{\\fad(150,150)}" + " ".join(toks)
        lines.append(
            f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Cap,,0,0,0,,{text}"
        )
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript")
    ap.add_argument("out")
    ap.add_argument("--style", choices=["karaoke", "plain"], default="karaoke")
    ap.add_argument("--font", default="Futura")
    a = ap.parse_args()
    with open(a.transcript) as fh:
        t = json.load(fh)
    ass = build(t, a.style, a.font)
    with open(a.out, "w") as fh:
        fh.write(ass)
    n = ass.count("Dialogue:")
    print(f"[subtitles] wrote {a.out}: {n} caption lines, style={a.style}, font={a.font}")


if __name__ == "__main__":
    main()
