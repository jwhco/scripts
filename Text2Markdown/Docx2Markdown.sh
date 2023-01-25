#!/bin/bash
#
# Convert from DocX to Markdown
#
# Purpose: Receive a filename, check docx, convert.
# Platform: Git Bash
# Author: Justin Hitt
# Usage: Will works with DOCX and HTML files.
#
#   find . -name "*.docx" -type f -print | while read file; do $0 "$file" ; done
#

echo DEBUG: START
# Allow space in filename
OIFS="$IFS"

# Get input filename
InputFile="$1"
if [ ! -f "$InputFile" ]
then
  echo "File Not Found"
  exit;
fi
echo DEBUG: InputFile = "$InputFile"

# Extract Root Path
FullPath=`readlink -f "$InputFile" `
RootPath=`dirname "$FullPath" `
echo DEBUG: FullPath = "$FullPath"
echo DEBUG: RootPath = "$RootPath"

# Build output file name
BaseFile=`basename "$InputFile" `
NewFile="${BaseFile%.*}".md
echo DEBUG: BaseFile = "$BaseFile"
echo DEBUG: NewFile = "$NewFile"

# Output needs to sidecar Original
OutputFile="$RootPath/$NewFile"
echo DEBUG: OutputFile = "$OutputFile"

# START: Use Pandoc to DocX to Markdown
pandoc -s "$FullPath" -t markdown -o "$OutputFile"

# Reset values
IFS="$OIFS"

echo DEBUG: END

###