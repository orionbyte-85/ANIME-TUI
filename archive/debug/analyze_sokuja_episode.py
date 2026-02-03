#!/usr/bin/env python3
"""Analyze Sokuja episode page structure"""

import requests
from bs4 import BeautifulSoup
import re

# Use episode URL from user's browser
url = "https://x3.sokuja.uk/boruto-naruto-next-generations-episode-280-subtitle-indonesia/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print(f"Fetching: {url}\n")
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

print("=" * 60)
print("Looking for video player and server options...")
print("=" * 60)

# Look for select/dropdown elements
selects = soup.find_all('select')
print(f"\nFound {len(selects)} select elements:")
for i, select in enumerate(selects, 1):
    print(f"\n{i}. Select element:")
    print(f"   ID: {select.get('id')}")
    print(f"   Name: {select.get('name')}")
    print(f"   Class: {select.get('class')}")
    
    options = select.find_all('option')
    print(f"   Options ({len(options)}):")
    for opt in options:
        value = opt.get('value')
        text = opt.get_text(strip=True)
        print(f"     - {text}: {value[:80] if value else 'No value'}...")

# Look for iframe
print("\n" + "=" * 60)
print("Looking for iframes...")
print("=" * 60)

iframes = soup.find_all('iframe')
print(f"\nFound {len(iframes)} iframes:")
for i, iframe in enumerate(iframes, 1):
    src = iframe.get('src', 'No src')
    print(f"{i}. {src[:100]}...")

# Look for video player div
print("\n" + "=" * 60)
print("Looking for video player container...")
print("=" * 60)

player_divs = soup.find_all('div', class_=re.compile('player|video'))
print(f"\nFound {len(player_divs)} player-related divs")
for div in player_divs[:3]:
    print(f"\nClass: {div.get('class')}")
    print(f"ID: {div.get('id')}")
    # Check for data attributes
    for attr in div.attrs:
        if attr.startswith('data-'):
            print(f"{attr}: {div[attr][:80]}...")
