#!/bin/bash
#
# Add YAML Text to Markdown Conversion
#
# Purpose: Create YAML header for text file then convert to Markdown
# Platform: MacOS, Git Bash
# Author: Justin Hitt
# Usage: Run in location you want files to show up, feeding it names.
#
#   find S0-IDEA -name "*.txt" -type f -print | while read file; do ./addYAMLtxt2md.sh "$file" ; done
#

echo DEBUG: START
# Allow space in filename
OIFS="$IFS"

# Will be original file {.docx,.txt,.rtf} with Markdown sidecar
InputFile="$1"
if [ ! -f "$InputFile" ]
then
  echo "File Not Found"
  exit;
fi
echo DEBUG: "$InputFile"

# Extract Root Path
FullPath=`readlink -f "$InputFile" `
RootPath=`dirname "$FullPath" `
echo DEBUG: FullPath = "$FullPath"
echo DEBUG: RootPath = "$RootPath"

# Output to Structured Note Filename
#   YYYYMMDDhhmm-{ORIGINAL WITH MD EXT}

# Determine Unique ID Serial based on Input file
SERIAL=`date -r "$InputFile" "+%Y%m%d%H%M" `

# Build output file name
BaseFile=`basename "$InputFile" `
YamlHeader="${BaseFile%.*}".yml # Generated by `createYAMLsidecar.sh`
MarkdownBody="${BaseFile%.*}".md # Generated by `Docx2Markdown.sh`

OutputFile="$RootPath"/$SERIAL-"$MarkdownBody"

echo DEBUG: YamlHeader = "$YamlHeader"
echo DEBUG: MarkdownBody = "$MarkdownBody"
echo DEBUG: OutputFile = "$OutputFile"

# Check for Sidecar Files
## Does YAML header exist?
if [ ! -f "$RootPath/$YamlHeader" ]
then
  echo "YAML Header Not Found: Run Generator"
  echo "createYAMLsidecar.sh $InputFile"
  exit;
fi
## Does Markdown sidecar exist?
if [ ! -f "$RootPath/$MarkdownBody" ]
then
  echo "Markdown Sidecar Missing: Run Generator"
  echo "Docx2Markdown.sh $InputFile"
  exit; 
fi

# Assemble sidecar files to output
## Start with YAML header and Markdown
cat "$RootPath/$YamlHeader" > "$OutputFile"
printf "\n\n" >> "$OutputFile" # Friendly spacing
cat "$RootPath/$MarkdownBody" >> "$OutputFile"

## Add EOF Marker
printf "\n\n/EOF/\n" >> "$OutputFile"

## Verify write, then purge sidecar
if [ -f "$OutputFile" ]
then 
  rm "$RootPath/$YamlHeader" "$RootPath/$MarkdownBody"
fi

# Reset values
IFS="$OIFS"

echo DEBUG: END

###