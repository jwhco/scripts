# Obsidian Quality Assurance Tools

## Overview

Python tools ran in the operating system to check for quality issues in an [Obsidian](https://obsidian.md/) vault. Tools seek to be platform agnostic, specifically working with Markdown.

## Requirements

- User runs script to check for similar repository file names, then checks for similarities within those files. Identify notes that are significantly similar, use Jaccard or BoW.
- List all files with special characters in filename, seek to standardize filenames with [0-9,a-z] or space. The use of `-` dash and `_` underscore fine. Avoid special characters. Understand that space and `_` will HTML URL encode. Find a blend between OS file system, human readable, and usage in scripts. A more automated way than entering characters `,` comma, `$` dollar, and `;` semicolin inside Obsidian search.
- Scripts have an option to produce a Obsidian Markdown report, complete with links to documents that need work. Script makes a table and output Markdown, then deposits it in the Obsidian vault root.

## Distribution

- Scripts are intended for internal collaboration, not general distribution.
- If you can see this publically, please contribute rather than knocking off overall scripts. 
- If there is significant interest, this script set will be spun off into a seperate responsitory.


> Copyright 2023 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=jwhco-scripts-readme) All rights reserved.


/EOF/