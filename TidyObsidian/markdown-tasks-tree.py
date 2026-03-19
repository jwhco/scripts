
"""
Markdown Tasks - Tree

- Walk task structure to create visual tree of relationships.

"""

import argparse
import os
import re
import sys
from collections import defaultdict
from markdowntasks import extract_tasks_from_line, get_tasks_from_file, get_tasks_from_directory

def build_dependency_tree(filtered_tasks, all_tasks):
    """Build a hierarchical dependency tree from filtered tasks and their dependencies.
    
    Shows which tasks depend on the filtered root tasks.
    
    Args:
        filtered_tasks: Tasks to use as root nodes (from filter/limit)
        all_tasks: All tasks in the corpus to find dependents from
    
    Returns:
        Tuple of (graph, task_map, root_task_ids)
    """
    # Create a lookup map for all tasks by their ID
    task_by_id = {}
    all_tasks_list = []
    for task in all_tasks:
        task_id = task.get('id')
        if task_id:
            task_by_id[task_id] = task
        all_tasks_list.append(task)
    
    # Build reverse dependency map: task_id -> [tasks that depend on this task]
    reverse_deps = defaultdict(list)
    for task in all_tasks_list:
        for dep_id in task.get('dependencies', []):
            if dep_id:
                reverse_deps[dep_id].append(task)
    
    # Graph: parent_task_id -> [child_task_ids]
    graph = defaultdict(list)
    task_map = {}
    visited = set()
    
    def add_task_tree(task, depth=0):
        """Recursively add task and its dependents to the graph."""
        task_id = task.get('id')
        if not task_id or task_id in visited or depth > 10:
            return
        visited.add(task_id)
        task_map[task_id] = task
        
        # Find tasks that depend on this task (direct dependents)
        for dependent_task in reverse_deps.get(task_id, []):
            dep_task_id = dependent_task.get('id')
            if dep_task_id and dep_task_id not in visited:
                graph[task_id].append(dep_task_id)
                add_task_tree(dependent_task, depth + 1)
    
    # Get root task IDs from filtered tasks
    root_task_ids = []
    for task in filtered_tasks:
        task_id = task.get('id')
        if task_id:
            root_task_ids.append(task_id)
            add_task_tree(task)
        else:
            # Task without ID - use a generated one for display
            gen_id = f"_unnamed_{id(task)}"
            task['_id'] = gen_id
            root_task_ids.append(gen_id)
            task_map[gen_id] = task
    
    return graph, task_map, root_task_ids


def display_tree(graph, task_map, root_tasks=None, indent=0, max_depth=3, visited=None):
    """Display the dependency tree in ANSI format with task descriptions.
    
    Args:
        graph: Dependency graph (parent -> [children])
        task_map: Task ID -> task object mapping
        root_tasks: List of root task IDs to start from
        indent: Current indentation level
        max_depth: Maximum tree depth
        visited: Set of already-visited task IDs to prevent duplicates
    """
    if visited is None:
        visited = set()
    
    if not root_tasks:
        # Start with tasks that have no parents (root tasks from filtered set)
        root_tasks = [tid for tid in task_map.keys() 
                      if tid not in visited]
    
    if max_depth <= 0 or not root_tasks:
        return
    
    for task_id in root_tasks:
        if task_id in visited:
            continue
        visited.add(task_id)
        
        task = task_map.get(task_id)
        if not task:
            continue
        
        # Format: indent + box corner + task text + status
        status_char = 'x' if task.get('status') == 'done' else ' '
        task_text = task.get('text', 'Unknown')
        prefix = '└── ' if indent > 0 else ''
        print(' ' * indent + prefix + f"[{status_char}] {task_text}")
        
        # Recursively display children
        children = graph.get(task_id, [])
        if children:
            display_tree(graph, task_map, children, indent + 4, max_depth - 1, visited)


def filter_tasks_by_hashtag(tasks, hashtag):
    """Filter tasks that contain the specified hashtag.
    """
    filtered_tasks = []
    for task in tasks:
        if hashtag in task.get('tags', []):
            filtered_tasks.append(task)
    return filtered_tasks


def filter_tasks_by_catalog(tasks, catalog):
    """Filter tasks by catalog (implementation depends on catalog format).
    """
    filtered_tasks = []
    for task in tasks:
        # This is a placeholder - implementation depends on how catalogs are stored
        if catalog in task.get('tags', []) or catalog in task.get('text', ''):
            filtered_tasks.append(task)
    return filtered_tasks


def filter_tasks_by_channel(tasks, channel):
    """Filter tasks by channel (implementation depends on channel format).
    """
    filtered_tasks = []
    for task in tasks:
        # This is a placeholder - implementation depends on how channels are stored
        if channel in task.get('tags', []) or channel in task.get('text', ''):
            filtered_tasks.append(task)
    return filtered_tasks


def sort_tasks_by_urgency(tasks):
    """Sort tasks by urgency (implementation to be defined).
    """
    # Placeholder sorting - could be based on:
    # - Number of dependents
    # - Due dates
    # - Project importance
    # - Status (todo vs done)
    return sorted(tasks, key=lambda x: (x.get('status', 'todo'), x.get('text', '')))


def get_tasks_from_source(source):
    """Get tasks from various input sources: stdin (-), file, or directory.
    """
    tasks = []
    
    if source == '-':
        # Read from stdin
        for line in sys.stdin:
            task = extract_tasks_from_line(line)
            if task:
                task['file'] = '<stdin>'
                tasks.append(task)
    elif os.path.isfile(source):
        # Single file
        tasks = get_tasks_from_file(source)
    elif os.path.isdir(source):
        # Directory - recurse
        tasks = get_tasks_from_directory(source, recursive=True)
    else:
        raise ValueError(f"Source '{source}' is not a valid file or directory")
    
    return tasks


def main():
    """Main function to parse arguments and run the script.
    """
    parser = argparse.ArgumentParser(
        description='Display markdown tasks in a dependency tree.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --hashtag Project
  %(prog)s --catalog personal --limit 5
  cat file.md | %(prog)s --channel work -
  %(prog)s /path/to/notes
        """
    )
    
    parser.add_argument(
        'source',
        nargs='?',
        default='.',
        help='Input source: directory (default: current), file path, or - for stdin'
    )
    
    # Filter options (mutually exclusive, optional)
    filter_group = parser.add_mutually_exclusive_group(required=False)
    filter_group.add_argument(
        '--hashtag',
        help='Filter tasks by hashtag'
    )
    filter_group.add_argument(
        '--catalog',
        help='Filter tasks by catalog'
    )
    filter_group.add_argument(
        '--channel',
        help='Filter tasks by channel'
    )
    
    # Options
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit to top N tasks'
    )
    parser.add_argument(
        '--max-depth',
        type=int,
        default=3,
        help='Maximum depth to display in the tree (default: 3)'
    )
    
    args = parser.parse_args()
    
    # Get all tasks from source (stdin, file, or directory)
    try:
        tasks = get_tasks_from_source(args.source)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    # Filter tasks based on the specified filter (optional)
    if args.hashtag:
        filtered_tasks = filter_tasks_by_hashtag(tasks, args.hashtag)
        filter_type = "hashtag"
        filter_value = args.hashtag
    elif args.catalog:
        filtered_tasks = filter_tasks_by_catalog(tasks, args.catalog)
        filter_type = "catalog"
        filter_value = args.catalog
    elif args.channel:
        filtered_tasks = filter_tasks_by_channel(tasks, args.channel)
        filter_type = "channel"
        filter_value = args.channel
    else:
        # No filter applied, show all tasks
        filtered_tasks = tasks
        filter_type = None
        filter_value = None
    
    # Sort tasks by urgency
    filtered_tasks = sort_tasks_by_urgency(filtered_tasks)
    
    # Apply limit if specified
    if args.limit and len(filtered_tasks) > args.limit:
        if filter_type:
            print(f"Showing top {args.limit} of {len(filtered_tasks)} tasks with {filter_type} '{filter_value}'")
        else:
            print(f"Showing top {args.limit} of {len(filtered_tasks)} tasks")
        filtered_tasks = filtered_tasks[:args.limit]
    else:
        if filter_type:
            print(f"Showing {len(filtered_tasks)} tasks with {filter_type} '{filter_value}'")
        else:
            print(f"Showing {len(filtered_tasks)} tasks")
    
    # Build and display dependency tree
    # Include all dependencies of the filtered tasks
    graph, task_map, root_task_ids = build_dependency_tree(filtered_tasks, tasks)
    
    display_tree(graph, task_map, root_task_ids, max_depth=args.max_depth)
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())