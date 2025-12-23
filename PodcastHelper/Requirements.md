---
tags:
- podcast-syndication
- podcast-publishing
date: 2025-12-23
author: Justin Hitt
status: S1-Draft
---

# YouTube Podcast Helper

## Tools

- Make
- Python3
- ffmpeg

## Requirements

- Scripts run under Make. This way, if sidecar or files exist, the work will be skipped.
- Video content recorded on Google Pixel 7a, stored in REPO by Adobe Bridge,
- Once videos are found, a sidecar is produced, and then audio conversion.
- After uploading to YouTube, Fabric extracts key notes from the video. Add to sidecar.
- The sidecar becomes the baseline for headlines, show notes, and promotion.
- The sidecar is both a configuration file for that individual media, metadata, and show notes.
- Maintain a list in the root directory of the media folder with the full path of podcast candidates.
- Every modification of the sidecar file updates the YAML front matter `updated: ` with the date `YYYY-MM-DD` format of the current date.
- The sidecar tracks parts, if the video is good for the audio podcast, and dates of activity. Use JSON front matter.
- The index needs to be a CSV that is edited rather than rebuilt. Once initialized, it is used to keep track of progress.
  - Especially if the script is running on multiple machines. A use case is to kick off the script on shared storage.
  - Maintain the basename of each source file, use it to derive sidecar and audio files.
  - Place flags to know the date certain modifications were made. Track workflow in the index and sidecar.
  - Be able to rebuild the index with the sidecar files. Never modify the index manually; it's a reference.
- When editing the sidecar, use markdown to change out sections. For example, after a transcript is downloaded, it is put in the sidecar, or saved in a directory as `{BASENAME}_transcript.md`, then flagged as complete in the sidecar. 

## Goals

- For every podcast, have five clips, ten social media, and two thumbnails. Have the script do the majority of the heavy lifting.
- In the case of select podcasts, convert video to audio based on the sidecar designation. Use sidecar as configuration.

## Steps

1. Find podcast-length media files,
   1. Build a list in the media root,
   2. Capture full relative path,
2. Create a sidecar with YAML meta,
   1. Meta includes creation date,
   2. Includes duration,
3. Place the sidecar next to the media,
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

/EOF/
