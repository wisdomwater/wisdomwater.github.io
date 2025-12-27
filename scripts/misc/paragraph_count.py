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

import argparse
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


def parse_args(argv: list[str]) -> argparse.Namespace:
    def parse_args(argv: list[str]) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Count paragraphs in markdown files.")
        parser.add_argument("path", help="File or directory to process")
        parser.add_argument(
            "--below",
            type=int,
            metavar="N",
            help="Only show files with paragraph count <= N",
        )
        parser.add_argument(
            "--above",
            type=int,
            metavar="N",
            help="Only show files with paragraph count >= N",
        )
        parser.add_argument(
            "--sort",
            choices=("asc", "desc", "file"),
            default="file",
            help="Sort by count (asc, desc) or by file. Default: file",
        )
        return parser.parse_args(argv[1:])


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    target = Path(args.path)
    if not target.exists():
        print(f"Path not found: {target}")
        return 3

    results = process_path(target)
    if not results:
        print("No markdown files found.")
        return 0

    # Remove values outside the limits
    if args.above:
        results = [x for x in results if int(x[0]) >= int(args.above)]
    if args.below:
        results = [x for x in results if int(x[0]) <= int(args.above)]

    # Determine width for count column
    max_count = max(cnt for cnt, _ in results)
    width = max(2, len(str(max_count)))

    # Sort by filename for consistent output
    def sort_by(t):
        sort_value = args.sort
        if sort_value == "file":
            return str(t[1])
        if sort_value == "asc":
            return int(t[0])
        if sort_value == "desc":
            return int(t[0]) * (-1)
        raise ValueError(f"Unknow sort value '{sort_value}'") 
    results.sort(key=sort_by)

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
