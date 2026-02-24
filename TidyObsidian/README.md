---
tags: 
- note-taking
- obsidian-utility
- second-brain
- quality-assurance
date: 2023-10-27
updated: 2025-12-23
type: Readme
author: Justin Hitt
status: S4-Publish
workflow: Approved
---

# Scripts to Tidy Obsidian

## Overview

- Over time large repositories of markdown files have problems. Especially those directories that represent note-taking applications.
- Over time errors lead to automation and scripting in note-taking applications to not function well. Need to identify problems quickly.
- Scripts are intended to work with Obsidian, Zettlr, and LogSeq repositories hosted on Github, or some other version control system.
- Most of my heavy lifting is done in a Kubernetes environment. Use an Unix philosophy for scripts. Have filter or manipulation function not both.
- If script can be ran in nightly batches, they can provide log file reports about what is automatically fixed. Autofix carefully.

## Tools

- [GitHub](https://www.github.com/). Used for notes related to project management and version control.
- [Visual Studio Code](https://code.visualstudio.com/Download). The development environment for maintenance uses a `bash` shell for the Terminal.
- [Obsidian.md](https://obsidian.md/). Note-taking application that is the front end of a Markdown-based notes repository.

## Usage

- Run from the root of the Obsidian vault. Checkout `scripts` and `obsidian` in the same workspace next to each other. Then run using `python3 ../scripts/TidyObsidian/find_similar_filenames.py` in the vault root.
- Run on a Kubernetes pod away from the workstation. Many of these scripts are CPU-intensive. If you have a large vault, running them on a cluster somewhere saves you a lot of headaches.
- Always commit before making changes. Some of these scripts do bulk changes to your Obsidian vault. Make sure you can recover from a change. No backup files are created because of version control.

## Requirements

- The script is Obsidian oriented, however, needs to be designed to work with Zettlr, FOAM, and LogSeq. At least NOT break any of these installations, or disrupt running of those note-taking applications.

## Warning

Use these scripts at your own risk. Look over the code carefully.

> Copyright 2023 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=jwhco-scripts-readme) All rights reserved.

/EOF/

