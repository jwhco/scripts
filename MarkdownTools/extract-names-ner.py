#!/usr/bin/env python3
"""
Extract PERSON named entities from markdown drafts using spaCy.

Usage:
  python3 scripts/extract_names_ner.py
  python3 scripts/extract_names_ner.py --include-notes  # also scan Scrivener/Notes
  python3 scripts/extract_names_ner.py --out outputs/people.csv

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
    people = defaultdict(lambda: {'count': 0, 'files': set()})
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
                        people[name]['count'] += 1
                        people[name]['files'].add(full)
    return people


def write_csv(people, outpath):
    os.makedirs(os.path.dirname(outpath) or '.', exist_ok=True)
    with open(outpath, 'w', newline='', encoding='utf-8') as csvf:
        # write CSV manually so the `files` column is a single quoted semicolon-delimited string:
        csvf.write('name,count,files\n')
        for name, info in sorted(people.items(), key=lambda x: (-x[1]['count'], x[0])):
            # safely escape double quotes by doubling them according to CSV rules
            name_esc = '"' + name.replace('"', '""') + '"'
            files_join = ';'.join(sorted(info['files']))
            files_esc = '"' + files_join.replace('"', '""') + '"'
            csvf.write(f'{name_esc},{info["count"]},{files_esc}\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--include-notes', action='store_true', help='Also scan `Scrivener/Notes`')
    p.add_argument('--out', default='outputs/people.csv', help='CSV output path')
    p.add_argument('--min-count', type=int, default=1, help='Minimum occurrences to include')
    args = p.parse_args()

    base = 'Scrivener'
    draft = os.path.join(base, 'Draft')
    notes = os.path.join(base, 'Notes')

    print('Loading spaCy model...')
    nlp = load_model()
    print('Model loaded.')

    paths = [draft]
    if args.include_notes:
        paths.append(notes)

    print('Scanning files...')
    people = scan_paths(paths, nlp)

    # filter by min_count
    filtered = {name: info for name, info in people.items() if info['count'] >= args.min_count}

    # write csv
    outpath = args.out
    write_csv(filtered, outpath)

    # print summary
    print('\nPeople found (sorted by frequency):\n')
    for name, info in sorted(filtered.items(), key=lambda x: (-x[1]['count'], x[0])):
        print(f"{name} — {info['count']} occurrence(s) — {len(info['files'])} file(s)")
        for f in sorted(info['files']):
            print(f"    {f}")
    print(f"\nCSV written to: {outpath}\nTotal people: {len(filtered)}")


if __name__ == '__main__':
    main()
