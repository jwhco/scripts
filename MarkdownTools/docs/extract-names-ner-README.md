# Extract Proper Names Script

## Use Case

- Determine all the characters in a book manuscript. The report will help identify misspelling, undeveloped, or missing names.
- Figure out if a certain person is in a directory of markdown files, report some meta information available in document context.
- Extract names from one set of documents, then feed to LLM to build dossier or person profile. Use in prospecting, research, or character development.

## Configuration

Under the `venv` established previously:

```bash
pip install spacy nltk pyspellchecker
python -m spacy download en_core_web_sm
```

Only `spacy` is required. `nltk` supplies the given-name gazetteer and
`pyspellchecker` the English dictionary; without them the script still runs but
reports more false positives and says so on stderr. The `nltk` `names` corpus
downloads itself on first use.

## Usage

Takes a directory to walk, a single file, or `-` for standard input.

```bash
# whole vault or repository
python3 MarkdownTools/extract-names-ner.py . --out outputs/people.csv

# only names the script is confident about, plus an audit trail of what it threw away
python3 MarkdownTools/extract-names-ner.py . --confidence high --rejected outputs/not-people.csv

# one file, or a pipe
python3 MarkdownTools/extract-names-ner.py Draft/chapter-01.md
cat notes.md | python3 MarkdownTools/extract-names-ner.py -
```

| Option | Effect |
| --- | --- |
| `--out PATH` | CSV output path. Default `outputs/people.csv`. |
| `--rejected PATH` | Also write discarded candidates with a reason code. |
| `--confidence high\|medium` | Lowest confidence to report. Default `medium`. |
| `--min-count N` | Minimum total evidence to include. Default 1. |
| `--model NAME` | Prefer a specific spaCy model, e.g. `en_core_web_lg`. |
| `--names PATH` | Extra given names, one per line, to raise confidence on names the gazetteer does not know. |
| `--config PATH` | YAML override for the word lists (`person_keys`, `channel_words`, `content_words`, `field_words`, `street_words`). |
| `--batch-size N` | Documents per spaCy batch. Default 64. |
| `--quiet` | Suppress progress. Status goes to stderr; stdout stays clean for pipelines. |

## Output

`name,mentions,frontmatter,files,confidence,evidence,variants`

| Column | Meaning |
| --- | --- |
| `name` | Canonical form of the person's name. |
| `mentions` | Times named in prose, headings or wikilinks. |
| `frontmatter` | Files naming them in a metadata field such as `author:`. |
| `files` | Distinct files holding any evidence. |
| `confidence` | `high` when the first name is in the gazetteer, `medium` otherwise. |
| `evidence` | Where they were found: `prose`, `heading`, `wikilink`, `frontmatter`, `alias`. |
| `variants` | Surface forms merged into this row, so every merge is auditable. |

`mentions` and `frontmatter` are deliberately separate columns. A vault whose
every note begins `author: Justin Hitt` would otherwise report that name once
per file and call it a mention count; splitting them shows at a glance whether
a person is actually discussed or merely credited.

Contacts and public figures are both reported. `Scott Vernon` and
`Thomas Jefferson` are equally valid output and no option separates them.

### How a name is judged

1. **Regions.** Frontmatter is parsed, not fed to the model, and only
   person-valued keys are read. Headings and wikilink text are kept as
   candidates, because in a Zettelkasten that is where people live. Code,
   comments, template placeholders, Dataview fields, hashtags and URLs are
   discarded outright.
2. **Shape.** At least two tokens, each sentence-case. Allows `E.J.`, `McCormick`,
   `O'Brien`, `MaryEllen` and `Li-Yu`; rejects ALL-CAPS and digits.
3. **Word lists.** Rejects channel/content compounds (`Facebook Reply`),
   metadata field names (`Workflow Types`) and street suffixes (`Spruce St`).
4. **Name evidence.** First name in the gazetteer gives `high`. Otherwise, if
   even the rarest token is a frequent English word the candidate is rejected as
   a common-noun phrase (`Implementation Schedule`); if not, it is kept as
   `medium` (`Masanobu Fukuoka`).
5. **Merging.** Variants collapse to one canonical row — `J. Hitt`,
   `Justin W Hitt`, `Justin William Hitt` and the byline form
   `Justin Hitt Publisher` all become `Justin Hitt`. Merging requires the first
   names to be compatible, so `John Smith` and `Jane Smith` stay separate.
   Single-token mentions are never rows, but a bare `Pete` credits `Pete Moyer`
   when exactly one person matches.

Use `--rejected` to check the filtering. It is the fastest way to spot a real
person being thrown out and to decide what belongs in a `--config` override.

## Requirements

### Phase 0. Basic Person Name Extraction

- [x] Run script from root of Markdown book, repository, or directory structure. Allow scripts to be outside of working directory.
- [x] Script extracts PERSON named entities from markdown drafts. Find, extract, dedupe, and output to CSV report. 
- [ ] Command line option `--dossier` to report as much contextual information about the individuals as Named Entity Recognition (NER) can provide.
  - At a minimum, report PERSON, ORGANIZATION, LOCATION (CITY, STATE), as well as any contact details. There is no need to mention where the NER is located in notes. The purpose of this output is to identify NER, not inclusion.

- [ ] Use `pandas` data frame to hold NER data table while doing counts and NER discovery. Hold this table as things progress, writing it at the end of processing.
  - Allow memory manipulation of the dataset while referencing an index of the original notes to making passes. 
  - Minimize read of files on the disk. On the initial read, grab the PERSON, ORGANIZTION, and LOCATION as a mass inventory, then second pass the relationships.
  - Data frames offer the best multiple column way to store associations, this may offer a matrix to build the final output file.
- [ ] In future versions of the script, as NER is extracted it will also pull email, phone, and postal address. Gather these details while moving through the files, choosing those elements most relevant to the PERSON.
- [x] Ignore single word names, even if case and use indicates this is a persons name. Focus on sentence case full PERSON names with at least first and last name.
  - Single-token names are never reported as rows. They are used as evidence: a bare `Pete` credits `Pete Moyer` when exactly one known person matches, and is dropped when the match is ambiguous.
- [ ] Script needs to be people oriented, however, if there is an organization with no associated people, then post in the ORGANIZTION column with a blank PERSON.
  - Organizations are currently rejected rather than reported. They appear in the `--rejected` file, so the material for this is already visible.


### Phase 1. Mapping Person and Organization Relationship

### Phase 1. Append Person Location If Available

- An inference can be made that is a person works at an organization and no location details for the person, that the organization location is good enough.

## User Story

- User runs script while sitting in the root directory of a Markdown book, repository, or directory structure. Command line includes options and output location.


> Copyright 2025-2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=extract-names-ner) All rights reserved.


/EOF/