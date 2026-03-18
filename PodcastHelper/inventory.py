#!/usr/bin/env python3
"""
Inventory - List Eligible Media

Find and report on markdown sidecars that exist in the media root.
Report dates created, published, and updated. Report channel, catalog, and duration.
Then filename of sidecar.

Usage:

    python3 inventory.py --media-root /path/to/media [--catalog CATALOG_CODE]

Examples:

    # List all sidecars with their metadata
    python3 inventory.py --media-root /path/to/media

    # List only sidecars flagged for specific catalog
    python3 inventory.py --media-root /path/to/media --catalog A1234B

    # Limit results to first 10 items
    python3 inventory.py --media-root /path/to/media --limit 10
"""

from __future__ import annotations

import argparse
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


def parse_yaml_frontmatter(text: str) -> Dict[str, str]:
    """Extract YAML front matter from markdown content."""
    frontmatter = {}
    
    lines = text.split('\n')
    if not lines or lines[0].strip() != '---':
        return frontmatter
    
    i = 1
    while i < len(lines):
        line = lines[i]
        if line.strip() == '---':
            break
        
        # Parse YAML key-value pairs
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ''
            # Remove quotes if present
            if value and value[0] in ('"', "'"):
                value = value[1:-1]
            frontmatter[key] = value
        
        i += 1
    
    return frontmatter


def get_sidecar_metadata(sidecar_path: Path) -> Dict[str, str]:
    """Read metadata from a markdown sidecar file."""
    metadata = {
        'created': '',
        'published': '',
        'updated': '',
        'channel': '',
        'catalog': '',
        'duration': '',
        'filename': '',
    }
    
    if not sidecar_path.exists():
        return metadata
    
    try:
        content = sidecar_path.read_text(encoding='utf-8', errors='ignore')
        frontmatter = parse_yaml_frontmatter(content)
        
        # Map frontmatter keys to metadata (case-insensitive)
        for key in metadata:
            # First try exact match
            if key in frontmatter:
                metadata[key] = frontmatter[key]
            else:
                # Try case-insensitive match
                for fm_key, fm_value in frontmatter.items():
                    if fm_key.lower() == key.lower():
                        metadata[key] = fm_value
                        break
    except Exception as e:
        print(f"Warning: Could not read {sidecar_path}: {e}")
    
    return metadata


def format_output_row(metadata: Dict[str, str], sidecar_filename: str) -> str:
    """Format a row for list output in standard format."""
    # Determine status (default to 'Unknown')
    status = 'Published' if metadata.get('published') else 'Unknown'
    
    duration = metadata.get('duration', 'Unknown')
    created = metadata.get('created', 'Unknown')
    
    # Format date as YYYY-MM-DD HH:mm if available
    date_str = created
    if created and len(created) >= 10:
        # Assume format is already YYYY-MM-DD
        date_str = created  # Keep in YYYY-MM-DD format
    
    # Format: {STATUS}  {DURATION} {YYYY-MM-DD HH:mm} {FILENAME}
    return f"{status:12} {duration:10} {date_str:12} {sidecar_filename}"


def inventory(media_root: Path, catalog_filter: Optional[str] = None, 
              limit: Optional[int] = None) -> int:
    """
    Find and list all markdown sidecars in media root with their metadata.
    
    Args:
        media_root: Path to the media root directory
        catalog_filter: Optional catalog code to filter results
        limit: Maximum number of items to return
    
    Returns:
        Exit code (0 for success)
    """
    media_root = media_root.resolve()
    
    if not media_root.exists():
        print(f"Error: Media root {media_root} does not exist")
        return 2
    
    sidecars: List[tuple[Path, Dict[str, str]]] = []
    
    # Find all .md files (sidecars) in media root
    for root, dirs, files in os.walk(media_root):
        for fn in files:
            if fn.lower().endswith('.md'):
                sidecar_path = Path(root) / fn
                metadata = get_sidecar_metadata(sidecar_path)
                
                # Filter by catalog if specified
                if catalog_filter and metadata.get('catalog') != catalog_filter:
                    continue
                
                sidecars.append((sidecar_path, metadata))
    
    if not sidecars:
        if catalog_filter:
            print(f"No sidecars found with catalog: {catalog_filter}")
        else:
            print("No sidecars found")
        return 0
    
    # Sort by created date (most recent first)
    sidecars.sort(key=lambda x: x[1].get('created', ''), reverse=True)
    
    # Print header
    print(f"{'Status':<12} {'Duration':<10} {'Created':<12} {'Filename'}")
    print('-' * 80)
    
    # Print results
    count = 0
    for sidecar_path, metadata in sidecars:
        # Use absolute path for display (VS Code clickable)
        abs_path = str(sidecar_path)
        
        # Format the output row
        output = format_output_row(metadata, abs_path)
        print(output)
        
        count += 1
        if limit is not None and count >= limit:
            break
    
    print('-' * 80)
    if limit is not None and len(sidecars) > count:
        print(f"Showing: {count} of {len(sidecars)} sidecar(s) found")
    else:
        print(f"Total: {len(sidecars)} sidecar(s) found")
    
    return 0


def main():
    p = argparse.ArgumentParser(
        description="List eligible media from markdown sidecars",
        epilog="Paths will be relative to media root for VS Code clickability."
    )
    p.add_argument('--media-root', required=True, 
                   help='Root directory containing media and sidecars')
    p.add_argument('--catalog', 
                   help='Filter by catalog code (e.g., A1234B)')
    p.add_argument('--limit', type=int, 
                   help='Limit number of results (like SQL LIMIT)')
    args = p.parse_args()
    
    media_root = Path(args.media_root)
    raise SystemExit(inventory(media_root, catalog_filter=args.catalog, limit=args.limit))


if __name__ == '__main__':
    main()
