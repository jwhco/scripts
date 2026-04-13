#!/usr/bin/env python3
"""
Inventory script to list and filter podcast media files based on metadata.

Usage:
    python3 inventory.py --catalog=A1234B --min-duration=600 --index=index.csv --media-root=/path/to/media

This script uses sidecar files for metadata and supports filtering by catalog code and duration.
"""

import argparse
import csv
from pathlib import Path
from datetime import timedelta

def parse_sidecar(sidecar_path: Path):
    """Parse metadata from a sidecar file."""
    metadata = {}
    with sidecar_path.open('r', encoding='utf-8') as f:
        lines = f.readlines()
        if lines and lines[0].strip() == '---':
            for line in lines[1:]:
                if line.strip() == '---':
                    break
                key, _, value = line.partition(':')
                metadata[key.strip()] = value.strip()
    return metadata

def parse_duration(duration: str) -> int:
    """Parse a duration string in HH:mm:ss format into total seconds."""
    parts = list(map(int, duration.split(':')))
    while len(parts) < 3:  # Ensure HH:mm:ss format
        parts.insert(0, 0)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]

def list_inventory(media_root: Path, index_file: Path = None, catalog: str = None, min_duration: int = 600):
    """List media files based on filters."""
    media_root = media_root.resolve()
    results = []

    # Determine index file location
    if not index_file:
        index_file = media_root / 'index.csv'

    # Check if index file exists
    if not index_file.exists():
        print(f"Error: Index file not found at {index_file}. Please ensure the index file exists.")
        return

    # Read index file
    with index_file.open('r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            duration_seconds = parse_duration(row['minutes'])

            if catalog and row.get('catalog') != catalog:
                continue
            if duration_seconds < min_duration:
                continue

            results.append({
                'media_file': row['path'],
                'sidecar_file': row['sidecar'],
                'duration': str(timedelta(seconds=duration_seconds)),
                'catalog': row.get('catalog', 'N/A'),
                'published': row.get('published', 'No')
            })

    # Print results
    print("Media File\tSidecar File\tDuration\tCatalog\tPublished")
    for result in results:
        print(f"{result['media_file']}\t{result['sidecar_file']}\t{result['duration']}\t{result['catalog']}\t{result['published']}")

def main():
    parser = argparse.ArgumentParser(description="Inventory podcast media files.")
    parser.add_argument('--catalog', type=str, help="Filter by catalog code.")
    parser.add_argument('--min-duration', type=int, default=600, help="Minimum duration in seconds (default: 10 minutes).")
    parser.add_argument('--index', type=Path, help="Path to the index file (optional if --media-root is provided).")
    parser.add_argument('--media-root', type=Path, required=True, help="Root directory for media files.")

    args = parser.parse_args()

    list_inventory(
        media_root=args.media_root,
        index_file=args.index,
        catalog=args.catalog,
        min_duration=args.min_duration
    )

if __name__ == '__main__':
    main()