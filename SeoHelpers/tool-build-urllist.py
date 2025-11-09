#
# tool-build-urllist - download URL for `urllist.txt`
#
import requests
from bs4 import BeautifulSoup
 
 
url = 'https://iunctura.com/'
reqs = requests.get(url)
soup = BeautifulSoup(reqs.text, 'html.parser')
 
urls = []
# traverse paragraphs from soup
for link in soup.find_all('a'):
    print(link.get('href'))

# END