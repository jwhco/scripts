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

# Configuration
ZETTEL_ROOT = "/home/hittjw/Documents/GitHub/obsidian/Zettelkasten"

# Whitelist: These stay as single tokens (case-insensitive check)
WHITELIST = {"vscode", "latex", "zettlr", "github", "obsidian", "python", "jupyter", "linux", "linkedin", "facebook", "hubspot", "google", "grammarly"}

# Load NLTK words and merge with whitelist to ensure segmenter recognizes them
WORD_SET = set(w.lower() for w in words.words())
WORD_SET.update(WHITELIST)

def segment_words(text):
    """
    Recursive maximum matching algorithm.
    Exempts alphanumeric codes and whitelisted terms.
    """
    # 1. If the term is in our whitelist, don't split it
    if text.lower() in WHITELIST:
        return text.lower()

    # 2. If the text contains digits, don't split it (Category Codes)
    if any(char.isdigit() for char in text):
        return text

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
        # Safety: if split into mostly single letters, revert to original
        if segmented and len([x for x in segmented if len(x) == 1]) > (len(text) / 2):
            return text
        return " ".join(segmented) if segmented else text
    return text

def normalize_term(term):
    if not term:
        return ""
    
    # PROTECT CATEGORY CODES: All uppercase + alphanumeric
    if term.isupper() and any(c.isalpha() for c in term):
        return term.strip()

    # Check against whitelist before splitting CamelCase
    if term.lower() in WHITELIST:
        return term.lower()

    # 1. Split CamelCase
    term = re.sub(r'([a-z])([A-Z])', r'\1 \2', str(term))
    
    # 2. Replace separators with spaces
    term = re.sub(r'[-_]', ' ', term)
    term = term.strip()
    
    # 3. Dictionary-based segmentation
    return segment_words(term.lower())

def extract_hashtags(root_dir):
    hashtags = set()
    # Fixed-width compatible pattern (start of line or whitespace)
    tag_pattern = re.compile(r'(?:^|\s)#([A-Za-z0-9-_]+)')
    
    for path in Path(root_dir).rglob('*.[mM][dD]'):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                content = re.sub(r'^---\s*\n(.*?)\n---\s*\n', '', content, flags=re.DOTALL)
                matches = tag_pattern.findall(content)
                for m in matches:
                    normalized = normalize_term(m)
                    if normalized:
                        hashtags.add(normalized)
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
                