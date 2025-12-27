#!/usr/bin/env python3
"""
Condense consecutive plain lines into single-line paragraphs in Markdown files.

Usage:
  python scripts\misc\condense_paragraphs.py PATH

If PATH is a file, process that file. If PATH is a directory, recursively process
all files with the .md extension beneath it.

Behavior:
- Consecutive non-blank lines that are not list items, headings, blockquotes,
  code fences, table rows, or indented code will be combined into one line.
- List items (starting with -, +, *, or numbered lists like "1. ") are left
  alone and will cause paragraph boundaries.
- Code fences (```), HTML blocks, and lines starting with 4+ spaces are
  preserved as-is.
- The script overwrites files in-place. No backups are made by default.
"""

from __future__ import annotations

import sys
import re
from pathlib import Path
from typing import Iterable

LIST_RE = re.compile(r"^\s*(?:[-+*]|\d+\.)\s+")
HEADING_RE = re.compile(r"^\s*#{1,6}\s+")
BLOCKQUOTE_RE = re.compile(r"^\s*>\s+")
TABLE_LINE_RE = re.compile(r"^\s*\|.+\|\s*$")
CODE_FENCE_RE = re.compile(r"^\s*```")
INDENTED_CODE_RE = re.compile(r"^(?:\s{4,})")
HTML_BLOCK_START_RE = re.compile(r"^\s*<([a-zA-Z]+)(\s|>)")


def find_md_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        yield root
        return
    for p in root.rglob("*.md"):
        if p.is_file():
            yield p


def should_treat_as_plain(line: str, in_code_fence: bool) -> bool:
    """Return True if the line should be considered part of a plain paragraph.

    We exclude lines that look like lists, headings, blockquotes, table rows,
    code fences, indented code, or HTML block starts.
    """
    if in_code_fence:
        return False
    if line.strip() == "":
        return False
    if CODE_FENCE_RE.match(line):
        return False
    if LIST_RE.match(line):
        return False
    if HEADING_RE.match(line):
        return False
    if BLOCKQUOTE_RE.match(line):
        return False
    if TABLE_LINE_RE.match(line):
        return False
    if INDENTED_CODE_RE.match(line):
        return False
    if HTML_BLOCK_START_RE.match(line):
        return False
    return True


def condense_text(text: str) -> str:
    lines = text.replace('\r\n', '\n').split('\n')

    out_lines: list[str] = []
    para_buf: list[str] = []
    in_code_fence = False

    def flush_para():
        nonlocal para_buf
        if not para_buf:
            return
        # Join buffer with single spaces, collapsing extra spaces
        joined = ' '.join(s.strip() for s in para_buf)
        out_lines.append(joined)
        para_buf = []

    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        # detect code fence toggling
        if CODE_FENCE_RE.match(ln):
            # Flush any pending paragraph before entering code fence
            flush_para()
            # Write fence line and copy until closing fence
            out_lines.append(ln)
            i += 1
            # If this fence opens a code block, copy until closing fence or EOF
            while i < n:
                out_lines.append(lines[i])
                if CODE_FENCE_RE.match(lines[i]):
                    i += 1
                    break
                i += 1
            continue

        # HTML block: treat as non-plain - flush and copy the line
        if HTML_BLOCK_START_RE.match(ln):
            flush_para()
            out_lines.append(ln)
            i += 1
            continue

        if ln.strip() == "":
            # blank line: paragraph separator
            flush_para()
            out_lines.append("")
            i += 1
            continue

        if not should_treat_as_plain(ln, in_code_fence=False):
            # Non-plain line: flush current paragraph then append the line as-is
            flush_para()
            out_lines.append(ln)
            i += 1
            continue

        # Plain line -> accumulate
        para_buf.append(ln)
        i += 1
        # Continue collecting until a non-plain or blank occurs

    # End while
    flush_para()

    # Ensure file ends with a single trailing newline
    result = '\n'.join(out_lines).rstrip() + '\n'
    return result


def process_file(path: Path) -> None:
    try:
        orig = path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Failed to read {path}: {e}")
        return
    new = condense_text(orig)
    if new != orig:
        try:
            path.write_text(new, encoding='utf-8')
            print(f"Condensed: {path}")
        except Exception as e:
            print(f"Failed to write {path}: {e}")
    else:
        print(f"No changes: {path}")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python scripts\\misc\\condense_paragraphs.py PATH")
        return 2
    target = Path(argv[1])
    if not target.exists():
        print(f"Path not found: {target}")
        return 3

    files = list(find_md_files(target))
    if not files:
        print("No markdown files found")
        return 0

    for f in files:
        process_file(f)

    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
