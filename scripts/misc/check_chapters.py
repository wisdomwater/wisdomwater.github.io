#!/usr/bin/env python3
"""Check chapter headers for a book and optionally normalize dashes/newlines.

Usage: python check_chapters.py <book> [--hyphen|--emdash]

Loads the book factory from `scripts.do` and calls `get_chapters()` to obtain
chapter file paths. Prints header lines found in each chapter, reports
duplicate headers, checks for em-dash vs hyphen consistency, and (optionally)
converts header dash style. Ensures each file ends with exactly one newline.
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import os
from pathlib import Path
import re
import sys
from typing import Iterable, List, Tuple

scripts_dir = Path(__file__).parent.parent
sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(scripts_dir.parent))


HEADER_RE = re.compile(r'^(?P<prefix>\s*#{1,6}\s*)(?P<header>.*?)(\s*)$')
EMDASH = '\u2014'


def load_book_factory(book_name: str):
    try:
        from scripts import do as do_mod
    except Exception:
        # Try importing by path as fallback
        spec = importlib.util.spec_from_file_location('do', scripts_dir / 'do.py')
        if spec is None:
            raise
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
        do_mod = mod

    factory = do_mod.BOOKS.get(book_name)
    if not factory:
        raise KeyError(f"Unknown book: {book_name}")
    return factory


def iter_chapter_files(chapters) -> Iterable[str]:
    # Accept various return shapes from get_chapters()
    if isinstance(chapters, dict):
        for v in chapters.values():
            yield from iter_chapter_files(v)
    elif isinstance(chapters, (list, tuple)):
        for item in chapters:
            if isinstance(item, (list, tuple)) and item:
                # commonly (path, title)
                yield str(item[0])
            else:
                yield str(item)
    else:
        yield str(chapters)


def find_headers_in_file(path: str) -> List[Tuple[int, str, str]]:
    """Return list of (lineno, prefix, header_text) for header lines."""
    headers = []
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            for i, line in enumerate(fh, start=1):
                m = HEADER_RE.match(line.rstrip('\n'))
                if m:
                    prefix = m.group('prefix')
                    header = m.group('header').strip()
                    headers.append((i, prefix, header))
    except FileNotFoundError:
        pass
    return headers


def convert_header_dashes(header: str, to_emdash: bool) -> str:
    # Convert only hyphen surrounded by spaces to em-dash, and vice-versa.
    if to_emdash:
        # Replace space-hyphen-space with space-em-dash-space
        header = re.sub(r'\s-\s', f' {EMDASH} ', header)
        # Also convert double hyphen (--)
        header = header.replace('--', EMDASH)
        # Leave existing em-dashes
    else:
        # Replace em-dash with space-hyphen-space
        header = header.replace(EMDASH, ' - ')
    return header


def normalize_file_newline(path: str, text: str) -> str:
    # Normalize line endings to \n and ensure exactly one trailing newline.
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Strip all trailing newlines then add one
    text = text.rstrip('\n') + '\n'
    return text


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Check chapter headers')
    parser.add_argument('book', help='book name as registered in scripts.do')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--hyphen', action='store_true', help='convert headers to hyphen (ASCII)')
    group.add_argument('--emdash', action='store_true', help='convert headers to em-dash')
    parser.add_argument('--fix', action='store_true', help='write fixes to files (newline and dash conversion)')
    args = parser.parse_args(argv)

    try:
        factory = load_book_factory(args.book)
    except Exception as e:
        print('Error loading book:', e)
        return 2

    booker = factory()
    if not hasattr(booker, 'get_chapters'):
        print('Book object has no get_chapters()')
        return 3

    chapters = booker.get_chapters(format=None)

    files = list(iter_chapter_files(chapters))
    if not files:
        print('No chapter files found')
        return 0

    header_index = {}
    duplicates = {}
    emdash_count = 0
    hyphen_count = 0
    modified_files = []

    for f in files:
        if not os.path.isabs(f):
            # assume relative to repo root
            fpath = scripts_dir.parent / f
        else:
            fpath = Path(f)
        headers = find_headers_in_file(fpath)
        if not headers:
            print(f'[{f}] (no headers)')
            continue
        print(f'[{f}]')
        for lineno, prefix, header in headers:
            print(f'  {lineno}: {prefix}{header}')
            key = header.strip()
            header_index.setdefault(key, []).append((f, lineno))
            if EMDASH in header:
                emdash_count += 1
            if '-' in header:
                hyphen_count += 1

        # Optionally modify file
        if args.fix or args.hyphen or args.emdash:
            try:
                with open(fpath, 'r', encoding='utf-8') as fh:
                    text = fh.read()
            except FileNotFoundError:
                continue
            lines = text.splitlines()
            changed = False
            for idx, line in enumerate(lines):
                m = HEADER_RE.match(line)
                if m:
                    prefix = m.group('prefix')
                    header_text = m.group('header').strip()
                    new_header = header_text
                    if args.hyphen:
                        new_header = convert_header_dashes(header_text, to_emdash=False)
                    elif args.emdash:
                        new_header = convert_header_dashes(header_text, to_emdash=True)
                    if new_header != header_text:
                        lines[idx] = prefix + new_header
                        changed = True
            # normalize trailing newline
            new_text = '\n'.join(lines)
            new_text = normalize_file_newline(fpath, new_text)
            if new_text != text:
                changed = True
            if changed and args.fix:
                with open(fpath, 'w', encoding='utf-8', newline='\n') as fh:
                    fh.write(new_text)
                modified_files.append(fpath)

    # report duplicates
    dup_count = 0
    for key, occ in sorted(header_index.items(), key=lambda x: (-len(x[1]), x[0])):
        if len(occ) > 1:
            dup_count += 1
            print('\nDuplicate header:', key)
            for f, lineno in occ:
                print('  ', f, lineno)

    print('\nDash summary: em-dash count =', emdash_count, 'hyphen count =', hyphen_count)
    if emdash_count and hyphen_count:
        print('Warning: mixed em-dash and hyphen usage in headers')

    if modified_files:
        print('\nModified files:')
        for p in modified_files:
            print('  ', p)

    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
