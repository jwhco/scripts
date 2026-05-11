# Extract N-Gram Phrases

## Use Case

- Extract from a file all of the ngrams (trigram by default), then print on the screen. Use to better understand a single file or a corpus of files.
- The n-grams can be piped into a script for further analysis, or handled by another tool for clustering. 

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

## Requirements

- Be able to provide a corpus of text via command line pipe. Process standard input to then report on combined ngrams.


## User Story

- User writes an article in markdown, wanting to determine which matching keyword phrases. Runs ngram script to get trigram phrases in list. Runs from the command line.


> Copyright 2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=extract-ngram-phrases) All rights reserved.


/EOF/