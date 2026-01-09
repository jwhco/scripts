import os
import re
import multiprocessing

def extract_tasks_from_file(file_path):
    """
    Reads a file and returns a list of left-aligned task strings.
    """
    tasks = []
    # Pattern matches standard markdown task: - [ ]
    # Also handles potential leading whitespace by stripping it later
    task_pattern = re.compile(r'^\s*-\s*\[ \].*')
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if task_pattern.match(line):
                    # Left-align by stripping leading whitespace
                    tasks.append(line.lstrip().rstrip())
    except Exception:
        # Silently skip files that can't be read (e.g. permission issues)
        pass
    return tasks

def main(root_dir='.'):
    # Collect all markdown file paths recursively
    md_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))

    if not md_files:
        print("No markdown files found.")
        return

    # Use multiprocessing to parse files in parallel
    # This is significantly faster for large Obsidian vaults
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(extract_tasks_from_file, md_files)

    # Flatten the list of lists and print
    for task_list in results:
        for task in task_list:
            if task:
                print(task)

if __name__ == "__main__":
    # Change '.' to your vault path if running outside the vault directory
    main('.')