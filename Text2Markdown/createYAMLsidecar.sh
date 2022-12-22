#!/bin/bash
#
# Create YAML Sidecar Based on File
#
# Purpose: Create a sidecar .yml file for reference.
# Platform: Git Bash
# Author: Justin Hitt
# Usage: Run from any location, place sidecar next to original.
#
#   find . -name "*.txt" -type f -print | while read file; do ./createYAMLsidecar.sh "$file" ; done
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
echo DEBUG: RootPath = "$RootPath"

# Build output file name
BaseFile=`basename "$InputFile" `
HeaderFile="${BaseFile%.*}".yml
echo DEBUG: BaseFile = "$BaseFile"
echo DEBUG: HeaderFile = "$HeaderFile"

OutputFile="$RootPath/$HeaderFile"
echo DEBUG: OutputFile = "$OutputFile"

# START: Build YAML Markdown Header
tmpHeaderFile=/tmp/"$HeaderFile"
cat > "$tmpHeaderFile"  << EOF
---
tags:
type: 
EOF

## Print last modified date
echo "date:" `date -r "$InputFile" "+%Y-%m-%d" ` >> "$tmpHeaderFile"
echo "serial:" `date -r "$InputFile" "+%Y%m%d%H%M" ` >> "$tmpHeaderFile"

## Capture original fielname
echo "original: $BaseFile" >> "$tmpHeaderFile"

## Update YAML Markdown header (CUSTOM)
cat >> "$tmpHeaderFile" << EOF
author: Justin Hitt
status: Draft
workflow: Received
---
EOF

# Move header to sidecar
cp "$tmpHeaderFile" "$OutputFile"

# Clean up Temporary
rm "$tmpHeaderFile"

# Reset values
IFS="$OIFS"

echo DEBUG: END

###