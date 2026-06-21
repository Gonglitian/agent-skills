# Asset Pipeline (figures, GIFs, video for academic decks)

How to prepare real media for a research deck: paper-figure crops, simulator/2D-render GIFs, and real-world footage. Recipes assume `ffmpeg` + `pdftoppm` (poppler) are available.

## Directory layout

```
deck/
  materials/          # raw inputs, centralized (PDFs, source videos, original renders) — not served
  public/figs/        # cropped paper figures (PNG)        → referenced as /figs/foo.png
  public/media/       # slide GIFs + looping MP4s          → referenced as /media/foo.gif|mp4
  slides.md  style.css  vite.config.ts
```

Keep originals in `materials/`; only put final, sized assets in `public/`. (See `slidev-gotchas.md` #3 for the Slidev-52 `vite.config.ts` needed when referencing `public/` via absolute URLs.)

## GIF vs MP4 — choose by content

- **Synthetic / 2D-sim / screen renders** (flat colors, text overlays) → **optimized GIF**. Crisp, loops natively in `<img>`, small.
- **Real-world / photographic footage** → **looping muted MP4**. GIF is a terrible codec for camera video (a 13 s clip is ~6 MB as GIF, ~0.5 MB as H.264). Embed with `<video autoplay loop muted playsinline src="/media/x.mp4">`.

## GIF: two-pass palette (high quality, small)

`palettegen` + `paletteuse` beats single-pass. **ffmpeg 8.x quirk:** the palette output needs `-update 1 -frames:v 1` or pass-1 silently writes nothing and the GIF never appears.

```bash
F="crop=W:H:X:Y,setpts=0.5*PTS,fps=12,scale=500:-1:flags=lanczos"   # crop/speed/scale as needed
ffmpeg -y -i in.gif -vf "$F,palettegen=max_colors=220:stats_mode=diff" \
       -update 1 -frames:v 1 /tmp/pal.png
ffmpeg -y -i in.gif -i /tmp/pal.png \
       -lavfi "$F [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=3" out.gif
```

- `setpts=0.5*PTS` = 2× speed (long sim rollouts loop better short).
- Trim a source video into a GIF window with `-ss <start> -t <dur>` before `-i`.

## Looping muted MP4 for slides

```bash
ffmpeg -y -ss 206 -t 14 -i source.mp4 -an \
  -vf "crop=W:H:X:Y,scale=760:-2" \
  -c:v libx264 -crf 24 -preset slow -pix_fmt yuv420p -movflags +faststart out.mp4
```

`-pix_fmt yuv420p` + `+faststart` = plays in every browser; `-an` drops audio.

## Paper-figure extraction (iterative crop)

PDF figures are cleaner re-rendered + cropped than screenshotted.

```bash
pdftoppm -png -r 200 -f 3 -l 3 paper.pdf /tmp/p   # render page 3 @200dpi → /tmp/p-03.png (1700×2200 for US-letter)
ffmpeg -y -i /tmp/p-03.png -vf "crop=1500:620:100:112" figs/fig2.png   # crop=w:h:x:y
```

Loop: render → **view the PNG with the Read tool** → crop → **view the crop** → adjust x/y/w/h. Figures usually sit in the top band; the caption is just below — crop it out and write your own. Expect 2–3 crop iterations per figure; verify visually, don't guess coordinates once.

## Verify media before shipping

- `ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 file` → dimensions.
- Extract and **view the first frame** of every GIF/MP4 — exports show only frame 0 (`slidev-gotchas.md` #4). Crop off any stray title bar / wrong-project label / transition so frame 0 is representative.
