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

def process_file(file_path, existing_ids, live=False):
    """
    Standardizes tasks and adds unique IDs. 
    existing_ids is used to prevent duplicates.
    """
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
                meta = {m[0]: m[1].strip() for m in meta_pattern.findall(body)}
                
                if 'id' not in meta:
                    # Generate and register the new unique ID
                    new_id = generate_short_id(existing_ids)
                    meta['id'] = new_id
                    existing_ids.add(new_id) 
                    modified_count += 1
                    
                    description = meta_pattern.sub('', body).strip()
                    meta_str = " ".join([f"[{k}:: {v}]" for k, v in meta.items()])
                    new_lines.append(f"{indent}{description} {meta_str}".rstrip() + "\n")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        if live and modified_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
                
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        
    return modified_count

def main():
    parser = argparse.ArgumentParser(
        description="Renegade Task Manipulator: Unique ID Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("dir", nargs="?", help="Vault directory")
    parser.add_argument("--fix-id", type=str, choices=['dry', 'true'], help="Mode: dry or true")
    parser.add_argument("--limit", type=int, help="Limit number of files modified")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    target_dir = args.dir if args.dir else "."

    # 1. THE GLOBAL AUDIT (Scan all files for existing IDs)
    print("--- Phase 1: Global ID Audit (Scanning all files) ---", file=sys.stderr)
    all_files = []
    for root, _, fs in os.walk(target_dir):
        for f in fs:
            if f.endswith('.md'):
                all_files.append(os.path.join(root, f))
    
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        id_sets = pool.map(audit_file_for_ids, all_files)
    
    # Flatten all found IDs into one master set
    master_id_registry = set().union(*id_sets)
    print(f"Audit Complete. {len(master_id_registry)} existing IDs registered.", file=sys.stderr)

    # 2. SELECTION (Apply limit for modification phase)
    files_to_modify = all_files[:args.limit] if args.limit else all_files
    is_live = (args.fix_id == 'true')

    # 3. THE MODIFICATION PHASE
    # Note: We don't use multiprocessing for the write phase here because 
    # generate_short_id needs to update the master_id_registry to prevent 
    # two workers from picking the same new ID simultaneously.
    print(f"--- Phase 2: Processing {len(files_to_modify)} files ---", file=sys.stderr)
    
    total_modified = 0
    for f in files_to_modify:
        total_modified += process_file(f, master_id_registry, is_live)

    status = "MODIFIED" if is_live else "WOULD REQUIRE FIX"
    print(f"--- Summary ---\n{status}: {total_modified} tasks.", file=sys.stderr)

if __name__ == "__main__":
    main()