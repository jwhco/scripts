import os
import re
import yaml
import argparse
from pathlib import Path
from itertools import islice
from spellchecker import SpellChecker

# Configuration
ZETTEL_ROOT = "/home/hittjw/Documents/GitHub/obsidian/Zettelkasten"

WHITELIST = {
    "vscode", "latex", "zettlr", "github", "obsidian", "python", "jupyter", 
    "linux", "linkedin", "facebook", "hubspot", "google", "grammarly", 
    "youtube", "zotero", "wordpress", "woocommerce", "pandoc", "shopify", 
    "podcast", "logseq", "semrush", "spreaker", "ahrefs", "zettelkasten", 
    "wintak", "civtak", "tumblr", "locals", "kubernetes", "DFARS", "CMMC", 
    "cyber", "aweber", "aioseo"
}

# Initialize SpellChecker
spell = SpellChecker()
# Ensure all whitelist words are recognized as correct
spell.word_frequency.load_words([w.lower() for w in WHITELIST])

def is_channel_hashtag(term):
    return 1 <= len(term) <= 3 and term.isupper() and term.isalpha()

def is_catalog_code(term):
    if len(term) > 10:
        return False
    return any(c.isdigit() for c in term) and any(c.isupper() for c in term)

def segment_words(text):
    text_lower = text.lower()
    for white_word in sorted(WHITELIST, key=len, reverse=True):
        if white_word in text_lower:
            parts = text_lower.split(white_word, 1)
            prefix = segment_words(parts[0]) if parts[0] else ""
            suffix = segment_words(parts[1]) if parts[1] else ""
            return f"{prefix} {white_word} {suffix}".strip()

    # Recursive MaxMatch fallback
    def solve(s):
        if not s: return []
        for i in range(len(s), 0, -1):
            word = s[:i]
            # Use spellchecker's dictionary for segmentation lookup
            if word in spell or i == 1:
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
    if is_channel_hashtag(term) or is_catalog_code(term):
        return term
    term_lower = term.lower()
    if term_lower in WHITELIST:
        return term_lower
    contains_whitelist = any(w in term_lower for w in WHITELIST)
    if not contains_whitelist:
        term = re.sub(r'([a-z])([A-Z])', r'\1 \2', term)
    term = re.sub(r'[-_]', ' ', term)
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
                yaml_match = yaml_pattern.search(content)
                body_content = content
                if yaml_match:
                    try:
                        meta = yaml.safe_load(yaml_match.group(1))
                        if meta and 'tags' in meta:
                            tags = meta['tags']
                            tag_list = tags if isinstance(tags, list) else [tags]
                            for t in tag_list:
                                norm = normalize_term(str(t))
                                if norm:
                                    all_terms.add(re.sub(r'\s+', ' ', norm).strip())
                    except (yaml.YAMLError, TypeError):
                        pass
                    body_content = yaml_pattern.sub('', content)
                for m in tag_pattern.findall(body_content):
                    norm = normalize_term(m)
                    if norm:
                        all_terms.add(re.sub(r'\s+', ' ', norm).strip())
        except (OSError, IOError):
            continue
    return all_terms

def check_spelling(term_list):
    """Filters for terms with at least one misspelled word, ignoring structural tags."""
    misspelled = []
    for term in term_list:
        if is_channel_hashtag(term) or is_catalog_code(term):
            continue
        
        words_to_check = term.split()
        # Find misspelled words that aren't in our whitelist
        unknown = spell.unknown(words_to_check)
        if unknown:
            misspelled.append(term)
    return misspelled

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and normalize tags from Zettelkasten.")
    parser.add_argument("directory", nargs="?", default=ZETTEL_ROOT)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--spellcheck", action="store_true")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} not found")
    else:
        files_gen = get_file_generator(args.directory)
        if args.limit:
            files_gen = islice(files_gen, args.limit)

        results = sorted(list(process_files(files_gen)))
        
        if args.spellcheck:
            results = check_spelling(results)
            if not results:
                print("No misspellings found.")
            else:
                print(f"--- Misspelled/Unknown Terms ({len(results)}) ---")
                for term in results:
                    print(term)
        else:
            print(f"--- Unique Normalized Terms ({len(results)}) ---")
            for term in results:
                print(term)
                