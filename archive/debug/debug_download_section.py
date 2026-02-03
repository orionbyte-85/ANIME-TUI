#!/usr/bin/env python3
"""Detailed analysis of download-eps section"""

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

# Find download-eps section
dl_section = soup.find('div', {'class': 'download-eps'})
if not dl_section:
    print("ERROR: download-eps not found!")
    exit(1)

print("✓ Found download-eps section\n")

# Get all <li> items
items = dl_section.find_all('li')
print(f"Found {len(items)} <li> items\n")

for i, li in enumerate(items):
    print(f"=== Item {i} ===")
    text = li.get_text(strip=True)
    print(f"Text: {text[:100]}")
    
    # Find all links
    links = li.find_all('a', href=True)
    print(f"Links ({len(links)}):")
    for link in links:
        href = link['href']
        link_text = link.get_text(strip=True)
        print(f"  - {link_text}: {href}")
    print()

# Try to find specific server patterns
print("\n=== Server Pattern Analysis ===")
all_links = dl_section.find_all('a', href=True)
print(f"Total links in download section: {len(all_links)}")

server_patterns = {
    'Pixeldrain': r'pixeldrain\.com',
    'Google Drive': r'(?:drive\.google\.com|gdriveplayer\.me)',
    'Krakenfiles': r'krakenfiles\.com',
    'Gofile': r'gofile\.io',
    'Zippyshare': r'zippyshare\.com',
    'Reupload': r'reupload\.org',
    'Mediafire': r'mediafire\.com',
    'Mega': r'mega\.nz',
    'Fembed': r'fembed|streamsb',
}

found_servers = {}
for link in all_links:
    href = link['href']
    for server_name, pattern in server_patterns.items():
        if re.search(pattern, href, re.I):
            if server_name not in found_servers:
                found_servers[server_name] = []
            found_servers[server_name].append(href)

print("\nServers found:")
for server, urls in found_servers.items():
    print(f"  {server}: {len(urls)} links")
    for url in urls[:2]:
        print(f"    - {url}")
