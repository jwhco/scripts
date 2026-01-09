import os
import re
import argparse
import multiprocessing
import pandas as pd
import hashlib
import uuid

def generate_short_id():
    """Generates a unique 6-character ID (Obsidian Tasks style)."""
    return uuid.uuid4().hex[:6]

def get_hash(text):
    if not text: return ""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]

def standardize_and_id(line, force_fix=False):
    """
    Standardizes a task line and adds an ID if missing.
    Maintains the leading indentation.
    """
    # 1. Capture leading whitespace/indentation
    match = re.match(r'^(\s*-\s*\[ \]\s*)(.*)', line)
    if not match:
        return line, False

    indent, body = match.groups()
    
    # 2. Extract existing metadata
    meta_pattern = re.compile(r'\[(\w+)::\s*([^\]]+)\]')
    metadata = {m[0]: m[1].strip() for m in meta_pattern.findall(body)}
    
    # 3. Check for existing ID
    modified = False
    if 'id' not in metadata:
        if force_fix:
            metadata['id'] = generate_short_id()
            modified = True
    
    # 4. Standardize: Remove metadata from description to rebuild it at the end
    description = meta_pattern.sub('', body).strip()
    
    # Reconstruct the line: Indent + Description + Metadata
    meta_str = " ".join([f"[{k}:: {v}]" for k, v in metadata.items()])
    new_line = f"{indent}{description} {meta_str}".rstrip() + "\n"
    
    return new_line, modified

def process_file_inplace(file_path, force_fix=False):
    """Reads and potentially rewrites a file line-by-line."""
    modified_count = 0
    new_lines = []
    task_pattern = re.compile(r'^\s*-\s*\[ \].*')

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for line in lines:
            if task_pattern.match(line):
                new_line, was_fixed = standardize_and_id(line, force_fix)
                new_lines.append(new_line)
                if was_fixed:
                    modified_count += 1
            else:
                new_lines.append(line)

        if force_fix and modified_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
                
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        
    return modified_count

def main():
    parser = argparse.ArgumentParser(description="Obsidian Task ID Fixer and Standardizer")
    parser.add_argument("directory", nargs="?", default=".", help="Vault directory")
    parser.add_argument("--fix-id", type=str, choices=['dry', 'true'], default='dry', 
                        help="Generate missing IDs. 'dry' (default) only reports; 'true' writes to disk.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files scanned")
    args = parser.parse_args()

    # 1. Collect Files
    all_files = []
    for root, _, files in os.walk(args.directory):
        for f in files:
            if f.endswith('.md'):
                all_files.append(os.path.join(root, f))
                if args.limit and len(all_files) >= args.limit: break
        if args.limit and len(all_files) >= args.limit: break

    # 2. Process Files
    is_live = (args.fix_id == 'true')
    print(f"--- Running in {'LIVE' if is_live else 'DRY RUN'} mode ---")
    
    # Use starmap to pass the 'force_fix' flag
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        results = pool.starmap(process_file_inplace, [(f, is_live) for f in all_files])

    total_modified = sum(results)
    
    if is_live:
        print(f"Successfully modified {total_modified} tasks across {len(all_files)} files.")
    else:
        print(f"Dry Run: {total_modified} tasks would receive a new ID and be standardized.")

if __name__ == "__main__":
    main()