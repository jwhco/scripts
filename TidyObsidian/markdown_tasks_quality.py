import os
import re
import argparse
import multiprocessing
import pandas as pd
import sys

def standardize_task_line(line):
    """
    Core logic: Deconstructs a line, repairs malformed parts, 
    and rebuilds it to the 'Perfect Standard'.
    """
    # 1. Isolate leading structure (indentation + marker + checkbox)
    # This regex is surgical: it preserves the exact leading whitespace (\t or spaces)
    match = re.match(r'^([\t ]*[-*]\s*\[ . \]\s*)(.*)', line)
    if not match:
        return line, False

    prefix, body = match.groups()
    
    # 2. Heuristic Repair: Fix single colon metadata [key: val] -> [key:: val]
    # We do this before extraction so the main regex picks them up
    repaired_body = re.sub(r'\[(\w+):\s*([^\]]+)\]', r'[\1:: \2]', body)

    # 3. Extract all valid metadata [key:: value]
    meta_pattern = re.compile(r'\[(\w+)::\s*([^\]]+)\]')
    metadata_items = meta_pattern.findall(repaired_body)
    
    # 4. Extract Description (everything NOT a metadata box)
    description_raw = meta_pattern.sub('', repaired_body)
    
    # 5. Emoji to Dataview Conversion
    emoji_map = {
        '📅': 'due', '🛫': 'start', '⏳': 'scheduled', 
        '✅': 'completed', '➕': 'created', 
        '⏫': 'priority_high', '🔼': 'priority_medium', '🔽': 'priority_low'
    }
    
    metadata = {k: v.strip() for k, v in metadata_items}
    
    for emoji, key in emoji_map.items():
        if emoji in description_raw:
            emoji_regex = re.compile(fr'{emoji}\s*([\d\w\-\:]+)?')
            val_match = emoji_regex.search(description_raw)
            if val_match and val_match.group(1):
                metadata[key] = val_match.group(1).strip()
                description_raw = emoji_regex.sub('', description_raw)
            else:
                metadata[key] = 'true'
                description_raw = description_raw.replace(emoji, '')

    # 6. Final Cleaning
    # Collapse multiple spaces into one, trim ends
    clean_description = " ".join(description_raw.split()).strip()
    
    # 7. Rebuild the Task
    # Force single space between description and metadata, and between metadata boxes
    meta_str = " ".join([f"[{k}:: {v}]" for k, v in metadata.items()])
    
    # Standardize the prefix to " - [ ] " (one space after the marker)
    # but KEEP the 'leading_indent' (the \t or spaces before the dash)
    # We extract the leading indent from the original prefix
    indent_only = re.match(r'^([\t ]*)', prefix).group(1)
    marker_char = "-" # Standardize * to -
    checkbox = "[ ] " if "[ ]" in prefix else "[x] "
    final_prefix = f"{indent_only}{marker_char} {checkbox}"
    
    standardized_line = f"{final_prefix}{clean_description} {meta_str}".rstrip() + "\n"
    
    # 8. Compare
    # If the standardized version differs from the original, we have a modification
    return standardized_line, standardized_line != line

def process_file(file_path, live=False):
    """Line-by-line processor using the standardization logic."""
    modified_count = 0
    new_lines = []
    # Add a counter to track the number of tasks reviewed
    reviewed_count = 0
    # Updated task pattern to only match incomplete tasks
    task_pattern = re.compile(r'^[\t ]*[-*]\s*\[ \].*')

    # Add logic to fix malformed tasks with '-\t[ ]' pattern
    malformed_task_pattern = re.compile(r'^([\t ]*)-\t\[ \](.*)')

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # We use a simple list here for line-by-line processing, 
        # but the transformation itself is "atomic" per line
        # Refined debugging to only log non-standard markdown tasks that couldn't be fixed
        # Ensure 'new_line' is always defined before use
        # Skip completed tasks explicitly
        for line in lines:
            if malformed_task_pattern.match(line):
                reviewed_count += 1
                line = malformed_task_pattern.sub(r'\1- [ ] \2', line)  # Fix the malformed task
                new_line, was_modified = standardize_task_line(line)
                if not was_modified:
                    print(f"Non-standard task could not be fixed: {line}", file=sys.stderr)
            elif task_pattern.match(line):
                reviewed_count += 1
                new_line, was_modified = standardize_task_line(line)
                if not was_modified:
                    print(f"Non-standard task could not be fixed: {line}", file=sys.stderr)
            elif re.match(r'^[\t ]*[-*]\s*\[x\].*', line):
                continue  # Skip completed tasks
            else:
                new_line = line  # Default to the original line if no match
                was_modified = False  # Ensure was_modified is defined
            new_lines.append(new_line)
            if was_modified:
                modified_count += 1

        print(f"Reviewed {reviewed_count} tasks in file: {file_path}", file=sys.stderr)

        if live and modified_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
                
    except Exception as e:
        # Enhanced error logging in process_file
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        
    return modified_count

def main():
    parser = argparse.ArgumentParser(description="Quality Control: Surgical Task Standardizer")
    parser.add_argument("dir", nargs="?", default=".", help="Vault directory")
    parser.add_argument("--fixtasks", nargs="?", const="dry", choices=['dry', 'true'], 
                        help="Standardize tasks: 'dry' (report only) or 'true' (modify disk)")
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    is_live = (args.fixtasks == 'true')

    # Collect files ignoring hidden directories
    all_files = []
    # Adjusted file collection to include additional markdown extensions
    for root, dirs, fs in os.walk(args.dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in fs:
            if f.endswith(('.md', '.markdown')):
                all_files.append(os.path.join(root, f))

    print(f"--- Quality Audit: {len(all_files)} files ---", file=sys.stderr)
    
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        counts = pool.starmap(process_file, [(f, is_live) for f in all_files])

    total = sum(counts)
    status = "REPAIRED/MODIFIED" if is_live else "NON-STANDARD FOUND"
    print(f"{status}: {total} tasks.", file=sys.stderr)

if __name__ == "__main__":
    main()