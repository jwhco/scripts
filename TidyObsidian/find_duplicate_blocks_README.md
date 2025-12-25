# Find Duplicate Blocks

## Purpose

- Sus out blocks of duplicate text across an entire directory tree. 

## Issues

- Will need a way to save a cache or incrementally work. With a large repo, it's drawing up a large number of files and takes a long time even on a good machine.
- It's hard to tell if the script is running. Using a debugger it is running, however, there are no command line indicators that something started or is happening.
- Script grinds out a lot of CPU and memory. Need a more incremental way of processing. Maybe read blocks into blocks on disk, then come back and compare. There are 38K files in this Obsidian vault. That's too many.

## Requirements

- Determine which blocks in Markdown files are duplicate. Run through whole files first, then if desired run through individual files. When checking a whole file, a checksum is good enough. 
- Report of possible duplicate files, or percent duplicate. Report with "=== Similar files: %% match ===" then list of markdown files. That's enough for an operator to search on strings to find files.


/EOF/