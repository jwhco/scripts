#!/usr/bin/env python3
"""
Find similar files in a directory tree # and group them by their normalized names. 

Features:
- Recursively scans all files in the specified directory.
- Normalizes filenames by removing numeric prefixes (except Zettelkasten keys), punctuation, and standardizing separators.
- Groups files with similar normalized names together for easy identification.
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

ZETTEL_RE = re.compile(r'^(\d{12})[\s_-]+(.+)$')

def is_in_hidden_dir(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)

def normalize(name: str) -> str:
    stem, dot, ext = name.lower().rpartition(".")
    if not dot:
        return ""

    zettel_match = ZETTEL_RE.match(stem)

    if zettel_match:
        # Preserve full Zettelkasten key
        zettel_id, rest = zettel_match.groups()
        stem = f"{zettel_id} {rest}"
    else:
        # Remove non-zettel numeric prefixes
        stem = re.sub(r'^[\d\W_]+', '', stem)

    # Normalize separators
    stem = re.sub(r'[\s\-_]+', ' ', stem)

    # Remove remaining punctuation
    stem = re.sub(r'[^\w\s]', '', stem)

    return f"{stem.strip()}.{ext}"

def main(root="."):
    groups = defaultdict(list)

    for path in Path(root).rglob("*"):
        if is_in_hidden_dir(path):
            continue
        if path.is_file():
            key = normalize(path.name)
            if key:
                groups[key].append(path)

    for key, files in sorted(groups.items()):
        if len(files) > 1:
            print(f"\n=== Similar group: {key} ===")
            for f in files:
                print(f"  {f}")

if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    main(root)
