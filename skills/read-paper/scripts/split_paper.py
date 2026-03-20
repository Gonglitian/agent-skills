#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Analyze paper length and split into chunks for parallel subagent processing.

Usage:
    uv run split_paper.py <paper_text_path> [--output-dir <dir>] [--target-words 6000] [--threshold 12000]

Short papers (< threshold): outputs strategy="standard", no splitting.
Long papers (>= threshold): splits at heading boundaries into N chunks + overview extract.

Supports multiple heading formats commonly found in arxiv-converted markdown:
  - Standard markdown: # Heading, ## Heading
  - Bold numbered: **1** **INTRODUCTION**, **2.1** **Background**
  - Numbered plain: 1 Introduction, 1. Introduction
  - ALL CAPS on own line: INTRODUCTION, RELATED WORK

Falls back to paragraph-boundary splitting when headings are sparse.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def count_words(text: str) -> int:
    """Count words, handling mixed CJK + Latin text."""
    cjk_count = len(re.findall(r"[\u4e00-\u9fff\u3000-\u303f]", text))
    latin_text = re.sub(r"[\u4e00-\u9fff\u3000-\u303f]", " ", text)
    latin_count = len(latin_text.split())
    return cjk_count + latin_count


# Heading detection patterns (ordered by priority)
HEADING_PATTERNS = [
    # Standard markdown: # Title, ## Title, ### Title
    (re.compile(r"^(#{1,3})\s+(.+)$"), lambda m: (len(m.group(1)), m.group(2).strip())),
    # Bold numbered sections: **1** **INTRODUCTION**, **2.1** **GLOBAL** **SOLVER** **1:**...
    # Captures full line after the number, strips all ** markers
    (
        re.compile(r"^\*\*(\d+(?:\.\d+)?)\*\*\s+\*\*(.+)$"),
        lambda m: (1 if "." not in m.group(1) else 2, f"{m.group(1)} {re.sub(r'[*]+', '', m.group(2)).strip()}"),
    ),
    # Numbered plain: 1 Introduction, 1. Introduction, 2.1 Background
    (
        re.compile(r"^(\d+(?:\.\d+)?)[.\s]+([A-Z][A-Za-z\s:,&-]{3,})$"),
        lambda m: (1 if "." not in m.group(1) else 2, f"{m.group(1)} {m.group(2).strip()}"),
    ),
]


def strip_references(text: str) -> tuple[str, int]:
    """Remove the references/bibliography section from the end of the paper.

    Returns (text_without_refs, removed_word_count).
    References are typically 30-60% of a survey paper's raw text but contain
    no useful information for summarization.
    """
    # Common reference section headers
    ref_patterns = [
        r"^#{1,3}\s+(?:References|Bibliography|REFERENCES|BIBLIOGRAPHY)",
        r"^\*\*(?:References|REFERENCES|Bibliography)\*\*",
        r"^(?:References|REFERENCES|Bibliography)\s*$",
    ]
    combined = re.compile("|".join(ref_patterns), re.MULTILINE)
    match = combined.search(text)

    if match:
        before = text[: match.start()]
        removed = text[match.start() :]
        return before.rstrip(), count_words(removed)

    # Heuristic: detect dense citation blocks at end (e.g. "[123] A. Author...")
    lines = text.split("\n")
    citation_start = None
    citation_density = 0
    window = 20

    for i in range(len(lines) - 1, max(len(lines) - 500, -1), -1):
        if re.match(r"^\s*\[?\d{1,4}\]?\s", lines[i]):
            citation_density += 1
        if i <= len(lines) - window and citation_density > window * 0.5:
            citation_start = i
            break

    if citation_start and citation_start < len(lines) - 30:
        before = "\n".join(lines[:citation_start])
        removed = "\n".join(lines[citation_start:])
        return before.rstrip(), count_words(removed)

    return text, 0


def detect_heading(line: str) -> tuple[int, str] | None:
    """Try to parse a line as a section heading.

    Returns (level, heading_text) or None.
    """
    stripped = line.strip()
    if not stripped or len(stripped) > 200:
        return None

    for pattern, extractor in HEADING_PATTERNS:
        m = pattern.match(stripped)
        if m:
            level, text = extractor(m)
            # Filter out false positives: headings that are just numbers
            clean = re.sub(r"[\d.*#\s]", "", text)
            if len(clean) >= 2:
                return (level, text)
    return None


def find_sections(text: str) -> list[dict]:
    """Split text into sections by detected headings."""
    lines = text.split("\n")
    sections = []
    current_heading = "(preamble)"
    current_lines: list[str] = []
    current_level = 0

    for line in lines:
        result = detect_heading(line)
        if result:
            level, heading = result
            if current_lines:
                content = "\n".join(current_lines)
                sections.append(
                    {
                        "heading": current_heading,
                        "level": current_level,
                        "text": content,
                        "words": count_words(content),
                    }
                )
            current_heading = heading
            current_level = level
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        content = "\n".join(current_lines)
        sections.append(
            {
                "heading": current_heading,
                "level": current_level,
                "text": content,
                "words": count_words(content),
            }
        )

    return sections


def split_by_paragraphs(text: str, target_words: int) -> list[dict]:
    """Fallback: split text into chunks at paragraph boundaries (double newline).

    Used when heading detection finds too few sections to split meaningfully.
    """
    paragraphs = re.split(r"\n\s*\n", text)
    sections = []
    current_lines: list[str] = []
    current_words = 0

    for para in paragraphs:
        para_words = count_words(para)
        if current_words > 0 and current_words + para_words > target_words:
            content = "\n\n".join(current_lines)
            sections.append(
                {
                    "heading": f"(segment {len(sections) + 1})",
                    "level": 0,
                    "text": content,
                    "words": current_words,
                }
            )
            current_lines = []
            current_words = 0
        current_lines.append(para)
        current_words += para_words

    if current_lines:
        content = "\n\n".join(current_lines)
        sections.append(
            {
                "heading": f"(segment {len(sections) + 1})",
                "level": 0,
                "text": content,
                "words": current_words,
            }
        )

    return sections


def extract_overview(sections: list[dict], full_text: str) -> str:
    """Extract abstract + introduction + conclusion for high-level analysis."""
    parts = []

    # Abstract
    for sec in sections:
        h = sec["heading"].lower()
        if "abstract" in h or "(preamble)" in h:
            # Preamble often contains abstract for non-standard formats
            text = sec["text"]
            # Try to extract just the abstract portion
            abs_match = re.search(
                r"(?:abstract|Abstract|ABSTRACT)[^a-zA-Z]*[—:\s]*(.*?)(?=\n\s*\n\s*(?:\*\*|#|\d+[.\s]))",
                text,
                re.DOTALL,
            )
            if abs_match and len(abs_match.group(1).strip()) > 100:
                parts.append(abs_match.group(1).strip())
            else:
                parts.append(text[:3000])  # First 3000 chars of preamble
            break

    # Introduction
    for sec in sections:
        h = sec["heading"].lower()
        if "introduction" in h or re.match(r"^1[\s.]", sec["heading"]):
            parts.append(sec["text"])
            break

    # Conclusion / Discussion (search from end)
    for sec in reversed(sections):
        h = sec["heading"].lower()
        if any(kw in h for kw in ["conclusion", "discussion", "summary", "limitation", "future"]):
            parts.append(sec["text"])
            break

    if not parts:
        # Fallback: first and last 2000 words
        words = full_text.split()
        first = " ".join(words[:2000])
        last = " ".join(words[-2000:])
        return f"{first}\n\n---\n\n{last}"

    return "\n\n---\n\n".join(parts)


def merge_into_chunks(sections: list[dict], target_words: int) -> list[list[dict]]:
    """Group consecutive sections into chunks of ~target_words."""
    chunks: list[list[dict]] = []
    current: list[dict] = []
    current_words = 0

    for sec in sections:
        if current_words > 0 and current_words + sec["words"] > target_words * 1.3:
            chunks.append(current)
            current = []
            current_words = 0

        current.append(sec)
        current_words += sec["words"]

    if current:
        chunks.append(current)

    # Merge very small trailing chunks
    while len(chunks) > 1 and sum(s["words"] for s in chunks[-1]) < target_words * 0.3:
        last = chunks.pop()
        chunks[-1].extend(last)

    return chunks


def main():
    parser = argparse.ArgumentParser(description="Split paper for parallel subagent processing")
    parser.add_argument("paper_path", help="Path to paper text (markdown)")
    parser.add_argument("--output-dir", "-o", help="Directory for chunk files")
    parser.add_argument("--target-words", type=int, default=6000, help="Target words per chunk (default: 6000)")
    parser.add_argument("--threshold", type=int, default=12000, help="Min words to trigger splitting (default: 12000)")
    args = parser.parse_args()

    paper_path = Path(args.paper_path)
    if not paper_path.exists():
        print(f"Error: File not found: {paper_path}", file=sys.stderr)
        sys.exit(1)

    text = paper_path.read_text(encoding="utf-8")

    # Strip references section — often 30-60% of survey papers
    text_clean, refs_words = strip_references(text)
    if refs_words > 0:
        print(f"Stripped references section ({refs_words} words)", file=sys.stderr)

    total_words = count_words(text_clean)

    if total_words < args.threshold:
        result = {
            "strategy": "standard",
            "total_words": total_words,
            "total_words_with_refs": total_words + refs_words,
            "refs_stripped_words": refs_words,
            "num_chunks": 0,
            "message": f"Paper is {total_words} words (< {args.threshold}). Use standard 2-subagent pipeline.",
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    # Long paper: detect sections
    sections = find_sections(text_clean)

    # If heading detection yielded too few sections, fall back to paragraph splitting
    non_preamble = [s for s in sections if s["heading"] != "(preamble)"]
    if len(non_preamble) < 3:
        print(
            f"Few headings detected ({len(non_preamble)}), using paragraph-boundary splitting",
            file=sys.stderr,
        )
        sections = split_by_paragraphs(text, args.target_words)

    overview_text = extract_overview(sections, text_clean)
    chunks = merge_into_chunks(sections, args.target_words)

    output_dir = Path(args.output_dir) if args.output_dir else paper_path.parent / "chunks"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write overview
    overview_path = output_dir / "overview.md"
    overview_path.write_text(overview_text, encoding="utf-8")

    # Write chunks
    chunk_info = []
    for i, chunk_sections in enumerate(chunks):
        chunk_text = "\n\n".join(sec["text"] for sec in chunk_sections)
        chunk_path = output_dir / f"chunk_{i}.md"
        chunk_path.write_text(chunk_text, encoding="utf-8")

        chunk_info.append(
            {
                "id": i,
                "path": str(chunk_path),
                "words": sum(sec["words"] for sec in chunk_sections),
                "headings": [sec["heading"] for sec in chunk_sections],
            }
        )

    result = {
        "strategy": "dynamic",
        "total_words": total_words,
        "total_words_with_refs": total_words + refs_words,
        "refs_stripped_words": refs_words,
        "num_chunks": len(chunks),
        "target_words_per_chunk": args.target_words,
        "overview_path": str(overview_path),
        "overview_words": count_words(overview_text),
        "chunks": chunk_info,
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
