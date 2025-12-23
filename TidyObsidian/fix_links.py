#!/usr/bin/env python3
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

