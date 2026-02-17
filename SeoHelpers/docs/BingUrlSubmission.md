# Bing URL Submission Script

## Purpose

- Push a list of URLs to bing search engine.
- Making sure deep links get indexed.

## Reqiurement

- Identification of website to promote from the command line. `--url` command line.
- Command line option, `--bing-api` to include key without hardcoding in the script.
- Command  line identification of `urllist.txt` to be able to push from dynamic file.

- Some kind of randomization of submission as not to flood the platform with pings. Throttling to prevent from getting banned. 
  - Or randomly spread them over proxy. Bing would be seeing a lot of pinging from the same url.
  - Perhaps feed into a network, blending other plaform as a SAAS offering.
  - Even if spreading it around, the same API key is being used. Don't abuse the system.

/EOF/