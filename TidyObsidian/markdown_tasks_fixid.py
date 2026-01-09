import os
import re
import argparse
import multiprocessing
import uuid

def process_file(file_path, live=False):
    task_pattern = re.compile(r'^(\s*-\s*\[ \]\s*)(.*)')
    meta_pattern = re.compile(r'\[(\w+)::\s*([^\]]+)\]')
    modified = 0
    new_lines = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for line in lines:
            match = task_pattern.match(line)
            if match:
                indent, body = match.groups()
                meta = {m[0]: m[1].strip() for m in meta_pattern.findall(body)}
                
                # Check for missing ID
                if 'id' not in meta:
                    meta['id'] = uuid.uuid4().hex[:6]
                    modified += 1
                
                # Standardize while we're at it
                desc = meta_pattern.sub('', body).strip()
                meta_str = " ".join([f"[{k}:: {v}]" for k, v in meta.items()])
                new_lines.append(f"{indent}{desc} {meta_str}".rstrip() + "\n")
            else:
                new_lines.append(line)

        if live and modified > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
    except Exception: pass
    return modified

def main():
    parser = argparse.ArgumentParser(description="Manipulator: Fix Task IDs")
    parser.add_argument("dir", nargs="?", default=".")
    parser.add_argument("--fix-id", type=str, choices=['dry', 'true'], default='dry')
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    files = [os.path.join(r, f) for r, _, fs in os.walk(args.dir) for f in fs if f.endswith('.md')]
    if args.limit: files = files[:args.limit]

    is_live = (args.fix_id == 'true')
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        counts = pool.starmap(process_file, [(f, is_live) for f in files])

    print(f"{'MODIFIED' if is_live else 'WOULD MODIFY'}: {sum(counts)} tasks.", file=os.sys.stderr)

if __name__ == "__main__":
    main()