---
tags:
    - readme-file
    - github-repository
    - read-me
    - script-repository
    - command-line
date: 2022-10-28
updated: 2025-12-23
type: Readme
author: Justin Hitt
status: S4-Publish
workflow: Approved
---

# Useful Scripts and Tools

## Overview

Subdirectories indicate automation scripts for Utilities. The goal is to make these scripts platform-independent; however, most commands will be for macOS and Linux.

## Modules

- **Opml2RSSList**. Dump an OPML file into an RSS feed. Playlist migration.
- **SeoHelpers**. Help with technical Search Engine Optimization (SEO).
- **Text2Markdown**. Support migration to markdown from common formats and tools.
- **TidyObsidian**. Quality assurance scripts for Obsidian, Zettlr, and LogSeq.
- **MarkdownTools**. Data extraction from markdown files using text analysis.
- **winAutomate**. Scripts to setup environment in Windows using one-click.
- **WordPressOpt**. Reference and optimization concepts for WordPress hosting.

As these tools mature, they may be forked off into standalone libraries and modules. Until then, each are managed here. When opening an issue, mention module in description.

These labels represent application tags for reference on other platforms. Use GitHub to manage the application. Use Obsidian when writing about those applications.

## Concepts

- Would  be interesting to have a 1980s VT100 terminl mode. 
  - Design using `curses` to do a Emacs style VT100 SSH terminal compatible interface. 
  - A control window on the bottom, right above a `F` key short cuts. Like old DEC VT100 terminals.
  -  Use this to let someone scroll up and down report tables from asks of Obsidian, without losing CLI.
  -  Move around the tool like CMOS, without taking hands off the keyboard. The CLI could work like Vim with an escape.
-  When working in a terminal via Vscode, any file reference prints to the screen so it is a link. 
   -  The command line tool is the finder, while VsCode is the editor. Try to make them work together.

## Guidelines

- The standard for modules is camel case. For tool names it is kebab-case. Use snake_case for Python functions.

## Warning

Use these scripts at your own risk. Look over the code carefully. Some have hardcoded paths for this office environment. 

*Some scripts were for one-time use and may no longer function as expected.*

> Copyright 2023-2025 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=jwhco-scripts-readme) All rights reserved.

/EOF/
