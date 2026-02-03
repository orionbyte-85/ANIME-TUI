#!/usr/bin/env python3
"""Test Otakudesu scraper with verification"""

import sys
sys.path.insert(0, '/home/stecustecu/Documents/samehadaku-addon')

import otakudesu_scraper

# Test with Maou Gakuin Episode 1 (from user's log)
episode_url = "https://otakudesu.best/episode/maogkn-ftkg-episode-1-sub-indo/"

print("Testing Otakudesu scraper with verification...")
print(f"Episode: {episode_url}\n")
print("="*60)

links = otakudesu_scraper.get_video_links(episode_url)

print("\n" + "="*60)
print(f"\nFinal Results: {len(links)} working servers")
print("\nServers:")
for i, link in enumerate(links, 1):
    print(f"{i}. [{link['quality']:>6}] {link['server']}")
    print(f"   URL: {link['url'][:80]}...")
    print()
