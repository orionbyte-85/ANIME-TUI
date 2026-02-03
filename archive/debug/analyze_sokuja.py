#!/usr/bin/env python3
"""Analyze Sokuja website structure"""

import requests
from bs4 import BeautifulSoup

# Use Boruto page from user's browser
url = "https://x3.sokuja.uk/anime/boruto-naruto-next-generations-subtitle-indonesia/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print(f"Fetching: {url}\n")
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

print("=" * 60)
print("Looking for episode links...")
print("=" * 60)

# Look for episode list
episode_divs = soup.find_all('div', class_='eplister')
print(f"\nFound {len(episode_divs)} eplister divs")

for div in episode_divs:
    uls = div.find_all('ul')
    print(f"  ULs in this div: {len(uls)}")
    
    for ul in uls:
        lis = ul.find_all('li')
        print(f"    LIs in this UL: {len(lis)}")
        
        # Show first 5 episodes
        for i, li in enumerate(lis[:5], 1):
            a = li.find('a')
            if a:
                title = a.get_text(strip=True)
                href = a.get('href')
                print(f"      {i}. {title}")
                print(f"         {href}")

# Look for any links with "episode" in them
print("\n" + "=" * 60)
print("Looking for links with 'episode'...")
print("=" * 60)

all_links = soup.find_all('a', href=True)
episode_links = [link for link in all_links if 'episode' in link['href'].lower()]
print(f"\nFound {len(episode_links)} links with 'episode'")

for i, link in enumerate(episode_links[:10], 1):
    print(f"{i}. {link.get_text(strip=True)[:50]}")
    print(f"   {link['href']}")
