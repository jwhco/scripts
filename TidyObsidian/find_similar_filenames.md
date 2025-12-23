# Find Similar Filenames

## Purpose

- Help find duplicate files across the Obsidian vault.
- Identify a keyword phrase to search for file in Obisidian.
- A way to reduce the Git repo size removing duplicates.
- Fix duplicate content from previous imports. Resolve similar names.

## Usage

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

- Ignore all `.obsidian*` configuration directories.
- Ignore similar names with different zettelkasten keys.
- Ignore similar names in `.trash` folder.

/EOF/