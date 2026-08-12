#!/usr/bin/env python3
"""
Find markdown files ready to publish based on content maturity.

Evaluates articles by word count, readability, and publication status.
Reports candidates ranked by completion readiness.

Usage:
  python3 find-ready-to-publish.py
  python3 find-ready-to-publish.py /path/to/markdown/repo
  python3 find-ready-to-publish.py . --min-words 400 --max-words 2500
  python3 find-ready-to-publish.py . --yaml-type article
"""

import os
import sys
import re
import argparse
import yaml
from collections import defaultdict


def parse_yaml_front_matter(text):
    """Extract YAML front matter from markdown.
    
    Returns (yaml_dict, body_text) or ({}, text) if no front matter.
    """
    yaml_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    match = yaml_pattern.search(text)
    
    if not match:
        return {}, text
    
    try:
        meta = yaml.safe_load(match.group(1))
        body = yaml_pattern.sub('', text)
        return meta or {}, body
    except Exception:
        return {}, text


def count_words(text):
    """Count words in text."""
    return len(text.split())


def is_published(meta):
    """Check if article is already published.
    
    Published if:
    - type: Post/Feature/Article and has permalink
    - status: S4-Publish and has permalink
    """
    has_permalink = 'permalink' in meta and meta['permalink']
    
    if has_permalink:
        status = meta.get('status', '').lower()
        type_field = meta.get('type', '').lower()
        
        if status == 's4-publish' or type_field in ('post', 'feature', 'article'):
            return True
    
    return False


def calculate_readability_score(text):
    """Simple readability score (0-100).
    
    Factors:
    - Sentence length (shorter = more readable)
    - Word length (shorter = more readable)
    - Paragraph distribution (consistent = more readable)
    """
    if not text or len(text.split()) < 10:
        return 0
    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return 0
    
    words = text.split()
    avg_sentence_length = len(words) / len(sentences)
    avg_word_length = sum(len(w) for w in words) / len(words)
    
    # Flesch-Kincaid-like metric (simplified)
    # Ideal: ~15 words/sentence, ~4.5 chars/word
    score = 100
    score -= abs(avg_sentence_length - 15) * 2
    score -= abs(avg_word_length - 4.5) * 5
    
    return max(0, min(100, score))


def score_completeness(meta, body_text, word_count):
    """Score article readiness (0-100).
    
    Factors:
    - Word count (400-800 optimal)
    - Readability (higher = better)
    - YAML structure completeness
    - Content maturity indicators
    """
    score = 0
    
    # Word count: 400-800 is optimal
    if 400 <= word_count <= 800:
        score += 40
    elif 200 <= word_count < 400:
        score += 20
    elif word_count >= 400:
        score += 30
    
    # Readability
    readability = calculate_readability_score(body_text)
    score += readability * 0.3
    
    # YAML structure
    yaml_score = 0
    if meta.get('title'):
        yaml_score += 10
    if meta.get('tags'):
        yaml_score += 10
    if meta.get('type'):
        yaml_score += 10
    if meta.get('status'):
        yaml_score += 5
    score += yaml_score
    
    # Paragraphs (structure indicator)
    paragraphs = len([p for p in body_text.split('\n\n') if p.strip()])
    if paragraphs >= 3:
        score += 10
    
    return min(100, int(score))


def scan_directory(root_dir, min_words=400, max_words=2500, yaml_type=None):
    """Scan directory for markdown candidates.
    
    Args:
        root_dir: Directory to scan
        min_words: Minimum word count
        max_words: Maximum word count
        yaml_type: Optional YAML type filter (case-insensitive)
    
    Returns list of dicts with file info and scores.
    """
    candidates = []
    
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if not fname.lower().endswith('.md'):
                continue
            
            full_path = os.path.join(dirpath, fname)
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                continue
            
            meta, body = parse_yaml_front_matter(content)
            word_count = count_words(body)
            
            # Filter: skip published, filter by word count
            if is_published(meta):
                continue
            
            if word_count < min_words or word_count > max_words:
                continue
            
            # Filter: yaml type (case-insensitive)
            if yaml_type:
                doc_type = meta.get('type', '').lower()
                if doc_type != yaml_type.lower():
                    continue
            
            # Score the candidate
            completeness = score_completeness(meta, body, word_count)
            
            candidate = {
                'file': full_path,
                'title': meta.get('title', fname),
                'type': meta.get('type', 'Unknown'),
                'status': meta.get('status', 'Draft'),
                'word_count': word_count,
                'readability': calculate_readability_score(body),
                'completeness': completeness,
                'yaml_complete': bool(meta.get('title') and meta.get('tags')),
            }
            
            candidates.append(candidate)
    
    return candidates


def report_candidates(candidates):
    """Print ranked list of publication-ready candidates."""
    if not candidates:
        print("No candidates found.\n")
        return
    
    # Sort by completeness score (descending)
    ranked = sorted(candidates, key=lambda x: -x['completeness'])
    
    print(f"\nReady-to-Publish Candidates ({len(ranked)} found)\n")
    print(f"{'Rank':<6} {'Score':<8} {'Words':<8} {'Title':<40} {'Status':<12}")
    print("-" * 90)
    
    for i, c in enumerate(ranked, 1):
        title = c['title'][:39]
        print(f"{i:<6} {c['completeness']:<8} {c['word_count']:<8} {title:<40} {c['status']:<12}")
    
    print("\nTop Candidate Details:\n")
    top = ranked[0]
    print(f"File:        {top['file']}")
    print(f"Title:       {top['title']}")
    print(f"Type:        {top['type']}")
    print(f"Status:      {top['status']}")
    print(f"Word Count:  {top['word_count']}")
    print(f"Readability: {top['readability']:.1f}")
    print(f"Completeness: {top['completeness']}/100")
    print(f"YAML Ready:  {'Yes' if top['yaml_complete'] else 'No'}")


def main():
    parser = argparse.ArgumentParser(
        description='Find markdown files ready to publish.'
    )
    parser.add_argument('directory', nargs='?', default='.',
                        help='Directory to scan (default: current directory)')
    parser.add_argument('--min-words', type=int, default=400,
                        help='Minimum word count (default: 400)')
    parser.add_argument('--max-words', type=int, default=2500,
                        help='Maximum word count (default: 2500)')
    parser.add_argument('--yaml-type', type=str, default=None,
                        help='Filter by YAML type field (case-insensitive, e.g., "article")')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: directory not found: {args.directory}")
        sys.exit(1)
    
    print(f"Scanning {args.directory}...")
    candidates = scan_directory(args.directory, args.min_words, args.max_words, args.yaml_type)
    
    if args.json:
        import json
        print(json.dumps(candidates, indent=2))
    else:
        report_candidates(candidates)


if __name__ == '__main__':
    main()
