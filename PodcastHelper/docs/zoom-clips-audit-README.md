# Zoom Clips Audit - From Zoom Clips Export Which Covered


## Ues Case

- Determine if Markdown episode sidecar has been created. Create, update, and report.

## Requirements

## Specifications

### Format of Zoom Clips Export

- The CSV identified as the Zoom Clips export by `--zoom-clips` has a header including the following:
	- `Clip Name`, is complete title of the Zoom Clip to use as a key for finding the Markdown episode sidecar in the `--directory` repository.
	- `Clip Duration`, the duration of the clip that needs to be converted for YAML front matter `duration` as formatted `HH:MM:SS` or `MM:SS` when under an hour.
	- `Owner Name`, this is equivalent to YAML front matter `author`.
	- `Create Time`, is equivalent to YAML front matter `date` formatted as `YYYY-MM-DD` from format provided.

## User Story

### Update Missing Details in YAML Front Matter

- User wants an inventory of via an audit of YAML front matter in Markdown episode sidecars according to a Zoom Clips export.
  - Runs, `zoom-clips-audit.py --zoom-clips PodcastHelper/tests/zoom_clips__20260519.csv --directory  /workspaces/obsidian/ --update --dry-run`
  - Script uses `Clip Name` from Zoom Clips export as key. Search with `git grep` the to find sidecar. 
  - Determine if YAML front matter in Markdown extension sidecar are accurate.
- Use the `--check-yaml` function for just a check, this always does a `--dry-run` yet identifies where sidecar exists but data is out of date.

## Configure

## Reference

> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=zoom-clips-audit) All rights reserved.

/EOF/