# Visualize Content Clusters

## Use Case

- For a directory of markdown notes, determine what are the top five topical clusters.
- Because hashtags and front matter tags are normalized, related terms will group on tags.
- Works with markdown note-taking applications like Obsidian, Zettlr, LogSeq, and FOAM.

## Configuration

- The only reason to run the script under Jupyter is to see the graph. It's not going to display on command line.

## Requirements

- Break out YAML front matter tags and Camel case hashtags as plain words.
    - Example, `key-word` becomes `key word` for analysis.
    - Example, `KeyWord` becomes `key word` for analysis.
    - Conversion happens before n-gram analysis of body text.
- Ignore short common headers. If the header is common, found in templates for example, then skip. Or only tokenize headers three words or longer.
- The ability to have custom stop words to clean up cluster results. Use this for brands, fractional words, and other words that show up in clusters but isn't useful.
- Use Jupyter for concepts, for implementation use command line script that can focus on specific directories.

## Interpretation

### Scatter Plot: Content Semantic Map

Each dot represents one markdown note from your corpus `ZETTEL_ROOT`, a markdown repo.

Here's how to interpret the scatter plot it produces:

- **Color/cluster membership** indicates semantic similarity—notes of the same color share similar concepts and vocabulary
- **Physical proximity** means notes are highly semantically related; dots clustered together contain overlapping ideas
- **Distance between clusters** shows conceptual separation—far clusters represent distinct topics
- **Cluster density** reflects thematic cohesion—tight clusters have focused meaning; loose clusters contain diverse but related concepts
- **Isolated outliers** (dots far from clusters) represent unique notes that don't align well with major themes
- **Top terms printed for each cluster** (C0, C1, etc.) reveal the dominant concepts defining that cluster
- **Dimensionality reduction caveat** as the 2D plot compresses high-dimensional semantic space, so visual distance is approximate

The key insight: **examine cluster labels and look for outliers**, then review the notes associated with them to validate whether the semantic grouping makes sense for your content.

## User Story

### "Is my writing on topic?" Individual documents or chapters in directory.

- User has a markdown note-taking application with files stored as plain text. They want to get an idea of what they have been writing about.
    - After running the script, they can see the top eight clusters of note-taking topics.
    - After careful consideration, the user focuses on a specific cluster to create a report.
- For the desired cluster, the tool reports observed context. User sees tight mapping of dots.

### "Where to prune research set? Tighten work up?" Check directory stucture.

- User is examining a body of research, looking for a concentration to write a paper, but also wants awareness when it comes to distractions.
    - All relevant research, proposal, and paper outline is put in the same directory.
    - There may include draft materials, relevant commentary, and research notes.
- User runs script against directory to see if there are any outliers to validate. Decision on tangents.
- An outlier is found, a cluster of n-grams that has out of place words. User searches corpus to move those notes out of the project.
    - There is a level of curation, determining if the note is on topic for the project.
    - In some cases, the outlier indicates a relevant topic that needs more research or expanding of context.

> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=visualize-content-clusters) All rights reserved.

/EOF/
