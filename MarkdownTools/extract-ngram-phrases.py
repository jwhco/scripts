#!/usr/bin/env python3
"""
extract-ngram-phrase.py

Extract ngrams from a Markdown file, filter for meaningful contextual keywords,
and list them with counts. Present trigrams as default.

Usage examples:
  extract-ngram-phrase.py filename.md --start "## Transcript" --end "## Reference" --top 50
  extract-ngram-phrase.py filename.md --ngram-size 2 --min-count 2 --csv > bigrams.csv
  extract-ngram-phrase.py filename.md --ngram-size 4 --min-count 3  # 4-grams

"""

import argparse
import collections
import re
import sys
from typing import List, Tuple

from nltk.corpus import stopwords

# NLTK English stopwords
NLTK_STOPWORDS = set(stopwords.words('english'))

# Custom stopwords to append to NLTK list. Modify this for domain-specific filtering.
CUSTOM_STOPWORDS = {
    # Add custom stopwords here, e.g.: 'word1', 'word2'
    'eof', 'hittjw', 'http', 'https', 'www', 'com', 'org', 'net', 'io', 'github', 'gitlab',
}

# Universal English stopwords (NLTK + custom)
STOPWORDS = NLTK_STOPWORDS | CUSTOM_STOPWORDS

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


def ngrams_from_tokens(tokens: List[str], n: int) -> List[Tuple[str, ...]]:
    return [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]


def join_ngram(ngram: Tuple[str, ...]) -> str:
    return ' '.join(ngram)


def sample_contexts(original_text: str, ngram: str, max_samples: int=3) -> List[str]:
    # find sentences that contain the ngram (approximate by searching ngram in cleaned text)
    sent_end = re.compile(r'[.!?]\s+')
    sentences = sent_end.split(original_text)
    out = []
    lowered = ngram.lower()
    for s in sentences:
        if lowered in s.lower():
            s_clean = ' '.join(s.split())
            out.append(s_clean)
            if len(out) >= max_samples:
                break
    return out


def compute_ngrams(text: str, ngram_size: int = 3, min_nonstop: int = 2) -> Tuple[collections.Counter, dict]:
    cleaned = clean_markdown(text)
    tokens = tokens_from_text(cleaned)
    ngrams = ngrams_from_tokens(tokens, ngram_size)
    counts = collections.Counter()
    contexts = {}
    for ngram in ngrams:
        # Exclude any ngram containing a stopword or single-letter word
        if not any(w in STOPWORDS for w in ngram) and not any(len(w) == 1 for w in ngram):
            key = join_ngram(ngram)
            counts[key] += 1
    return counts, contexts


def main(argv=None):
    p = argparse.ArgumentParser(description='Extract meaningful ngrams from a Markdown file and count occurrences.')
    p.add_argument('file', help='Path to markdown file (or - for stdin)')
    p.add_argument('--start', help='Optional start marker (include text after first occurrence). Exact substring match.')
    p.add_argument('--end', help='Optional end marker (stop before this marker). Exact substring match.')
    p.add_argument('--ngram-size', type=int, default=3, help='Size of n-grams to extract (2 for bigrams, 3 for trigrams, 4 for 4-grams, etc.) (default 3)')
    p.add_argument('--min-nonstop', type=int, default=2, help='Minimum number of non-stopwords required in ngram (default 2)')
    p.add_argument('--min-count', type=int, default=1, help='Only show ngrams occurring at least this many times (default 1)')
    p.add_argument('--top', type=int, default=0, help='Show top N results (default all)')
    p.add_argument('--csv', action='store_true', help='Emit CSV: ngram,count')
    p.add_argument('--limit-context', type=int, default=0, help='If >0, also print up to N example contexts (requires reading file contents)')
    args = p.parse_args(argv)

    if args.file == '-':
        data = sys.stdin.read()
    else:
        with open(args.file, 'r', encoding='utf-8') as f:
            data = f.read()

    region = extract_region(data, args.start, args.end)
    counts, contexts = compute_ngrams(region, ngram_size=args.ngram_size, min_nonstop=args.min_nonstop)

    # filter by min_count and sort
    items = [ (k,v) for k,v in counts.items() if v >= args.min_count ]
    items.sort(key=lambda x: x[1], reverse=True)
    if args.top > 0:
        items = items[:args.top]

    if args.csv:
        print('ngram,count')
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
