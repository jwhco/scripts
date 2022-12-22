#!/bin/bash
#
# Merge YAML as header to Markdown
#
# Purpose: If a YAML exists and Markdown, then merge to Output.
# Platform: Git Bash
# Author: Justin Hitt
# Usage: Feed it Markdown files, finished files drop locally.
#
#   find . -name "*.md" -type f -print | while read file; do $0 "$file" ; done
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
YAMLFile="${BaseFile%.*}".yml
NewFile=$RANDOM-"${BaseFile%.*}".md
echo DEBUG: BaseFile = "$BaseFile"
echo DEBUG: YAMLFile = "$YAMLFile"
echo DEBUG: NewFile = "$NewFile"

OutputFile="$NewFile"
echo DEBUG: OutputFile = "$OutputFile"

# START: Assemble Files Then Endcap
## Check If Files Exist
if [ ! -f "$RootPath/$YAMLFile" ]
then
    echo "YAML Header Not Found"
    exit;
fi

## Read Files Into Output
cat "$RootPath/$YAMLFile" > "$OutputFile"
echo "" >> "$OutputFile"
cat "$FullPath" >> "$OutputFile"
echo "" >> "$OutputFile"
echo "/EOF/" >> "$OutputFile"

# Reset values
IFS="$OIFS"

echo DEBUG: END

###