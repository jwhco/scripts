# Sidecar - Create Note From RSS

## Use Case

- To collect information from an RSS feed to create markdown sidecar representing the episode.

## Requirements

- The podcast RSS feed contains episodes and is hosted on Spreaker. The matching domain of the RSS feed will include `spreaker.com` in all cases.
	- The script can have different options to include RSS from Apple, or other platforms. However, for the first version make sure it works perfect for Spreaker feeds.
- The script runs from the command line with the name `sidecar.py`. All output is suitable for a basic xterm. 
  - It's okay to have spinny things for outputs, or curses to make text smoother, however, it must work over an SSH terminal in VsCode.
- The script will be written in python. Download any files using the lowest overhead way possible. 
  - Use environmental variables to determine where a temporary folder exists for downloading RSS, or staging any files.
  - Use environmental variables to determine if script is running via an SSH terminal, an xterminal, or under VsCode. Reduce overhead by making outputs clean and compatiable for all terminal environments.
- Don't spam the RSS hosting and enclosure hosting platforms. Rate check the download of transcripts by queing them up then running in the background while building the markdown episode sidecar.
- When possible use `git grep ` to look at only markdown extensions `.md` to reduce overhead when searching files. Check to make sure we're in a git environment, then error out if not. Look in the `directory` location.

## User Story

### User Wants to Find Podcast Sidecars

- User is trying to figure out what podcast sidecars already exist in a markdown notes vault.
- They run `sidecar.py --directory  /workspaces/obsidian/ --report` to get a list of markdown sidecars that exist in the directory.
- When reporting, provide sttus so the user know the script is doing something. Print the path of the file containing a podcast episode sidecar.
- You'll know it is a podcast sidecar because the YAML front matter will include `type: Podcast` and `permalink: ` with a value. 
- Quickly report on front matter values that are relevant for an RSS feed, or other updating processes for this script.

### User Wants to Build Podcast Sidecars

- User wants to archive a podast via RSS feed. They run `sidecar.py --rss-feed https://www.spreaker.com/show/3257924/episodes/feed --directory /workspaces/obsidian/ --limit 10`
    - The `--limit 10` is to process 10 new episodes then stop. This allows the user to check their work.
    - A command line option `--dry-run` will do the matching and discovery of what is missing WITHOUT creating any markdown sidecar files. No modifications will be made.
    - If `--diretory` is NOT mentioned, then it will start in the current working directory. Any files created will go in the `pages` subfolder off the root of running.
      - If the `pages` subfolder doesn't exist in the root, then alternatively the current working directory.
    - Script downloads the RSS feed,
    - Uses `git grep -n -- "permalink: {PERMALINK}" -- '*.md'` to find a reference to the podcast episode in the front matter of referencing permalink.
        - The variable `{PERMALINK}` would be replaced by the RSS `link` value from the `item` representing this episode.
        - If the permalink doesn't exist in the `directory` markdown files, then create a new sidecar markdown file with the following details from RSS (on sidecar per podcast episode.)
        - Use the `pages` directory in the root of the `directory` folder, error if it doesn't exist.
        - Create a filename based on the episode `pubDate` yet formatted in a zettelkasten key as `YYYYMMDDmmhh` followed a three word phrase derived from `title` (removing stop words). The title will be in title case, capitalizing the first letter in each word.
    - Script builds YAML front matter, then follows with a `#` title, then description. Convert HTML description to markdown.
        - If there are any URL's where the `href` and text are the same, then only include the text.
    - The script runs in the background with status so user knows where they left off. Provide status suitable for running over SSH terminal session.
    - When complete, provide single line status of number of episodes processed, how many files created.
    - After creating a file, report to the screen with the full path so that text can be crtl-clicked to open in VsCode. Most sessions will run in VsCode bash terminal.

## Specifications

### Template for Podcast Markdown Sidecar 

- Filename = "YYYMMDDmmss Key Word Phrase"
- The markdown sidecar has a simple template, referencing only the transcript if available. 

Template:

```markdown
---
{YAML FRONT MATTER}
---

# {TITLE}

## Podcast

{TITLE}

{PLATFORM}, {FILENAME} -->

{DESCRIPTION}

- Tags = {TAGS}

```


Where: 

- `YAML FRONT MATTER`, replace with the fully generated front matter as described elsewhere in this document.
- `FILENAME` comes from the RSS `item` episode `enclosure` URL filename. Not the whole URL, just the filename `.mp3` or what ever media name.
- `TAGS` is the RSS `item` episode 	`itunes:keywords` with spaces between the comma, all on a single line.

### Building of Sidecar YAML Front Matter

- The markdown sidecar has front matter containing the following values. Complete all possible values from RSS feed episode details.

```yaml
tags:
author: Justin Hitt

date:
created:
published:
updated:

type: Podcast
channel:
catalog:
platform: Spreaker
episode:
duration:
permalink:
download:
root-keyword:
```

Where:

- `channel` is the RSS `channel` abriviated. If the channel name is "AdBriefing Copywriting Tips" then channel name will be "ABR" from first letters.
- `permalink` is from RSS `link` in the `item` representing an episode.
- `platform` is the title case of the RSS `item` value `link` domain name, not including "www" or ".com" which represents the hosting platform name.
- `download` is the RSS `item` value from `enclosure` URL to include the full canonical address.
- `date` is the `YYYY-MM-DD` verion of the RSS `item` episode `pubDate`, translated.
- `duration` is a calculation from an episodes `itunes:duration` which is represented in minutes. Transform those minutes to `hh:mm:ss` or `mm:ss` to best represent.
- `tags` come from RSS `item` for the episode `itunes:keywords` then are presented in YAML front matter as newline, dash, then keyword list as presented in RSS.


Notes:

- If a value `podcast:transcript` exists in the RSS episode `item`, then include in YAML front matter as `transcript` URL.
  - Also download the transcript file `type="text/plain` into an `asset` subfolder. 
  - Include in a section near the end of the markdown sidecar to include `## Related` then line break, then `- Transcript [[{FILENAME}]]` followed by another newline.
  - It's important that I'm able to find transcripts from the sidecar when looking at this file in my note taking application.

### Update Missing Details in YAML Front Matter

- User wants to refresh any missing information in the YAML front matter of a markdown sidecar based on RSS feed.
- User runs `sidecar.py --rss-feed https://www.spreaker.com/show/3257924/episodes/feed --directory /workspaces/obsidian/ --update --dry-run` to figure out what might be updated.
- When ran without the `--dry-run` the script will update only the YAML front matter in existing markdown episode sidecars. Not replacing a field with an exiting value.
- There is a `--check-yaml` option that always does a `--dry-run` yet will identify where a markdown episode sidecar exists, however, one or more values are in conflict.
- Everything is matching on the PERMALINK form the RSS as a key. 


## Configuration

> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=sidecar-podcast-helper) All rights reserved.

/EOF/
