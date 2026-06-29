#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pymupdf>=1.24.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Extract figures from a PDF paper.

Usage:
    uv run extract_figures.py <pdf_path> [--output-dir <dir>] [--min-size 150] [--format png]

Extracts embedded images from a PDF that are likely paper figures (filters out
tiny icons, logos, and decorative elements by size threshold).

Output:
    - Saves images to <output_dir>/fig_<page>_<idx>.<format>
    - Prints JSON metadata to stdout for each extracted figure
"""

import argparse
import json
import sys
from pathlib import Path

import fitz  # pymupdf


def extract_figures(
    pdf_path: str,
    output_dir: str | None = None,
    min_size: int = 150,
    fmt: str = "png",
) -> list[dict]:
    """Extract figures from PDF, filtering by minimum dimension."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"Error: PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    if output_dir is None:
        output_dir = pdf_path.parent / f"{pdf_path.stem}_figures"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    figures = []
    seen_xrefs = set()

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_idx, img_info in enumerate(image_list):
            xref = img_info[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            try:
                base_image = doc.extract_image(xref)
            except Exception:
                continue

            if not base_image:
                continue

            width = base_image["width"]
            height = base_image["height"]

            # Filter out small images (icons, logos, bullets)
            if width < min_size and height < min_size:
                continue

            # Filter out very narrow images (likely decorative lines)
            aspect = max(width, height) / max(min(width, height), 1)
            if aspect > 15:
                continue

            image_bytes = base_image["image"]
            img_ext = base_image.get("ext", fmt)

            filename = f"fig_p{page_num + 1}_{img_idx}.{img_ext}"
            filepath = output_dir / filename

            with open(filepath, "wb") as f:
                f.write(image_bytes)

            # Convert to PNG if needed (for consistent VLM input)
            if img_ext != fmt and fmt == "png":
                from PIL import Image
                import io

                try:
                    img = Image.open(io.BytesIO(image_bytes))
                    png_filename = f"fig_p{page_num + 1}_{img_idx}.png"
                    png_filepath = output_dir / png_filename
                    img.save(str(png_filepath), "PNG")
                    filepath.unlink()  # remove original
                    filepath = png_filepath
                    filename = png_filename
                except Exception:
                    pass  # keep original format

            fig_meta = {
                "filename": filename,
                "path": str(filepath),
                "page": page_num + 1,
                "width": width,
                "height": height,
                "area": width * height,
            }
            figures.append(fig_meta)

    doc.close()

    # Sort by page then by area (larger figures first within same page)
    figures.sort(key=lambda f: (f["page"], -f["area"]))

    return figures


def main():
    parser = argparse.ArgumentParser(description="Extract figures from PDF")
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("--output-dir", "-o", help="Output directory for figures")
    parser.add_argument(
        "--min-size",
        type=int,
        default=150,
        help="Minimum width/height to keep (default: 150px)",
    )
    parser.add_argument("--format", default="png", choices=["png", "jpg"])
    args = parser.parse_args()

    figures = extract_figures(args.pdf_path, args.output_dir, args.min_size, args.format)

    result = {
        "pdf": args.pdf_path,
        "output_dir": str(
            Path(args.output_dir)
            if args.output_dir
            else Path(args.pdf_path).parent / f"{Path(args.pdf_path).stem}_figures"
        ),
        "count": len(figures),
        "figures": figures,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
