import os
import re
import yaml
from pathlib import Path

# --- Configuration ---
ZETTEL_ROOT = "/home/hittjw/Documents/GitHub/obsidian/Zettelkasten"

def normalize_term(term):
    """
    Standardizes tags by:
    1. Splitting CamelCase into separate words.
    2. Replacing hyphens and underscores with spaces.
    3. Lowercasing the entire string.
    """
    if not term:
        return ""
    # Split CamelCase
    term = re.sub(r'([a-z])([A-Z])', r'\1 \2', str(term))
    # Replace separators (kebab-case or snake_case) with spaces
    term = re.sub(r'[-_]', ' ', term)
    return term.lower().strip()

def extract_hashtags(root_dir):
    """Extracts hashtags from the body of markdown files."""
    hashtags = set()
    # Matches #CamelCase, #kebab-case, or #simple tags
    # Excludes the # symbol from the capture group
    tag_pattern = re.compile(r'#([A-Za-z0-9-_]+)')
    
    for path in Path(root_dir).rglob('*.[mM][dD]'):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove YAML front matter to avoid duplicate counting
                content = re.sub(r'^---\s*\n(.*?)\n---\s*\n', '', content, flags=re.DOTALL)
                matches = tag_pattern.findall(content)
                for m in matches:
                    hashtags.add(normalize_term(m))
        except (OSError, IOError):
            continue
    return hashtags

def extract_yaml_tags(root_dir):
    """Extracts tags from YAML front matter."""
    yaml_tags = set()
    
    for path in Path(root_dir).rglob('*.[mM][dD]'):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if match:
                    meta = yaml.safe_load(match.group(1))
                    if meta and 'tags' in meta:
                        tags = meta['tags']
                        if isinstance(tags, list):
                            for t in tags:
                                if t: yaml_tags.add(normalize_term(t))
                        elif tags:
                            yaml_tags.add(normalize_term(tags))
        except (yaml.YAMLError, OSError, IOError):
            continue
    return yaml_tags

# --- Execution ---
if __name__ == "__main__":
    if not os.path.isdir(ZETTEL_ROOT):
        print(f"directory_not_found: {ZETTEL_ROOT}")
    else:
        h_tags = extract_hashtags(ZETTEL_ROOT)
        y_tags = extract_yaml_tags(ZETTEL_ROOT)
        
        # Combine, unique-ify, and sort
        combined_terms = sorted(list(h_tags.union(y_tags)))
        
        print(f"--- Unique Normalized Terms ({len(combined_terms)}) ---")
        for term in combined_terms:
            if term: # Ensure no empty strings
                print(term)

				