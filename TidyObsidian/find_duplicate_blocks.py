#!/usr/bin/env python3
"""
Find duplicate or near-duplicate blocks of text in Markdown files within a Git repo.

Optimized version:
- Hashes whole files first to avoid expensive block comparisons.
- Groups identical files and reports them immediately.
- Only performs block-level duplicate detection on non-identical files.
"""

import subprocess
import sys
import difflib
import hashlib
from collections import defaultdict

# ---------------- CONFIGURATION ----------------
BLOCK_SIZE = 3
SIMILARITY_THRESHOLD = 0.9
# ------------------------------------------------

def get_markdown_files():
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.md", "*.markdown"],
            capture_output=True, text=True, check=True
        )
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except subprocess.CalledProcessError:
        print("Error: Not a Git repository or Git command failed.")
        sys.exit(1)

def strip_yaml_front_matter(lines):
    if lines and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                return lines[idx + 1:]
        return []
    return lines

def filter_lines(lines):
    lines = strip_yaml_front_matter(lines)
    filtered = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("##"):
            continue
        filtered.append(stripped)
    return filtered

def read_filtered_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.readlines()
        return filter_lines(raw)
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return []

def hash_file(lines):
    """Hash the entire filtered file content."""
    joined = "\n".join(lines)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()

def read_blocks(lines, block_size):
    blocks = []
    for i in range(len(lines) - block_size + 1):
        block = "\n".join(lines[i:i + block_size])
        blocks.append((block, i + 1))
    return blocks

def find_duplicates(files, block_size, similarity_threshold):
    print("Hashing files to detect whole-file duplicates...\n")

    file_contents = {}
    file_hashes = defaultdict(list)

    # Step 1: Read + hash files
    for f in files:
        lines = read_filtered_file(f)
        file_contents[f] = lines
        h = hash_file(lines)
        file_hashes[h].append(f)

    # Step 2: Report whole-file duplicates
    whole_file_dupes = {h: flist for h, flist in file_hashes.items() if len(flist) > 1}

    if whole_file_dupes:
        print("=== Whole-file duplicates detected ===")
        for h, flist in whole_file_dupes.items():
            print("\nGroup:")
            for f in flist:
                print(f"  {f}")
        print("\nSkipping block-level scanning for these identical files.\n")

    # Step 3: Only scan unique files
    unique_files = [f for h, flist in file_hashes.items() if len(flist) == 1 for f in flist]

    print(f"Proceeding with block-level scanning on {len(unique_files)} unique files...\n")

    seen_blocks = defaultdict(list)

    for idx, file in enumerate(unique_files, start=1):
        print(f"[{idx}/{len(unique_files)}] Scanning {file}...")
        blocks = read_blocks(file_contents[file], block_size)

        for block, line_num in blocks:
            found_match = False
            for existing_block in seen_blocks.keys():
                ratio = difflib.SequenceMatcher(None, block, existing_block).ratio()
                if ratio >= similarity_threshold:
                    seen_blocks[existing_block].append((file, line_num))
                    found_match = True
                    break
            if not found_match:
                seen_blocks[block].append((file, line_num))

    # Step 4: Keep only blocks appearing in >1 file
    duplicates = []
    for block, locations in seen_blocks.items():
        unique_files = {f for f, _ in locations}
        if len(unique_files) > 1:
            duplicates.append((block, locations))

    return whole_file_dupes, duplicates

def main():
    files = get_markdown_files()
    if not files:
        print("No Markdown files found in this Git repository.")
        return

    print(f"Scanning {len(files)} Markdown files...\n")
    whole_file_dupes, block_dupes = find_duplicates(files, BLOCK_SIZE, SIMILARITY_THRESHOLD)

    print("\n--- Scan Complete ---\n")

    if not whole_file_dupes:
        print("No whole-file duplicates found.\n")

    if not block_dupes:
        print("No duplicate/near-duplicate blocks found across different files.")
        return

    print(f"Found {len(block_dupes)} duplicate/near-duplicate blocks:\n")
    for idx, (block, locations) in enumerate(block_dupes, start=1):
        print(f"--- Duplicate Block #{idx} ---")
        print(block)
        print("Locations:")
        for file, line in locations:
            print(f"  {file}:{line}")
        print()

if __name__ == "__main__":
    main()
