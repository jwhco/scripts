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

# Whitelist: These stay as single tokens (lower-cased in final output)
WHITELIST = {"vscode", "latex", "zettlr", "github", "obsidian", "python", "jupyter", "linux", "linkedin", "facebook", "hubspot", "google", "grammarly", "youtube", "zotero", "wordpress", "woocommerce", "pandoc", "obsidian"}

WORD_SET = set(w.lower() for w in words.words())
WORD_SET.update(WHITELIST)

def is_catalog_code(term):
    """
    Checks if a term matches catalog code heuristics:
    - Length <= 10
    - Contains at least one digit
    - Contains at least one uppercase letter (to preserve A1234B vs a1234b)
    """
    if len(term) > 10:
        return False
    has_digit = any(c.isdigit() for c in term)
    has_upper = any(c.isupper() for c in term)
    return has_digit and has_upper

def segment_words(text):
    """Recursive maximum matching algorithm for long lowercased tags."""
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
        # Don't segment if it contains digits (safety for alphanumeric strings)
        if any(char.isdigit() for char in text):
            return text
        
        segmented = solve(text.lower())
        # Safety: if split into mostly single letters, revert to original
        if segmented and len([x for x in segmented if len(x) == 1]) > (len(text) / 2):
            return text
        return " ".join(segmented) if segmented else text
    return text

def normalize_term(term):
    if not term:
        return ""
    
    term = term.strip()

    # 1. PRESERVE CATALOG CODES: 
    # Catch A1234B, 001_A1234B, GL7 before any modification.
    if is_catalog_code(term):
        return term

    # 2. WHITELIST CHECK: (Pre-lower)
    if term.lower() in WHITELIST:
        return term.lower()

    # 3. NORMALIZATION PIPELINE
    # Split CamelCase (e.g., WorkplaceWellness -> Workplace Wellness)
    term = re.sub(r'([a-z])([A-Z])', r'\1 \2', str(term))
    
    # Replace separators with spaces
    term = re.sub(r'[-_]', ' ', term)
    term = term.strip()
    
    # Dictionary-based segmentation for unspaced tags (lower-cased)
    return segment_words(term.lower())

def extract_hashtags(root_dir):
    hashtags = set()
    # Pattern looks for # preceded by start of line or space to avoid anchors
    tag_pattern = re.compile(r'(?:^|\s)#([A-Za-z0-9-_]+)')
    
    for path in Path(root_dir).rglob('*.[mM][dD]'):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Strip YAML for hashtag search
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
                                if t: yaml_tags.add(normalize_term(str(t)))
                        elif tags:
                            yaml_tags.add(normalize_term(str(tags)))
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
                