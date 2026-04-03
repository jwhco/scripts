#!/usr/bin/env python3

"""
Extract Media Filename

- Make a list of the known media filenames in text pipe.
- Print these filenames as a simple text list.

"""

import re
import sys

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

def main():
    # Initialize a set to store unique filenames
    unique_files = set()

    # Process line by line from standard input
    for line in sys.stdin:
        # Combine both extraction methods
        found_files = extract_pixel_filenames(line) + extract_apple_filenames(line)
        
        # Add found files to the set
        unique_files.update(found_files)

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