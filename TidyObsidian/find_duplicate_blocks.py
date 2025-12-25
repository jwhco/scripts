#!/usr/bin/env python3
"""
Find duplicate or near-duplicate blocks of text in Markdown files within a Git repo.

Changes from previous version:
- Shows progress while scanning files.
- Only reports duplicates that occur in more than one file.
- Still supports configurable block size and similarity threshold.
"""

import subprocess
import os
import sys
import difflib
from collections import defaultdict

# ---------------- CONFIGURATION ----------------
BLOCK_SIZE = 3        # Number of consecutive lines to treat as a block
SIMILARITY_THRESHOLD = 0.9  # 1.0 = exact match, 0.9 = near match
# ------------------------------------------------

def get_markdown_files():
    """Get a list of tracked Markdown files in the Git repo."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.md", "*.markdown"],
            capture_output=True, text=True, check=True
        )
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        return files
    except subprocess.CalledProcessError:
        print("Error: Not a Git repository or Git command failed.")
        sys.exit(1)

def read_blocks(file_path, block_size):
    """Yield (block_text, start_line) tuples from a file."""
    blocks = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]  # remove empty lines
        for i in range(len(lines) - block_size + 1):
            block = "\n".join(lines[i:i + block_size])
            blocks.append((block, i + 1))
    except (OSError, UnicodeDecodeError) as e:
        print(f"Warning: Could not read {file_path}: {e}")
    return blocks

def find_duplicates(files, block_size, similarity_threshold):
    """Find duplicate or near-duplicate blocks across different files."""
    seen_blocks = defaultdict(list)  # block_text -> list of (file, line)

    for idx, file in enumerate(files, start=1):
        print(f"[{idx}/{len(files)}] Scanning {file}...")
        for block, line_num in read_blocks(file, block_size):
            found_match = False
            for existing_block in seen_blocks.keys():
                ratio = difflib.SequenceMatcher(None, block, existing_block).ratio()
                if ratio >= similarity_threshold:
                    seen_blocks[existing_block].append((file, line_num))
                    found_match = True
                    break
            if not found_match:
                seen_blocks[block].append((file, line_num))

    # Keep only blocks that appear in more than one file
    duplicates = []
    for block, locations in seen_blocks.items():
        unique_files = {f for f, _ in locations}
        if len(unique_files) > 1:
            duplicates.append((block, locations))

    return duplicates

def main():
    files = get_markdown_files()
    if not files:
        print("No Markdown files found in this Git repository.")
        return

    print(f"Scanning {len(files)} Markdown files for duplicate blocks...\n")
    duplicates = find_duplicates(files, BLOCK_SIZE, SIMILARITY_THRESHOLD)

    print("\n--- Scan Complete ---")
    if not duplicates:
        print("No duplicate blocks found across different files.")
        return

    print(f"Found {len(duplicates)} duplicate/near-duplicate blocks across files:\n")
    for idx, (block, locations) in enumerate(duplicates, start=1):
        print(f"--- Duplicate Block #{idx} ---")
        print(block)
        print("Locations:")
        for file, line in locations:
            print(f"  {file}:{line}")
        print()

if __name__ == "__main__":
    main()
