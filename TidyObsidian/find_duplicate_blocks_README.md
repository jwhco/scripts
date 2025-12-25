# Find Duplicate Blocks

## Purpose

- Sus out blocks of duplicate text across an entire directory tree. 
- Script works very well with any directory full of Markdown. Any file based note-taking.

## Issues

- Will need a way to save a cache or incrementally work. With a large repo, it's drawing up a large number of files and takes a long time even on a good machine.
- It's hard to tell if the script is running. Using a debugger it is running, however, there are no command line indicators that something started or is happening.
- Script grinds out a lot of CPU and memory. Need a more incremental way of processing. Maybe read blocks into blocks on disk, then come back and compare. There are 38K files in this Obsidian vault. That's too many.
- Make more command line friendly. Return any non-zero number of duplicate blocks. Have a `--silent` mode which writes the output to a local file in the root directory.


## Requirements

- Determine which blocks in Markdown files are duplicate. Run through whole files first, then if desired run through individual files. When checking a whole file, a checksum is good enough. 
- Report of possible duplicate files, or percent duplicate. Report with "=== Similar files: %% match ===" then list of markdown files. That's enough for an operator to search on strings to find files.
- Ignores headers `##` and `##` because those are likely to be similar in note-taking templates. 
- Completely ignore YAML front matter materials. Metadata contained is highly likely to be duplicate across many files.
- Use of parallel scanning with multiprocessing. For file reading, filtering, hashing, and block extraction.
- Near-duplicate whole-file detection (e.g., 90% simliar entire files.) 
- Token-based Jaccard similarity for fast near-duplicate detection. 

## Usuage

- When a duplicate is found, search for it globally in your note-taking applications. Address on case-by-case basis.
- Understand it is possible there are false positive matches. Unable to avoid when working with large files.


/EOF/