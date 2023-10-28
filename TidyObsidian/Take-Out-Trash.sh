#!/bin/bash

# Purges files in `Obsidian/.trash` not mofified +90 days

# Notes:
# - Must be ran in Obsidian vault root with full path.
# - Has safety to prevent running when `.trash` missing.

RootDir=`pwd`

if [ ! -d "$RootDir/.trash" ];
then
    echo "ERROR: Missing \`.trash\` -- Not Obsidian Root"
    exit;
fi

OIFS="$IFS"
IFS=$'\n'
for i in `find .trash -type f -print`  
do
     echo rm "~/Documents/GitHub/obsidian/$i"
done
IFS="$OIFS"

###