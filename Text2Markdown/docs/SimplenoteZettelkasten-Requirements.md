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



- Front matter will be bound with `---` YAML Front matter like in Obsidian. Front matter `---` always starts on the first line of the file. Containing all converted meta values.
- File names will have any special characters removed. Keep only `0-9a-zA-Z -` characters. Simply remove special characters.

## Front Matter

When `source/notes.json` mentions `tags`, those convey to the related note in an Obsidian compatible format. In the `source/notes.json` it looks like:

```json
"tags": [
"clients-want",
"consultative-selling",
"customers-want"
]
```

Which would become the following Obsidian front matter compatible tags.

```
tags:
- clients-want
- consultative-selling
- customers-want
```

When there is a creation date in `source/notes.json` for a specific note it will looke like this:

```json
"creationDate": "2025-08-06T19:39:11.000Z",
"lastModified": "2025-10-30T01:50:25.901Z",
```

That becomes the following in the resulting zettelkasten formatted document:

```
date: YYYY-MM-DD
modified: YYYY-MM-DD
```

Using values from the `source/notes.json` file.