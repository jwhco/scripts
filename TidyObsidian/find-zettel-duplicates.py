#!/usr/bin/env python3
"""
Find duplicate zettelkasten serials (YYYYMMDDnnnn) in markdown filenames.
Prints clusters of files sharing the same serial prefix.
"""
import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# Pattern: YYYYMMDD followed by 4 digits (nnnn) at start of filename
SERIAL_PATTERN = re.compile(r'^(\d{8}\d{4})')

def find_markdown_files(root_dir):
    """Find all .md files recursively."""
    md_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip hidden directories and .obsidian, .git, .trash
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in {'.obsidian', '.git', '.trash', 'node_modules'}]
        for fname in filenames:
            if fname.endswith('.md'):
                full_path = os.path.join(dirpath, fname)
                md_files.append(full_path)
    return md_files

def extract_serial(filename):
    """Extract YYYYMMDDnnnn serial from filename."""
    basename = os.path.basename(filename)
    match = SERIAL_PATTERN.match(basename)
    if match:
        return match.group(1)
    return None

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Find duplicate zettelkasten serials in markdown filenames."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan recursively (default: current working directory)",
    )
    args = parser.parse_args(argv)

    root = Path(args.directory).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        parser.error(f"Directory does not exist or is not a directory: {root}")

    print(f"Scanning: {root}\n")
    
    md_files = find_markdown_files(root)
    print(f"Found {len(md_files)} markdown files\n")
    
    # Group by serial
    serial_map = defaultdict(list)
    for f in md_files:
        serial = extract_serial(f)
        if serial:
            serial_map[serial].append(f)
    
    # Find duplicates (serials with more than 1 file)
    duplicates = {s: files for s, files in serial_map.items() if len(files) > 1}
    
    if not duplicates:
        print("No duplicate zettelkasten serials found.")
        return
    
    print(f"Found {len(duplicates)} serial(s) with duplicates:\n")
    
    # Print clusters
    for serial in sorted(duplicates.keys()):
        files = duplicates[serial]
        print(f"{'='*60}")
        print(f"Serial: {serial}")
        print(f"Count:  {len(files)} files")
        print(f"{'='*60}")
        for f in sorted(files):
            # Show relative path from root
            rel_path = os.path.relpath(f, root)
            print(f"  {rel_path}")
        print()

if __name__ == '__main__':
    main(sys.argv[1:])
