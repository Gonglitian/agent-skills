"""Shared environment detection for the vlog-editor scripts.

Makes the pipeline portable: instead of hardcoding the author's conda path,
it auto-detects a drawtext-capable ffmpeg, ffprobe, a usable font, and the
best available H.264 encoder. Everything is overridable via env vars:
    FFMPEG, FFPROBE, VLOG_FONT
"""
import functools
import os
import shutil
import subprocess

# A common spot for the full conda-forge ffmpeg (has drawtext + libass).
CONDA_GUESS = "/opt/homebrew/Caskroom/miniconda/base/envs/whisper/bin"


@functools.lru_cache(maxsize=None)
def _has_drawtext(ff):
    try:
        out = subprocess.run([ff, "-hide_banner", "-filters"],
                             capture_output=True, text=True).stdout
        return " drawtext " in out
    except Exception:
        return False


@functools.lru_cache(maxsize=None)
def ffmpeg():
    """First ffmpeg that has drawtext; else any ffmpeg; else raise."""
    cands = []
    if os.environ.get("FFMPEG"):
        cands.append(os.environ["FFMPEG"])
    if shutil.which("ffmpeg"):
        cands.append(shutil.which("ffmpeg"))
    cands.append(os.path.join(CONDA_GUESS, "ffmpeg"))
    existing = [c for c in cands if c and os.path.exists(c)]
    for c in existing:
        if _has_drawtext(c):
            return c
    if existing:
        return existing[0]          # found ffmpeg but no drawtext (caller warns)
    raise RuntimeError(
        "ffmpeg not found. Install a full build with drawtext/libfreetype "
        "(e.g. `conda install -c conda-forge ffmpeg` or `brew install ffmpeg`).")


@functools.lru_cache(maxsize=None)
def has_drawtext():
    try:
        return _has_drawtext(ffmpeg())
    except Exception:
        return False


@functools.lru_cache(maxsize=None)
def ffprobe():
    if os.environ.get("FFPROBE") and os.path.exists(os.environ["FFPROBE"]):
        return os.environ["FFPROBE"]
    if shutil.which("ffprobe"):
        return shutil.which("ffprobe")
    near = os.path.join(os.path.dirname(ffmpeg()), "ffprobe")
    if os.path.exists(near):
        return near
    c = os.path.join(CONDA_GUESS, "ffprobe")
    return c if os.path.exists(c) else "ffprobe"


@functools.lru_cache(maxsize=None)
def _encoder_list():
    try:
        return subprocess.run([ffmpeg(), "-hide_banner", "-encoders"],
                              capture_output=True, text=True).stdout
    except Exception:
        return ""


def video_encoder_args(bitrate="12M"):
    """Prefer Apple VideoToolbox; fall back to libx264; last resort mpeg4."""
    enc = _encoder_list()
    if "h264_videotoolbox" in enc:
        return ["-c:v", "h264_videotoolbox", "-b:v", bitrate]
    if "libx264" in enc:
        return ["-c:v", "libx264", "-crf", "18", "-preset", "medium",
                "-pix_fmt", "yuv420p"]
    return ["-c:v", "mpeg4", "-q:v", "3"]


FONT_CANDIDATES = [
    os.environ.get("VLOG_FONT"),
    "/System/Library/Fonts/Supplemental/Futura.ttc",          # macOS
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",   # Debian/Ubuntu
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",            # Fedora
    "/Library/Fonts/Arial.ttf",
]


@functools.lru_cache(maxsize=None)
def font():
    for f in FONT_CANDIDATES:
        if f and os.path.exists(f):
            return f
    try:                                  # let fontconfig pick something
        out = subprocess.run(["fc-match", "-f", "%{file}", "sans:bold"],
                             capture_output=True, text=True).stdout.strip()
        if out and os.path.exists(out):
            return out
    except Exception:
        pass
    raise RuntimeError("no usable font found; set VLOG_FONT=/path/to/font.ttf")


def resolve_font(requested):
    """Use the EDL's font if it exists on this machine, else auto-detect."""
    if requested and os.path.exists(requested):
        return requested
    return font()
