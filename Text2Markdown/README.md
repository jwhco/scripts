---
tags: obsidian-markdown, yaml-metadata, bash-script
author: Justin Hitt
date: 2022-10-28
type: Readme
title: Text2Markdown
status: Publish
workflow: Approved
---

# Text to Obsidian Markdown

## Summary

Add YAML Metadata Header To Text, Make Markdown for Obsidian.

## Process

### Convert {docx,html} to Markdown

1. Run, `createYAMLsidecar.sh`
2. Run, `Docx2Markdown.sh`
3. Run, `addYAMLtext2md.sh`

The commands can be ganged up in large loop. Works even if you are working from a root directory and scripts are outside that directory.

```bash
find . -name "*.docx" -type f -print | while read file; do /d/WORKING-JustinHitt/GitHub/scripts/Text2Markdown/createYAMLsidecar.sh "$file"; /d/WORKING-JustinHitt/GitHub/scripts/Text2Markdown/Docx2Markdown.sh "$file"; /d/WORKING-JustinHitt/GitHub/scripts/Text2Markdown/addYAMLtxt2md.sh "$file"; done
```

I've tested this on {.docx,.rtf}. May need to use [pptx2md](https://github.com/ssine/pptx2md) for PowerPoint.

/EOF/
