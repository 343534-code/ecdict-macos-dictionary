#!/usr/bin/env python3
"""Export ECDICT MDX entries to styled Apple Dictionary XHTML."""
from pathlib import Path
from html import unescape
from xml.sax.saxutils import escape, quoteattr
import re
import sys

from readmdict import MDX

marker = re.compile(r"`([1-4])`")
breaks = re.compile(r"<\s*/?br\s*/?\s*>", re.I)
spaces = re.compile(r"[ \t\f\v]+")

def clean(s: str) -> str:
    s = unescape(s).replace('\r', '')
    return spaces.sub(' ', s).strip()

def render(key: str, raw: bytes) -> str:
    text = breaks.sub('\n', raw.decode('utf-8', 'replace'))
    # MDX stylesheet markers: 1=headword, 3=phonetic, 4=metadata.
    text = marker.sub(lambda m: f'\u0001{m.group(1)}\u0001', text)
    chunks = re.split(r'(\u0001[1-4]\u0001)', text)
    style, parts = '0', []
    for chunk in chunks:
        hit = re.fullmatch(r'\u0001([1-4])\u0001', chunk)
        if hit:
            style = hit.group(1)
            continue
        for line in chunk.splitlines():
            line = clean(line)
            if not line:
                continue
            value = escape(line)
            if style == '1':
                continue  # the Apple Dictionary heading is emitted below
            if style == '3':
                # Lookup popovers may discard custom CSS colors on generic divs.
                # Store pronunciation as primary heading content so it keeps the
                # foreground text color in both light and dark appearances.
                parts.append(f'<h3 class="pronunciation">{value}</h3>')
            elif style == '4' or line.startswith(('时态:', '级别:', '(')):
                parts.append(f'<div class="meta">{value}</div>')
            elif re.match(r'^(n|v[ti]?|a|ad|prep|conj|pron|aux|num|int)\.', line, re.I):
                pos, definition = line.split('.', 1)
                parts.append(f'<div class="sense"><span class="pos">{escape(pos)}.</span>{escape(definition.strip())}</div>')
            else:
                parts.append(f'<div class="sense">{value}</div>')
    if not parts:
        parts.append('<div class="sense">（无释义）</div>')
    return ''.join(parts)

def main(source: Path, destination: Path) -> None:
    mdx = MDX(str(source))
    with destination.open('w', encoding='utf-8', buffering=1024*1024) as out:
        out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        out.write('<d:dictionary xmlns="http://www.w3.org/1999/xhtml" xmlns:d="http://www.apple.com/DTDs/DictionaryService-1.0.rng">\n')
        for ordinal, (raw_key, raw_value) in enumerate(mdx.items(), 1):
            key = raw_key.decode('utf-8', 'replace').strip()
            if not key:
                continue
            out.write(f'<d:entry id="ecdict_{ordinal}" d:title={quoteattr(key)}><d:index d:value={quoteattr(key)}/>')
            out.write(f'<h1>{escape(key)}</h1>{render(key, raw_value)}</d:entry>\n')
            if ordinal % 100000 == 0:
                print(f'exported {ordinal}', file=sys.stderr, flush=True)
        out.write('</d:dictionary>\n')

if __name__ == '__main__':
    main(*map(Path, sys.argv[1:3]))
