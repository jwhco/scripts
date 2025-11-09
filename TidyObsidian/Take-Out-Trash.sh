#!/bin/bash

# Purges files in `Obsidian/.trash` not mofified +90 days

# Notes:
# - Must be ran in Obsidian vault root with full path.
# - Has safety to prevent running when `.trash` missing.

RootDir=`pwd`

if [ ! -d "$RootDir/.trash" ];
then
    echo "ERROR: Missing \`.trash\` -- Not Obsidian Root"
    exit 1;
fi

OIFS="$IFS"
IFS=$'\n'
for i in `find .trash -type f -mtime +90 -print`  
do
     rm "$RootDir/$i"
done
IFS="$OIFS"

exit 0;

###