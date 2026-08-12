---
tags:
    - content-marketing
    - recycle-marketing
service: Monetize Back Catalog
script: find-ready-to-publish.py
author: Justin Hitt
date: 2026-03-17
---

# Find Mature Content in Repository

## Purpose

- Find ready to publish content in repository. Focus on good grammar, reading level, and topical relevance.
- To find all the content that is 80% done, then finish it to publish on-line.
- Make the most of content in draft, either as a Post or Report.
- Publish more, rather than writing so many dead end notes.

## Issues

- There aren't any tools to mind notes to determine what content is ready to be finished. Draft articles get lost, ideas don't mature, and materials are missed.

## Requirements

- Determine if something is already published, so that it can be omited from analysis. 
  - If something is `type: Post` and contains a value in `permalink` YAML front matter. Then published.
  - If `status: S4-Publish` and a `permalink` exists in YAML front matter, then published.

- Use a *root keyword* to find chunks of content that look relevant to become an article.
- Use algorithms to find content that is well written, but not yet published. Score "ready to publish".
- Something is ready to publish if it is a certain length (400-800 words), 


## Usage

Find all articles that cluster around "increase income" that are longer than 400 words. 

```bash
python3 find-mature-content.py --yaml-type article --min-wordcount 400 --root-keyword "increase income"

```

After scanning a list of articles would present. From that list an article can be drafted and published.

## Specifications

- Start by creating a file index with right YAML front matter, then determine content candidates by size. 
- Process the file index of what remains, judging content against algorythms to determine maturity.Then report on findings.


### Create File Index

- Calculate the minimum file size for 400 words, then list all files greater than that size into register.
- Work from this master list. Qualify each document as in scope. Then narrow scope, before using list to do analysis.
- This will reduce disk reads, focusing on narrow scope of files. Also the list can be randomized for hashing contents.
- The zettelkasten key prefix can sort into a timeline, however, that has very little value here. List itself beats sequential on disk.

### Determine Content Candidates

- Look for documents with the YAML front matter, `type` category of Article, Post, Feature, or Discussion.
- If there is no YAML but the word count is good or the word "Article" is in the body, then consider for quality check.

### Judge Content Quality

- Limit analysis to documents with 400 words or more of body copy. However, less than 2,500 words total.
  - The `--max-wordcount` and `--min-wordcount` can govern the range of words. With some kind of max/min wordcount in code.
- Use readability score to determine if content is meaningful. The more readable the better.
- Observe the development of concept, including clarity of message and clear benefit to reader.
- Content quality is about being ready to publish. What's on the page is thought out and meaningful in root-keyword context.

## Report Quality Content

- Report including a headline summary, brief description of concept, then link to original file by name.
- Include a bullet list of why the article is a good candidate, contextually for a specific audience.
- It's about knowing which articles to finish, at least a narrow scope list. What will be easy to finish off and post online.


/EOF/