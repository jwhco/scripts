#!/usr/bin/env python3

"""
Extract Media Filename

- Make a list of the known media filenames in text pipe.
- Print these filenames as a simple text list.

"""

import re
import sys
import os
from argparse import ArgumentParser

def extract_pixel_filenames(text):
    """Regex for PXL_YYYYMMDD_HHMMSSmmm.ext"""
    pixel_regex = re.compile(r'PXL_\d{8}_\d{9}\.(?:jpg|mp4)', re.IGNORECASE)
    return pixel_regex.findall(text)

def extract_apple_filenames(text):
    """
    Regex for IMG_XXXX.ext
    - Matches 'IMG_' followed by 4 or more digits.
    - Handles 'IMG_E' (edited photos).
    - Includes common Apple extensions: .JPG, .HEIC, .MOV, .MP4.
    """
    apple_regex = re.compile(r'IMG_(?:E)?\d{4,}\.(?:jpg|heic|mov|mp4)', re.IGNORECASE)
    return apple_regex.findall(text)

def parse_arguments():
    parser = ArgumentParser(description="Extract and process media filenames.")
    parser.add_argument("--missing", action="store_true", help="Print filenames on disk not in the incoming stream.")
    parser.add_argument("--media-root", type=str, help="Root directory to search for media files.")
    return parser.parse_args()

def find_files_on_disk(media_root):
    """Recursively find all media files under the given root directory."""
    media_files = set()
    for root, _, files in os.walk(media_root):
        for file in files:
            if file.lower().endswith(("jpg", "heic", "mov", "mp4")):
                media_files.add(os.path.join(root, file))
    return media_files

def main():
    args = parse_arguments()

    # Initialize a set to store unique filenames from the input stream
    unique_files = set()

    # Process line by line from standard input
    for line in sys.stdin:
        # Combine both extraction methods
        found_files = extract_pixel_filenames(line) + extract_apple_filenames(line)
        
        # Add found files to the set
        unique_files.update(found_files)

    if args.missing:
        if not args.media_root:
            print("Error: --media-root must be specified when using --missing.", file=sys.stderr)
            sys.exit(1)

        # Find all files on disk
        disk_files = find_files_on_disk(args.media_root)

        # Find files on disk not in the input stream
        missing_files = disk_files - unique_files

        # Print missing files
        for missing_file in sorted(missing_files):
            print(missing_file)
    else:
        # Sort the unique filenames
        sorted_files = sorted(unique_files)

        # Print the sorted filenames
        for filename in sorted_files:
            print(filename)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)