# Extract Media Filenames

## Purpose

- From a stream of text, extract known filename formats. By default print to screen. However, as a function these can append metadata to facilitate inventory.
- Use to extract from Obsidian notes (Git repo) known filenames, then compare with known file names found on disk. Determine which are missing from inventory.

## Issues

## Requirements

- Use to answer the question, "Is this podcast candidate mentioned in notes?" If not it is a candidate to upload to YouTube.
- When ran as a function, be able to build a table with additional metadata. Inclue date produced, generic camera name, and filename where found.
- Sort and dedupe filenames in the script itself. Do this before printing out the lines. The sort and dedupe will speed up using those files. This is more meaningful results.

## Usage

Pipe text to script to create a list of found filenames. Launch in directory with text.

```bash
git grep -E "(PXL_|IMG_)"| python3 /workspaces/scripts/PodcastHelper/extract-media-filename.py 
```

Using `git grep` returns only the matching pattern, meaning less text to process. Extraction goes very fast.


/EOF/