
"""
Markdown Tasks - Tree

- Walk task structure to create visual tree of relationships.

"""

import argparse
import os
import re
from collections import defaultdict
from markdowntasks import extract_tasks_from_line, get_tasks_from_file

def build_dependency_tree(tasks, root_tag=None):
    """Build a hierarchical dependency tree from tasks.
    """
    tree = defaultdict(list)
    task_map = {}

    # Create task map and identify root tasks
    for task in tasks:
        if not task:
            continue
        task_id = f"{task['text']}-{id(task)}"
        task_map[task_id] = task
        if root_tag and any(tag == root_tag for tag in task.get('tags', [])):
            tree['root'].append(task_id)
        else:
            # Find dependencies that exist in task_map
            for dep in task.get('dependencies', []):
                if dep in task_map:
                    tree[dep].append(task_id)
    return tree, task_map


def display_tree(tree, task_map, indent=0, max_depth=3):
    """Display the dependency tree in ANSI format.
    """
    if not tree:
        return
    for node in tree:
        # Display node with indentation
        if node == 'root':
            print(' ' * indent + '└── Tasks')
        else:
            print(' ' * indent + '└── ' + node)
        # Recursively display children if within max_depth
        if max_depth > 0:
            display_tree(tree[node], task_map, indent + 2, max_depth - 1)


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
  %(prog)s --channel work --directory /path/to/notes
        """
    )
    
    # Filter options (mutually exclusive)
    filter_group = parser.add_mutually_exclusive_group(required=True)
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
        '--directory',
        default='.',
        help='Directory to search for markdown files (default: current directory)'
    )
    parser.add_argument(
        '--recursive',
        action='store_true',
        default=True,
        help='Search recursively (default: True)'
    )
    parser.add_argument(
        '--max-depth',
        type=int,
        default=3,
        help='Maximum depth to display in the tree (default: 3)'
    )
    
    args = parser.parse_args()
    
    # Get all tasks from markdown files
    try:
        tasks = get_tasks_from_directory(args.directory, args.recursive)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    # Filter tasks based on the specified filter
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
    
    # Sort tasks by urgency
    filtered_tasks = sort_tasks_by_urgency(filtered_tasks)
    
    # Apply limit if specified
    if args.limit and len(filtered_tasks) > args.limit:
        print(f"Showing top {args.limit} of {len(filtered_tasks)} tasks with {filter_type} '{filter_value}'")
        filtered_tasks = filtered_tasks[:args.limit]
    else:
        print(f"Showing {len(filtered_tasks)} tasks with {filter_type} '{filter_value}'")
    
    # Build and display dependency tree
    tree, task_map = build_dependency_tree(filtered_tasks)
    display_tree(tree, task_map, max_depth=args.max_depth)
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())