# Specifications for Markdown Tools

## Functional

- Tools to determine quality, context, and do overall analysis of any markdown documents.

### Procedural

- Have standard set of command line arguments, then function like stackable unix command.
- Needs to be aware of front matter, subheadings, and layout that may impact text analysis.

### Commands

- `extract-names-ner.py`, Use NER to extract PERSON named entities from markdown.
- `topic-modeling-clusters.py`, Report topical clusters in markdown documents.
- `extract-ngram-phrases.py`, Report n-grams (three word default) found in a markdown document.
- `extract-hashtag-terms.py`, Combine both YAML front matter and in body hashtags to list phrases.

## Technical

### Bulk Markdown QACM

- Looking at a large corpus of markdown files in a directory, do basic textual analysis, reporting, and extractions.
- Report on text quality, length of text, and ratios. Be useful for writing large documents.

> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=markdown-tools-specifications) All rights reserved.

/EOF/
