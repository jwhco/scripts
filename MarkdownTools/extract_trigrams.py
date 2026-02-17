#!/usr/bin/env python3
"""
trigrams.py

Extract trigrams from a Markdown file, filter for meaningful contextual keywords,
and list them with counts.

Usage examples:
  python scripts/trigrams.py path/to/file.md --start "## Transcript" --end "## Reference" --top 50
  python scripts/trigrams.py notes.md --min-nonstop 2 --min-count 2 --csv > trigrams.csv

No external dependencies. Works with Python 3.7+.
"""

import argparse
import collections
import re
import sys
from typing import List, Tuple

# A modest stopword list. Extend as needed.
STOPWORDS = {
    'a','an','the','and','or','but','if','then','else','when','while','of','for','on','in','to',
    'is','are','was','were','be','been','being','it','that','this','these','those','with','as',
    'by','at','from','not','no','yes','you','i','we','they','he','she','them','his','her','my',
    'our','your','their','me','do','did','does','done','have','has','had','will','would','can',
    'could','should','about','which','what','who','whom','how','so','just','also','any','all',
    'more','most','some','such','into','over','up','down','out','only','now','then'
}

RE_CODEBLOCK = re.compile(r"```.*?```", re.S)
RE_INLINE_CODE = re.compile(r"`[^`]*`")
RE_IMAGE = re.compile(r"!\[[^\]]*\]\([^\)]*\)")
RE_LINK = re.compile(r"\[([^\]]+)\]\([^\)]*\)")
RE_BRACKET_LINK = re.compile(r"\[\[([^\]]+)\]\]")
RE_MARKDOWN = re.compile(r"(^>.*$|^\s*#.*$)", re.M)
RE_NONWORD = re.compile(r"[^A-Za-z0-9' ]+")


def extract_region(text: str, start_marker: str, end_marker: str) -> str:
    if not start_marker and not end_marker:
        return text
    start_idx = 0
    if start_marker:
        i = text.find(start_marker)
        if i == -1:
            # fall back to start of file
            start_idx = 0
        else:
            start_idx = i + len(start_marker)
    end_idx = len(text)
    if end_marker:
        j = text.find(end_marker, start_idx)
        if j != -1:
            end_idx = j
    return text[start_idx:end_idx]


def clean_markdown(text: str) -> str:
    # remove code blocks and inline code
    text = RE_CODEBLOCK.sub(' ', text)
    text = RE_INLINE_CODE.sub(' ', text)
    # remove images
    text = RE_IMAGE.sub(' ', text)
    # convert links [label](url) -> label
    text = RE_LINK.sub(lambda m: m.group(1), text)
    # convert wiki links [[label]] -> label
    text = RE_BRACKET_LINK.sub(lambda m: m.group(1), text)
    # remove headings/blockquote lines
    text = RE_MARKDOWN.sub(' ', text)
    # strip punctuation (keep apostrophes within words)
    text = RE_NONWORD.sub(' ', text)
    # normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def tokens_from_text(text: str) -> List[str]:
    # extract words (keeps apostrophes inside words)
    toks = re.findall(r"[A-Za-z']+", text)
    toks = [t.lower() for t in toks if t]
    return toks


def trigrams_from_tokens(tokens: List[str]) -> List[Tuple[str,str,str]]:
    return [ (tokens[i], tokens[i+1], tokens[i+2]) for i in range(len(tokens)-2) ]


def join_tri(tri: Tuple[str,str,str]) -> str:
    return ' '.join(tri)


def sample_contexts(original_text: str, tri: str, max_samples: int=3) -> List[str]:
    # find sentences that contain the trigram (approximate by searching tri in cleaned text)
    sent_end = re.compile(r'[.!?]\s+')
    sentences = sent_end.split(original_text)
    out = []
    lowered = tri.lower()
    for s in sentences:
        if lowered in s.lower():
            s_clean = ' '.join(s.split())
            out.append(s_clean)
            if len(out) >= max_samples:
                break
    return out


def compute_trigrams(text: str, min_nonstop: int = 2) -> Tuple[collections.Counter, dict]:
    cleaned = clean_markdown(text)
    tokens = tokens_from_text(cleaned)
    tris = trigrams_from_tokens(tokens)
    counts = collections.Counter()
    contexts = {}
    for tri in tris:
        nonstop = sum(1 for w in tri if w not in STOPWORDS)
        if nonstop >= min_nonstop:
            key = join_tri(tri)
            counts[key] += 1
    return counts, contexts


def main(argv=None):
    p = argparse.ArgumentParser(description='Extract meaningful trigrams from a Markdown file and count occurrences.')
    p.add_argument('file', help='Path to markdown file (or - for stdin)')
    p.add_argument('--start', help='Optional start marker (include text after first occurrence). Exact substring match.')
    p.add_argument('--end', help='Optional end marker (stop before this marker). Exact substring match.')
    p.add_argument('--min-nonstop', type=int, default=2, help='Minimum number of non-stopwords required in trigram (default 2)')
    p.add_argument('--min-count', type=int, default=1, help='Only show trigrams occurring at least this many times (default 1)')
    p.add_argument('--top', type=int, default=0, help='Show top N results (default all)')
    p.add_argument('--csv', action='store_true', help='Emit CSV: trigram,count')
    p.add_argument('--limit-context', type=int, default=0, help='If >0, also print up to N example contexts (requires reading file contents)')
    args = p.parse_args(argv)

    if args.file == '-':
        data = sys.stdin.read()
    else:
        with open(args.file, 'r', encoding='utf-8') as f:
            data = f.read()

    region = extract_region(data, args.start, args.end)
    counts, contexts = compute_trigrams(region, min_nonstop=args.min_nonstop)

    # filter by min_count and sort
    items = [ (k,v) for k,v in counts.items() if v >= args.min_count ]
    items.sort(key=lambda x: x[1], reverse=True)
    if args.top > 0:
        items = items[:args.top]

    if args.csv:
        print('trigram,count')
        for k,v in items:
            print(f'"{k}",{v}')
        return

    # pretty print
    maxk = max((len(k) for k,_ in items), default=20)
    for k,v in items:
        print(f'{v:5d}  {k}')
        if args.limit_context > 0:
            samples = sample_contexts(region, k, max_samples=args.limit_context)
            for s in samples:
                print(f'       -> {s}')

if __name__ == '__main__':
    main()
