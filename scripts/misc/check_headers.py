#!/usr/bin/env python3
import re
import sys
import unicodedata
from pathlib import Path

HEADER_RE = re.compile(r'^(#{1,6})\s+(.*)$')
EXPLICIT_ID_RE = re.compile(r'\{#([A-Za-z0-9_:.-]+)\}')


def slugify(text: str) -> str:
    text = re.sub(r'\{#[-_:.A-Za-z0-9]+\}', '', text)
    text = text.strip()
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def iter_headers(path: Path):
    try:
        text = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        text = path.read_text(encoding='latin-1')

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = HEADER_RE.match(line)
        if m:
            content = m.group(2).strip()
            explicit = EXPLICIT_ID_RE.search(content)
            hid = explicit.group(1) if explicit else slugify(content)
            yield hid, path, i + 1, content
            i += 1
            continue

        if i + 1 < len(lines) and re.match(r'^(-{3,}|={3,})\s*$', lines[i + 1]):
            content = line.strip()
            explicit = EXPLICIT_ID_RE.search(content)
            hid = explicit.group(1) if explicit else slugify(content)
            yield hid, path, i + 1, content
            i += 2
            continue

        i += 1


def main():
    if len(sys.argv) != 2:
        print('Usage: python scripts/misc/check_headers.py <book-folder>')
        print('Example: python scripts/misc/check_headers.py number-go-up')
        raise SystemExit(1)

    book_folder = sys.argv[1]
    root = Path('external') / book_folder
    if not root.exists():
        print(f'Folder not found: {root}')
        raise SystemExit(1)

    seen = {}
    duplicate_ids = {}

    for md_file in sorted(root.rglob('*.md')):
        if 'raw' in md_file.parts:
            # raw/ is historical and not part of the build, but we keep the script simple
            continue
        if 'README.md' in md_file.name:
            # README.md is not part of the build, but we keep the script simple
            continue
        for hid, path, line_no, title in iter_headers(md_file):
            if not hid:
                continue
            seen.setdefault(hid, []).append((str(path), line_no, title))

    for hid, entries in sorted(seen.items()):
        if len(entries) > 1:
            duplicate_ids[hid] = entries

    if not duplicate_ids:
        print(f'No duplicate header ids found under {root}')
        return

    print(f'Duplicate header ids found under {root}:')
    for hid, entries in sorted(duplicate_ids.items()):
        print(f'\nID: {hid} ({len(entries)} occurrences)')
        for path, line_no, title in entries:
            print(f'  - {path}:{line_no}: {title}')


if __name__ == '__main__':
    main()
