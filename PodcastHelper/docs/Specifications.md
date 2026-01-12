# Specifications

## Functional

### Procedural

1. Find podcast-length media files,
   1. Build a list in the media root,
   2. Capture full relative path,
2. Create a sidecar with YAML meta,
   1. Meta includes creation date,
   2. Includes duration,
3. Place the sidecar next to the media,
   1. Name sidecar basename `.md`
4. END

### Commands

- (discovery.py) Find media eligible for podcast.
  - `discovery.py {MEDIA_SOURCE} {MINUTES}`
- (export.py) Copy specific media to external disk.
  - `export.py {MEDIA_SOURCE} {DESTINATION_DIR}`

## Technical

### Determine Duration of Mp4

```bash
ffprobe -i PXL_20250301_191304585.mp4 -show_format -v quiet | grep duration
```

- Extracts duration in seconds,
- Works with `ffmpeg` installed,

### Creation of Sidecar 

- See [[Example_sidecar.md]] for details about sidecar.
- Much of the front matter is borrowed from the `Podcast` template in Obsidian.

/EOF/
