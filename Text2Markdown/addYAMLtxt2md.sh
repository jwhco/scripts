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

# Build out YAML Markdown header (CUSTOM)
cat > $HeaderFile  << EOF
---
tags:
type: Social
EOF

# Print last modified date
echo "date:" `date -r "$InputFile" "+%Y-%m-%d" ` >> $HeaderFile

# Update YAML Markdown header (CUSTOM)
cat >> $HeaderFile << EOF
author: Justin Hitt
status: Publish
workflow: Approved
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