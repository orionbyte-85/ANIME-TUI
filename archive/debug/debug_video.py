#!/usr/bin/env python3
"""Debug video URL extraction"""

import requests
from bs4 import BeautifulSoup

url = "https://v1.samehadaku.how/maou-gakuin-no-futekigousha-episode-1/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

print(f"Fetching: {url}")
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

# Look for download section
dl_section = soup.find('div', {'class': 'download-eps'})
if dl_section:
    print("✓ Found download-eps div")
    print(f"HTML snippet:\n{str(dl_section)[:1000]}")
else:
    print("✗ download-eps div not found")
    
    # Try alternative patterns
    print("\nSearching for alternative download sections...")
    
    # Try different class names
    alternatives = [
        ('div', 'download'),
        ('div', 'dl-box'),
        ('div', 'content-download'),
        ('div', 'venutama'),
    ]
    
    for tag, cls in alternatives:
        section = soup.find(tag, class_=cls)
        if section:
            print(f"✓ Found {tag}.{cls}")
            print(f"HTML snippet:\n{str(section)[:500]}")
            break
    
    # Search for any elements with "download" in class or text
    print("\nSearching for elements with 'download' keyword...")
    download_related = soup.find_all(class_=lambda x: x and 'download' in x.lower())
    print(f"Found {len(download_related)} elements with 'download' in class")
    for elem in download_related[:3]:
        print(f"  - {elem.name}.{elem.get('class')}: {str(elem)[:200]}")
