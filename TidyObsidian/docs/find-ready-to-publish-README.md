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


	- What is "highly structured enough to publish"? Number of words. Structure of sentences. Readability. Size of paragraphs and grammar. 
	- Evaluate clarity, structure, and strength of the arguments. Does the content make sense. Are there any python libraries to support this, minimal AI.
	- Develop a checklist that includes analysis, review, and a punch list of items. Like how SEO analysis works.
		- Zettlr editor has [readability algorithm](https://www.zettlr.com/readability) implementation. It's available during editing.

- Use a dictionary to expand root keyword terms. For each word in phrase, or bi-gram, find synonoms to produce a search combination. Also find words near each other.



- Use a *root keyword* to find chunks of content that look relevant to become an article.
- Use algorithms to find content that is well written, but not yet published. Score "ready to publish".
- Something is ready to publish if it is a certain length (400-800 words), 


- If I was looking for a special report in draft, I could search `type: Report` with more than 2,500 words. That assumes the report hasn't been broken out into #StoryLine or #Scrivener. 
  - To find reports, I may need to look for YAML front matter with `xelatex` as the pdf output mode. That's for a single file report likely referenced as manuscript from `type: Report` or `type: Proposal` note.


### Quantitative Signals
- Word Count Range — 400–800 words for articles, 2,500+ for reports (minimum threshold for maturity). Count only the words in the body of the file.
- Document Size — Could be a proxy for content depth, excludes stubs and notes. Document size is NOT an indicator of the readiness for publishing.
- Readability Score — Measurable metric (Zettlr algorithm or similar) indicating prose quality. Do a measure like Hemmingway App talking about document complexity.
- Text Density — Paragraphs per section, sentence length distribution, complexity metrics. More paragraphs and sentences is closer to a ready to publish article.
### Publication Status
- Published vs. Unpublished — Distinction via YAML front matter (permalink, status, type fields). 
  - Determine if something is already published, so that it can be omited from analysis. 
    - If something is `type: Post` and contains a value in `permalink` YAML front matter. Then published.
    - If `status: S4-Publish` and a `permalink` exists in YAML front matter, then published.
- YAML Front Matter — Presence and completeness (type, status, permalink indicators)
- Type Classification — Article, Post, Feature, Report,  Discussion, Proposal (context for completion readiness)
- Status Field Values — e.g., "S4-Publish" signaling publication intent
### Content Quality Dimensions
- Clarity & Message Coherence — Does the argument make logical sense? There can be logical fallacy detection in text if it doesn't take up a lot of processor.
- Concept Development — Progression from introduction through supporting points to conclusion. A document with a strong headline, then three subheadings with paragraphs between each is better than not.
- Argument Strength — Quality of evidence, examples, reasoning. Determine these things by Named Entity Recognition (NER), as well as language that indicates persuasive writing.
- Reader Benefit — Clear value proposition and relevance to audience. Is this something that can be done with semantic analysis within NLTK?
### Semantic & Topical Relevance
- Root Keywords — Primary topic terms used to cluster related content. Use to short list documents that may be talking about that topic.
- Bi-gram & N-gram Analysis — Multi-word phrases indicating topic maturity. This is only the case when looking at *root keywords* expanded into a keyword phrase.
- Synonym Expansion — Related terms and keyword variations for topical coverage. From a two word root keyword, expand it into more terms to search better. Not sure which python library.
- Topic Clustering — Grouping articles around shared themes (e.g., "increase income"). This isn't as necessary for reporting or presentation, only seconarily if better 
- Contextual Fit — Relevance to target audience and publication strategy if building content from scratch.
### Structural Indicators
- Document Organization — Hierarchy, section coherence, logical flow. The main headline will be `#` with subheads being `##` formatted with markdown. A good heading will be more then 3 words.
- Paragraph Structure — Appropriate length, topic clarity, transitions. There needs to be a way to determine if it is actually a paragraph, or nonsense.
- Grammar & Syntax — Correctness and consistency. A high word count with low grammar could be a bullet point list. That can be converted into an article.

### Composite Assessment
- Readiness Score — Multi-factor composite indicating publication proximity. 
- Completion Effort — How much work remains to publish (low/medium/high)
- Priority Ranking — Which articles to finish first based on score and effort

### Reporting Output
- Candidates List — Ranked articles meeting criteria. A list of content with filename, title, and scoring.
- Rationale Summary — Why each article is ready-to-finish (strengths, gaps). This can be a ranking, some articles are more ready to publish than others.
- Action Punch List — Specific improvements needed before publication. This would be something for a human to look at when they find a good candidate.

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