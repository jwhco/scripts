import os
import re
import argparse
import multiprocessing
import uuid
import sys

def generate_short_id(existing_ids):
    """Generates a 6-char ID that is guaranteed not to be in existing_ids."""
    while True:
        new_id = uuid.uuid4().hex[:6]
        if new_id not in existing_ids:
            return new_id

def audit_file_for_ids(file_path):
    """Fast scan of a file to extract all existing [id:: value] strings."""
    found_ids = set()
    id_pattern = re.compile(r'\[id::\s*([^\]]+)\]')
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                matches = id_pattern.findall(line)
                for m in matches:
                    found_ids.add(m.strip())
    except Exception:
        pass
    return found_ids

def process_file(file_path, existing_ids, live=False, remaining_limit=None):
    """
    Standardizes tasks and adds unique IDs.
    Stops adding IDs if remaining_limit is reached.
    """
    task_pattern = re.compile(r'^(\s*-\s*\[ \]\s*)(.*)')
    meta_pattern = re.compile(r'\[(\w+)::\s*([^\]]+)\]')
    modified_in_file = 0
    new_lines = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for line in lines:
            match = task_pattern.match(line)
            if match:
                indent, body = match.groups()
                meta = {m[0]: m[1].strip() for m in meta_pattern.findall(body)}
                
                # Check if we need an ID AND if we haven't hit our global task limit
                if 'id' not in meta:
                    if remaining_limit is not None and remaining_limit <= 0:
                        # Limit reached; keep original line
                        new_lines.append(line)
                    else:
                        new_id = generate_short_id(existing_ids)
                        meta['id'] = new_id
                        existing_ids.add(new_id) 
                        modified_in_file += 1
                        if remaining_limit is not None:
                            remaining_limit -= 1
                        
                        description = meta_pattern.sub('', body).strip()
                        meta_str = " ".join([f"[{k}:: {v}]" for k, v in meta.items()])
                        new_lines.append(f"{indent}{description} {meta_str}".rstrip() + "\n")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        if live and modified_in_file > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
                
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        
    return modified_in_file

def main():
    parser = argparse.ArgumentParser(
        description="Renegade Task Manipulator: Unique ID Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("dir", nargs="?", help="Vault directory")
    parser.add_argument("--fix-id", type=str, choices=['dry', 'true'], help="Mode: dry or true")
    parser.add_argument("--limit", type=int, help="Stop after this many TASKS are modified")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    target_dir = args.dir if args.dir else "."

    # 1. THE GLOBAL AUDIT (Scan all files for ID integrity)
    all_files = []
    for root, dirs, fs in os.walk(target_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in fs:
            if f.endswith('.md'):
                all_files.append(os.path.join(root, f))
    
    print(f"--- Phase 1: Auditing {len(all_files)} files for existing IDs ---", file=sys.stderr)
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        id_sets = pool.map(audit_file_for_ids, all_files)
    
    master_id_registry = set().union(*id_sets)
    print(f"Audit Complete. {len(master_id_registry)} IDs registered.", file=sys.stderr)

    # 2. THE MODIFICATION PHASE (Serial to ensure task-level limit accuracy)
    is_live = (args.fix_id == 'true')
    total_modified = 0
    remaining_task_limit = args.limit

    print(f"--- Phase 2: Processing (Target: {'Unlimited' if args.limit is None else args.limit} tasks) ---", file=sys.stderr)
    
    for f in all_files:
        # Pass the current remaining limit to the processor
        file_mod_count = process_file(f, master_id_registry, is_live, remaining_task_limit)
        total_modified += file_mod_count
        
        if remaining_task_limit is not None:
            remaining_task_limit -= file_mod_count
            if remaining_task_limit <= 0:
                print(f"Reached task limit of {args.limit}. Stopping.", file=sys.stderr)
                break

    status = "MODIFIED" if is_live else "WOULD REQUIRE FIX"
    print(f"--- Summary ---\n{status}: {total_modified} tasks.", file=sys.stderr)

if __name__ == "__main__":
    main()