#!/usr/bin/env python3
"""Find streaming server data attributes and script content"""

import requests
from bs4 import BeautifulSoup
import re
import json

url = "https://v1.samehadaku.how/maou-gakuin-no-futekigousha-season-2-episode-1/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

print(f"Fetching: {url}")
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

# Look for elements with data-* attributes that might contain streaming URLs
print("\n=== Elements with data-content or data-url attributes ===")
data_elements = soup.find_all(attrs={'data-content': True})
print(f"Found {len(data_elements)} elements with data-content")
for elem in data_elements[:5]:
    print(f"{elem.name}.{elem.get('class')}")
    print(f"  data-content: {elem.get('data-content')[:200]}")

data_url_elements = soup.find_all(attrs={'data-url': True})
print(f"\nFound {len(data_url_elements)} elements with data-url")
for elem in data_url_elements[:5]:
    print(f"{elem.name}.{elem.get('class')}: {elem.get('data-url')}")

# Look for all data-* attributes
print("\n=== All elements with data-* attributes (first 10) ===")
all_data = soup.find_all(lambda tag: any(attr.startswith('data-') for attr in tag.attrs.keys()))
for elem in all_data[:10]:
    data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
    if data_attrs:
        print(f"{elem.name}.{elem.get('class')}: {data_attrs}")

# Search for URLs in script tags
print("\n=== Searching for streaming URLs in <script> tags ===")
scripts = soup.find_all('script')
print(f"Found {len(scripts)} script tags")

streaming_patterns = [
    r'https?://[^\s\'"]+(?:blogspot|mega|nakama|vidhide|fembed|wibu)',
    r'["\']url["\']:\s*["\']([^"\']+)["\']',
    r'src:\s*["\']([^"\']+)["\']',
]

for i, script in enumerate(scripts):
    content = script.string
    if content:
        for pattern in streaming_patterns:
            matches = re.findall(pattern, content, re.I)
            if matches:
                print(f"\nScript {i} matches:")
                for match in matches[:5]:
                    print(f"  {match}")
