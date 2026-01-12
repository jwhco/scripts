---
tags: obsidian-markdown, yaml-metadata, bash-script
author: Justin Hitt
date: 2022-10-28
type: Readme
title: Text2Markdown Toolkit
status: Publish
workflow: Approved
---

# Text to Obsidian Markdown

## Summary

- This project facilitiates the conversion of {.docx, .rtf, .odt, .txt, .doc} to Markdown.
- For use in Machine Learning (ML) or knowledge management toolsl ike Obsidian. 
- It converts binary into Markdown with YAML front matter.
- Scripts in this directory are supportive of converting from one note-taking platform to another.

## Process

### Migrate From SimpleNotes to Markdown



### Convert {docx,html} to Markdown

These need to run in a `bash` environent. Works on Windows and MacOS as well.

1. Run, `createYAMLsidecar.sh`
2. Run, `Docx2Markdown.sh`
3. Run, `addYAMLtext2md.sh`

The commands can be ganged up in large loop. Works even if you are working from a root directory and scripts are outside that directory.

```bash
find . -name "*.docx" -type f -print | while read file; do /d/WORKING-JustinHitt/GitHub/scripts/Text2Markdown/createYAMLsidecar.sh "$file"; /d/WORKING-JustinHitt/GitHub/scripts/Text2Markdown/Docx2Markdown.sh "$file"; /d/WORKING-JustinHitt/GitHub/scripts/Text2Markdown/addYAMLtxt2md.sh "$file"; done
```

I've tested this on {.docx,.rtf}. May need to use [pptx2md](https://github.com/ssine/pptx2md) for PowerPoint.

### Post Text2Markdown Toolkit Cleanup

Use instructions in `Text2Markdown` documentation. Migration isn't perfect, but most of the changes can be made in bulk if you have the patience to save your work. Otherwise, manual corrections and editing in Markdown can be doen as you use the files.

## Enhancements

- Be able to convert, {.doc, .odt, .htm*} historically. For `.doc` use `Doc2Docx.ps1` PowerScript. Execution instructions pending.
- Write scripts in `Python` to use libraries instead of secondary software packages. This will also make standardization and formatting easier.
- Add tools to digest Markdown to prepare for Text Mining, Machine Learning, and Knowledge Management. See Jupyter files for details.

## How to Support

- If you use the scripts, Watch the repository.

- If you see a bug or problem, Open an Issue.

- If you like the work, Star to show support.

After 100 watching, I'll spin it off as a Toolkit. That means it's own repository, a development plan, and scripts to install as standalone product.  Paypal email is paypal(at)jwhco.com -- Any support goes towards GitHub subscription and future releases. 

> Copyright 2023 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=jwhco-scripts-readme) All rights reserved.

/EOF/
