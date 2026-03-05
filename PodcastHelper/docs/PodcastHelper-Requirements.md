---
tags:
- podcast-syndication
- podcast-publishing
- youtube-publishing
- podcast-content
- business-requirements
date: 2025-12-23
title: "YouTube Podcast Helper"
manager: Justin Hitt
author: Justin Hitt
status: S2-Review
---


# Business Requirements Document (BRD) for YouTube Podcast Helper

## Summary

Support the finding and selection of YouTube content from media source directory. 

Speed up the upload (via third-party) of podcast duration media while maintaining metadata for tracking progress.

Make it easier to publish all relevant media and handling large files associated with podcast.

## Objectives

- Find podcast duration files, flag them with sidecar, then be able to export them to media for uploading.
- Once uploaded to YouTube use sidecar to track permalink to later use for AI description generation.
- Feed published videos to Fabric for description, meta, and social media generation. Thumbnail description.

## Scope

- Focus on "from laptop to published" workflow. Get initial ingested content ready to upload then create metadata.
- Don't create final descriptions. Only background necessary to write descriptions. Use Obsidian for final.
- Try to speed up process, gathering as much support details as possible with some search optimization.
- Use AI to extract transcripts, write summaries, and initial social posts. Enough to manually finalize.
- For every podcast, have five clips, ten social media, and two thumbnails. Have the script do the majority of the heavy lifting.
- In the case of select podcasts, convert video to audio based on the sidecar designation. Use sidecar as configuration.


## Requirements


- Use different scripts, so steps can be taken manually. Each script has a specific single purpose. All scripts read-write the sidecar following the same specifications.

- Scripts run under Make. This way, if sidecar or files exist, the work will be skipped.
- Video content recorded on Google Pixel 7a, stored in REPO by Adobe Bridge,
- Once videos are found, a sidecar is produced, and then audio conversion.
- After uploading to YouTube, Fabric extracts keynotes from the video. Add to sidecar.
- The sidecar becomes the baseline for headlines, show notes, and promotion.
- The sidecar is both a configuration file for that individual media, metadata, and show notes.
- Maintain a list in the root directory of the media folder with the full path of podcast candidates.
- Every modification of the sidecar file updates the YAML front matter `updated: ` with the date `YYYY-MM-DD` format of the current date.
- The sidecar tracks parts, if the video is good for the audio podcast, and dates of activity. Use JSON front matter.
- The index needs to be a CSV that is edited rather than rebuilt. Once initialized, it is used to keep track of progress.
  - Especially if the script is running on multiple machines. A use case is to kick off the script on shared storage.
  - Maintain the base name of each source file, use it to derive sidecar and audio files.
  - Place flags to know the date certain modifications were made. Track workflow in the index and sidecar.
  - Be able to rebuild the index with the sidecar files. Never modify the index manually; it's a reference.
- When editing the sidecar, use Markdown to change out sections. For example, after a transcript is downloaded, it is put in the sidecar, or saved in a directory as `{BASENAME}_transcript.md`, then flagged as complete in the sidecar. 

- The `index.csv`  isn't meant to be human readable, it is a cache file for building sidecars. Maintain duration in minutes, reference file names, and use to allow multiple system processing. 
  - The index is updated with all available scripts, as well as read. Placing it in the media home directory is best.


- Be able to run the script from inside the media folder, or from tools root. Be careful about where the work is being done, define paths in advance. 
  - Paths can also be defined from the command line, however, that is not as practical as by a configuration file.

## Stakeholders

- Subject-matter expert,
- YouTube platform,
- Channel manager,
- Channel subscriber,

## Constraints

- Bulk uploads need to be done on-site with high upload speeds using external media.
- Storage location for media is located on laptop hosted on external drive. NAS would be better.
- Need Kubernetes cluster running Fabric deployment and recipes. Access for analysis. If Fabric is slow batching may not be an option.
- Limited AI credits, while bulk finding of podcasts is good, processing by AI may need to be on a case by case basis. Limit initial inputs and outputs to single file.
- All commands have a `--limit` option to quit after the first X changes. That way scripts can be tested faster, they won't run for hours, and less impact on resources. Works like SQL LIMIT option.
- Podcasts may be uploaded out of order, or get out of sync with supporting documents. Make sure side-car include the base name of the media file.
- Video files typically don't have EXIF specific data. Python can pull EXIF from images and audio, but something else will be needed for video. 
  - To reach from image and audion, use Python `Pillow` for EXIF data.
- Meta data is not always accurate. For video date creation, it will need to be combination of file, metadata, and comparison with local assets. If there is an image in the same directory, then EXIF from that image may help too.

/EOF/
