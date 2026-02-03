#!/usr/bin/env python3
"""Find streaming mirrors"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://v1.samehadaku.how/maou-gakuin-no-futekigousha-season-2-episode-1/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

print(f"Fetching: {url}")
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

# Look for mirrorstream or similar sections
print("\n=== All divs with 'mirror' in class ===")
mirrors = soup.find_all(class_=re.compile('mirror', re.I))
print(f"Found {len(mirrors)} elements")
for m in mirrors:
    print(f"{m.name}.{m.get('class')}")
    print(f"  HTML: {str(m)[:500]}\n")

# Look for all <a> tags in the page that might be streaming links
print("\n=== Looking for streaming-related <a> tags ===")
all_links = soup.find_all('a', href=True)
streaming_keywords = ['blogspot', 'vidhide', 'mega', 'nakama', 'premium', 'stream', 'player']
for link in all_links:
    href = link['href']
    text = link.get_text(strip=True)
    if any(kw in href.lower() or kw in text.lower() for kw in streaming_keywords):
        print(f"  {text}: {href}")

# Look for <ul> with mirrors/servers
print("\n=== Looking for <ul> with server lists ===")
uls = soup.find_all('ul', class_=re.compile('mirror|server|stream', re.I))
for ul in uls:
    print(f"\nFound ul.{ul.get('class')}")
    links = ul.find_all('a', href=True)
    for link in links[:10]:
        print(f"  - {link.get_text(strip=True)}: {link['href']}")
