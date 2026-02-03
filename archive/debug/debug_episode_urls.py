#!/usr/bin/env python3
"""Debug script to check episode URLs before filtering"""

import requests
from bs4 import BeautifulSoup

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

anime_url = "https://otakudesu.best/anime/maou-gakuin-futekigousha-sub-indo/"

resp = requests.get(anime_url, headers=get_headers())
soup = BeautifulSoup(resp.text, 'html.parser')

episode_list = soup.find('div', class_='episodelist')
if episode_list:
    print(f"Found episode list div\n")
    for i, li in enumerate(episode_list.find_all('li')):
        link = li.find('a', href=True)
        if link:
            url = link['href']
            title = link.get_text(strip=True)
            
            has_lengkap = '/lengkap/' in url
            has_batch = 'batch' in url.lower()
            
            print(f"Episode {i+1}:")
            print(f"  title: {title[:60]}")
            print(f"  url: {url}")
            print(f"  has /lengkap/: {has_lengkap}")
            print(f"  has batch: {has_batch}")
            print(f"  FILTERED: {has_lengkap or has_batch}")
            print()
else:
    print("No episode list found!")
