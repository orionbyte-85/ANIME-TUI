#!/usr/bin/env python3
"""Test Samehadaku with proxy fix"""

import sys
sys.path.insert(0, '/home/stecustecu/Documents/samehadaku-addon')

from scraper import get_all_video_links

# Test with Maou Gakuin Episode 1
episode_url = "https://v1.samehadaku.how/maou-gakuin-no-futekigousha-episode-1-subtitle-indonesia/"

print("Testing Samehadaku scraper...")
print(f"Episode: {episode_url}\n")
print("="*60)

links = get_all_video_links(episode_url)

print("\n" + "="*60)
print(f"\nFound {len(links)} servers")
print("\nServers:")
for i, link in enumerate(links[:10], 1):  # Show first 10
    print(f"{i}. [{link['quality']:>6}] {link['server']}")
    url = link['url']
    if isinstance(url, dict):
        print(f"   URL: {url['url'][:80]}...")
        print(f"   Headers: {url.get('headers', {})}")
    else:
        print(f"   URL: {url[:80]}...")
    print()
