#!/usr/bin/env python3
"""Download audio/video for OmniBox video targets. RUN IN THE py3.12 'xhs' env (has XHS-Downloader + yt-dlp).

  conda run -n xhs python download_videos.py --targets video_targets.json --out ./audio [--xhs-repo <path>] [--cookie '<xhs cookie>']

Bilibili: resolve b23.tv -> BV, then `python -m yt_dlp -x` (m4a).
Xiaohongshu: XHS-Downloader (proper signed API, recovers most) -> fallback to page masterUrl.
Skips files already present. Writes download_manifest.json with per-item status.
Why two methods for XHS: yt-dlp's xiaohongshu extractor is broken ("No video formats");
the page __INITIAL_STATE__ masterUrl is a cached signed URL that is often expired (404);
XHS-Downloader re-requests a FRESH signed URL via the official API, so it succeeds far more often.
"""
import json, os, re, sys, glob, subprocess, urllib.request, asyncio, argparse
from collections import Counter

UA_M = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"

def have(audio, idd): return bool(glob.glob(f"{audio}/*_{idd}.*"))

def http_get(url, out, referer="https://www.xiaohongshu.com/", timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": referer})
    data = urllib.request.urlopen(req, timeout=timeout).read()
    if len(data) < 10000:
        return False
    open(out, "wb").write(data); return True

def dl_bili(t, audio):
    url = t["url"]
    if "b23.tv" in url:
        try:
            real = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20).geturl()
        except Exception as e:
            return "fail", "resolve:" + str(e)[:30]
        m = re.search(r'BV[0-9A-Za-z]+', real)
        if not m: return "fail", "noBV"
        vurl = f"https://www.bilibili.com/video/{m.group(0)}"
    else:
        vurl = url
    out = f"{audio}/bili_{t['id']}.%(ext)s"
    try:
        p = subprocess.run([sys.executable, "-m", "yt_dlp", "-x", "--audio-format", "m4a", "--no-playlist",
                            "--user-agent", "Mozilla/5.0", "--referer", "https://www.bilibili.com", "-o", out, vurl],
                           capture_output=True, text=True, timeout=300)
    except Exception as e:
        return "fail", "timeout"
    return ("ok", "") if p.returncode == 0 else ("fail", ((p.stderr or p.stdout or "").strip().splitlines() or ["rc"])[-1][:60])

def dl_xhs_masterurl(t, audio):
    try:
        html = urllib.request.urlopen(urllib.request.Request(t["url"], headers={"User-Agent": UA_M}), timeout=25).read().decode('utf-8', 'ignore')
    except Exception as e:
        return "fail", "page"
    urls = re.findall(r'"masterUrl":"(https?:[^"]+)"', html)
    if not urls: return "fail", "no_masterUrl"
    vu = urls[0].encode().decode('unicode_escape')
    try:
        return ("ok", "") if http_get(vu, f"{audio}/xhs_{t['id']}.mp4") else ("fail", "tiny")
    except Exception:
        return "fail", "cdn"

async def run(targets, audio, xhs_repo, cookie):
    os.makedirs(audio, exist_ok=True)
    results = []
    bili = [t for t in targets if t["src"] == "bilibili"]
    xhs = [t for t in targets if t["src"] == "xhs"]

    # --- Bilibili (threaded yt-dlp) ---
    import concurrent.futures as cf
    def work_b(t):
        if have(audio, t["id"]): return {**t, "status": "skip", "err": ""}
        st, err = dl_bili(t, audio); return {**t, "status": st, "err": err}
    print(f"bilibili: {len(bili)}", flush=True)
    with cf.ThreadPoolExecutor(max_workers=10) as ex:
        results += list(ex.map(work_b, bili))

    # --- Xiaohongshu (XHS-Downloader primary, masterUrl fallback) ---
    XHS = None
    if xhs_repo and os.path.isdir(xhs_repo):
        sys.path.insert(0, xhs_repo)
        try:
            from source import XHS as _XHS; XHS = _XHS
        except Exception as e:
            print(f"WARN: XHS-Downloader import failed ({e}); using masterUrl only", flush=True)
    print(f"xhs: {len(xhs)} (XHS-Downloader={'on' if XHS else 'off'})", flush=True)
    if XHS:
        async with XHS(download_record=False, record_data=False, cookie=cookie or "") as xhs_api:
            for i, t in enumerate(xhs):
                if have(audio, t["id"]):
                    results.append({**t, "status": "skip", "err": ""}); continue
                st, err = "?", ""
                try:
                    d = await xhs_api.extract(t["url"], False)
                    d = d[0] if isinstance(d, list) and d else d
                    urls = (d or {}).get("下载地址") or []
                    if urls and http_get(urls[0], f"{audio}/xhs_{t['id']}.mp4"):
                        st = "ok"
                    else:
                        st, err = dl_xhs_masterurl(t, audio)  # fallback
                except Exception:
                    st, err = dl_xhs_masterurl(t, audio)
                results.append({**t, "status": st, "err": err})
                if (i + 1) % 20 == 0: print(f"  xhs {i+1}/{len(xhs)}", flush=True)
    else:
        for t in xhs:
            if have(audio, t["id"]): results.append({**t, "status": "skip", "err": ""}); continue
            st, err = dl_xhs_masterurl(t, audio); results.append({**t, "status": st, "err": err})

    json.dump(results, open("download_manifest.json", "w"), ensure_ascii=False, indent=0)
    print("DONE", dict(Counter(f"{r['src']}:{r['status']}" for r in results)), flush=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", required=True)
    ap.add_argument("--out", default="./audio")
    ap.add_argument("--xhs-repo", default=os.path.expanduser("~/.cache/XHS-Downloader"),
                    help="path to a cloned JoeanAmier/XHS-Downloader repo (py3.12). If missing, XHS falls back to masterUrl.")
    ap.add_argument("--cookie", default="", help="optional Xiaohongshu web cookie (raises success rate / resolution)")
    a = ap.parse_args()
    targets = json.load(open(a.targets))
    asyncio.run(run(targets, a.out, a.xhs_repo, a.cookie))

if __name__ == "__main__":
    main()
