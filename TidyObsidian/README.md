---
tags: note-taking, obsidian-utility, second-brain
date: 2023-10-27
type: Readme
author: Justin Hitt
status: S4-Publish
workflow: Approved
---

# Scripts to Tidy Obsidian

## Overview

My Obsidian vault lives in GitHub. When files are deleted, they stick around. GitHub lets me sync between devices. But Obsidian doesn't purge trash folders without a plug-in.

## Tools

- [GitHub](https://www.github.com/). Used for notes related to project management and version control.
- [Visual Studio Code](https://code.visualstudio.com/Download). The development environment for maintenance uses a `bash` shell for the Terminal.
- [Obsidian.md](https://obsidian.md/). Note-taking application that is the front end of Markdown-based notes repository.

## Purpose

- Purge `.trash` files with modifications older than 90 days.
- (Future #2 ) Delete files from `git` repository upon completion.
- (Future #3 ) Issue command `git clean` to reduce size.

## Warning

Use these scripts at your own risk. Look over the code carefully.

> Copyright 2023 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=jwhco-scripts-readme) All rights reserved.

/EOF/
