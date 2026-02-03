#!/usr/bin/env python3
"""Debug script to check Boruto episode links"""

from bs4 import BeautifulSoup
import re

with open('boruto_page.html', 'r') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Check if it's a Cloudflare challenge
if 'Just a moment' in html or 'challenge-platform' in html:
    print("❌ Cloudflare challenge detected!")
else:
    print("✓ Page loaded successfully")

# Find all links
all_links = soup.find_all('a', href=True)
print(f"\nTotal links found: {len(all_links)}")

# Filter for episode-like links
episode_links = []
for link in all_links:
    href = link['href']
    text = link.get_text(strip=True)
    
    # Check if this looks like an episode link
    if 'boruto' in href.lower() and ('episode' in href.lower() or 'episode' in text.lower()):
        episode_links.append({
            'text': text,
            'href': href
        })

print(f"\nEpisode-like links found: {len(episode_links)}")

# Show first 10
for i, ep in enumerate(episode_links[:10], 1):
    print(f"{i}. {ep['text']}")
    print(f"   {ep['href']}")
