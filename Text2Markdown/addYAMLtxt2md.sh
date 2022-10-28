#!/bin/bash
#
# Version: $Id$
#
# Purpose: Create YAML header for text file then convert to Markdown
# Platform: MacOS
# Usage: Run in location you want files to show up, feeding it names.
#
#   find S0-IDEA -name "*.txt" -type f -print | while read file; do ./addYAMLtxt2md.sh "$file" ; done
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
echo DEBUG: "$InputFile"

# Generate temporary file
HeaderFile=`echo /tmp/$RANDOM-yaml-header.md`
echo DEBUG: $HeaderFile

# Build output file name
BaseFile=`basename "$InputFile" `
OutputFile=$RANDOM-"${BaseFile%.*}".md
echo DEBUG: "$OutputFile"

# Build out YAML Markdown header
cat > $HeaderFile  << EOF
---
tags:
type: Message
EOF

# Print last modified date
echo "date:" `date -r "$InputFile" "+%Y-%m-%d" ` >> $HeaderFile

cat >> $HeaderFile << EOF
author: Justin Hitt
status: Idea
workflow: Requested
---
EOF

cat $HeaderFile "$InputFile" > "$OutputFile"

# Add EOF Marker
printf "\n\n/EOF/\n" >> "$OutputFile"

# Clean up Temporary
rm $HeaderFile

# Reset values
IFS="$OIFS"

echo DEBUG: END

###
