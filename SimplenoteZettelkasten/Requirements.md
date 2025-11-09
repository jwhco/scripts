# Simplenote to Zettelkasten Format Conversion

## Overview

- Convert a Simplenote export into a Zettelkasten format.
	- Simplenote contains `source/notes.json` metadata.
		- `creationDate`, date of creation. "YYYY-MM-ddTHH:mm:ss.nnnZ"
		- `tags`, associated note tags.
		- `content`, filename is first three words,
	- Simplenote has files in root as {FILENAME}.txt,
	- Zettelkasten format "YYYYMMddHHmm {FILENAME}.md"
		- Where "YYYYMMddHHmm" is `creationDate` value.
- Use an Obsidian YAML front matter compatible format.

## User Story

1. User executes command with Simplenote export archive as argument. `command note.zip`
2. Script extracts folder, creating directory `notes`.
3. Script reads `source/notes.json` for creation dates.
4. Matching file name with `content` first line, rename `*.txt` to `*.md` using the Zettelkasten file name format.
	- Files are renamed to preserve `content` from the original archive.
5. Front matter materials are created for each file from `tags`,
	- Insert front matter dates.
6. End.


## Front Matter

Where:

```json
"tags": [
"clients-want",
"consultative-selling",
"customers-want"
]
```

Becomes:

```
tags:
- clients-want
- consultative-selling
- customers-want
```

Values:

```json
"creationDate": "2025-08-06T19:39:11.000Z",
"lastModified": "2025-10-30T01:50:25.901Z",
```

Becomes:

```
date: YYYY-MM-DD
modified: YYYY-MM-DD
```

Using values from the `source/notes.json` file.