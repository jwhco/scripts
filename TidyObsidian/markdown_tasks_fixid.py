import os
import re
import argparse
import multiprocessing
import uuid
import sys

def generate_short_id():
    """Generates a unique 6-character ID."""
    return uuid.uuid4().hex[:6]

def process_file(file_path, live=False):
    """
    Reads a file, identifies tasks missing IDs, and optionally fixes them.
    Preserves exact indentation for outlines and nested lists.
    """
    # Pattern captures: 1. Indentation/Marker, 2. The rest of the line
    task_pattern = re.compile(r'^(\s*-\s*\[ \]\s*)(.*)')
    meta_pattern = re.compile(r'\[(\w+)::\s*([^\]]+)\]')
    modified_count = 0
    new_lines = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for line in lines:
            match = task_pattern.match(line)
            if match:
                indent, body = match.groups()
                # Parse existing metadata into a dict
                meta = {m[0]: m[1].strip() for m in meta_pattern.findall(body)}
                
                # Logic: If ID is missing, we create one and trigger standardization
                if 'id' not in meta:
                    meta['id'] = generate_short_id()
                    modified_count += 1
                    
                    # Standardize: Extract pure description and append metadata to end
                    description = meta_pattern.sub('', body).strip()
                    meta_str = " ".join([f"[{k}:: {v}]" for k, v in meta.items()])
                    new_lines.append(f"{indent}{description} {meta_str}".rstrip() + "\n")
                else:
                    # If ID exists, we leave the line exactly as it was found
                    new_lines.append(line)
            else:
                # Non-task lines remain untouched (preserves outlines/notes)
                new_lines.append(line)

        if live and modified_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
                
    except Exception as e:
        # Standard error for issues so it doesn't pollute piped output
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        
    return modified_count

def main():
    parser = argparse.ArgumentParser(
        description="Renegade Task Manipulator: Idempotently add IDs and standardize tasks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example Usage:
  python markdown_tasks_fixid.py . --fix-id dry    # Scan and report potential changes
  python markdown_tasks_fixid.py . --fix-id true   # EXECUTE: Modify files on disk
  python markdown_tasks_fixid.py . --limit 10      # Test against a small subset of files
        """
    )
    parser.add_argument("dir", nargs="?", help="The directory/vault to process")
    parser.add_argument("--fix-id", type=str, choices=['dry', 'true'], 
                        help="Mode: 'dry' (report only) or 'true' (write to disk)")
    parser.add_argument("--limit", type=int, help="Limit scanning to the first N files found")

    # If no arguments are provided, print help and exit
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    
    # Validation: Ensure a directory was provided if we got past the help check
    target_dir = args.dir if args.dir else "."

    # 1. Collect Files
    files = []
    for root, _, fs in os.walk(target_dir):
        for f in fs:
            if f.endswith('.md'):
                files.append(os.path.join(root, f))
                if args.limit and len(files) >= args.limit:
                    break
        if args.limit and len(files) >= args.limit:
            break

    if not files:
        print("No markdown files found in the specified directory.", file=sys.stderr)
        return

    # 2. Execute with Multiprocessing
    is_live = (args.fix_id == 'true')
    print(f"--- Processing {len(files)} files ({'LIVE MODE' if is_live else 'DRY RUN'}) ---", file=sys.stderr)
    
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        counts = pool.starmap(process_file, [(f, is_live) for f in files])

    total_modified = sum(counts)
    
    # 3. Final Report
    status = "MODIFIED" if is_live else "WOULD REQUIRE FIX"
    print(f"--- Task Summary ---", file=sys.stderr)
    print(f"{status}: {total_modified} tasks.", file=sys.stderr)

if __name__ == "__main__":
    main()