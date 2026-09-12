#!/usr/bin/env python3
import os, re, sys
from pathlib import Path
import unicodedata

ROOT = Path('external/number-go-up')

def slugify(text):
    # Remove explicit ID braces if present
    text = re.sub(r"\{#[-_:.A-Za-z0-9]+\}", '', text)
    text = text.strip()
    # Normalize
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = text.lower()
    # Replace non-alnum with hyphen
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

header_re = re.compile(r'^(#{1,6})\s+(.*)$')
explicit_id_re = re.compile(r"\{#([A-Za-z0-9_:.-]+)\}")

occurrences = {}

for path in sorted(ROOT.rglob('*.md')):
    try:
        txt = path.read_text(encoding='utf-8')
    except Exception:
        txt = path.read_text(encoding='latin-1')
    lines = txt.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = header_re.match(line)
        if m:
            level = len(m.group(1))
            content = m.group(2).strip()
            # check for explicit id
            mid = explicit_id_re.search(content)
            if mid:
                hid = mid.group(1)
            else:
                # remove trailing slug braces if any
                content = re.sub(r"\s*\{#[-_:.A-Za-z0-9]+\}\s*$", '', content)
                hid = slugify(content)
            occurrences.setdefault(hid, []).append((str(path), i+1, content))
            i += 1
            continue
        # setext-style headings: underline of === or --- on next line
        if i+1 < len(lines) and re.match(r'^(-{3,}|={3,})\s*$', lines[i+1]):
            content = line.strip()
            mid = explicit_id_re.search(content)
            if mid:
                hid = mid.group(1)
            else:
                content = re.sub(r"\s*\{#[-_:.A-Za-z0-9]+\}\s*$", '', content)
                hid = slugify(content)
            occurrences.setdefault(hid, []).append((str(path), i+1, content))
            i += 2
            continue
        i += 1

dups = {k:v for k,v in occurrences.items() if k and len(v) > 1}
if not dups:
    print('No duplicate heading IDs found in external/number-go-up')
    sys.exit(0)

print('Duplicate heading IDs found:')
for hid, items in sorted(dups.items(), key=lambda x: (-len(x[1]), x[0])):
    print(f"\nID: {hid} — {len(items)} occurrences")
    for (p,ln,content) in items:
        print(f" - {p}:{ln}: {content}")

print('\nSuggestion: add explicit unique ids to the headings listed above, e.g.:')
for hid, items in dups.items():
    for idx,(p,ln,content) in enumerate(items, start=1):
        suggested = f"{hid}-{idx}"
        print(f" - {p}:{ln}: {content}  -> add {{#{suggested}}} to the heading")
