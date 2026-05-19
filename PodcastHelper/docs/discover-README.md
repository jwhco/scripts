# Discover - Find Eligible Media

## Use Case

- Find eligible podcast media on internal or external drive and create sidecar.

## Requirements

- Discover MP4 type media files (video, audio) longer than a threshold length and create markdown sidecar file.
- Handle YAML front matter writing in markdown sidecar. This is where select metadata from the media will live, as well as status controls.
- Must work for all common media extensions. Anything that might be an audio or video podcast episode of desired length. Automatically use the right tool to pull metadata.
- Cache the directories so we aren't running down the entire media root everytime. Assume large number of media files in the tens of thousands.
- When printing file names to screen, or saving them in a sidecar, use something that in a VsCode terminal will be clickable. Ctrl-click to open.

## User Story

- Attaching an external drive of media, a User wants to quickly find media suitable for podcast episodes.
    - User runs the script, sidecars are produced. These contain the media name, path, length, and extracted metadata.
    - Using markdown tools, or OS search, the markdown sidecar can be removed. Looking at front matter Obsidian can report.
    - Once discovered, the User can start uploading materials

## Configuration

- Install `ffmpeg` before use.

> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=inventory-podcast-helper) All rights reserved.

/EOF/
