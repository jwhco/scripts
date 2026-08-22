# Deployment Plan

## Environment

- Runs in WSL or Native Linux machine with direct access to media files.
- Needs high speed storage because podcast media is large gig
- Make
- Python3
- ffmpeg

## Deployment

- Script can run as a single thread, or multiple processors to run through volume quickly. 

### Find And Audit Media Directory

Purpose:
- Determine which media is eligible to produce podcast.
- Determine which media is already published and not.

Steps:
1. Run, `python3 PodcastHelper/discovery.py --media-root /mnt/e/Media/` to inventory. This builds the `index.csv` file.
2. Run, `python3 PodcastHelper/inventory.py --index=/mnt/e/Media/index.csv --media-root=/mnt/e/Media/ --published false --content-root /mnt/c/Users/User/GitHub/obsidian/` to find unpublished materials.
3. Upload everything that is mentioned as unpublished.

### Exporting Podcast Length Media

1. Make sure media directory is online,
2. Make sure export media attached,
3. Run `discovery.py` to find podcasts from media directory,
4. Run `export.py` to push to external media,
5. Provide a report to user,
6. END

## Rollback

- Backing out of any changes is done in GitHub.
- Each command needs a reset or check option.
- Sidcars need structure to be modified.

## Configuration

- `environment`, Are you running in WSL, Local, or K8S?
- `mediaRoot`, Where do podcast media files life? Audio and video in the same tree. Typically in date subdirectories like "YYYYMMDD" or "YYYY-MM-DD", as imported by Adobe Bridge, Adobe Lightroom, or other media management.
- `obsidianRoot`, Where does your Obsidian or markdown notes life? Used to audit media against what has been published.
- `minDuration`, How many minutes in seconds is the smallest media duration to be considered podcast?

/EF/