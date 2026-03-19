# Markdown Tasks Tree 

## Use Case

- Extract markdown related tasks in the Obsidian Dataview Task plugin format, display them in a heirarchal tree according to dependences.
- 

## Configuration

- Run scripts from command-line, later be a function in CLI #TidyObsidian tool. Standardize arguments and unix like tool interactions.
- Must function well via SSH or VsCode terminal. Assume user is remote. Use libraries like `argparse` or `click` to create a Claude-Code similar command-line application.

## Specifications

- Extract key functions from `markdown-tasks-extract.py` to use here. Place in external file for use with both scripts.

## Requirements

- The tree displayed will be like the MS-DOS `tree` command that would outline directories visually. Show in ANSI characters suitable for an `xterm` terminal.

## User Story

- User wants to see which projects are most urgent according to their dependence relationships. 
	- Running the Script the Use chooses `--catalog`, `--channel`, or `--hashtag` to filter tasks.
	- With the `--hashtag Project` the User finds Tasks like `- [ ] #Project, Title of Project.` then maps dependences. 
  	- The dependences don't need to have the hashtag. The hashtag represents a starting point for the tree.
	- What is returned to the output is a heirarchy with the most important project at top, then continues.
	- With the `--limit 5` option, the User can see the top five of that hashtag, as well as everything in the tree. 

> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=markdown-tasks-tree) All rights reserved.

/EOF/