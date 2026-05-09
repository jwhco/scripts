# Extract Media Filenames

## Purpose

- From a stream of text, extract known filename formats. By default print to screen. However, as a function these can append metadata to facilitate inventory.
- Use to extract from Obsidian notes (Git repo) known filenames, then compare with known file names found on disk. Determine which are missing from inventory.

## Issues

- May be better presented as single command. `missing.py mp4 --media-root /mnt/e/Media `

## Requirements

- Use to answer the question, "Is this podcast candidate mentioned in notes?" If not it is a candidate to upload to YouTube.
- When ran as a function, be able to build a table with additional metadata. Inclue date produced, generic camera name, and filename where found.
- Sort and dedupe filenames in the script itself. Do this before printing out the lines. The sort and dedupe will speed up using those files. This is more meaningful results.
- The `--missing` command line option prints filenames on disk that are not known in the incoming stream. This script helps the user find files on disk not in notes. Needs `--media-root` set.
- By default the script prints filenames mentioned in piped text.
- The media on disk will have the same filename formatting as the media looked for in pipe.

## Usage

### Find Missing Media

- Find media on disk, but not mentioned in Obisidan using a media stream from repository.
- Pipe text to script to create a list of found filenames. Launch in directory with text.
- Using `git grep` returns only the matching pattern, meaning less text to process.

```bash
git grep -E "(PXL_|IMG_)"| python3 /workspaces/scripts/PodcastHelper/extract-media-filename.py --missing --media-root /mnt/e/Media
```

- Media root must be defined. These are available files to upload to video sharing.
- This will look for all types of media, including images. May mention control files.

### Find Missing MP4 Media

- Find the specific `.mp4` files not mentioned in notes, yet on the local disk. 
  - Then sort so oldest is on bottom. Upload that stuff.

```bash
git grep -E "(PXL_|IMG_)" | python ~/GitHub/scripts/PodcastHelper/extract-media-filename.py --missing --media-root /mnt/e/Media/ | grep mp4 | sort -r
```

- Start looking for filenames on the bottom. Get them uploaded while capturing in note taking.

/EOF/