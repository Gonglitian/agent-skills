#!/usr/bin/env python3
"""Extract a COMPLETE figure from a PDF page (no cropping of figure content).

Run with: uv run --with pymupdf python extract_full_figure.py <pdf> [opts]

Strategy: locate the figure's caption ("Figure N" / "Fig. N") to find its page,
then bound the figure as the union of all vector-drawing + raster-image rects on
that page that sit ABOVE the caption (caption is normally below the figure).
Crop with padding at high DPI. Nothing inside the figure is cut.

Options:
  --find "Figure 2"   find page by caption text, isolate the figure above caption
  --page N            (1-indexed) force a page; bound all drawings/images on it
  --clip top|bottom|full   restrict region when using --page (default full)
  --fullpage          just render the whole page (fallback)
  --output out.png    output path (default <pdf>_figN.png)
  --dpi 220           render DPI (default 220)
  --pad 14            padding in PDF points around the bbox (default 14)
"""
import argparse, sys, re
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--find", default=None, help='caption label e.g. "Figure 2"')
    ap.add_argument("--page", type=int, default=None, help="1-indexed page")
    ap.add_argument("--clip", default="full", choices=["top", "bottom", "full"])
    ap.add_argument("--fullpage", action="store_true")
    ap.add_argument("--output", default=None)
    ap.add_argument("--dpi", type=int, default=220)
    ap.add_argument("--pad", type=float, default=14.0)
    a = ap.parse_args()

    import fitz  # pymupdf
    doc = fitz.open(a.pdf)
    npages = len(doc)

    def rects_on(page, ymax=None, ymin=None):
        R = page.rect
        out = []
        for d in page.get_drawings():
            r = d["rect"]
            if r.is_empty or r.width < 4 or r.height < 4:
                continue
            if r.width * r.height > 0.95 * R.width * R.height:
                continue  # page-background rect
            out.append(fitz.Rect(r))
        for img in page.get_images(full=True):
            try:
                for r in page.get_image_rects(img[0]):
                    if r.width >= 4 and r.height >= 4:
                        out.append(fitz.Rect(r))
            except Exception:
                pass
        if ymax is not None:
            out = [r for r in out if r.y1 <= ymax + 6]
        if ymin is not None:
            out = [r for r in out if r.y0 >= ymin - 6]
        return out

    def union(rects):
        if not rects:
            return None
        b = fitz.Rect(rects[0])
        for r in rects[1:]:
            b |= r
        return b

    page = None
    bbox = None

    if a.fullpage:
        page = doc[(a.page or 1) - 1]
        bbox = page.rect

    elif a.find:
        m = re.match(r"\s*(Figure|Fig\.?)\s*([0-9]+)", a.find, re.I)
        label_num = m.group(2) if m else None
        pat = re.compile(r"^\s*(Figure|Fig\.?)\s*" + re.escape(label_num or "") + r"\b", re.I)
        cap = None
        for pno in range(npages):
            p = doc[pno]
            for blk in p.get_text("blocks"):
                txt = blk[4].strip()
                if pat.match(txt):
                    cap = (pno, fitz.Rect(blk[:4]))
                    break
            if cap:
                break
        if not cap:
            print(f"WARN: caption '{a.find}' not found; falling back to fullpage page {a.page or 1}", file=sys.stderr)
            page = doc[(a.page or 1) - 1]
            bbox = page.rect
        else:
            pno, caprect = cap
            page = doc[pno]
            above = rects_on(page, ymax=caprect.y0)
            bbox = union(above)
            if bbox is None:  # caption above figure
                bbox = union(rects_on(page, ymin=caprect.y1))
            if bbox is None:
                bbox = page.rect
            print(f"found '{a.find}' caption on page {pno+1}; figure bbox={tuple(round(x,1) for x in bbox)}", file=sys.stderr)
    else:
        if a.page is None:
            print("ERROR: need --find, --page, or --fullpage", file=sys.stderr)
            sys.exit(2)
        page = doc[a.page - 1]
        R = page.rect
        ymax = ymin = None
        if a.clip == "top":
            ymax = R.height / 2
        elif a.clip == "bottom":
            ymin = R.height / 2
        bbox = union(rects_on(page, ymax=ymax, ymin=ymin)) or R

    # pad + clamp
    bbox = fitz.Rect(bbox.x0 - a.pad, bbox.y0 - a.pad, bbox.x1 + a.pad, bbox.y1 + a.pad)
    bbox &= page.rect

    out = a.output or f"{Path(a.pdf).stem}_fig.png"
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    pix = page.get_pixmap(matrix=fitz.Matrix(a.dpi / 72, a.dpi / 72), clip=bbox)
    pix.save(out)
    print(f"OK {out}  {pix.width}x{pix.height}px  (page {page.number+1}/{npages})")

if __name__ == "__main__":
    main()
