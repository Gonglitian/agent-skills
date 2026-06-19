#!/usr/bin/env python3
"""Perception layer for AUDIO: turn music into structured numbers the agent
can reason over (since the LLM can't hear the signal).

Emits: tempo (BPM), every beat time, and downbeat candidates (every 4th beat,
the bar lines) — these become cut points for beat-synced editing.

Usage: python3 bin/beats.py footage/music.mp3 [--downbeat-every 4]
"""
import argparse
import json
import sys

import librosa
import numpy as np


def analyze(path, meter=4):
    y, sr = librosa.load(path, mono=True)          # decode to waveform
    # 1) onset strength envelope: where energy SUDDENLY rises (drum hits, plucks)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    # 2) tempo + 3) beat positions via dynamic programming over the envelope
    tempo, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_env, sr=sr, units="frames"
    )
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    # downbeats: the "1" of each bar. Cheap heuristic = strongest beat phase.
    # Pick the phase (0..meter-1) whose beats sit on the largest onset spikes.
    strengths = onset_env[beat_frames] if len(beat_frames) else np.array([])
    best_phase, best_score = 0, -1
    for p in range(meter):
        s = strengths[p::meter].sum() if len(strengths) else 0
        if s > best_score:
            best_score, best_phase = s, p
    downbeats = beat_times[best_phase::meter]
    return {
        "file": path,
        "duration_s": round(len(y) / sr, 2),
        "bpm": round(float(np.atleast_1d(tempo)[0]), 1),
        "n_beats": int(len(beat_times)),
        "beat_times": [round(float(t), 3) for t in beat_times],
        "downbeat_times": [round(float(t), 3) for t in downbeats],
        "meter_assumed": meter,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--downbeat-every", type=int, default=4)
    a = ap.parse_args()
    r = analyze(a.audio, a.downbeat_every)
    print(json.dumps(r, ensure_ascii=False))
    # human-friendly preview to stderr
    print(f"\nBPM={r['bpm']}  beats={r['n_beats']}  "
          f"downbeats={len(r['downbeat_times'])}", file=sys.stderr)
    print("first 12 beats:    " +
          "  ".join(f"{t:5.2f}" for t in r["beat_times"][:12]), file=sys.stderr)
    print("first 6 downbeats: " +
          "  ".join(f"{t:5.2f}" for t in r["downbeat_times"][:6]), file=sys.stderr)


if __name__ == "__main__":
    main()
