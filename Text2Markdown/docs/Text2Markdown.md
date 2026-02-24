---
tags: script-instructions, user-guide, script-usage
author: Justin Hitt
date: 2023-02-01
type: Readme
project: Text2Markdown Toolkit
title: Post Conversion Text2Markdown Instructions
status: Draft
workflow: Pending
---

# Post Conversion Text2Markdown Instructions

## Summary

A summary of what needs to be done to standardize resulting Markdown. Tools don't make a perfect Obsidian, or broad Markdown tool ready text.  This tool can facilitate one time migration from {.docx, .rtf, .odt, .txt, .doc} to Markdown.

## Process

### Bulk Correcting Tables

The text processor `pandoc` creates readable tables, but aren't in good Markdown format. Using `Visual Studio Code` do bulk search and replace as follows. Scope files to include `*.md` for safety.

These tables have problems like text crossing multiple rows, extra human readable but not Markdown friend characters, and odd formatting. Most of this needs clean up that can be done with search and replace.

The number of dashes matter, otherwise you'll blow up Mermaid, JavaScript, YAML front matter and other code legitimately in Markdown depending on your editor.

#### First pass, Tables with dashes

Change the following Regex into equivalent Markdown by replacing `+` with `|` pipe. One expression per line below.

```regex
^\+---
---\+$
--\+--
```

Check your work every step of the way. Bad things happen if you don't use the `\` shash correctly. One mistake here will wipe out unknown chunks of text. Be sure to save work before, check into a repository, and check changes before making a commit.

#### Second pass, Tables with equals (If you dare)

In the next step replace `=` with `-` dash. There will be thousands of changes, be sure to check your work before and after.

```regex
^\+===
===\+$
===\+===
```

These bulk changes will NOT be consistent if you have large tables. It may be easier to find specific references, then bulk remove those. Regular expression to do between two points (i.e. the multiple `=` equals) has too much risk.

A complex RegEx can represent this weird double line in tables:

```regex
^\+===(.+)==\+===(.+)==\+$
```

But not really because the `+===` can repeat. But here's what the RegEx replacement would look like:

```regex
\|===\|===\|===\|
```

As long as there are an equal number of  `|` pipe as `+` plus. Don't do it unless you are a complete idiot. Learn from my mistakes in testing expressions. You may even want to commit after doing the first set.

The following sequence tends to work:

```regex
\+===
===\+$
-=======
-======
-=====
-====
==\|--
=\|--
--=--
-=\|-
```

Replacing `=` equal with `-` dash, till cleaning up end caps. You'll end up with some `-====` multple times. Replacing `-====` with `---` reduces overall character count without impacting Markdown tables.

Don't go less than four characters in the RegEx, otherwise there isn't enough context to match. Most of this is safe unless you have ANSII artwork somewhere. Be mindful of the order and check your work as you go.

#### Check your work stupid

After both sets are done, make sure tables render and dyou don't have giant chunks of text missing. You'll need to use `git diff` or `Visual Studio Code` like tools. Once you commit it will be hard to know how bad you messed up.



### Acceptable But Not Convient Filenames

These scripts will process file names with some special characters and spaces that work on the file system, but aren't convient for Obsidian. You'll need to find these file names manually, then change them in bulk if referenced.

```bash
`
$
;
:
```

Many of these will be escaped with a `\` slash, most will not. Depending on what knowledge management tool you are using, some of these characters will make a mess but they are all valid for the file system.

If you bulk change the filenames in the OS, Obsidian may not pick up the changes. It would be better to enhance the original code to sanitie filenames with basic ASCII characters in the conversion.

/EOF/
