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

### Phase 0. Basic Person Name Extraction

- Run script from root of Markdown book, repository, or directory structure. Allow scripts to be outside of working directory.
- Script extracts PERSON named entities from markdown drafts. Find, extract, dedupe, and output to CSV report. 
- Command line option `--dossier` to report as much contextual information about the individuals as Named Entity Recognition (NER) can provide.
  - At a minimum, report PERSON, ORGANIZATION, LOCATION (CITY, STATE), as well as any contact details. There is no need to mention where the NER is located in notes. The purpose of this output is to identify NER, not inclusion.

- Use `pandas` data frame to hold NER data table while doing counts and NER discovery. Hold this table as things progress, writing it at the end of processing.
  - Allow memory manipulation of the dataset while referencing an index of the original notes to making passes. 
  - Minimize read of files on the disk. On the initial read, grab the PERSON, ORGANIZTION, and LOCATION as a mass inventory, then second pass the relationships.
  - Data frames offer the best multiple column way to store associations, this may offer a matrix to build the final output file.
- In future versions of the script, as NER is extracted it will also pull email, phone, and postal address. Gather these details while moving through the files, choosing those elements most relevant to the PERSON.
- Ignore single word names, even if case and use indicates this is a persons name. Focus on sentence case full PERSON names with at least first and last name.
- Script needs to be people oriented, however, if there is an organization with no associated people, then post in the ORGANIZTION column with a blank PERSON.


### Phase 1. Mapping Person and Organization Relationship

### Phase 1. Append Person Location If Available

- An inference can be made that is a person works at an organization and no location details for the person, that the organization location is good enough.

## User Story

- User runs script while sitting in the root directory of a Markdown book, repository, or directory structure. Command line includes options and output location.


> Copyright 2025-2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=extract-names-ner) All rights reserved.


/EOF/