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

def list_inventory(media_root: Path, index_file: Path, catalog: str, min_duration: int):
    """List media files based on filters."""
    media_root = media_root.resolve()
    results = []

    # Read index file
    if index_file.exists():
        with index_file.open('r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                duration_seconds = int(row['minutes']) * 60

                if catalog and row.get('catalog') != catalog:
                    continue
                if min_duration and duration_seconds < min_duration:
                    continue

                results.append({
                    'path': row['path'],
                    'duration': str(timedelta(seconds=duration_seconds)),
                    'catalog': row.get('catalog', 'N/A'),
                    'published': row.get('published', 'No')
                })

    # Print results
    print("Path\tDuration\tCatalog\tPublished")
    for result in results:
        print(f"{result['path']}\t{result['duration']}\t{result['catalog']}\t{result['published']}")

def main():
    parser = argparse.ArgumentParser(description="Inventory podcast media files.")
    parser.add_argument('--catalog', type=str, help="Filter by catalog code.")
    parser.add_argument('--min-duration', type=int, help="Minimum duration in seconds.")
    parser.add_argument('--index', type=Path, required=True, help="Path to the index file.")
    parser.add_argument('--media-root', type=Path, required=True, help="Root directory for media files.")

    args = parser.parse_args()

    list_inventory(
        media_root=args.media_root,
        index_file=args.index,
        catalog=args.catalog,
        min_duration=args.min_duration or 0
    )

if __name__ == '__main__':
    main()