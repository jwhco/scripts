import os
import re
import argparse
import multiprocessing
import pandas as pd
import hashlib

def get_hash(text):
    """Returns a stable hex hash of the input text to avoid comma issues."""
    if not text:
        return ""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]

def parse_task_line(line):
    """Extracts description and all [key:: value] pairs into a dictionary."""
    metadata_pattern = re.compile(r'\[(\w+)::\s*([^\]]+)\]')
    metadata = {m[0]: m[1].strip() for m in metadata_pattern.findall(line)}
    description = metadata_pattern.sub('', line).replace('- [ ]', '').strip()
    
    return {
        "raw_text": line.strip(),
        "description": description,
        "metadata": metadata,
        "desc_hash": get_hash(description)
    }

def worker(file_paths):
    """Processes a batch of files and returns a list of task records."""
    task_pattern = re.compile(r'^\s*-\s*\[ \].*')
    batch_results = []
    
    for path in file_paths:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if task_pattern.match(line):
                        task_data = parse_task_line(line)
                        task_data['file_source'] = path
                        # Extract the ID into its own field for sorting logic
                        task_data['id'] = task_data['metadata'].get('id', '')
                        deps = task_data['metadata'].get('dependson', '')
                        task_data['deps_hash'] = get_hash(deps) if deps else ""
                        batch_results.append(task_data)
        except Exception:
            pass
    return batch_results

def main():
    parser = argparse.ArgumentParser(description="High-speed Renegade Task Extractor")
    parser.add_argument("directory", nargs="?", default=".", help="Vault directory")
    parser.add_argument("--standardize", action="store_true", help="Display Tasks in Dataview format (Sorted by ID Desc)")
    parser.add_argument("--csv", action="store_true", help="Output in CSV format (Sorted by ID Desc)")
    parser.add_argument("--limit", type=int, default=None, help="Stop after finding N files with tasks")
    args = parser.parse_args()

    # 1. Collection Phase (Ignoring hidden dirs)
    all_files = []
    for root, dirs, files in os.walk(args.directory):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if f.endswith('.md'):
                all_files.append(os.path.join(root, f))
                if args.limit and len(all_files) >= args.limit:
                    break
        if args.limit and len(all_files) >= args.limit:
            break

    # 2. Extraction Phase (Multiprocessing)
    num_procs = multiprocessing.cpu_count()
    if not all_files:
        return
        
    chunk_size = max(1, len(all_files) // num_procs)
    chunks = [all_files[i:i + chunk_size] for i in range(0, len(all_files), chunk_size)]

    with multiprocessing.Pool(num_procs) as pool:
        results = pool.map(worker, chunks)

    flattened = [item for sublist in results for item in sublist]
    df = pd.DataFrame(flattened)

    if df.empty:
        return

    # 3. Logic: If using standardized, CSV, or limit, sort by ID descending
    # Tasks with IDs will appear at the top in descending order.
    if args.standardize or args.csv or args.limit:
        # Sort by 'id' descending. empty strings go to bottom.
        df = df.sort_values(by='id', ascending=False, na_position='last')

    # 4. Output Phase
    if args.csv:
        df['created'] = df['metadata'].apply(lambda x: x.get('created', ''))
        df['priority'] = df['metadata'].apply(lambda x: x.get('priority', ''))
        df['due'] = df['metadata'].apply(lambda x: x.get('due', ''))
        output_cols = ['id', 'created', 'priority', 'due', 'desc_hash', 'deps_hash']
        print(df[output_cols].to_csv(index=False))

    elif args.standardize:
        def format_row(row):
            meta_str = " ".join([f"[{k}:: {v}]" for k, v in row['metadata'].items()])
            return f"- [ ] {row['description']} {meta_str}".strip()
        print("\n".join(df.apply(format_row, axis=1).tolist()))
        
    else:
        # Default: Raw unsorted list
        print("\n".join(df['raw_text'].tolist()))

if __name__ == "__main__":
    main()