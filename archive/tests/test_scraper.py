#!/usr/bin/env python3
"""Quick test of scraper functions"""

from scraper import search_anime, get_anime_episodes

# Test search
print("Testing search...")
results = search_anime("one piece")
print(f"Found {len(results)} results")
for i, r in enumerate(results[:3]):
    print(f"  [{i}] {r['title']}")
    print(f"      URL: {r['url']}")

# Test episode list
if results:
    print(f"\nTesting episode list for: {results[0]['title']}")
    episodes = get_anime_episodes(results[0]['url'])
    print(f"Found {len(episodes)} episodes")
    for i, ep in enumerate(episodes[:5]):
        print(f"  [{i}] {ep['title']} - {ep['url']}")
