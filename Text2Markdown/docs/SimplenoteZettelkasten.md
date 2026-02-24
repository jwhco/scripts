# Simplenote -> Zettelkasten (Obsidian) Converter

This small script converts an extracted Simplenote export into Obsidian-compatible markdown files using a Zettelkasten filename format.

Features
- Reads `source/notes.json` from the Simplenote export
- Creates files named `YYYYMMddHHmm {title}.md` using the note `creationDate` and first content line as title
- Adds simple front-matter: `tags`, `date`, and `modified`

Usage

1. Ensure you have an extracted Simplenote export folder (contains `notes/` and `source/notes.json`).
2. Run the converter:

```bash
python3 simplenote2zk.py /path/to/extracted/notes --out ./zk_notes
```

Output
- A folder `zk_notes/` (or the path you provide) filled with markdown files.

Notes and limitations
- The script expects `source/notes.json` in the export. It only processes `activeNotes`.
- Titles are derived from the first non-empty line of each note.
- No external dependencies; works with Python 3.8+

Next steps
- Optionally support reading directly from the ZIP archive.
- Add more front-matter fields (pinned, markdown flag) and configurable filename templates.
