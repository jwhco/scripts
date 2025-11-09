

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This Python script reads urllist.txt which contains several URLs, one per line and will submit all the URLs to Bing.
This script uses Bing's API Key and URL Submission APIs.
The documentation is found at these two webpages:
    (1) https://docs.microsoft.com/en-us/bingwebmaster/getting-access 
    (2) https://www.bing.com/webmasters/url-submission-api#APIs
Written by Arul John
Blog Post: https://aruljohn.com/blog/python-bing-submission-api/
"""

import requests

# Read all URLs in urllist.txt, join them and return the string
def get_urllist(urllist='urllist.txt'):
    urlstr = ''
    try:
        with open(urllist) as f:
            urls = f.readlines()
            urls = [f'"{u.strip()}"' for u in urls]
            urlstr = ', '.join(urls)
    except FileNotFoundError:
        print(f'ERROR: File {urllist} was not found')
        exit()
    except Exception:
        print('ERROR, quitting')
        exit()
    return f'{urlstr}'

# Constants - replace tehse values with your own
myurl = 'https://iunctura.com'  # replace with your own URL
api_key = 'xxx' # JWH Consolidated LLC

# Variables
url = f'https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlbatch?apikey={api_key}'
headers = { 'Content-Type': 'application/json' }

# Main
if __name__ == '__main__':
    urlliststr = get_urllist()
    data = f'{{ "siteUrl":"{myurl}", "urlList":[{urlliststr}] }}'
    response = requests.post(url, headers=headers, data=data)
    print(response.status_code) # 200 is successful submission
    print(response.text)        # {"d":null} is a successful output
