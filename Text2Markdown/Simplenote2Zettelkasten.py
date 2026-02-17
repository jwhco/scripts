#!/usr/bin/env python3
"""
Simplenote export -> Zettelkasten (Obsidian) markdown converter

Usage:
  python3 simplenote2zk.py /path/to/extracted/notes/ --out outdir

Behavior:
 - reads source/notes.json for metadata
 - for each active note, creates a file named "YYYYMMddHHmm {title}.md"
 - title is the first line of the note content (trimmed) or derived from filename
 - writes YAML-like front matter (not fenced) with keys: tags (list), date, modified
 - preserves the original note body below front matter

This is a small, dependency-free script compatible with Python 3.8+
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


def parse_args():
    p = argparse.ArgumentParser(description="Convert Simplenote export to Zettelkasten markdown files")
    p.add_argument("src", help="Path to extracted Simplenote export folder (contains notes/ and source/)")
    p.add_argument("--out", default=None, help="Output directory (default: ./zk_notes)")
    return p.parse_args()


def load_notes_json(src: Path) -> Dict[str, Any]:
    jpath = src / "source" / "notes.json"
    if not jpath.exists():
        raise FileNotFoundError(f"notes.json not found at {jpath}")
    with jpath.open("r", encoding="utf-8") as f:
        return json.load(f)


def iso_to_datepart(iso: str) -> str:
    # parse ISO like 2025-02-04T14:30:57.000Z
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.strftime("%Y%m%d%H%M")


def iso_to_ymd(iso: str) -> str:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%d")


def sanitize_title(title: str) -> str:
    # remove problematic filesystem chars and collapse whitespace
    title = title.strip()
    # replace newlines with space
    title = re.sub(r"\s+", " ", title)
    # replace slashes with dash
    title = title.replace("/", "-")
    # remove characters typically disallowed in filenames: ?<>\\:*|"\n\r\t
    title = re.sub(r"[\\\\\?:<>\*\|\"]+", "", title)
    # replace any remaining filesystem-unfriendly characters with hyphen
    title = re.sub(r"[\x00-\x1f]+", "", title)
    # collapse multiple spaces to single
    title = re.sub(r" +", " ", title)
    # remove leading/trailing dots and spaces that can be problematic on some filesystems
    title = title.strip(" .")
    # limit length
    if len(title) > 80:
        title = title[:80].rstrip()
    return title


def note_to_filename(creation_iso: str, title: str) -> str:
    prefix = iso_to_datepart(creation_iso)
    safe = sanitize_title(title)
    # if title ends up empty, fall back to a safe id fragment
    if not safe:
        safe = "untitled"
    return f"{prefix} {safe}.md"


def write_note(outdir: Path, filename: str, tags: Optional[List[str]], creation_iso: str, modified_iso: Optional[str], body: str):
    path = outdir / filename
    with path.open("w", encoding="utf-8") as f:
        # fenced YAML front matter for Obsidian compatibility
        f.write("---\n")
        # tags: ensure we write a list (empty list if None)
        tag_list = tags or []
        f.write("tags:\n")
        for t in tag_list:
            f.write(f"  - {t}\n")
        # dates
        f.write(f"date: {iso_to_ymd(creation_iso)}\n")
        if modified_iso:
            f.write(f"modified: {iso_to_ymd(modified_iso)}\n")
        f.write("---\n\n")
        # body
        f.write(body.lstrip('\n'))


def main():
    args = parse_args()
    src = Path(args.src)
    out = Path(args.out) if args.out else Path("zk_notes")
    out.mkdir(parents=True, exist_ok=True)

    data = load_notes_json(src)

    notes = data.get("activeNotes", [])
    count = 0
    for n in notes:
        content = n.get("content", "")
        if not content:
            continue
        # Simplenote content often includes CRLF sequences; normalize
        content = content.replace('\r\n', '\n')
        # title is first non-empty line
        first_line = ""
        for line in content.splitlines():
            if line.strip():
                first_line = line.strip()
                break
        title = first_line if first_line else f"note-{n.get('id')[:8]}"

        creation = n.get("creationDate") or n.get("created") or datetime.utcnow().isoformat()
        modified = n.get("lastModified")
        filename = note_to_filename(creation, title)
        # ensure unique filename
        target = out / filename
        i = 1
        while target.exists():
            target = out / f"{filename[:-3]}-{i}.md"
            i += 1

        tags = n.get("tags")
        write_note(out, target.name, tags, creation, modified, content)
        count += 1

    print(f"Converted {count} notes -> {out}")


if __name__ == "__main__":
    main()
