#!/usr/bin/env python3

"""
Find similar files in a directory tree # and group them by their normalized names. 

Features:
- Recursively scans all files in the specified directory. Omit directories hidden or templates.
- Normalizes filenames by removing numeric prefixes (except Zettelkasten keys), punctuation, and standardizing separators.
- Groups files with similar normalized names together for easy identification.
"""

import re
import argparse
from pathlib import Path
from collections import defaultdict

ZETTEL_RE = re.compile(r'^(\d{12})[\s_-]+(.+)$')
STRUCTURED_TIMESTAMP_RE = re.compile(
    r'^(?:\d{2}_)?(?P<timestamp>\d{4}(?:_\d{2}){4})(?:_\d{2})?$'
)
COMPACT_TIMESTAMP_RE = re.compile(r'^\d{12}$')
DATE_TOKEN_RE = re.compile(
    r'(?<!\d)(?:\d{4}[-_.]\d{2}[-_.]\d{2}|\d{8}(?:\d{4}(?:\d{2})?)?)(?!\d)'
)

def is_in_hidden_dir(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)

def normalize(name: str) -> str:
    stem, dot, ext = name.lower().rpartition(".")
    if not dot or ext == "json":
        return ""

    timestamp_match = STRUCTURED_TIMESTAMP_RE.fullmatch(stem)
    if timestamp_match:
        timestamp = timestamp_match.group("timestamp").replace("_", "")
        return f"{timestamp}.{ext}"
    if COMPACT_TIMESTAMP_RE.fullmatch(stem):
        return f"{stem}.{ext}"

    numeric_key = re.sub(r'[-_]', '', stem)
    if numeric_key.isdigit():
        return f"{numeric_key}.{ext}"

    zettel_match = ZETTEL_RE.match(stem)

    if zettel_match:
        # Preserve full Zettelkasten key
        zettel_id, rest = zettel_match.groups()
        stem = f"{zettel_id} {rest}"
    else:
        date_match = DATE_TOKEN_RE.search(stem)
        if date_match:
            prefix = stem[:date_match.start()]
            if prefix and re.fullmatch(r'[\d\W_]+', prefix):
                stem = stem[date_match.start():]
        else:
            # Remove non-zettel numeric prefixes
            stem = re.sub(r'^[\d\W_]+', '', stem)

    # Normalize separators
    stem = re.sub(r'[\s\-_]+', ' ', stem)

    # Remove remaining punctuation
    stem = re.sub(r'[^\w\s]', '', stem)

    return f"{stem.strip()}.{ext}"

def main(root=".", limit=None):
    groups = defaultdict(list)

    for path in Path(root).rglob("*"):
        if is_in_hidden_dir(path):
            continue
        if path.is_file():
            key = normalize(path.name)
            if key:
                groups[key].append(path)

    printed_groups = 0
    for key, files in sorted(groups.items()):
        if len(files) > 1:
            if limit is not None and printed_groups >= limit:
                break
            print(f"\n=== Similar group: {key} ===")
            for f in files:
                print(f"  {f}")
            printed_groups += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find groups of files with similar names.")
    parser.add_argument("root", nargs="?", default=".", help="Directory tree to scan (default: current directory)")
    parser.add_argument("--limit", type=int, help="Limit the number of similar groups printed")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be zero or greater")
    main(args.root, args.limit)
