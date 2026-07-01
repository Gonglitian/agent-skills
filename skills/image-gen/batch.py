#!/usr/bin/env python3
"""Parallel batch generation for image-gen.

gpt backend (default here): submits ALL jobs first (async submit->poll), then polls
them together — wall time ≈ slowest single image, not the serial sum. This is the
main reason batch exists (gpt is ~60-90s/image).
nano backend: fast & sync, so jobs run sequentially via generate.py (still one call).

Usage:
  python3 batch.py --backend gpt --style fast_wam --aspect 16:9 \
      --job out1.png=prompt1.txt --job out2.png=prompt2.txt \
      --resume out3.png=image_xxxx          # adopt an already-submitted task_id (gpt)

  python3 batch.py --backend nano --model nb2 --aspect 16:9 \
      --job a.jpg=promptA.txt --job b.jpg=promptB.txt

Notes:
  - --style appends the STYLE block text to every prompt AND attaches style refs
    (gpt: catbox URLs; nano: local files), same as generate.py.
  - Failures don't abort the batch; a summary prints at the end; non-zero exit if any failed.
  - Timed-out gpt tasks print a ready-to-paste --resume arg (no re-billing).
"""
import argparse, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate as G  # noqa: E402


def curl_download(url, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.check_output(["curl", "-fsSL", "-o", str(out), url], timeout=180)
    except subprocess.CalledProcessError:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r:
            out.write_bytes(r.read())


def run_gpt(args):
    key = G.resolve_key("gpt", args.key)
    refs = G.gpt_style_ref_urls(args.style) if args.style else []
    suffix = ("\n\n" + G.load_style_block(args.style)) if args.style else ""
    size = args.aspect or "auto"

    tasks = {}  # task_id -> out Path
    for spec in args.resume:
        out, tid = spec.split("=", 1); tasks[tid] = Path(out)
        print(f"[resume] {out} <- {tid}", file=sys.stderr)
    for spec in args.job:
        out, pf = spec.split("=", 1)
        prompt = Path(pf).read_text().strip() + suffix
        body = {"prompt": prompt}
        if size != "auto":
            body["size"] = size
        if refs:
            body["urls"] = refs
        resp = G.gpt_http("POST", G.GPT_SUBMIT, key, body)
        if resp.get("code") != 200:
            print(f"[submit-FAIL] {out}: {resp}", file=sys.stderr); continue
        tid = resp["data"]["id"]; tasks[tid] = Path(out)
        print(f"[submit] {out} <- {tid}", file=sys.stderr)

    pending = dict(tasks); done, failed = {}, {}
    deadline = time.time() + args.timeout
    while pending and time.time() < deadline:
        for tid in list(pending):
            url = f"{G.GPT_DETAIL}?{urllib.parse.urlencode({'id': tid})}"
            try:
                resp = G.gpt_http("GET", url, key)
            except Exception as e:
                print(f"[poll-err] {tid}: {e}", file=sys.stderr); continue
            st = resp.get("data", {}).get("status")
            if st == 2:
                out = pending.pop(tid); u = (resp["data"].get("result") or [None])[0]
                if u:
                    curl_download(u, out); done[out] = u
                    print(f"[done {len(done)}/{len(tasks)}] {out}", file=sys.stderr); print(u)
                else:
                    failed[out] = f"no result url: {resp}"
            elif st == 3:
                out = pending.pop(tid)
                failed[out] = resp["data"].get("message", "") or str(resp)
                print(f"[FAIL] {out}: {failed[out]}", file=sys.stderr)
        if pending:
            time.sleep(args.interval)
    for tid, out in pending.items():
        failed[out] = f"timeout — resume with: --backend gpt --resume {out}={tid}"

    print(f"\nsummary: {len(done)} ok, {len(failed)} failed/pending", file=sys.stderr)
    for out, why in failed.items():
        print(f"  FAILED {out}: {why}", file=sys.stderr)
    return 1 if failed else 0


def run_nano(args):
    gp = str(Path(__file__).resolve().parent / "generate.py")
    ok, bad = 0, []
    for spec in args.job:
        out, pf = spec.split("=", 1)
        prompt = Path(pf).read_text().strip()
        cmd = ["python3", gp, prompt, "--backend", "nano", "-o", out]
        if args.model:
            cmd += ["--model", args.model]
        if args.style:
            cmd += ["--style", args.style]
        if args.aspect:
            cmd += ["--aspect", args.aspect]
        if args.key:
            cmd += ["--key", args.key]
        print(f"[nano] {out} …", file=sys.stderr)
        if subprocess.run(cmd).returncode == 0:
            ok += 1
        else:
            bad.append(out)
    print(f"\nsummary: {ok} ok, {len(bad)} failed", file=sys.stderr)
    for o in bad:
        print(f"  FAILED {o}", file=sys.stderr)
    return 1 if bad else 0


def main():
    p = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__)
    p.add_argument("--backend", choices=("nano", "gpt"), default="gpt")
    p.add_argument("--job", action="append", default=[], metavar="OUT=PROMPT_FILE")
    p.add_argument("--resume", action="append", default=[], metavar="OUT=TASK_ID (gpt)")
    p.add_argument("--style", choices=G.VALID_STYLES)
    p.add_argument("--model", help="[nano] lite|nb2|pro")
    p.add_argument("--aspect", default=None)
    p.add_argument("--key")
    p.add_argument("--interval", type=float, default=4.0, help="[gpt] poll interval s")
    p.add_argument("--timeout", type=float, default=600.0, help="[gpt] overall timeout s")
    a = p.parse_args()
    if not a.job and not a.resume:
        sys.exit("need at least one --job or --resume")
    sys.exit(run_gpt(a) if a.backend == "gpt" else run_nano(a))


if __name__ == "__main__":
    main()
