#!/usr/bin/env python3
"""
Parallelized duplicate/near-duplicate Markdown scanner.

Features:
- Whole-file hashing to skip redundant block comparisons.
- Multiprocessing for file reading, filtering, hashing, and block extraction.
- Only block-scans unique files.
"""

import subprocess
import sys
import difflib
import hashlib
from collections import defaultdict
from multiprocessing import Pool, cpu_count

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

def read_and_hash_file(file_path):
    """Read file, filter it, and return (file_path, filtered_lines, sha256_hash)."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.readlines()
        lines = filter_lines(raw)
        joined = "\n".join(lines)
        h = hashlib.sha256(joined.encode("utf-8")).hexdigest()
        return (file_path, lines, h)
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return (file_path, [], None)

def extract_blocks(args):
    """Extract blocks from a file's filtered lines."""
    file_path, lines, block_size = args
    blocks = []
    for i in range(len(lines) - block_size + 1):
        block = "\n".join(lines[i:i + block_size])
        blocks.append((file_path, block, i + 1))
    return blocks

def find_duplicates(files, block_size, similarity_threshold):
    print(f"Using {cpu_count()} CPU cores for parallel scanning...\n")

    # Step 1: Parallel read + filter + hash
    print("Hashing files in parallel...")
    with Pool() as pool:
        results = pool.map(read_and_hash_file, files)

    file_contents = {f: lines for f, lines, h in results}
    file_hashes = defaultdict(list)
    for f, lines, h in results:
        if h:
            file_hashes[h].append(f)

    # Step 2: Whole-file duplicates
    whole_file_dupes = {h: flist for h, flist in file_hashes.items() if len(flist) > 1}

    if whole_file_dupes:
        print("\n=== Whole-file duplicates detected ===")
        for h, flist in whole_file_dupes.items():
            print("\nGroup:")
            for f in flist:
                print(f"  {f}")
        print("\nSkipping block-level scanning for these identical files.\n")

    # Step 3: Unique files only
    unique_files = [f for h, flist in file_hashes.items() if len(flist) == 1 for f in flist]
    print(f"Proceeding with block-level scanning on {len(unique_files)} unique files...\n")

    # Step 4: Parallel block extraction
    block_args = [(f, file_contents[f], block_size) for f in unique_files]
    with Pool() as pool:
        block_results = pool.map(extract_blocks, block_args)

    # Flatten list of lists
    all_blocks = [item for sublist in block_results for item in sublist]

    # Step 5: Block-level duplicate detection
    seen_blocks = defaultdict(list)

    for file_path, block, line_num in all_blocks:
        found_match = False
        for existing_block in seen_blocks.keys():
            ratio = difflib.SequenceMatcher(None, block, existing_block).ratio()
            if ratio >= similarity_threshold:
                seen_blocks[existing_block].append((file_path, line_num))
                found_match = True
                break
        if not found_match:
            seen_blocks[block].append((file_path, line_num))

    # Step 6: Keep only blocks appearing in >1 file
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
