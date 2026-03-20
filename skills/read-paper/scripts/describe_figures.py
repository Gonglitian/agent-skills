#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "openai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Use SiliconFlow VLM API to describe paper figures.

Usage:
    uv run describe_figures.py <figures_dir> [--output <output.json>] [--api-key <key>] [--model <model>] [--max-figures 12]

Reads all PNG/JPG images from a directory, sends each to a VLM for description,
and outputs structured JSON with figure descriptions.

Environment:
    SILICONFLOW_API_KEY - API key (or pass via --api-key)
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path

from openai import OpenAI
from PIL import Image
import io


FIGURE_PROMPT = """你是一个学术论文图片分析专家。请仔细分析这张来自学术论文的图片，给出结构化描述。

请用以下格式回答（中文）：

**类型**: (架构图 / 流程图 / 实验结果图 / 对比图 / 示意图 / 表格截图 / 算法伪代码 / 其他)
**内容描述**: (详细描述图中展示的内容，包括各个组件、箭头流向、标签文字等)
**关键信息**: (提取图中的关键数据点、趋势、对比结论等定量或定性信息)
**论文位置推测**: (推测此图可能对应论文的哪个部分：方法/实验/架构/数据 等)

请尽量详细、准确，保留图中可见的所有文字和数据。"""


def image_to_base64(image_path: str) -> tuple[str, str]:
    """Convert image to base64 webp for API transmission."""
    with Image.open(image_path) as img:
        # Convert to RGB if necessary (handle RGBA, palette, etc.)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # Resize if too large (save tokens/bandwidth)
        max_dim = 2048
        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return b64, "image/webp"


def describe_figure(client: OpenAI, model: str, image_path: str) -> str:
    """Send a single figure to VLM and get description."""
    b64_data, mime_type = image_to_base64(image_path)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{b64_data}",
                            "detail": "high",
                        },
                    },
                    {
                        "type": "text",
                        "text": FIGURE_PROMPT,
                    },
                ],
            }
        ],
        max_tokens=1024,
        temperature=0.2,
    )

    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="Describe paper figures via VLM")
    parser.add_argument("figures_dir", help="Directory containing extracted figures")
    parser.add_argument("--output", "-o", help="Output JSON path (default: stdout)")
    parser.add_argument("--api-key", help="SiliconFlow API key (or set SILICONFLOW_API_KEY)")
    parser.add_argument(
        "--model",
        default="Qwen/Qwen2.5-VL-72B-Instruct",
        help="VLM model to use",
    )
    parser.add_argument(
        "--max-figures",
        type=int,
        default=12,
        help="Max number of figures to process (largest first)",
    )
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("SILICONFLOW_API_KEY")
    if not api_key:
        print("Error: No API key. Set SILICONFLOW_API_KEY or pass --api-key", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.siliconflow.cn/v1",
    )

    figures_dir = Path(args.figures_dir)
    if not figures_dir.exists():
        print(f"Error: Directory not found: {figures_dir}", file=sys.stderr)
        sys.exit(1)

    # Collect image files
    image_files = []
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        image_files.extend(figures_dir.glob(ext))

    if not image_files:
        print(f"No images found in {figures_dir}", file=sys.stderr)
        result = {"figures_dir": str(figures_dir), "count": 0, "descriptions": []}
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    # Sort by file size (larger = likely more important figures), take top N
    image_files.sort(key=lambda f: f.stat().st_size, reverse=True)
    image_files = image_files[: args.max_figures]
    # Re-sort by filename for consistent ordering
    image_files.sort(key=lambda f: f.name)

    descriptions = []
    for i, img_path in enumerate(image_files):
        print(
            f"[{i + 1}/{len(image_files)}] Describing {img_path.name}...",
            file=sys.stderr,
        )
        try:
            desc = describe_figure(client, args.model, str(img_path))
            descriptions.append(
                {
                    "filename": img_path.name,
                    "path": str(img_path),
                    "description": desc,
                }
            )
        except Exception as e:
            print(f"  Error: {e}", file=sys.stderr)
            descriptions.append(
                {
                    "filename": img_path.name,
                    "path": str(img_path),
                    "description": f"[Error: {e}]",
                }
            )

    result = {
        "figures_dir": str(figures_dir),
        "model": args.model,
        "count": len(descriptions),
        "descriptions": descriptions,
    }

    output_json = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output_json)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
