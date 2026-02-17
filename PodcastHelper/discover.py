#!/usr/bin/env python3
"""
Discover MP4 files longer than a threshold and create sidecar markdown files.

Usage: python3 discover.py --media-root /path/to/media --min-duration 600 --index index.csv

This script requires `ffprobe` (from ffmpeg) on PATH to measure durations.
"""

from __future__ import annotations

import argparse
import csv
import os
import shlex
import subprocess
from datetime import timedelta
from pathlib import Path
from typing import Optional


def ffprobe_duration(path: Path) -> Optional[int]:
    try:
        res = subprocess.run([
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ], capture_output=True, text=True, check=False)
        out = res.stdout.strip()
        if not out:
            return 0
        # round to nearest second
        return int(round(float(out)))
    except FileNotFoundError:
        raise RuntimeError("ffprobe not found; please install ffmpeg and ensure ffprobe is on PATH")


def strip_leading_front_matter(text: str) -> str:
    # If the file begins with a YAML front matter block (--- newline ... --- newline), remove it.
    lines = text.splitlines(True)
    i = 0
    # skip optional BOM or blank lines until first non-empty
    if i < len(lines) and lines[i].lstrip().startswith('\ufeff'):
        lines[i] = lines[i].lstrip('\ufeff')
    if i < len(lines) and lines[i].strip() == '---':
        # find closing --- on its own line
        i += 1
        while i < len(lines) and lines[i].strip() != '---':
            i += 1
        # skip the closing --- if present
        if i < len(lines) and lines[i].strip() == '---':
            i += 1
            # skip a single following blank line
            if i < len(lines) and lines[i].strip() == '':
                i += 1
            return ''.join(lines[i:])
    return ''.join(lines)


def write_sidecar(sidecar_path: Path, rel_media: str, duration: int):
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    if sidecar_path.exists():
        # Read existing content and remove leading front matter (first block only)
        old = sidecar_path.read_text(encoding="utf-8", errors="ignore")
        body = strip_leading_front_matter(old)
    else:
        body = ""

    # Convert duration to HH:mm:ss format
    duration_human_readable = str(timedelta(seconds=duration))

    header = f"---\nfilename: \"{rel_media}\"\nduration: {duration_human_readable}\n---\n\n"
    sidecar_path.write_text(header + body, encoding="utf-8")


def discover(media_root: Path, min_duration: int, index_file: Path, append: bool = False, limit: Optional[int] = None):
    rows = []
    media_root = media_root.resolve()
    count = 0  # Counter to track the number of processed files

    for root, dirs, files in os.walk(media_root):
        for fn in files:
            if not fn.lower().endswith('.mp4'):
                continue
            full = Path(root) / fn
            try:
                dur = ffprobe_duration(full)
            except RuntimeError as e:
                print(f"ERROR: {e}")
                return 1
            if dur is None:
                dur = 0
            if dur >= min_duration:
                rel = str(full.relative_to(media_root))
                sidecar = full.with_suffix('.md')
                write_sidecar(sidecar, rel, dur)
                rows.append((rel, str(dur), str(sidecar.relative_to(media_root))))

                count += 1
                if limit is not None and count >= limit:
                    print(f"Limit of {limit} media files reached. Stopping discovery.")
                    break
        if limit is not None and count >= limit:
            break

    # Update the index_file path to be in the root of the media folder
    index_file = media_root / index_file.name

    # Ensure the index file is written in the correct location
    mode = 'a' if append and index_file.exists() else 'w'
    with index_file.open(mode, newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if mode == 'w':
            w.writerow(['path', 'minutes', 'sidecar'])  # Updated column name from 'duration' to 'minutes'
        for r in rows:
            w.writerow(r)

    print(f"Discovered {len(rows)} media files (index: {index_file})")
    return 0


def discover_file(file_path: Path, min_duration: int, index_file: Optional[Path] = None, append: bool = False, media_root: Optional[Path] = None):
    full = file_path.resolve()
    if not full.exists():
        print(f"File not found: {full}")
        return 2
    if not full.suffix.lower() == '.mp4':
        print(f"Skipping non-mp4 file: {full}")
        return 3
    try:
        dur = ffprobe_duration(full)
    except RuntimeError as e:
        print(f"ERROR: {e}")
        return 1
    if dur is None:
        dur = 0
    if dur < min_duration:
        print(f"File duration {dur}s shorter than min {min_duration}s; skipping")
        return 0

    # Determine filename field: relative to media_root if provided, else absolute path
    if media_root:
        try:
            rel = str(full.relative_to(media_root.resolve()))
        except Exception:
            rel = str(full)
    else:
        rel = str(full)

    sidecar = full.with_suffix('.md')
    write_sidecar(sidecar, rel, dur)

    if index_file:
        mode = 'a' if append and index_file.exists() else 'w'
        with index_file.open(mode, newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            if mode == 'w':
                w.writerow(['path', 'minutes', 'sidecar'])  # Updated column name from 'duration' to 'minutes'
            # write sidecar path relative to media_root when possible
            try:
                side_rel = str(sidecar.relative_to(media_root)) if media_root else str(sidecar)
            except Exception:
                side_rel = str(sidecar)
            w.writerow([rel, str(dur), side_rel])

    print(f"Processed file: {full} (duration: {dur}s, sidecar: {sidecar})")
    return 0


def main():
    p = argparse.ArgumentParser(description="Discover MP4s and create sidecar markdown files")
    p.add_argument('--media-root', required=True)
    p.add_argument('--min-duration', type=int, default=600)
    p.add_argument('--index', default='index.csv')
    p.add_argument('--limit', type=int, help="Limit the number of media files to process")
    args = p.parse_args()

    media_root = Path(args.media_root)
    index_file = media_root / args.index  # Place index.csv in the media root

    if not media_root.exists():
        print(f"Media root {media_root} does not exist")
        raise SystemExit(2)

    raise SystemExit(discover(media_root, args.min_duration, index_file, limit=args.limit))


if __name__ == '__main__':
    main()
