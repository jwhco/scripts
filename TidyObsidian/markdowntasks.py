# tidy_obsidian.py - Shared library for TidyObsidian scripts

import re
from collections import defaultdict

def extract_tasks_from_line(line):
    """Parse a single markdown task line into task data.
    Example: '- [ ] #Project, Title of Project.'
    """
    task = {}
    # Extract task status
    if line.startswith('- [ ]'):
        task['status'] = 'todo'
    elif line.startswith('- [x]'):
        task['status'] = 'done'
    else:
        return None

    # Extract task text
    text_match = re.search(r'\] (.*)', line)
    if not text_match:
        return None
    task['text'] = text_match.group(1).strip()

    # Extract tags
    tags_match = re.search(r'#([^\s]+)', line)
    if tags_match:
        task['tags'] = [tag.strip() for tag in tags_match.group(1).split(',')]
    else:
        task['tags'] = []

    # Extract dependencies
    dep_match = re.search(r'\[[^\]]+\]', line)
    if dep_match:
        task['dependencies'] = [dep.strip()[1:-1] for dep in dep_match.group(0).split('->')]
    else:
        task['dependencies'] = []

    return task


def get_tasks_from_file(file_path):
    """Extract all tasks from a markdown file.
    """
    tasks = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                task = extract_tasks_from_line(line)
                if task:
                    task['file'] = file_path
                    tasks.append(task)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return tasks


def get_tasks_from_directory(directory, recursive=True):
    """Extract tasks from all markdown files in a directory.
    """
    tasks = []
    md_extensions = ('.md', '.markdown')
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(md_extensions):
                file_path = os.path.join(root, file)
                file_tasks = get_tasks_from_file(file_path)
                tasks.extend(file_tasks)
        
        if not recursive:
            break
    
    return tasks


def add_task_ids(tasks):
    """Add unique IDs to tasks that don't have them.
    """
    for task in tasks:
        if 'id' not in task:
            # Create a simple hash-based ID
            task_text = task['text']
            task_id = f"task_{hash(task_text)}"
            task['id'] = task_id
    return tasks