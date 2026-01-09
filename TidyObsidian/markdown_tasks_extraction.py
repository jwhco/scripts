import os
import re
import argparse
import multiprocessing
import pandas as pd

def parse_task_line(line):
    """
    Extracts description and all [key:: value] pairs into a dictionary.
    """
    # Regex to find all Dataview metadata
    metadata_pattern = re.compile(r'\[(\w+)::\s*([^\]]+)\]')
    metadata = {m[0]: m[1].strip() for m in metadata_pattern.findall(line)}
    
    # Remove the metadata from the line to get the raw description
    description = metadata_pattern.sub('', line).replace('- [ ]', '').strip()
    
    return {
        "raw_text": line.strip(),
        "description": description,
        "metadata": metadata
    }

def worker(file_paths):
    """
    Processes a batch of files and returns a list of task records.
    """
    task_pattern = re.compile(r'^\s*-\s*\[ \].*')
    batch_results = []
    
    for path in file_paths:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if task_pattern.match(line):
                        task_data = parse_task_line(line)
                        task_data['file_source'] = path
                        batch_results.append(task_data)
        except Exception:
            pass
    return batch_results

def main():
    parser = argparse.ArgumentParser(description="High-speed Obsidian Task Parser")
    parser.add_argument("directory", nargs="?", default=".", help="Vault directory")
    parser.add_argument("--standardize", action="store_true", help="Display Tasks in Dataview-compliant format")
    args = parser.parse_args()

    # 1. Collect file list (The 'Find' phase)
    all_files = []
    for root, _, files in os.walk(args.directory):
        for f in files:
            if f.endswith('.md'):
                all_files.append(os.path.join(root, f))

    if not all_files:
        print("No markdown files found.")
        return

    # 2. Batching for Multiprocessing (The 'Extract' phase)
    num_procs = multiprocessing.cpu_count()
    chunk_size = len(all_files) // num_procs + 1
    chunks = [all_files[i:i + chunk_size] for i in range(0, len(all_files), chunk_size)]

    with multiprocessing.Pool(num_procs) as pool:
        # Results is a list of lists of dictionaries
        results = pool.map(worker, chunks)

    # Flatten results into a single list of dicts
    flattened = [item for sublist in results for item in sublist]

    # 3. Load into Pandas (The 'Future Analysis' phase)
    df = pd.DataFrame(flattened)

    if df.empty:
        print("No tasks found.")
        return

    # 4. Display/Standardization (The 'Output' phase)
    if args.standardize:
        def format_row(row):
            meta_str = " ".join([f"[{k}:: {v}]" for k, v in row['metadata'].items()])
            return f"- [ ] {row['description']} {meta_str}".strip()
        
        # Apply the standardization across the Series and print
        print("\n".join(df.apply(format_row, axis=1).tolist()))
    else:
        # Simple print of description only or raw_text
        print("\n".join(df['raw_text'].tolist()))

if __name__ == "__main__":
    main()