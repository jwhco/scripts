#!/usr/bin/env python3

import re
import sys
from pathlib import Path
from collections import defaultdict

def normalize(name: str) -> str:
    stem, dot, ext = name.lower().rpartition(".")
    if not dot:
        return ""

    # Remove leading numbers and separators
    stem = re.sub(r'^[\d\W_]+', '', stem)

    # Normalize separators to spaces
    stem = re.sub(r'[\s\-_]+', ' ', stem)

    # Remove remaining punctuation
    stem = re.sub(r'[^\w\s]', '', stem)

    return f"{stem.strip()}.{ext}"

def main(root="."):
    groups = defaultdict(list)

    for path in Path(root).rglob("*"):
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

