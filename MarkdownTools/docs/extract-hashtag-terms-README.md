# Extract Hashtag Terms

## Requirements

- [ ] Issue. Stop words are not being removed from the inventory of outputs. Stop words need to be removed before bi-grams are created. 
  - The stop words are to stop single word terms. If `wordpress` is a stop word, the single word is low value, `wordpress blog` is high value.
- [ ] The terms returned ought not be a single word. Single word hashtags tend to be brand names.
  - Root keywords are typically two words which implied meaning. Listed terms will be two words, not one word.
  - A multiple word n-gram reported may help remove complex hashtags. Don't limit outputs to two words, but definitely don't show one word.
- [ ] A command line argument that allows `--limit n` the number of lines returned, and `--random` which random sorts output. 
  - The random option is useful when auditing hashtag terms. The script will have to read the entire corpus before it can return a random output. (sample)
  - Otherwise, the list of terms are presented in alphabetical order. Using `--limit n` would return after certain number of records are found. (fast)
- Include a whitelist dictionary for terms that will never be split. Words like "VsCode", "LaTeX", and "GitHub".
- Preserve catalog codes like `A1234B`, `001_A1234B` and `GL7` that are hashtags. They are short (under 10 characters), typically with upper case and numbers.
- Handle CamelCase, kebab-case, and snake_case, when converting to n-gram phrases. Normalize before listing.
- Preserve channel hashtags like `#ABR` and `#SWS` making sure to keep uppercase. When presented in normalization, they will remain upper case.
- Prune down paths,
  - Run through files faster by skipping hidden directories. Ignore anything in a `.directory` type folder. Git, Obsidian and LogSeq have hidden folders.
  - Ignore any directories named `Templates` and files with the word "TEMPLATE" in the filename. These are common in Obsidian.

- PRIORITIZE WHITELIST: If the substring is a whitelisted term, take it as a whole even if 'you' and 'tube' are in the dictionary. String `#YouTubeStudio` gets turned into `youtube studio` rather than `you tube studio`.
- [ ] An option to show not list but errors only, `--errors` to figure out YAML front matter and Markdown formatting problems as a dry run.

## User Story

- User wants proper spelling and consistency in hashtags.
  -  By running the script a list of n-gram phrases show normalized camel case hashtags, YAML front matter tags, and hashed catalog codes. 
  - User notices misspellings. They then search for those terms in their note-taking repository. Terms are corrected with a replacement.
- User doesn't want singular and plural hashtags to dilute keyword clustering. After running script, a list of normalized hashtags are presented.
  - Notices `knowledge worker` and `knowledge workers`, a search can be done to determine context. 
  - The search would need to be the lesser of the phrase,  `#KnowledgeWorker`, `#knowledge-worker`, or `-knowledge-worker` to determine use.
  - The most appropriate term can be selected. A search and replace can standardize across note-taking application.



> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=extract-hashtag-terms) All rights reserved.

/EOF/