#!/bin/bash
#
# Aweber To Markdown Conversion
#
# Purpose: Create YAML header for text file then convert to Markdown
# Platform: MacOS, Git Bash
# Author: Justin Hitt
# Usage: Run in target output directory. One time use.
#


TargetDir=/Volumes/Archive/Aweber/hittpubl_2014_03_26

# loop directory
ls $TargetDir | grep -v txt | while read Directory
do
	OutputDirectory=Aweber-$Directory
	mkdir $OutputDirectory
	cd $OutputDirectory
	find $TargetDir/$Directory -name "*.txt" -type f -print | while read File
	do
		../addYAMLtxt2md.sh "$File"
	done
	cd ..
done

###
