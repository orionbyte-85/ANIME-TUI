#!/usr/bin/env python3
"""Debug script to check episode listing"""

import otakudesu_scraper

# Test with the anime URL
anime_url = "https://otakudesu.best/anime/maou-gakuin-futekigousha-sub-indo/"

print(f"Testing episodes for: {anime_url}\n")

episodes = otakudesu_scraper.get_anime_episodes(anime_url)
print(f"✓ Found {len(episodes)} episodes\n")

for i, ep in enumerate(episodes):
    print(f"Episode {i+1}:")
    print(f"  title: {ep.get('title', 'N/A')}")
    print(f"  url: {ep.get('url', 'N/A')}")
    print(f"  episode_number: {ep.get('episode_number', 'N/A')}")
    print()
    
    # Test the last one (batch episode)
    if i == len(episodes) - 1:
        print("Testing video links for this episode...")
        try:
            links = otakudesu_scraper.get_video_links(ep['url'])
            print(f"  ✓ Found {len(links)} links")
            if links:
                for link in links[:3]:
                    print(f"    - {link['server']} ({link['quality']})")
            else:
                print("  ⚠️  No links found (might be batch page)")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        print()
