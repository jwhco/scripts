# Markdown Quality Assurance Tools

## Overview

Python tools ran in the operating system to check for quality issues in a directory hierarchy of Markdown files. Like an [Obsidian](https://obsidian.md/) vault. Tools seek to be platform agnostic, specifically working with Markdown.

## Requirements

- Python 3 or better.

### Specific Functionality

- User runs script to check for similar repository file names, then checks for similarities within those files. Identify notes that are significantly similar, use Jaccard or BoW. Output JSON compatitable with visualization tool. Or Markdown tables.

- List all files with special characters in filename, seek to standardize filenames with [0-9,a-z] or space. The use of `-` dash and `_` underscore fine. Avoid special characters. Understand that space and `_` will HTML URL encode. Find a blend between OS file system, human readable, and usage in scripts. A more automated way than entering characters `,` comma, `$` dollar, and `;` semicolin inside Obsidian search.

- Script to check general syntax of Markdown to identify files in a folder that are NOT Markdown. Identify the problem, throw an error code according to defect. Find corrupt files.

- Script to determine if Markdown file in a repository conforms to file standard. Including filename "{SERIAL} {KEYWORD PHRASE}", file contains YAML front matter, header structure, and file contains `## Related ` header that is complete.

- Identify duplicate images that may have different or the same names. Do this by hashing files, then comparing all hashes, finally printing a report. End user will be able to bulk corrections, linking to primary file, then deleting all duplicate images. Sugguest the oldest original image as survivor.

### Universal Design Elements

- Scripts have an option to produce a Obsidian Markdown report, complete with links to documents that need work. Script makes a table and output Markdown, then deposits it in the Obsidian vault root.

- Write as libraries to incorporate into other utilities and facilitate adding an interface in the future. Centralize configuration, remember user preferences. Use JSON file to store configuration.

- Do not make these an Obsidian plug-in. Keep them in the realm of Markdown centric tools. Use flags for platform specific awareness.

- Primary objective is to use these scripts to keep a directory of Markdown clean. Primary compatibility with flags to [GitHub Markdown](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github) [Obsidian Markdown](https://www.markdownguide.org/tools/obsidian/), and [Leanpub Markua](https://leanpub.com/markua/read).

- Use [Jupyter Notebook](https://jupyter.org/) to build scripts while documenting them. Focus on scripts that can report inside the Jupyter interface before breaking them out into stand alond command-line scripts.

- If it doesn't work on the command line, then it isn't worth trying to put an interface on it. Make scripts clean enough to run in a Terminal window, or feed out to a cluster to run in parallel.

## Distribution

- Scripts are intended for internal collaboration, not general distribution.
- If you can see this publically, please contribute rather than knocking off overall scripts.
- If there is significant interest, this script set will be spun off into a seperate responsitory.

> Copyright 2023 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=jwhco-scripts-readme) All rights reserved.

/EOF/
