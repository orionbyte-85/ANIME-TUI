#!/usr/bin/env python3
"""Debug search queries for Maou Gakuin"""

import sokuja_scraper

# Test different search queries
queries = [
    "Maou Gakuin",
    "Maou Gakuin no Futekigousha",
    "maou gakuin",
    "demon king academy",
]

print("Testing Sokuja search...")
for query in queries:
    print(f"\nQuery: '{query}'")
    results = sokuja_scraper.search_anime(query)
    if results:
        print(f"  ✓ Found {len(results)} results:")
        for r in results[:3]:
            print(f"    - {r['title']}")
    else:
        print(f"  ✗ No results")
