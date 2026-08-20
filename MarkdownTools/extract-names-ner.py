#!/usr/bin/env python3
"""
Extract PERSON named entities from markdown drafts using spaCy.

Usage:
    python3 MarkdownTools/extract-names-ner.py /path/to/markdown
    python3 MarkdownTools/extract-names-ner.py --out outputs/people.csv

The script expects `spacy` and the `en_core_web_sm` model to be installed.
It will produce a CSV at `outputs/people.csv` (default) and print a summary.
"""

import os
import sys
import re
import argparse
import csv
from collections import defaultdict

try:
    import spacy
except Exception as e:
    print("spaCy is not installed. Please run: pip3 install spacy")
    sys.exit(2)


def load_model():
    # try loading common model names
    names = ["en_core_web_sm", "en_core_web_md", "en_core_web_lg"]
    for n in names:
        try:
            return spacy.load(n)
        except Exception:
            continue
    # fallback: try to load by shortcut which may raise helpful message
    try:
        return spacy.load("en")
    except Exception:
        print("Could not load an English model. Run: python3 -m spacy download en_core_web_sm")
        sys.exit(3)


def clean_name(name):
    """Normalize and validate a PERSON entity string.

    Returns cleaned name or None if it should be ignored.
    """
    if not name or not isinstance(name, str):
        return None
    # remove surrounding markdown emphasis/heading chars and brackets
    name = name.strip().strip("*_`[](){}<>~#")
    # remove stray markdown bold markers (e.g. **Justin Hitt**)
    name = name.replace('**', '').replace("__", '')
    # collapse whitespace
    name = ' '.join(name.split())
    if not name:
        return None

    low = name.lower()
    # remove trailing possessive (e.g. "Justin Hitt's", "Justin Hitt`s", "Justin Hitt’s")
    name = re.sub(r"(?:['’`])s$", '', name)

    # collapse whitespace again (in case we removed characters)
    name = ' '.join(name.split())

    # skip URLs or strings that look like URLs
    if 'http://' in low or 'https://' in low or 'www.' in low or '/' in name or ':' in name:
        return None
    # skip emails
    if '@' in name:
        return None
    # skip results that contain digits
    if any(ch.isdigit() for ch in name):
        return None

    # limit to reasonable length
    if len(name) > 60:
        return None

    # limit number of words (most person names are <= 4 words)
    parts = name.split()
    if len(parts) > 4 or len(parts) < 1:
        return None

    # allow letters (including common accented Latin range), spaces, hyphen and apostrophe
    # reject if any character is outside allowed set
    allowed = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ'\- ]+$")
    if not allowed.match(name):
        return None

    # reject common non-name tokens accidentally tagged as PERSON
    common_non_names = {
        'there', 'what', 'when', 'how', 'do', 'they', 'these', 'all', 'some', 'most',
        'use', 'we', 'you', 'it', 'who', 'action', 'forward', 'novelty'
    }
    # if it's a single word that is a common non-name, skip
    if len(parts) == 1 and parts[0].lower() in common_non_names:
        return None

    # normalize spacing and return
    return ' '.join(parts)


def scan_paths(paths, nlp):
    people = defaultdict(int)
    for path in paths:
        if not os.path.exists(path):
            continue
        for dirpath, _, filenames in os.walk(path):
            for fname in filenames:
                if not fname.lower().endswith('.md'):
                    continue
                full = os.path.join(dirpath, fname)
                try:
                    with open(full, 'r', encoding='utf-8') as f:
                        text = f.read()
                except Exception:
                    # skip unreadable files
                    continue
                doc = nlp(text)
                for ent in doc.ents:
                    if ent.label_ == 'PERSON':
                        raw = ent.text
                        name = clean_name(raw)
                        if not name:
                            continue
                        people[name] += 1
    return people


def write_csv(people, outpath):
    os.makedirs(os.path.dirname(outpath) or '.', exist_ok=True)
    with open(outpath, 'w', newline='', encoding='utf-8') as csvf:
        csvf.write('name,count\n')
        for name, count in sorted(people.items(), key=lambda x: (-x[1], x[0])):
            # safely escape double quotes by doubling them according to CSV rules
            name_esc = '"' + name.replace('"', '""') + '"'
            csvf.write(f'{name_esc},{count}\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('directory', nargs='?', default='.',
                   help='Base directory to scan (default: current directory)')
    p.add_argument('--include-notes', action='store_true', help='Also scan `Notes` under the base directory')
    p.add_argument('--out', default='outputs/people.csv', help='CSV output path')
    p.add_argument('--min-count', type=int, default=1, help='Minimum occurrences to include')
    args = p.parse_args()

    base = args.directory

    print('Loading spaCy model...', file=sys.stderr)
    nlp = load_model()
    print('Model loaded.', file=sys.stderr)

    # Scan the provided base directory recursively for all Markdown files.
    # The previous behavior scanned `Draft` (and optionally `Notes`) subfolders;
    # this script now walks the entire base directory tree and processes all
    # files ending in `.md`.
    if not os.path.isdir(base):
        print(f"Error: base directory not found: {base}", file=sys.stderr)
        sys.exit(1)

    print('Scanning files...', file=sys.stderr)
    people = scan_paths([base], nlp)

    # filter by min_count
    filtered = {name: count for name, count in people.items() if count >= args.min_count}

    # write csv
    outpath = args.out
    write_csv(filtered, outpath)

    # keep status on stderr so stdout remains clean for Unix-style pipelines
    print(f"CSV written to: {outpath}", file=sys.stderr)


if __name__ == '__main__':
    main()
