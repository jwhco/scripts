# Extract N-Gram Phrases

## Use Case

- Extract from a file all of the ngrams (trigram by default), then print on the screen. Use to better understand a single file or a corpus of files.
- The n-grams can be piped into a script for further analysis, or handled by another tool for clustering. 

## Configure Run-Time Environment

1. Work from a `.venv` Python Virtual Environment,
2. Prepare packages, `pip install -r requirements.txt`,
3. Install NLTK data sets, https://www.nltk.org/data.html

```python
import nltk
nltk.download('stopwords')
nltk.download('punkt')
```

## Requirements

- Be able to provide a corpus of text via command line pipe. Process standard input to then report on combined ngrams.


## User Story

- User writes an article in markdown, wanting to determine which matching keyword phrases. Runs ngram script to get trigram phrases in list. Runs from the command line.


> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=extract-ngram-phrases) All rights reserved.


/EOF/