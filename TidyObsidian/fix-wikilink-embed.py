#!/usr/bin/env python3

"""
An example of Correcting Embeded Media Links

Features:
- No guardrails, the script will change markdown files without notice.
- Starts working from the current then crawling every directory.

"""


import re
from pathlib import Path

pattern = re.compile(r'!\[\[(?P<name>.*?\s.*?\.mp3)\]\]')

def repl(match):
    name = match.group("name")
    return f"![[{name.replace(' ', '-') }]]"

for md in Path(".").rglob("*.md"):
    text = md.read_text(encoding="utf-8")
    new_text = pattern.sub(repl, text)
    if new_text != text:
        md.write_text(new_text, encoding="utf-8")
        print(f"Updated: {md}")

