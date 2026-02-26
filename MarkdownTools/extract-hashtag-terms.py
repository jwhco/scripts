import os
import re
import yaml
import nltk
import argparse
from pathlib import Path
from nltk.corpus import words
from itertools import islice

# Initialize dictionary for segmentation
try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

WHITELIST = {
    "vscode", "latex", "zettlr", "github", "obsidian", "python", "jupyter", 
    "linux", "linkedin", "facebook", "hubspot", "google", "grammarly", 
    "youtube", "zotero", "wordpress", "woocommerce", "pandoc", "shopify", 
    "podcast", "logseq", "semrush", "spreaker", "ahrefs", "zettelkasten", "wintak", "civtak", "tumblr", "locals", "kubernetes", "DFARS", "CMMC", "cyber", "aweber", "aioseo"
}

WORD_SET = set(w.lower() for w in words.words())
WORD_SET.update(WHITELIST)

def is_channel_hashtag(term):
    """Checks for 1-3 character all-uppercase channel identifiers (e.g., ABR, SWS)."""
    return 1 <= len(term) <= 3 and term.isupper() and term.isalpha()

def is_catalog_code(term):
    """Checks for alphanumeric catalog codes (e.g., A1234B, GL7, 001_A1234B)."""
    if len(term) > 10:
        return False
    return any(c.isdigit() for c in term) and any(c.isupper() for c in term)

def segment_words(text):
    text_lower = text.lower()
    
    # 1. Check if a WHITELIST word is INSIDE the string
    # We look for the longest whitelist word present and split around it
    for white_word in sorted(WHITELIST, key=len, reverse=True):
        if white_word in text_lower:
            # Split the string where the whitelist word is found
            parts = text_lower.split(white_word, 1)
            # Recursively segment the prefix and suffix, then sandwich the white_word
            prefix = segment_words(parts[0]) if parts[0] else ""
            suffix = segment_words(parts[1]) if parts[1] else ""
            return f"{prefix} {white_word} {suffix}".strip()

    # 2. Fallback to standard MaxMatch if no Whitelist words are found
    def solve(s):
        if not s: return []
        for i in range(len(s), 0, -1):
            word = s[:i]
            if word in WORD_SET or i == 1:
                remainder = solve(s[i:])
                if remainder is not None:
                    return [word] + remainder
        return None

    if ' ' not in text_lower and len(text_lower) > 4:
        if any(char.isdigit() for char in text_lower):
            return text_lower
        
        segmented = solve(text_lower)
        if segmented and len([x for x in segmented if len(x) == 1]) > (len(text_lower) / 2):
            return text_lower
        return " ".join(segmented).strip()
    
    return text_lower

def normalize_term(term):
    if not term: return ""
    term = term.strip()

    # 1. PRESERVE CHANNELS AND CATALOG CODES
    if is_channel_hashtag(term) or is_catalog_code(term):
        return term
        
    # 2. FULL STRING WHITELIST CHECK
    # If the whole tag is a whitelist word (e.g., #YouTube), lower and return.
    term_lower = term.lower()
    if term_lower in WHITELIST:
        return term_lower

    # 3. SELECTIVE CAMELCASE SPLITTING
    # We check if the term contains a whitelisted word. 
    # If it does (like YouTubeStudio), we skip the regex split and let 
    # segment_words handle it using the priority logic we just built.
    contains_whitelist = any(w in term_lower for w in WHITELIST)
    
    if not contains_whitelist:
        # Only split CamelCase if no whitelisted "atomic" words are present
        term = re.sub(r'([a-z])([A-Z])', r'\1 \2', term)
    
    # 4. CLEAN SEPARATORS
    term = re.sub(r'[-_]', ' ', term)
    
    # 5. SEGMENTATION (With the priority logic from the previous step)
    return segment_words(term.lower().strip())

def get_file_generator(root_dir):
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.lower().endswith('.md'):
                yield os.path.join(root, file)

def process_files(file_list):
    all_terms = set()
    tag_pattern = re.compile(r'(?:^|\s)#([A-Za-z0-9-_]+)')
    yaml_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

    for filepath in file_list:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
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
                                if norm:
                                    # Collapse multiple spaces into one and strip
                                    clean_norm = re.sub(r'\s+', ' ', norm).strip()
                                    all_terms.add(clean_norm)
                    except (yaml.YAMLError, TypeError):
                        pass
                    body_content = yaml_pattern.sub('', content)

                hash_matches = tag_pattern.findall(body_content)
                for m in hash_matches:
                    norm = normalize_term(m)
                    if norm:
                        # Collapse multiple spaces into one and strip
                        clean_norm = re.sub(r'\s+', ' ', norm).strip()
                        all_terms.add(clean_norm)
        except (OSError, IOError) as e:
            print(f"read_error: {filepath} - {e}")
            
    return all_terms

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and normalize tags from Zettelkasten.")
    parser.add_argument(
        "directory", 
        nargs="?", 
        default="/home/hittjw/Documents/GitHub/obsidian/Zettelkasten",
        help="Root directory of the Zettelkasten"
    )
    parser.add_argument(
        "--limit", 
        type=int, 
        default=None, 
        help="Limit the number of files scanned for testing"
    )
    
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"directory_not_found: {args.directory}")
    else:
        files_gen = get_file_generator(args.directory)
        if args.limit:
            files_gen = islice(files_gen, args.limit)

        unique_terms = sorted(list(process_files(files_gen)))
        
        print(f"--- Unique Normalized Terms ({len(unique_terms)}) ---")
        for term in unique_terms:
            if term.strip():
                print(term)
