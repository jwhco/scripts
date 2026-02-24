# Extract Proper Names Script

## Use Case

- Determine all the characters in a book manuscript. The report will help identify misspelling, undeveloped, or missing names.
- Figure out if a certain person is in a directory of markdown files, report some meta information available in document context.
- Extract names from one set of documents, then feed to LLM to build dossier or person profile. Use in prospecting, research, or character development.

## Configuration

Under the `venv` established previously:

```bash
pip install spacy
python -m spacy download en_core_web_sm
```

## Requirements

- Run script from root of Markdown book, repository, or directory structure. Allow scripts to be outside of working directory.
- Script extracts PERSON named entities from markdown drafts. Find, extract, dedupe, and output to CSV report.
- Command line option `--dossier` to report as much contextual information about the individuals as Named Entity Recognition (NER) can provide.
  - At a minimum, report Person, Organization, Location, as well as any contact details.

## User Story

- User runs script while sitting in the root directory of a Markdown book, repository, or directory structure. Command line includes options and output location.


> Copyright 2025-2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=extract-names-ner) All rights reserved.


/EOF/