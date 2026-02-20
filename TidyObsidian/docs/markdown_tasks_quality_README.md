# Markdown Task Quality Checker

## Purpose 

- Find non-standard markdown tasks, fix them or highlight for user, report all tasks.
- The script itself doesn't change the markdown files, it reports a higher quality version of the tasks.
- The tool can be used to find tasks, present them, and then copy-n-paste to fix via Obsidian.

## Syntax

- Using an improved markdown tasks, to possible include estimation of work. Otherwise, Obsidian Dataview Tasks plugin.

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
- Understand tasks that are hierachal, attributing the indented sub-tasks as inherint dependency to the higher level task. An outline of tasks implies highest level tasks are completed after the sub-tasks, or sub-sub-tasks are completed.


## Workflow Pseodocode

1. Isolate leading structure (indentation + marker + checkbox). Find the task via basic formatting. Only looking for `- [ ]` task in various forms.
2. Heuristic Repair: Fix single colon metadata [key: val] -> [key:: val]. Need to find known errors, clean them as we go.
3. Extract all valid metadata [key:: value]. This is where `created`, `due`, and other values are pulled out.
4. Extract Description (everything NOT a metadata box). A task is a single line. There could be bullets under the task that are not additional tasks.
5. Emoji to Dataview Conversion. While most data is likely to be dataview style, need to account for emoji style.
6. Final Cleaning. Collapse multiple spaces into one, trim ends.
7. Rebuild the Task. Force single space between description and metadata, and between metadata boxes.
8. Compare. If the standardized version differs from the original, we have a modification. This count is for limits.
9. Report best quality markdown task. Make sure that every task is hashed in a way to match back with original when updates are available.
10. END




## Notes

- Python library `markdown-checklist` can crate task lists with checkboxes in Markdown format. 
- Python library `markdown-analysis` can parse markdown, extracting headers, paragraphs, and links. https://pypi.org/project/markdown-analysis/

## Reference

- Matthew Rathbone. (2025, August 19) Markdown Task Lists and Checkboxes: Complete Guide for Project Management. https://blog.markdowntools.com/posts/markdown-task-lists-and-checkboxes-complete-guide
  - Highlights good and bad syntax for basic task list. As well as some platform specific.

/EOF/