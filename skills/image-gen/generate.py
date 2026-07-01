#!/usr/bin/env python3
"""
image-gen — unified image generation. User picks the backend and (optionally) a style.

BACKENDS  (--backend, default: nano)
  nano : Google Gemini "Nano Banana" — fast (~3-10s), sync, cheap. Models via --model:
           lite (gemini-3.1-flash-lite-image $0.034) | nb2 (gemini-3.1-flash-image, default $0.067)
           | pro (gemini-3-pro-image $0.134, best text/4K)
  gpt  : 速创API GPT-Image-2 — async submit->poll, stronger realism & fine text; slower (~60-90s).

STYLE PRESETS  (--style, work with EITHER backend)
  univla | physical_intelligence | fast_wam | bluebook
  Auto-appends the preset's STYLE text block AND attaches its reference images.

KEY RESOLUTION
  nano: --key -> $GEMINI_API_KEY -> $GOOGLE_API_KEY -> ~/.config/gemini/api_key
  gpt : --key -> $WUYINKEJI_API_KEY -> ~/.config/wuyinkeji/api_key

EXAMPLES
  python3 generate.py "a banana on a beach" -o out.jpg                       # nano (default), nb2
  python3 generate.py "product shot" --backend nano --model lite --aspect 1:1 -o p.jpg
  python3 generate.py "make it night" --ref out.jpg -o n.jpg                 # edit (nano, local ref direct)
  python3 generate.py "photoreal portrait, tiny text 'HELLO'" --backend gpt --aspect 3:4 -o g.png
  python3 generate.py "Method overview of a VLA policy ..." --backend gpt --style univla --aspect 16:9 -o fig.png
"""
import argparse, base64, json, mimetypes, os, subprocess, sys, time
import urllib.parse, urllib.request, urllib.error
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
STYLE_DIR = SKILL_DIR / "prompt_styles"
STYLE_REFS_DIR = SKILL_DIR / "style_refs"
VALID_STYLES = ("univla", "physical_intelligence", "fast_wam", "bluebook")

# ---- nano (Gemini) ----
GEMINI_API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
NANO_ALIAS = {"lite": "gemini-3.1-flash-lite-image", "nb2": "gemini-3.1-flash-image",
              "flash": "gemini-3.1-flash-image", "pro": "gemini-3-pro-image"}
NANO_PRICE = {"gemini-3.1-flash-lite-image": 30.0, "gemini-3.1-flash-image": 60.0,
              "gemini-3-pro-image": 120.0}

# ---- gpt (速创API) ----
GPT_SUBMIT = "https://api.wuyinkeji.com/api/async/image_gpt"
GPT_DETAIL = "https://api.wuyinkeji.com/api/async/detail"
CATBOX_API = "https://catbox.moe/user/api.php"
GPT_SIZES = {"auto", "1:1", "3:2", "2:3", "16:9", "9:16", "4:3", "3:4",
             "21:9", "9:21", "1:3", "3:1", "2:1", "1:2"}


# ============ shared helpers ============
def resolve_key(backend, cli_key):
    if cli_key:
        return cli_key.strip()
    if backend == "nano":
        for e in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            if os.environ.get(e):
                return os.environ[e].strip()
        f = Path.home() / ".config/gemini/api_key"
    else:
        if os.environ.get("WUYINKEJI_API_KEY"):
            return os.environ["WUYINKEJI_API_KEY"].strip()
        f = Path.home() / ".config/wuyinkeji/api_key"
    if f.exists():
        return f.read_text().strip()
    sys.exit(f"no API key for backend '{backend}'. set --key or write {f}")


def load_style_block(style):
    """Extract the <<<STYLE ... STYLE>>> text block from prompt_styles/<style>.md."""
    md = STYLE_DIR / f"{style}.md"
    if not md.exists():
        print(f"[style] {md} missing; skipping text block", file=sys.stderr)
        return ""
    lines = md.read_text().splitlines()
    out, grab = [], False
    for ln in lines:
        if ln.startswith("<<<STYLE"):
            grab = True; continue
        if ln.startswith("STYLE>>>"):
            break
        if grab:
            out.append(ln)
    return "\n".join(out).strip()


def style_ref_paths(style):
    d = STYLE_REFS_DIR / style
    if not d.is_dir():
        return []
    return sorted(p for p in d.iterdir()
                  if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"))


def jpeg_png_dims(raw):
    import struct
    try:
        if raw[:2] == b"\xff\xd8":
            i = 2
            while i < len(raw):
                if raw[i] != 0xFF:
                    i += 1; continue
                m = raw[i + 1]
                if m in (0xC0, 0xC1, 0xC2, 0xC3):
                    return (struct.unpack(">H", raw[i + 7:i + 9])[0],
                            struct.unpack(">H", raw[i + 5:i + 7])[0])
                i += 2 + struct.unpack(">H", raw[i + 2:i + 4])[0]
        elif raw[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", raw[16:24]); return w, h
    except Exception:
        pass
    return None, None


# ============ nano backend ============
def nano_load_ref_inline(src):
    if src.startswith(("http://", "https://")):
        with urllib.request.urlopen(src, timeout=60) as r:
            raw, mime = r.read(), (r.headers.get_content_type() or "image/jpeg")
    else:
        p = Path(os.path.expanduser(src))
        raw, mime = p.read_bytes(), (mimetypes.guess_type(str(p))[0] or "image/jpeg")
    return {"inlineData": {"mimeType": mime, "data": base64.b64encode(raw).decode()}}


def nano_run(args, prompt, ref_srcs):
    model = NANO_ALIAS.get(args.model.lower(), args.model) if args.model else NANO_ALIAS["nb2"]
    key = resolve_key("nano", args.key)
    parts = [nano_load_ref_inline(s) for s in ref_srcs]
    if prompt:
        parts.append({"text": prompt})
    gen = {"responseModalities": ["IMAGE"]}
    icfg = {}
    if args.aspect:
        icfg["aspectRatio"] = args.aspect
    if args.res:
        if model == "gemini-3.1-flash-lite-image" and args.res.upper() != "1K":
            print(f"  [warn] lite is 1K only; ignoring --res {args.res}", file=sys.stderr)
        else:
            icfg["imageSize"] = args.res.upper()
    if icfg:
        gen["imageConfig"] = icfg
    body = {"contents": [{"parts": parts}], "generationConfig": gen}
    rate = NANO_PRICE.get(model, 60.0)

    saved, total = [], 0.0
    for i in range(args.n):
        req = urllib.request.Request(GEMINI_API.format(model=model), data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json", "X-goog-api-key": key},
                                     method="POST")
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                resp = json.loads(r.read())
        except urllib.error.HTTPError as e:
            sys.exit(f"HTTP {e.code} from Gemini:\n{e.read().decode(errors='replace')[:1000]}")
        dt = time.time() - t0
        if "error" in resp:
            sys.exit("Gemini error: " + json.dumps(resp["error"], ensure_ascii=False)[:600])
        imgs, texts, um = [], [], resp.get("usageMetadata", {})
        for c in resp.get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                if "inlineData" in p:
                    imgs.append((p["inlineData"]["mimeType"], base64.b64decode(p["inlineData"]["data"])))
                elif "text" in p:
                    texts.append(p["text"])
        if not imgs:
            sys.exit(f"no image (call {i+1}); model said: {' '.join(texts)[:300]}")
        tok = next((x["tokenCount"] for x in um.get("candidatesTokensDetails", [])
                    if x.get("modality") == "IMAGE"), 0)
        cost = tok / 1e6 * rate; total += cost
        for j, (mime, raw) in enumerate(imgs):
            ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}.get(mime, "jpg")
            stem = os.path.splitext(os.path.expanduser(args.out))[0]
            path = f"{stem}_{i+1}.{ext}" if args.n > 1 else f"{stem}.{ext}"
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_bytes(raw)
            w, h = jpeg_png_dims(raw)
            saved.append(path)
            print(f"  ✓ {path}  {w}x{h}  {len(raw)//1024}KB  {dt:.1f}s  {tok}tok  ${cost:.4f}")
    print(f"\nbackend=nano model={model} images={len(saved)} total≈${total:.4f}")
    for p in saved:
        print(p)


# ============ gpt backend ============
def gpt_http(method, url, key, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def catbox_upload(path):
    out = subprocess.check_output(
        ["curl", "-sS", "-F", "reqtype=fileupload", "-F", f"fileToUpload=@{path}", CATBOX_API],
        timeout=120).decode().strip()
    if not out.startswith("http"):
        sys.exit(f"catbox upload failed: {out!r}")
    return out


def gpt_style_ref_urls(style):
    """Local style refs -> catbox URLs, cached in style_refs/<style>/.urls.txt (no re-upload)."""
    d = STYLE_REFS_DIR / style
    imgs = style_ref_paths(style)
    if not imgs:
        print(f"[style] no ref images for '{style}'; text block only", file=sys.stderr)
        return []
    cache_file = d / ".urls.txt"
    cache = {}
    if cache_file.exists():
        for line in cache_file.read_text().splitlines():
            if "\t" in line:
                k, v = line.split("\t", 1); cache[k] = v
    urls, dirty = [], False
    for img in imgs:
        if img.name in cache:
            urls.append(cache[img.name]); continue
        print(f"[upload] {img.name} -> catbox …", file=sys.stderr)
        cache[img.name] = catbox_upload(img); urls.append(cache[img.name]); dirty = True
    if dirty:
        cache_file.write_text("\n".join(f"{k}\t{v}" for k, v in cache.items()) + "\n")
    return urls


def gpt_run(args, prompt, ref_srcs, style):
    key = resolve_key("gpt", args.key)
    aspect = args.aspect or "auto"
    if aspect not in GPT_SIZES:
        sys.exit(f"--aspect for gpt must be one of {sorted(GPT_SIZES)}")
    # refs: local paths -> catbox, urls pass through; + style refs
    urls = []
    for s in ref_srcs:
        urls.append(s if s.startswith(("http://", "https://")) else catbox_upload(Path(os.path.expanduser(s))))
    if style:
        urls.extend(gpt_style_ref_urls(style))

    if args.task_id:
        task_id = args.task_id
        print(f"resuming task_id={task_id}", file=sys.stderr)
    else:
        body = {"prompt": prompt}
        if aspect != "auto":
            body["size"] = aspect
        if urls:
            body["urls"] = urls
            print(f"using {len(urls)} reference image(s)", file=sys.stderr)
        resp = gpt_http("POST", GPT_SUBMIT, key, body)
        if resp.get("code") != 200:
            sys.exit(f"submit failed: {resp}")
        task_id = resp["data"]["id"]
        print(f"submitted task_id={task_id}", file=sys.stderr)

    # poll
    deadline = time.time() + args.timeout
    qurl = f"{GPT_DETAIL}?{urllib.parse.urlencode({'id': task_id})}"
    last = None
    while time.time() < deadline:
        resp = gpt_http("GET", qurl, key)
        st = resp.get("data", {}).get("status")
        if st != last:
            print(f"[{time.strftime('%H:%M:%S')}] status={st} "
                  f"({ {0:'init',1:'running',2:'success',3:'failed'}.get(st,'?') })", file=sys.stderr)
            last = st
        if st == 2:
            break
        if st == 3:
            sys.exit(f"task failed: {resp.get('data',{}).get('message')!r}")
        time.sleep(args.interval)
    else:
        sys.exit(f"timeout {args.timeout}s; resume with --backend gpt --task-id {task_id}")

    res_urls = resp["data"].get("result") or []
    if not res_urls:
        sys.exit(f"no result urls: {resp}")
    for i, u in enumerate(res_urls):
        print(u)
        if args.no_download:
            continue
        out = Path(os.path.expanduser(args.out))
        if len(res_urls) > 1:
            out = out.with_stem(f"{out.stem}_{i}")
        out.parent.mkdir(parents=True, exist_ok=True)
        # result CDN (e.g. scapi.net) 403s the default urllib UA; curl works (as documented)
        try:
            subprocess.check_output(["curl", "-fsSL", "-o", str(out), u], timeout=180)
        except subprocess.CalledProcessError:
            req2 = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req2, timeout=120) as r:
                out.write_bytes(r.read())
        print(f"  ✓ saved -> {out}  ({out.stat().st_size//1024}KB)", file=sys.stderr)
    print(f"\nbackend=gpt images={len(res_urls)}")


# ============ main ============
def main():
    ap = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=__doc__)
    ap.add_argument("prompt", nargs="?", default="", help="text prompt")
    ap.add_argument("-o", "--out", default="image.jpg", help="output path (ext auto-set to real mime)")
    ap.add_argument("--backend", choices=("nano", "gpt"), default="nano", help="default: nano")
    ap.add_argument("--model", help="[nano] lite | nb2 | pro | raw id (default nb2)")
    ap.add_argument("--style", choices=VALID_STYLES, help="apply a paper/科普 preset (text + refs)")
    ap.add_argument("--ref", action="append", default=[], help="reference image: local path or URL; repeatable")
    ap.add_argument("--aspect", help="aspect ratio, e.g. 1:1 16:9 9:16 4:3 3:4 21:9")
    ap.add_argument("--res", help="[nano] resolution 1K|2K|4K (2K/4K: nb2 & pro only)")
    ap.add_argument("-n", type=int, default=1, help="[nano] number of variations")
    ap.add_argument("--key", help="API key (else env / config file for the chosen backend)")
    # gpt-only
    ap.add_argument("--task-id", help="[gpt] resume polling an existing task")
    ap.add_argument("--interval", type=float, default=5.0, help="[gpt] poll interval s")
    ap.add_argument("--timeout", type=float, default=300.0, help="[gpt] overall timeout s")
    ap.add_argument("--no-download", action="store_true", help="[gpt] print URL only")
    a = ap.parse_args()

    # assemble prompt (+ style text block)
    prompt = a.prompt or ""
    if a.style:
        block = load_style_block(a.style)
        if block:
            prompt = f"{prompt}\n\n{block}" if prompt else block

    if a.backend == "gpt":
        if not prompt and not a.task_id:
            ap.error("gpt: need a prompt (or --task-id)")
        gpt_run(a, prompt, a.ref, a.style)
    else:
        if not prompt and not a.ref:
            ap.error("nano: need a prompt and/or --ref")
        # nano can take style refs as LOCAL inline images directly (no catbox)
        refs = list(a.ref)
        if a.style:
            refs += [str(p) for p in style_ref_paths(a.style)]
        nano_run(a, prompt, refs)


if __name__ == "__main__":
    main()
