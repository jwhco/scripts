#!/bin/bash
#
# Merge YAML as header to Markdown
#
# Purpose: If a YAML exists and Markdown, then merge to Output.
# Platform: Git Bash
# Author: Justin Hitt
# Usage: Feed it original files, finished files drop locally.
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

# Determine Unique ID Serial
SERIAL=`date -r "$InputFile" "+%Y%m%d%H%M" `

# Build output file name
BaseFile=`basename "$InputFile" `
YAMLFile="${BaseFile%.*}".yml
NewFile=$SERIAL-"${BaseFile%.*}".md
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

### Only Process Text Files - Feed Markdown
if file "$FullPath" | grep -iq ASCII;
then
  cat "$FullPath" >> "$OutputFile"
fi
### Not Feed Markdown, but It Exists
if [ -f "$RootPath/$NewFile" ]
then
  cat "$RootPath/$NewFile" >> "$OutputFile"
fi
echo "" >> "$OutputFile"
echo "/EOF/" >> "$OutputFile"

# Reset values
IFS="$OIFS"

echo DEBUG: END

###