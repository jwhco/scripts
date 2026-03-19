# Markdown Tasks Tree 

## Use Case

- Extract markdown related tasks in the Obsidian Dataview Task plugin format, display them in a heirarchal tree according to dependences.
- 

## Configuration

- Run scripts from command-line, later be a function in CLI #TidyObsidian tool. Standardize arguments and unix like tool interactions.
- Must function well via SSH or VsCode terminal. Assume user is remote. Use libraries like `argparse` or `click` to create a Claude-Code similar command-line application.

## Specifications


- Tasks are formatted in the markdown files are compatible with Obsidian Dataview Task plugins. There may be non-standard tasks, which it would be okay to report as errors. Only the single line indicated by the markdown task designation, i.e. `- [ ]` or `- [/]` (not complete tasks) is in scope.
- Dependences between tasks are indicated by the `[dependsOn:: A1B2C3]` YAML containing the ID of a precuser task. The linked task will include `[id:: A1B2C3]` clearly stated.
- Look at the [Obsidian Tasks plugin](https://github.com/obsidian-tasks-group/obsidian-tasks) repo for details on formatting. Also the [Tasks User Guide - Task Formats](https://publish.obsidian.md/tasks/Reference/Task+Formats/About+Task+Formats) for formatting.

- The `--catalog A1234B`, `--channel ABC`, and `--hashtag HashTag` are all strings. Contents will vary, but it will always be a string with no spaces, not case sensative, and textually included on the task line or in the YAML front matter of the same document.
- When determining urgency, all tasks will need to be extracted into memory, then dates calculated. Some dates will need to be updated with dates from the original note. 
  - At  very basic, use a network nodal relationship between dependences to determine which tasks are more important than others. A task with a lot of connections is more important than one with very few.
  - The task itself may have a `[priority:: high]` YAML value. If each of the possible priorities have a number value, then it can go in the decision matrix that determines urgency. Build a reference file, then model how [obsidian task plugin urgency](https://publish.obsidian.md/tasks/Advanced/Urgency) is calculated.

## Requirements

- The tree displayed will be like the MS-DOS `tree` command that would outline directories visually. Show in ANSI ASCII characters suitable for an `xterm` terminal.
  - The ASCII character range was 128 to 255, used for drawing lines and connecting elements in the graphical representation of the directory tree.
-  Extract key functions from `markdown-tasks-extract.py` to use here. Place in external file for use with both scripts. Write a library to contain common code.
- Works with the markdown extensions `.md` and `.mmd` exclusively. Expect the markdown to be commonmark, GitHub flavored, or Pandoc markdown. The markdown may include YAML front matter.
- Process all files with tasks. Optimize disk engagement to reduce overhead. Don't assume the markdown corpus is Obsidian. It could be managed by LogSeq, Zettlr, or FOAM.

## User Story

- User wants to see which projects are most urgent according to their dependence relationships. 
	- Running the Script the Use chooses `--catalog`, `--channel`, or `--hashtag` to filter tasks.
	- With the `--hashtag Project` the User finds Tasks like `- [ ] #Project, Title of Project.` then maps dependences. 
  	- The dependences don't need to have the hashtag. The hashtag represents a starting point for the tree.
	- What is returned to the output is a heirarchy with the most important project at top, then continues.
	- With the `--limit 5` option, the User can see the top five of that hashtag, as well as everything in the tree. 

> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=markdown-tasks-tree) All rights reserved.

/EOF/