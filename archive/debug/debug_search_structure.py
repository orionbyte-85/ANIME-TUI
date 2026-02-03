#!/usr/bin/env python3
"""Debug script to check search result structure"""

import otakudesu_scraper

# Test search
print("Testing Otakudesu search...")
results = otakudesu_scraper.search_anime("maou gakuin")
if results:
    print(f"✓ Found {len(results)} results\n")
    for i, anime in enumerate(results[:3]):
        print(f"Result {i+1}:")
        print(f"  title: {anime.get('title', 'N/A')}")
        print(f"  url: {anime.get('url', 'N/A')}")
        print(f"  source: {anime.get('source', 'N/A')}")
        print()
else:
    print("✗ No results found")
