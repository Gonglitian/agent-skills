#!/usr/bin/env python3
"""Environment doctor — one command to verify the whole vlog-editor pipeline.

Prints a ✅/❌ table per dependency, the fix command for each missing one, and
which capability tiers are available (CORE vs beat / subtitle / download).
Run this first on a new machine.

Usage: python3 bin/doctor.py
Exit:  0 if the CORE出片链路 works, else 1.
"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _env

OK, NO = "✅", "❌"


def line(ok, label, fix=""):
    print(f"  {OK if ok else NO} {label}" + (f"\n        → {fix}" if (not ok and fix) else ""))


def py_candidates():
    seen, out = set(), []
    for p in [sys.executable, os.path.join(_env.CONDA_GUESS, "python"),
              shutil.which("python3"), shutil.which("python")]:
        if p and p not in seen and os.path.exists(p):
            seen.add(p)
            out.append(p)
    return out


def find_bin(name):
    p = shutil.which(name)
    if p:
        return p
    c = os.path.join(_env.CONDA_GUESS, name)
    return c if os.path.exists(c) else None


def find_python_with(mod):
    # -I = isolated mode: drop cwd ('') and env from sys.path so a stray .py in
    # the working dir can't shadow a real dependency and skew detection.
    for p in py_candidates():
        if subprocess.run([p, "-I", "-c", f"import {mod}"],
                          capture_output=True).returncode == 0:
            return p
    return None


def main():
    print("\n=== vlog-editor 环境体检 ===\n")
    core = True

    print("CORE — 出片最小集 (probe / scan / assemble / qc):")
    try:
        ff = _env.ffmpeg()
    except Exception:
        ff = None
    line(bool(ff), f"ffmpeg: {ff or '未找到'}",
         "conda install -c conda-forge ffmpeg   或   brew install ffmpeg")
    core &= bool(ff)
    dt = _env.has_drawtext()
    line(dt, "└─ drawtext (字幕/标题渲染)", "当前 ffmpeg 缺 libfreetype；改用 conda-forge 版")
    core &= dt
    fp = _env.ffprobe()
    fp_ok = bool(shutil.which(fp) or os.path.exists(fp))
    line(fp_ok, f"ffprobe: {fp}", "随 ffmpeg 一并安装")
    core &= fp_ok
    enc = _env.video_encoder_args()
    kind = ("VideoToolbox 硬件加速" if "videotoolbox" in enc[1]
            else "libx264 (CPU)" if "x264" in enc[1] else "mpeg4 回落")
    line(True, f"video encoder: {enc[1]}  ({kind})")
    try:
        line(True, f"font: {_env.font()}")
    except Exception:
        line(False, "font", "set VLOG_FONT=/path/to/font.ttf  (Linux: apt install fonts-dejavu)")
        core = False
    line(True, f"python: {sys.version.split()[0]}  @ {sys.executable}")

    print("\nOPTIONAL — 按需模块:")
    pb = find_python_with("librosa")
    line(bool(pb), "卡点 beats: librosa" + (f"  @ {pb}" if pb else ""),
         "pip install librosa")
    p_mlx = find_python_with("mlx_whisper")
    p_fw = find_python_with("faster_whisper")
    pm = p_mlx or p_fw
    which = "mlx_whisper" if p_mlx else ("faster_whisper" if p_fw else "无")
    line(bool(pm), f"语音字幕 transcribe: {which}" + (f"  @ {pm}" if pm else ""),
         "Apple Silicon: pip install mlx-whisper   其他: pip install faster-whisper")
    yd = find_bin("yt-dlp")
    line(bool(yd), "下载素材 yt-dlp" + (f"  @ {yd}" if yd else ""),
         "brew install yt-dlp   或   pip install yt-dlp")
    ae = find_bin("auto-editor")
    line(bool(ae), "去静默 auto-editor" + (f"  @ {ae}" if ae else ""),
         "pip install auto-editor")

    print("\n=== 结论 ===")
    print(f"  CORE 出片链路：{'✅ 可用（一个带 drawtext 的 ffmpeg 即可出片）' if core else '❌ 不可用，先修上面 CORE 项'}")
    print(f"  卡点 {OK if pb else '—'}   语音字幕 {OK if pm else '—'}   "
          f"下载 {OK if yd else '—'}   去静默 {OK if ae else '—'}\n")
    sys.exit(0 if core else 1)


if __name__ == "__main__":
    main()
