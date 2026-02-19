#!/usr/bin/env python3

"""
Traverse Markdown to Find Duplicate File Names

Features:
- Spinny cursor to know it is still running because it must scan everything.

"""



import os
import glob
import difflib
from collections import defaultdict
import itertools
import sys
import time

# Built with OpenAI during base "Helper Script Novice User", doesn't work as expected.
# https://chatgpt.com/share/c66dfbfe-941b-4dca-921b-5be5cd8beba6

# Function to display a spinning cursor for progress indication
def spin_cursor():
    spinner = itertools.cycle(['-', '\\', '|', '/'])
    while True:
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')

# Function to compare filenames based on n-grams while preserving order
def similar_names(name1, name2, threshold=0.8):
    ngrams1 = [name1[i:i+3] for i in range(len(name1)-2)]
    ngrams2 = [name2[i:i+3] for i in range(len(name2)-2)]
    s = difflib.SequenceMatcher(None, ngrams1, ngrams2)
    return s.ratio() > threshold

# Function to scan the Obsidian vault
def scan_obsidian_vault(vault_path, limit=None):
    if not os.path.isdir(os.path.join(vault_path, '.obsidian')):
        return "Error: Not a valid Obsidian vault directory."

    all_files = glob.glob(os.path.join(vault_path, '**/*.md'), recursive=True)
    if limit:
        all_files = all_files[:limit]
    
    file_info = [(os.path.basename(file_path), file_path) for file_path in all_files if os.path.isfile(file_path)]

    similar_matrix = {}
    spinner = spin_cursor()

    for i, (name1, path1) in enumerate(file_info):
        for j, (name2, path2) in enumerate(file_info):
            if i < j:
                if (name1, name2) not in similar_matrix:
                    similar_matrix[(name1, name2)] = similar_names(name1, name2)
                next(spinner)  # show progress

    sys.stdout.write('\b')  # clear spinner
    sys.stdout.flush()

    similar_files = defaultdict(list)
    for (name1, path1) in file_info:
        for (name2, path2) in file_info:
            if name1 != name2 and similar_matrix.get((name1, name2), False):
                size1 = os.path.getsize(path1)
                size2 = os.path.getsize(path2)
                similar_files[name1].append((name2, size2, path2))

    markdown_output = "# Similar Files in Obsidian Vault\n\n"
    for name1, matches in similar_files.items():
        size1 = os.path.getsize(dict(file_info)[name1])
        markdown_output += f"## {name1} ({size1} bytes)\n"
        for name2, size2, path2 in matches:
            markdown_output += f"- Match, [[{name1}]] ({size1} bytes) and [[{name2}]] ({size2} bytes)\n"
        markdown_output += "\n"

    return markdown_output

if __name__ == "__main__":
    # vault_path = "/d/WORKING-JustinHitt/GitHub/obsidian/"
    vault_path = "d:\\WORKING-JustinHitt\\GitHub\\obsidian\\"
    limit = 100  # Limit the number of files for testing
    result = scan_obsidian_vault(vault_path, limit)
    print(result)
