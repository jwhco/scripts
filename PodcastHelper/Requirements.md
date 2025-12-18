# YouTube Podcast Helper

## Tools

- Make
- Python3
- ffmpeg

## Requirements

- Scripts run under Make. This way if sidecar or files exist, the work will be skipped.
- Video content recorded on Google Pixel 7a, stored in REPO by Adobe Bridge,
- Once videos are found, then a sidecar is produced, then audio conversion.
- After uploaded to YouTube, Fabric extracts key notes from video. Add to sidecar.
- The sidecar becomes the baseline for headlines, show notes, and promotion.
- The sidecar is both a configuration file for that individual media, meta data, and show notes.
- Maintain a list in the root directory of the media folder with full path of podcast candidates.
- Every modification of the sidecar file updates the YAML front matter `updated: ` with date `YYYY-MM-DD` format of current date.

## Goals

- For every podast, have five clips, ten social media, and two thumbnails.
- In the case of select podcasts, convert video to audio based on sidecar designation.

## Steps

1. Find podcast length media files,
   1. Build list in media root,
   2. Capture full relative path,
2. Create sidecar with YAML meta,
   1. Meta includes creation date,
   2. Includes duration,
3. Place sidecar next to media,
   1. Name sidecar basename `.md`
4. END

## Commands

### Determine Duration of Mp4

```bash
ffprobe -i PXL_20250301_191304585.mp4 -show_format -v quiet | grep duration
```

- Extracts duration in seconds,
- Works with `ffmpeg` installed,

## Sidecar Example

```markdown
---
type: Sidecar
date: {YYYY-MM-DD -- From date created.}
created: {YYYY-MM-DD -- From source media.}
published:
updated:

channel:
catalog:
duration: {Obtain with ffmpeg}

media: {FILENAME}.mp4
---

# Transcript

# Summary

```

- Much of the front matter is borrowed from the `Podcast` template in Obsidian.

/EOF/