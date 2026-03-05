# Visualize Content Clusters

## Use Case

- For a directory of markdown notes, determine what are the top five topical clusters. 
- Beacause hashtags and front matter tags are normalized, related terms will group on tags.
- Works with markdown note-taking applications like Obsidian, Zettlr, LogSeq, and FOAM.

## Configuration

- The only reason to run the script under Jupyter is to see the graph. It's not going to display on command line.

## Requirements

- Break out YAML front matter tags and Camel case hash tags as plain words. 
  - Example, `key-word` becomes `key word` for analysis. 
  - Example, `KeyWord` becomes `key word` for analysis.
  - Conversion happens before n-gram analysis of body text.
- Ignore short common headers. The best way to to only tokenize headers three words or longer.
- The ability to have custom stop words to clean up cluster results. Use this for brands, fractional words, and other words that show up in clusters but isn't useful.

## User Story


- User have a markdown note-taking application with files stored as plain text. They want to get an idea of what they have been writing about.
  - After running the script, they can see the top eight clusters of note-taking topics. 
  - After careful consideration, the user focuses on a specific cluster to create a report.


> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=visualize-content-clusters) All rights reserved.

/EOF/