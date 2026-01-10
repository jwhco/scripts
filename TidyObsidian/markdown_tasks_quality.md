# Quality Automation for Markdown Tasks

## Purpose 

- Find non-standard markdown tasks, fix them or highlight for user.

## Syntax

```markdown
- [ ] Task description. (Est: 8h)
	- [ ] Sub-Task Description (2h)
	- [ ] Sub-Task Two Description.
```

- Because Obsidian is my primary note-tking application, favor syntax compatable with Task plugin.

## Automation

- Find non-standard spacing. Look for Regex `-\t\[ \]` OR `-\s+\[\t\]` OR `- \[ \]\t` then replace with `- [ ] `, making standard format `- [ ] Description.`
- Clean up odd spacing, okay to be done with multiple passes. Regex `-\s{2}\[ \]\s` OR `- \[ \]\s{2}` would become `- [ ] ` on replacement.
- Incorrect syntax spacing after tick mark. Regex `-\[ \]` becomes `- [ ]`, restoring spacing.

## Requirements

- When cleaning up a task, don't change layout. Don't change indentation, tab spacing in front of bullet list. The task could have sub-tasks for details in a list.
- Find all the markdown tasks like `grep -r -E '^[\t ]*[-*]\s*\[.?\].*' /workspace/obsidian --include=*.md` which works well. It finds things the script mixed.
- Script needs to know if a task is in a `---` or code block as an example. Wholesale updating format may be okay, except in documentation showing poor syntax.

## Notes

- Python library `markdown-checklist` can crate task lists with checkboxes in Markdown format. 
- Python library `markdown-analysis` can parse markdown, extracting headers, paragraphs, and links. https://pypi.org/project/markdown-analysis/

## Reference

- Matthew Rathbone. (2025, August 19) Markdown Task Lists and Checkboxes: Complete Guide for Project Management. https://blog.markdowntools.com/posts/markdown-task-lists-and-checkboxes-complete-guide
  - Highlights good and bad syntax for basic task list. As well as some platform specific.

/EOF/