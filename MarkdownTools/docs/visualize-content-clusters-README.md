# Visualize Content Clusters

## Use Case

- For a directory of markdown notes, determine what are the top five topical clusters. 
- Beacause hashtags and front matter tags are normalized, related terms will group on tags.

## Configuration

## Requirements

- Break out YAML front matter tags and Camel case hash tags as plain words. 
  - Example, `key-word` becomes `key word` for analysis. 
  - Example, `KeyWord` becomes `key word` for analysis.
  - Conversion happens before n-gram analysis of body text.


## User Story


> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=visualize-content-clusters) All rights reserved.

/EOF/