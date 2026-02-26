import os
import re
import yaml
import nltk
from pathlib import Path
from nltk.corpus import words

# Initialize dictionary for segmentation
try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

WORD_SET = set(w.lower() for w in words.words())

# --- Configuration ---
ZETTEL_ROOT = "/home/hittjw/Documents/GitHub/obsidian/Zettelkasten"

def segment_words(text):
    """
    Recursive maximum matching algorithm to break unspaced strings.
    """
    def solve(s):
        if not s: return []
        for i in range(len(s), 0, -1):
            word = s[:i]
            if word in WORD_SET or i == 1:
                remainder = solve(s[i:])
                if remainder is not None:
                    return [word] + remainder
        return None

    if ' ' not in text and len(text) > 4:
        segmented = solve(text.lower())
        return " ".join(segmented) if segmented else text
    return text

def normalize_term(term):
    if not term:
        return ""
    # 1. Split CamelCase
    term = re.sub(r'([a-z])([A-Z])', r'\1 \2', str(term))
    # 2. Replace separators with spaces
    term = re.sub(r'[-_]', ' ', term)
    term = term.lower().strip()
    # 3. Dictionary-based segmentation
    return segment_words(term)

def extract_hashtags(root_dir):
    hashtags = set()
    # Fixed Pattern: (?:^|\s) matches start of string or whitespace (non-capturing)
    # #([A-Za-z0-9-_]+) captures the actual tag
    tag_pattern = re.compile(r'(?:^|\s)#([A-Za-z0-9-_]+)')
    
    for path in Path(root_dir).rglob('*.[mM][dD]'):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove YAML to prevent duplicate extraction
                content = re.sub(r'^---\s*\n(.*?)\n---\s*\n', '', content, flags=re.DOTALL)
                
                # findall on a pattern with one capturing group returns only the group
                matches = tag_pattern.findall(content)
                for m in matches:
                    hashtags.add(normalize_term(m))
        except (OSError, IOError):
            continue
    return hashtags

def extract_yaml_tags(root_dir):
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
        
        combined_terms = sorted(list(h_tags.union(y_tags)))
        
        print(f"--- Unique Normalized Terms ({len(combined_terms)}) ---")
        for term in combined_terms:
            if term.strip():
                print(term)
                