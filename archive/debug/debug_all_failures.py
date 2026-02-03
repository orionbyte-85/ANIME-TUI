#!/usr/bin/env python3
"""Debug script to reproduce all reported failures"""

import requests
from bs4 import BeautifulSoup
import scraper as samehadaku_scraper
import sokuja_scraper
import otakudesu_scraper

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

def print_section(title):
    print(f"\n{'='*50}\n{title}\n{'='*50}")

# 1. Samehadaku "No episodes found" (Season 1)
print_section("1. Samehadaku: No episodes found (Season 1)")
# I need to search first to get the URL
results = samehadaku_scraper.search_anime("Maou Gakuin no Futekigousha")
s1_url = None
for r in results:
    if r['title'].strip() == "Maou Gakuin no Futekigousha":
        s1_url = r['url']
        print(f"Found S1 URL: {s1_url}")
        break

if s1_url:
    episodes = samehadaku_scraper.get_anime_episodes(s1_url)
    print(f"Episodes found: {len(episodes)}")
    if not episodes:
        print("FAILURE REPRODUCED: No episodes found")
        # Inspect HTML to see why
        resp = requests.get(s1_url, headers=get_headers())
        print(f"HTML length: {len(resp.text)}")
        if "lstepsiode" in resp.text:
            print("Found 'lstepsiode' class in HTML")
        else:
            print("'lstepsiode' class NOT found in HTML")
else:
    print("Could not find S1 URL in search results")

# 2. Samehadaku "No servers found" (Season 2)
print_section("2. Samehadaku: No servers found (Season 2)")
# Search for S2
s2_url = None
for r in results:
    if "Season 2" in r['title'] and "Part 2" not in r['title']:
        s2_url = r['url']
        print(f"Found S2 URL: {s2_url}")
        break

if s2_url:
    episodes = samehadaku_scraper.get_anime_episodes(s2_url)
    if episodes:
        ep1 = episodes[-1] # Usually last in list is Ep 1? Or first? Samehadaku usually desc.
        # Let's find Episode 1 specifically
        for ep in episodes:
            if "Episode 1" in ep['title'] and "Episode 10" not in ep['title']:
                ep1 = ep
                break
        
        print(f"Testing Episode: {ep1['title']}")
        print(f"URL: {ep1['url']}")
        
        links = samehadaku_scraper.get_all_video_links(ep1['url'])
        print(f"Links found: {len(links)}")
        for l in links:
            print(f"  - {l['server']} ({l['quality']})")
            
        if not links:
            print("FAILURE REPRODUCED: No servers found")
    else:
        print("No episodes found for S2 (unexpected)")

# 3. Sokuja "No servers found"
print_section("3. Sokuja: No servers found")
sokuja_results = sokuja_scraper.search_anime("Maou Gakuin")
sokuja_url = None
for r in sokuja_results:
    if "Maou Gakuin" in r['title']:
        sokuja_url = r['url']
        print(f"Found Sokuja URL: {sokuja_url}")
        break

if sokuja_url:
    episodes = sokuja_scraper.get_anime_episodes(sokuja_url)
    if episodes:
        ep1 = episodes[0] # Sokuja usually has latest first? Or check title
        print(f"Testing Episode: {ep1['title']}")
        print(f"URL: {ep1['url']}")
        
        links = sokuja_scraper.get_video_links(ep1['url'])
        print(f"Links found: {len(links)}")
        for l in links:
            print(f"  - {l['server']} ({l['quality']})")
            
        if not links:
            print("FAILURE REPRODUCED: No servers found")
