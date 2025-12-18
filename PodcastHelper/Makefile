# YouTube Podcast Helpers
## See `Requirements.md` for procedurals

## Configuration
MEDIA_ROOT := /mnt/e/Media 
MIN_DURATION := 600

## Functions

### Function `discover` finds all `*.mp4` in MEDIA_ROOT that are longer than MIN_DURATION in seconds. Write relative file path to index and create markdown side car with YAML front matter to cpture filename and duration. Name sidecar according to media file. Index is CSV.
discover: *.mp4

### Function `metadata` reads index for media file, extracts creation date, and current date, to write in sidecar front matter. If `duration: ` is missing, then pudate as well.
metadata: index.csv

### Function `convert` checks {FILENAME}.md sidecar files for YAML front matter `convert: true` to extract audio from video via ffmpeg. Saving in same directory as original as `.wav` file.
convert: *.md


