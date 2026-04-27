#!/usr/bin/env python3
"""GPT-Image-2 text-to-image via 速创API (api.wuyinkeji.com).

Submit → poll → download. Single-file, stdlib-only (uploads use curl via subprocess).

Usage:
    python generate.py "a ginger cat astronaut" -o out.png --size 16:9
    python generate.py "edit this photo into a watercolor" --ref https://example.com/p.jpg -o out.png
    python generate.py "..." --ref-local /path/to/local.png -o out.png        # auto-uploads to catbox
    python generate.py "..." --style univla -o figure.png                     # auto-loads style refs
    python generate.py --task-id image_xxx -o out.png                         # resume polling

Key resolution order: --key arg > $WUYINKEJI_API_KEY > ~/.config/wuyinkeji/api_key
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

SUBMIT_URL = "https://api.wuyinkeji.com/api/async/image_gpt"
DETAIL_URL = "https://api.wuyinkeji.com/api/async/detail"
KEY_FILE = Path.home() / ".config" / "wuyinkeji" / "api_key"
SKILL_DIR = Path(__file__).resolve().parent
STYLE_REFS_DIR = SKILL_DIR / "style_refs"
CATBOX_API = "https://catbox.moe/user/api.php"

VALID_SIZES = {
    "auto", "1:1", "3:2", "2:3", "16:9", "9:16", "4:3", "3:4",
    "21:9", "9:21", "1:3", "3:1", "2:1", "1:2",
}

VALID_STYLES = ("univla", "physical_intelligence", "fast_wam")


def load_key(cli_key: str | None) -> str:
    if cli_key:
        return cli_key.strip()
    env = os.environ.get("WUYINKEJI_API_KEY")
    if env:
        return env.strip()
    if KEY_FILE.exists():
        return KEY_FILE.read_text().strip()
    sys.exit(
        "no API key found. set $WUYINKEJI_API_KEY, pass --key, "
        f"or write key to {KEY_FILE}"
    )


def http_json(method: str, url: str, key: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Authorization": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def upload_to_catbox(path: Path) -> str:
    """Anonymous upload to catbox.moe via curl. Returns the public URL."""
    if not path.exists():
        sys.exit(f"upload target does not exist: {path}")
    try:
        out = subprocess.check_output(
            ["curl", "-sS", "-F", "reqtype=fileupload",
             "-F", f"fileToUpload=@{path}", CATBOX_API],
            timeout=120,
        ).decode().strip()
    except subprocess.CalledProcessError as e:
        sys.exit(f"catbox upload failed: {e}")
    if not out.startswith("http"):
        sys.exit(f"catbox upload returned unexpected response: {out!r}")
    return out


def resolve_style_refs(style: str) -> list[str]:
    """Find local style ref images, upload-and-cache, return public URLs.

    Cache file (`.urls.txt`) sits next to the images and stores `filename<TAB>url`
    pairs so we never re-upload the same file twice.
    """
    style_dir = STYLE_REFS_DIR / style
    if not style_dir.is_dir():
        sys.exit(f"style dir not found: {style_dir}")
    cache_file = style_dir / ".urls.txt"
    cache: dict[str, str] = {}
    if cache_file.exists():
        for line in cache_file.read_text().splitlines():
            if "\t" in line:
                k, v = line.split("\t", 1)
                cache[k] = v

    images = sorted(p for p in style_dir.iterdir()
                    if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"))
    if not images:
        sys.exit(f"no images in {style_dir}")

    urls: list[str] = []
    dirty = False
    for img in images:
        name = img.name
        if name in cache:
            urls.append(cache[name])
            continue
        print(f"[upload] {name} -> catbox …", file=sys.stderr)
        url = upload_to_catbox(img)
        cache[name] = url
        urls.append(url)
        dirty = True
    if dirty:
        cache_file.write_text("\n".join(f"{k}\t{v}" for k, v in cache.items()) + "\n")
    return urls


def submit(key: str, prompt: str, size: str, refs: list[str]) -> str:
    body: dict = {"prompt": prompt}
    if size and size != "auto":
        body["size"] = size
    if refs:
        body["urls"] = refs
    resp = http_json("POST", SUBMIT_URL, key, body)
    if resp.get("code") != 200:
        sys.exit(f"submit failed: {resp}")
    return resp["data"]["id"]


def poll(key: str, task_id: str, interval: float, timeout: float) -> dict:
    deadline = time.time() + timeout
    qs = urllib.parse.urlencode({"id": task_id})
    url = f"{DETAIL_URL}?{qs}"
    last_status = None
    while time.time() < deadline:
        resp = http_json("GET", url, key)
        status = resp.get("data", {}).get("status")
        if status != last_status:
            label = {0: "init", 1: "running", 2: "success", 3: "failed"}.get(status, "?")
            print(f"[{time.strftime('%H:%M:%S')}] status={status} ({label})",
                  file=sys.stderr)
            last_status = status
        if status == 2:
            return resp
        if status == 3:
            sys.exit(f"task failed: {resp.get('data', {}).get('message')!r} | full={resp}")
        time.sleep(interval)
    sys.exit(f"timeout after {timeout}s, task_id={task_id} (re-run with --task-id to resume)")


def download(url: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as r, open(out, "wb") as f:
        f.write(r.read())


def main() -> None:
    p = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("prompt", nargs="?", help="text prompt (omit when using --task-id)")
    p.add_argument("-o", "--out", default="image.png", help="output path (.png)")
    p.add_argument("--size", default="auto", help=f"aspect ratio, one of {sorted(VALID_SIZES)}")
    p.add_argument("--ref", action="append", default=[],
                   help="reference image PUBLIC URL (repeat for multiple)")
    p.add_argument("--ref-local", action="append", default=[],
                   help="local image path; auto-uploaded to catbox.moe and used as ref")
    p.add_argument("--style", choices=VALID_STYLES,
                   help="auto-load all style ref images from style_refs/<style>/ "
                        "(uploads + caches URLs in .urls.txt)")
    p.add_argument("--key", help="API key (overrides env / config file)")
    p.add_argument("--interval", type=float, default=5.0, help="poll interval seconds")
    p.add_argument("--timeout", type=float, default=300.0, help="overall timeout seconds")
    p.add_argument("--task-id", help="resume polling an existing task instead of submitting")
    p.add_argument("--no-download", action="store_true", help="print URL only, skip downloading")
    p.add_argument("--print-refs", action="store_true",
                   help="print resolved ref URLs and exit (no API call)")
    args = p.parse_args()

    if args.size not in VALID_SIZES:
        sys.exit(f"--size must be one of {sorted(VALID_SIZES)}")

    refs: list[str] = list(args.ref)
    for local in args.ref_local:
        refs.append(upload_to_catbox(Path(local)))
    if args.style:
        refs.extend(resolve_style_refs(args.style))

    if args.print_refs:
        for u in refs:
            print(u)
        return

    if not args.task_id and not args.prompt:
        sys.exit("either prompt or --task-id is required")

    key = load_key(args.key)

    if args.task_id:
        task_id = args.task_id
        print(f"resuming task_id={task_id}", file=sys.stderr)
    else:
        if refs:
            print(f"using {len(refs)} reference image(s)", file=sys.stderr)
        task_id = submit(key, args.prompt, args.size, refs)
        print(f"submitted task_id={task_id}", file=sys.stderr)

    resp = poll(key, task_id, args.interval, args.timeout)
    urls = resp["data"].get("result") or []
    if not urls:
        sys.exit(f"no result urls in response: {resp}")
    for i, u in enumerate(urls):
        print(u)
        if args.no_download:
            continue
        out = Path(args.out)
        if len(urls) > 1:
            out = out.with_stem(f"{out.stem}_{i}")
        download(u, out)
        print(f"saved -> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
