#!/usr/bin/env python3
"""
High-performance duplicate / near-duplicate Markdown scanner.

Features:
- Whole-file hashing to skip redundant block comparisons.
- Multiprocessing for file reading/filtering/hashing and block extraction.
- Token-based Jaccard similarity for fast near-duplicate detection.
- Inverted index on signature tokens to aggressively prune comparisons.
- Optional --ignore-wikilink flag to strip wikilinks and drop low-value lines.
"""

import subprocess
import sys
import hashlib
import re
import argparse
from collections import defaultdict
from multiprocessing import Pool, cpu_count

# ---------------- CONFIGURATION ----------------
BLOCK_SIZE = 3                  # lines per block
SIMILARITY_THRESHOLD = 0.9      # Jaccard token similarity
SIGNATURE_TOKENS_PER_BLOCK = 5  # how many tokens to index per block
LENGTH_RATIO_TOLERANCE = 0.3    # +/- 30% length window for candidates
LOW_VALUE_LINE_THRESHOLD = 20   # drop lines shorter than this after wikilink removal
# ------------------------------------------------

WORD_RE = re.compile(r"\w+")
WIKILINK_RE = re.compile(r"\[\[.*?\]\]")

def remove_wikilinks(text):
    """Remove any [[wikilink]] from a line but keep the rest."""
    return WIKILINK_RE.sub("", text)

def get_markdown_files():
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.md", "*.markdown"],
            capture_output=True,
            text=True,
            check=True,
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


def filter_lines(lines, ignore_wikilink=False, short_line_threshold=20):
    lines = strip_yaml_front_matter(lines)
    filtered = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("##"):
            continue

        # Remove wikilinks if enabled
        if ignore_wikilink:
            stripped = remove_wikilinks(stripped).strip()

        # Drop low-value lines (unified rule)
        if len(stripped) < short_line_threshold:
            continue

        filtered.append(stripped)

    return filtered


def tokenize(text):
    """Simple lowercased tokenization."""
    return set(WORD_RE.findall(text.lower()))


def jaccard(tokens_a, tokens_b):
    if not tokens_a or not tokens_b:
        return 0.0
    inter = len(tokens_a & tokens_b)
    if inter == 0:
        return 0.0
    union = len(tokens_a | tokens_b)
    return inter / union


def read_and_hash_file(args):
    """Read file, filter it, and return (file_path, filtered_lines, sha256_hash)."""
    file_path, ignore_wikilink = args
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.readlines()
        lines = filter_lines(raw, ignore_wikilink)
        joined = "\n".join(lines)
        h = hashlib.sha256(joined.encode("utf-8")).hexdigest()
        return (file_path, lines, h)
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return (file_path, [], None)


def extract_blocks(args):
    """Extract blocks (file_path, block_text, line_num) from filtered lines."""
    file_path, lines, block_size = args
    blocks = []
    for i in range(len(lines) - block_size + 1):
        block = "\n".join(lines[i : i + block_size])
        blocks.append((file_path, block, i + 1))
    return blocks


def effective_cpu_count():
    """Respect Kubernetes CPU quota if present."""
    try:
        quota_path = "/sys/fs/cgroup/cpu/cpu.cfs_quota_us"
        period_path = "/sys/fs/cgroup/cpu/cpu.cfs_period_us"
        with open(quota_path) as q:
            quota = int(q.read())
        with open(period_path) as p:
            period = int(p.read())
        if quota > 0 and period > 0:
            return max(1, quota // period)
    except Exception:
        pass
    return cpu_count()


def find_duplicates(
    files,
    block_size,
    similarity_threshold,
    ignore_wikilink=False,
    short_line_threshold=20,
):
    worker_count = effective_cpu_count()
    print(f"Using up to {worker_count} CPU workers for parallel scanning...\n")

    # Step 1: Parallel read + filter + hash
    print("Hashing files in parallel...")
    with Pool(processes=worker_count) as pool:
        results = pool.map(read_and_hash_file, [(f, ignore_wikilink) for f in files])

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
    with Pool(processes=worker_count) as pool:
        block_results = pool.map(extract_blocks, block_args)

    all_blocks = [item for sublist in block_results for item in sublist]
    print(f"Collected {len(all_blocks)} blocks from unique files.\n")

    # Step 5: Aggressive, indexed block-level duplicate detection
    canonical_blocks = []
    token_index = defaultdict(set)

    def select_signature_tokens(tokens):
        if not tokens:
            return []
        sorted_tokens = sorted(tokens)
        return sorted_tokens[:SIGNATURE_TOKENS_PER_BLOCK]

    for file_path, block_text, line_num in all_blocks:
        tokens = tokenize(block_text)
        length = len(block_text)

        sig_tokens = select_signature_tokens(tokens)
        if not sig_tokens:
            cb_idx = len(canonical_blocks)
            canonical_blocks.append(
                {"text": block_text, "tokens": tokens, "length": length,
                 "locations": [(file_path, line_num)]}
            )
            continue

        candidate_indices = set()
        for t in sig_tokens:
            candidate_indices.update(token_index.get(t, ()))

        matched = False
        for idx in candidate_indices:
            cb = canonical_blocks[idx]

            shorter = min(cb["length"], length)
            longer = max(cb["length"], length)
            if longer == 0:
                continue
            if (longer - shorter) / longer > LENGTH_RATIO_TOLERANCE:
                continue

            sim = jaccard(tokens, cb["tokens"])
            if sim >= similarity_threshold:
                cb["locations"].append((file_path, line_num))
                matched = True
                break

        if not matched:
            cb_idx = len(canonical_blocks)
            canonical_blocks.append(
                {"text": block_text, "tokens": tokens, "length": length,
                 "locations": [(file_path, line_num)]}
            )
            for t in sig_tokens:
                token_index[t].add(cb_idx)

    # Step 6: Keep only blocks appearing in >1 file
    duplicates = []
    for cb in canonical_blocks:
        files_for_block = {f for f, _ in cb["locations"]}
        if len(files_for_block) > 1:
            duplicates.append((cb["text"], cb["locations"]))

    return whole_file_dupes, duplicates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
    "--ignore-short-lines",
    type=int,
    default=20,
    help="Ignore any line shorter than N characters after processing (default: 20)",
    )
    parser.add_argument(
        "--ignore-wikilink",
        action="store_true",
        help="Strip wikilinks [[...]] and drop low-value lines (<20 chars)",
    )
    args = parser.parse_args()

    files = get_markdown_files()
    if not files:
        print("No Markdown files found in this Git repository.")
        return

    print(f"Scanning {len(files)} Markdown files...\n")
    whole_file_dupes, block_dupes = find_duplicates(
        files,
        BLOCK_SIZE,
        SIMILARITY_THRESHOLD,
        ignore_wikilink=args.ignore_wikilink,
        short_line_threshold=args.ignore_short_lines,
    )


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
