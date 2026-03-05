# Find Similar Filenames

## Use Case

- Help find duplicate files across the Obsidian vault.
- Identify a keyword phrase to search for file in Obisidian.
- A way to reduce the Git repo size removing duplicates.
- Fix duplicate content from previous imports. Resolve similar names.

## Configuration

Steps:

1. Open, VsCode on suitable platform. (Kubernetes, Local workstation)
   1. Open, Terminal in root Obsidian vault clone.
   2. Run, `python3 ../scripts/TidyObsidian/find_similar_filenames.py`
   3. Start at the bottom with similar filenames.
2. Open, Obsidian vault Local workstation.
   1. Find suspected duplicate,
   2. Open side by side,
   3. Keep the desired document,
      1. Fix any wiki link references,
      2. Give unique file names.
   4. When possible give a Zettelkasten key.
   5. Commit work locally,
3. Check work after git push,
4. REPEAT,

- Not every file with a similar name has similar contents.
- Try to use the zettelkasten key for unique content.
- Give priority to files that are in right directory structure.
- Script doesn't modify anything. Check your work before commit.
- The "running on one machine, fixing on another" is for quality.
- Use text formatting if necessary, clean up resuling file.

## Requirements

- Treat zettelkasten key as unique value. If it exists, even when keyword string is similar, the zettelkasten key will override. Filenames with duplicate zettelkasten keys, no matter how unique otherwise need to be looked at by the user.
- Make sure the zettelkasten key is unique amoung all files in the repo. Have a specific warning about this when detecting duplicate file names. This is why `pandas` is so important. Either different hashs can be maintained, or a check can scan through the array of filenames.

## User Story

- User runs script to determine where duplicate files might exist in a large markdown repository. Script runs looking at filenames across the entire directory tree. Reporting back those filenames most likely to be the same.

> Copyright 2024-2026 [JWH Consolidated LLC](https://www.jwhco.com/?utm_source=repository&utm_medium=github.com&utm_content=find-similar-filenames) All rights reserved.


/EOF/