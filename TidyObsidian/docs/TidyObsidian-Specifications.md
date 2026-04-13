# Specifications for Tidy Obsidian

## Functional

- Tools specific for markdown in Obsidian, Zettlr, FOAM, and LogSeq. Focus on compatibility.

### Procedural

- Be able to represent a Markdown task in several visual forms.
- Allow editing of tasks in place, as well as in specific views.
- Be able to extract YAML front matter and markdown seperately. Such as tags and hashtags which may impact context.

### Commands

- `find_duplicate_blocks.py` Searches repo for blocks that are similar. This requires reading the entire directory structure to find markdown content.
- `markdown_tasks_extract.py` Print to the screen standardized markdown tasks no matter where they are found in the markdown repo.
- `markdown_tasks_quality.py` Run a set of QACM functions on markdown tasks across repo, report where there are defects. Provide enough context to search for string to fix.
- `markdown_tasks_fixid.py` Adds ID to every task that doesn't already have while while cleaning up some formatting. Using Obsidian Dataview Tasks format.

## Technical

### Stop Words Run-Time Environment

1. Use `.venv` Python Virtual Environment,
2. Install packages, `pip install -r requirements.txt`,
   1. Includes, `nltk` for stop-words data set, https://www.nltk.org/data.html
3. Execute,

```python
import nltk
nltk.download('stopwords')
nltk.download('punkt')
```

4. END

Stop words are used to reduce chunk sizes in duplicate detection.

### Task Dependency in Hierachial Relationship

- Start with Weighted Network Model or Graph.
- A task that is blocked is less important than the blocking task. The blocking task needs to be done first. So if task A depends on the completion of task B, then B is a higher priority by relationship. 
  - The priority and due dates of task A get passed to B in the network relationship. While priorities may be off, or additional tasks blocking, these calculations create task weighting.
  - To determine which task is valuable, a network diagram is build. Factors such as aging, priority, dependencies, and being in progress are weights in connections. 
- The tasks are the `nodes` with connections being dependencies. Those dependences can be a value on `dependsOn` or the same `channel`, `catalog` or `hashtag` reference. Nodes cluster when they are in the same file.
  - Common hashtags form communities.
  - The weight becomes the distance between each node. Then to get from one task to another, the tasks with the longest road needs to be done first. Like a bunch of tasks hanging off a `Goal` hashtag.
    - All `Goal` hashtags together is a nodal cluster, `--hashtag Goal` then weight based on the same category of tasks.
- All of this allows [Network Analysis](https://almeidasilvaf.github.io/NAR/chapters/02_network_statistics.html) on the tasks.  Calculations can be done on a GPU if you have  lot of tasks. Math is likely better than grinding out the text or using AI to interperet.

Reference:

- Sarah Lee (AI). (2025, May 19) The Ultimate Guide to Weighted Graphs. https://www.numberanalytics.com/blog/ultimate-guide-weighted-graphs

### Universal Task Editing Console

- When it comes to tasks, have a central place to edit with metadata and context. Properly store these details in a way users doesn't need to manage.
- Do this to make tasks themselves a basic unit, however, context for presentation doesn't have to be done manually by the user.
- When possible, have drag and drop ability. Sorting and filtering for a tabular display. Drag columns into desired order to save as views.

> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=tidy-obsidian-specifications) All rights reserved.

/EOF/
