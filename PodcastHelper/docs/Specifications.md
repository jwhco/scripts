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
  - Returns any media at this length or longer.
- (export.py) Copy specific media to external disk.
  - `export.py {MEDIA_SOURCE} {DESTINATION_DIR}`
  - (inventory.py) Use to determine, with insight from sidecar, what files are available. `inventory.py --catalog=A1234B` returns anything flagged for that catalog code, prints a list like `ls -l` to screen.

## Technical

### Determine Duration of Mp4

```bash
ffprobe -i PXL_20250301_191304585.mp4 -show_format -v quiet | grep duration
```

- Extracts duration in seconds,
- Works with `ffmpeg` installed,

### Creation of Sidecar 

- See [[Example_sidecar.md]] for details about sidecar. It looks very much like a note for Obsidian or Zettlr.
- Much of the front matter is borrowed from the `Podcast` template in Obsidian.
- Don't put too much in this that is beyond describing the media file. If there is social content, headlines, or other materials, think about putting that in a different sidecar. 
  - Don't clutter up the file. Make it easy to go from scanning of media to publishing of materials. Especially if {Social, Description, Featured Image, Metadata, Transcript} can be generated individually.

/EOF/
