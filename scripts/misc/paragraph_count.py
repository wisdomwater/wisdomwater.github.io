#!/usr/bin/env python3
"""
Count paragraphs in markdown files.

Usage:
    python scripts\misc\paragraph_count.py PATH

If PATH is a file, count paragraphs in that file. If PATH is a directory, recurse
and count paragraphs for all *.md files beneath it.

A paragraph is defined as a contiguous block of non-blank lines separated by
one or more blank (whitespace-only) lines.

Output format (aligned):
    <count> <filename>

The script prints one line per processed file. Returns exit code 0 on success.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, List, Tuple


def find_md_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        yield root
        return
    for p in root.rglob("*.md"):
        if p.is_file():
            yield p


def count_paragraphs(text: str) -> int:
    lines = text.replace('\r\n', '\n').split('\n')
    count = 0
    in_para = False
    for ln in lines:
        if ln.strip() == "":
            in_para = False
            continue
        if not in_para:
            count += 1
            in_para = True
    return count


def process_path(path: Path) -> List[Tuple[int, Path]]:
    results: List[Tuple[int, Path]] = []
    for f in find_md_files(path):
        try:
            text = f.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Failed to read {f}: {e}", file=sys.stderr)
            continue
        cnt = count_paragraphs(text)
        results.append((cnt, f))
    return results


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python scripts\\misc\\paragraph_count.py PATH")
        return 2
    target = Path(argv[1])
    if not target.exists():
        print(f"Path not found: {target}")
        return 3

    results = process_path(target)
    if not results:
        print("No markdown files found.")
        return 0

    # Determine width for count column
    max_count = max(cnt for cnt, _ in results)
    width = max(2, len(str(max_count)))

    # Sort by filename for consistent output
    results.sort(key=lambda t: str(t[1]))

    for cnt, f in results:
        # Print relative path from cwd for readability
        try:
            rel = f.relative_to(Path.cwd())
        except Exception:
            rel = f
        print(f"{str(cnt).rjust(width)} {rel}")

    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
