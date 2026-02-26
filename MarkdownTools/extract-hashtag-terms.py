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

# ANSI Color Codes: Red background (41), White foreground (37), Reset (0)
# This is the most compatible sequence for xterm and xterm-256color
RED_BG_WHITE_FG = "\033[41;37m"
RESET = "\033[0m"

# Initialize SpellChecker
spell = SpellChecker()
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

    def solve(s):
        if not s: return []
        for i in range(len(s), 0, -1):
            word = s[:i]
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

def check_spelling_with_color(term_list):
    """Filters for terms with misspellings and highlights the error in red."""
    flagged_output = []
    for term in term_list:
        if is_channel_hashtag(term) or is_catalog_code(term):
            continue
        
        words_to_check = term.split()
        unknown = spell.unknown(words_to_check)
        
        if unknown:
            colored_words = []
            for w in words_to_check:
                if w in unknown:
                    # Apply red background to misspelled word
                    colored_words.append(f"{RED_BG_WHITE_FG}{w}{RESET}")
                else:
                    colored_words.append(w)
            flagged_output.append(" ".join(colored_words))
            
    return flagged_output

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
            colored_results = check_spelling_with_color(results)
            if not colored_results:
                print("No misspellings found.")
            else:
                print(f"--- Misspelled/Unknown Terms ({len(colored_results)}) ---")
                for term in colored_results:
                    print(term)
        else:
            print(f"--- Unique Normalized Terms ({len(results)}) ---")
            for term in results:
                print(term)
                