# Extract Hashtag Terms

## Requirements

- Include a whitelist dictionary for terms that will never be split. Words like "VsCode", "LaTeX", and "GitHub".
- Preserve catalog codes like `A1234B`, `001_A1234B` and `GL7` that are hashtags. They are short (under 10 characters), typically with upper case and numbers.
- Handle CamelCase, kebab-case, and snake_case, when converting to n-gram phrases. Normalize before listing.
- Preserve channel hashtags like `#ABR` and `#SWS` making sure to keep uppercase. When presented in normalization, they will remain upper case.
- Run through files faster by skipping hidden directories. Ignore anything in a `.directory` type folder.

## User Story

- User wants proper spelling and consistency in hashtags.
  -  By running the script a list of n-gram phrases show normalized camel case hashtags, YAML front matter tags, and hashed catalog codes. 
  - User notices mispellings. They then search for those terms in their note-taking repository. Terms are corrected with a replace.
- User doesn't want singlar and plural hashtags to dilute keyword clustering. After running script, a list of normalized hashtags are presented.
  - Notices `knowledge worker` and `knowledge workers`, a search can be done to determine context. 
  - The search would need to be the lesser of the phrase,  `#KnowledgeWorker`, `#knowledge-worker`, or `- knowledge-worker` to determine use.
  - The most appropriate term can be selected. A search and replace can standardize across note taking application.



> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=extract-hashtag-terms) All rights reserved.

/EOF/