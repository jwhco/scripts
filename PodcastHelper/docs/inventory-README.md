# Inventory - List Eligible Media

## Requirements

- If `filename` is put in the YAML front matter, then it will be easier to find in notes and sidecar files.
  - When the `filename` is found in the body of the `--content-root` notes file, but not in the YAML front matter, then write to YAML front matter if it doesn't already exist.
  - When reading files, provide some kind of status on the screen so I can tell if the script is running. When files are modified, mention that, and use an output format similar to Unix log files.

- Find and report on markdown sidecars that exist in the media root.
    - Report dates `created`, `published`, and `updated`.
    - Report `channel`, `catalog`, and `duration`. Then filename of sidecar.

    To find media that has not been published, compare indexed media filenames with Markdown content:

    ```sh
    python3 PodcastHelper/inventory.py --published false --content-root=/path/to/obsidian --index=/path/to/media/index.csv --media-root=/path/to/media
    ```

    Media whose filename is absent from Markdown is treated as unpublished. A filename on an unchecked
    Markdown task (`- [ ]`) is also treated as unpublished. Omit `--published` to retain the default
    inventory output.

## User Story

- User has already done a discovery, markdown sidecar files exist. Now they want to list certain files by status eligible to upload.
    - User runs script, it searches the `--media-root` then reports what is available to review.

> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=inventory-podcast-helper) All rights reserved.

/EOF/
