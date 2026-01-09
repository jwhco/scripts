import os
import re
import multiprocessing
import argparse

def standardize_task(task_text):
    """
    Extracts [key:: value] metadata and moves it to the end of the task string.
    Example: "- [ ] [priority:: high] Buy milk [due:: 2026-01-16]"
    Becomes: "- [ ] Buy milk [priority:: high] [due:: 2026-01-16]"
    """
    # Regex to find [key:: value] patterns
    metadata_pattern = re.compile(r'\[\w+::\s*[^\]]+\]')
    
    # Extract all metadata matches
    metadata_items = metadata_pattern.findall(task_text)
    
    # Remove metadata from the original text to isolate the description
    description = metadata_pattern.sub('', task_text)
    
    # Clean up whitespace: remove the task marker, strip, then put marker back
    # This ensures "left-align" and removes gaps left by extracted metadata
    clean_desc = re.sub(r'^\s*-\s*\[ \]', '', description).strip()
    
    # Reconstruct the task: Marker + Description + All Metadata
    standardized = f"- [ ] {clean_desc} " + " ".join(metadata_items)
    return standardized.strip()

def process_file(file_path, standardize=False):
    """
    Reads a file and returns a collection of tasks.
    """
    tasks = []
    task_pattern = re.compile(r'^\s*-\s*\[ \].*')
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if task_pattern.match(line):
                    task = line.lstrip().rstrip()
                    if standardize:
                        task = standardize_task(task)
                    tasks.append(task)
    except Exception:
        pass
    return tasks

def main():
    parser = argparse.ArgumentParser(description="Extract and standardize Obsidian Tasks.")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to scan (default: current)")
    parser.add_argument("--standardize", action="store_true", help="Move metadata [key:: value] to the end of the line.")
    args = parser.parse_args()

    md_files = []
    for root, _, files in os.walk(args.directory):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))

    if not md_files:
        print("No markdown files found.")
        return

    # Use a Pool to process files into a collection of tasks
    # Passing the 'standardize' flag into the worker function
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        # We use a starmap or a wrapper to pass multiple arguments to the processor
        results = pool.starmap(process_file, [(f, args.standardize) for f in md_files])

    # Flatten the collection for display
    all_tasks = [task for sublist in results for task in sublist]

    for task in all_tasks:
        print(task)

if __name__ == "__main__":
    main()