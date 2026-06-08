---
tags:
    - podcast-syndication
    - podcast-publishing
    - content-marketing
date: 2025-12-23
updated: 2026-05-19
author: Justin Hitt
status: S2-Review
---

# Podcast Helper

Manage large podcast channels with less effort and greater efficiency. This works for any kind of episodic content.

## Description

Current:

- **Find podcast candidates faster**. Extract from a media directory podcast candidates. From a directory of audio or video, determine which files fit in a range for a podcast candidate that hasn't already been published.
- **Maintain your podcast episode catalog**. The concept is records retention for podcast episodes indexed by the published episode `permalink` or unpublished episode media `filename`. The media or content library feeds files to AI for transcriptions.


Roadmap:

- **Get more from every episode**. By having a complete picture of podcast episodes, you'll know what to promote. Metadata helps find existing content to reference in content marketing.
- **Recycle and combine podcast episodes**. Convert video podcasts that would work for audio. Rip audio tracks, convert formats, and prepare media for publishing. Shorts and excerpts can be found by shortening the media duration.

- **Export packaged episode from libraries**. Prepare podcasts on external drive for publishing, pulling media and Markdown text. If your local internet is slow, push episodes to an external drive to upload elsewhere.
- **Write show notes faster**. Turns transcripts into show notes and descriptions. Batch pull transcripts and write show notes with Fabric. When transcripts are found, they are captured in your content library for manual formatting.
- **Fast track episode promotions**. Turn transcripts, descriptions, media metadata, into context for promotion. Draft social media posts, show notes,
- **More complete channel promotion**. Maintain schema and metadata around podcast episodes. The ability to audit podcast episodes. Does every podcast have show notes, broadcast email, description, social media, newsletter mention, and shorts. Score to determine completeness or identify areas of opportunity.

## Installation

- **Checkout `Scripts` project**, best if placed in a `/workspace/scripts/` working directory next to your content library. From this space you need to be able to reach the media and content libraries.
- **Scripts require Python**, plus required modules. Some scripts use multiprocessing, and all scripts can run across SSH or under a VSCODE terminal. Simple outputs.
- **Setup a media directory**, example `/media/YYYY-MM-DD/` to organize by date. Metadata sidecars will be created next to media. An index will be created in the root.
- **Setup a content library**, a Markdown text directory often behind a note-taking application like Obsidian or Zettlr. This folder is a git repository. It contains draft and finished markdown episode sidecars. Best if next to the script folder.

## Scripts

- `discover.py`
- `sidecar.py`
- `inventory.py`
- `extract-media-filename.py`


## Usage

- **Channel Manager** charged with monetizing a podcast back catalog makes sure each episode to properly represented. No episode left behind.  Inventory podcasts by channel.
  - Auditing of metadata, descriptions, and bounce backs according to `Podcast` schema. See [Schema and Content Organization for Websites](https://us06web.zoom.us/clips/share/RXsS-SwaQW2LEauquKKZ2w)
- **Marketing Coordinator** finds published episodes, extract social media, show notes, and other complementary content. Able to see how Google Analytics UTM and redirects are implemented in promotions. Making sure there is a complete picture of every podcast.
  - A more organized approach to podcast promotion to generate leads and consulting sales. See [Strategic Podcast Promotion for Expert Podcasts](https://us06web.zoom.us/clips/share/jhQQc6ONSkicWMGvdgdN6Q)
  - Find like content topics according to an upcoming campaign, then create social media content and cross post comments to expand reach.
- **Content Marketer** find and transform podcasts into Reports, Courses, and service deliverables. Mine past episodes to extract key points, concepts, and ideas to better serve the underlying audience. 
  - Turn long form podcasts into shorts, cross edit short podcasts into longer, and republish back catalog into new channels.
  - Make the daily management of growing podcast episodes without making common mistakes. See [Which Content Marketing Problems Do You Have?](https://youtu.be/8fFwa35p3xU?si=17XaxYj0Ck-v2QCu)
  - Optimizing podcast episode descriptions across media channels (YouTube, Bitchute, Rumble) even if unique conversation on each. A podcast episode can branch as it moves across channels while keeping descriptive unique in content library.


## About `Podcast Helper`

- To assist marketing agency with management of eposodic content, typically podcast or show, while keeping overhead low. Focus is on managing each episode in the context of lead generation and sales.

> Copyright 2025-2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=jwhco-scripts-readme) All rights reserved.

/EOF/
