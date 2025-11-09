#
# OPML To Simple RSS List
#

# Purpose:
# - Convert export from Feedly into input for WP RSS Aggregator
#

import xml.etree.ElementTree as ET
import sys
import re

def clean_title(title):
    # Remove commas and special characters from the title
    cleaned_title = re.sub(r'[,!@#$%^&*()-]', '', title)
    return cleaned_title.strip()

def parse_opml(opml_file):
    tree = ET.parse(opml_file)
    root = tree.getroot()

    for outline in root.iter('outline'):
        title = outline.get('title')
        xml_url = outline.get('xmlUrl')
        if title and xml_url:
            cleaned_title = clean_title(title)
            print(f"{cleaned_title}, {xml_url}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python opml_parser.py <opml_file>")
        sys.exit(1)

    opml_file = sys.argv[1]
    parse_opml(opml_file)

###