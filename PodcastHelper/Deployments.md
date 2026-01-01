# Deployment Plan

## Environment

- Runs in WSL or Native Linux machine with direct access to media files.
- Needs high speed storage because podcast media is large gigabytes.

### Tools

- Make
- Python3
- ffmpeg

## Deployment
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

/EF/