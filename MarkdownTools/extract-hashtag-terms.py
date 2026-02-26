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

WHITELIST = {
    "vscode", "latex", "zettlr", "github", "obsidian", "python", "jupyter", 
    "linux", "linkedin", "facebook", "hubspot", "google", "grammarly", 
    "youtube", "zotero", "wordpress", "woocommerce", "pandoc", "shopify", 
    "podcast", "logseq"
}

WORD_SET = set(w.lower() for w in words.words())
WORD_SET.update(WHITELIST)

def is_catalog_code(term):
    if len(term) > 10:
        return False
    return any(c.isdigit() for c in term) and any(c.isupper() for c in term)

def segment_words(text):
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
        if any(char.isdigit() for char in text):
            return text
        segmented = solve(text.lower())
        if segmented and len([x for x in segmented if len(x) == 1]) > (len(text) / 2):
            return text
        return " ".join(segmented) if segmented else text
    return text

def normalize_term(term):
    if not term: return ""
    term = term.strip()

    if is_catalog_code(term):
        return term
    if term.lower() in WHITELIST:
        return term.lower()

    term = re.sub(r'([a-z])([A-Z])', r'\1 \2', str(term))
    term = re.sub(r'[-_]', ' ', term)
    return segment_words(term.lower().strip())

def process_zettelkasten(root_dir):
    """
    Single-pass extraction:
    1. Prunes hidden directories.
    2. Opens each file exactly once.
    3. Processes YAML and Body hashtags simultaneously.
    """
    all_terms = set()
    tag_pattern = re.compile(r'(?:^|\s)#([A-Za-z0-9-_]+)')
    yaml_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

    for root, dirs, files in os.walk(root_dir):
        # Prune hidden directories in-place
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.lower().endswith('.md'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # 1. Process YAML
                        body_content = content
                        yaml_match = yaml_pattern.search(content)
                        if yaml_match:
                            try:
                                meta = yaml.safe_load(yaml_match.group(1))
                                if meta and 'tags' in meta:
                                    tags = meta['tags']
                                    tag_list = tags if isinstance(tags, list) else [tags]
                                    for t in tag_list:
                                        norm = normalize_term(str(t))
                                        if norm: all_terms.add(norm)
                            except yaml.YAMLError:
                                pass
                            
                            # 2. Prepare body (remove YAML to avoid double counting)
                            body_content = yaml_pattern.sub('', content)

                        # 3. Process Hashtags in Body
                        hash_matches = tag_pattern.findall(body_content)
                        for m in hash_matches:
                            norm = normalize_term(m)
                            if norm: all_terms.add(norm)
                            
                except (OSError, IOError) as e:
                    print(f"read_error: {filepath} - {e}")
                    
    return all_terms

# --- Execution ---
if __name__ == "__main__":
    if not os.path.isdir(ZETTEL_ROOT):
        print(f"directory_not_found: {ZETTEL_ROOT}")
    else:
        unique_terms = sorted(list(process_zettelkasten(ZETTEL_ROOT)))
        
        print(f"--- Unique Normalized Terms ({len(unique_terms)}) ---")
        for term in unique_terms:
            if term.strip():
                print(term)
                