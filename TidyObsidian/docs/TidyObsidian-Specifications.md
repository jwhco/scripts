# Specifications for Tidy Obsidian

## Functional

- Tools specific for markdown in Obsidian, Zettlr, FOAM, and LogSeq. Focus on compatibility.

### Procedural

- Be able to represent a Markdown task in several visual forms.
- Allow editing of tasks in place, as well as in specific views.
- Be able to extract YAML front matter and markdown seperately. Such as tags and hashtags which may impact context.

### Commands

- `find_duplicate_blocks.py` Searches repo for blocks that are similar. This requires reading the entire directory structure to find markdown content.
- `markdown_tasks_extract.py` Print to the screen standardized markdown tasks no matter where they are found in the markdown repo.
- `markdown_tasks_quality.py` Run a set of QACM functions on markdown tasks across repo, report where there are defects. Provide enough context to search for string to fix.
- `markdown_tasks_fixid.py` Adds ID to every task that doesn't already have while while cleaning up some formatting. Using Obsidian Dataview Tasks format.

## Technical

### Universal Task Editing Console

- When it comes to tasks, have a central place to edit with metadata and context. Properly store these details in a way users doesn't need to manage.
- Do this to make tasks themselves a basic unit, however, context for presentation doesn't have to be done manually by the user.
- When possible, have drag and drop ability. Sorting and filtering for a tabular display. Drag columns into desired order to save as views.

> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=tidy-obsidian-specifications) All rights reserved.

/EOF/
