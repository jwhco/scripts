

"""
Markdown Tasks Library

- For quality assurance and management of markdown tasks following Obsidian Dataview Tasks format.

"""



import os
import re
from collections import defaultdict

def extract_tasks_from_line(line):
    """Parse a single markdown task line into task data.
    Example: '- [ ] #Project, Title of Project. [id:: A1B2C3] [dependsOn:: X9Y8Z7]'
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
    full_text = text_match.group(1).strip()
    task['text'] = full_text

    # Extract Obsidian Dataview metadata [key:: value]
    metadata_pattern = re.compile(r'\[(\w+)::\s*([^\]]+)\]')
    metadata = {}
    for match in metadata_pattern.finditer(full_text):
        key = match.group(1).lower()
        value = match.group(2).strip()
        metadata[key] = value
    
    task['id'] = metadata.get('id')
    task['priority'] = metadata.get('priority')
    task['due'] = metadata.get('due')
    task['created'] = metadata.get('created')
    task['dependson'] = metadata.get('dependson')
    
    # Extract hashtags (#Project)
    tags_pattern = re.compile(r'#(\w+)')
    tags = [tag.lower() for tag in tags_pattern.findall(full_text)]
    task['tags'] = tags if tags else []

    # Extract dependencies (dependsOn field)
    dependencies = []
    if task.get('dependson'):
        dependencies = [dep.strip() for dep in task['dependson'].split(',')]
    task['dependencies'] = dependencies

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