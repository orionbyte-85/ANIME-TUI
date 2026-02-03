#!/usr/bin/env python3
"""Test title matching with Maou Gakuin"""

import anilist_api
import sokuja_scraper
import otakudesu_scraper

# Search AniList for Maou Gakuin
print("=" * 60)
print("Searching AniList for 'Maou Gakuin'...")
print("=" * 60)

results = anilist_api.search_anime("Maou Gakuin", limit=3)
if results:
    anime = results[0]
    print(f"\n✓ Found: {anime['title']}")
    print(f"  Romaji: {anime.get('title_romaji')}")
    print(f"  English: {anime.get('title_english')}")
    print(f"  Native: {anime.get('title_native')}")
    
    # Extract keywords
    def extract_keywords(title):
        if not title:
            return []
        keywords = []
        parts = title.split(':')
        if len(parts) > 1:
            keywords.append(parts[0].strip())
        keywords.append(title)
        return keywords
    
    print(f"\n" + "=" * 60)
    print("Testing title matching strategies...")
    print("=" * 60)
    
    # Test different search queries
    queries = []
    
    # Romaji
    if anime.get('title_romaji'):
        queries.append(('Romaji', anime['title_romaji']))
        for kw in extract_keywords(anime['title_romaji']):
            queries.append(('Romaji keyword', kw))
    
    # English
    if anime.get('title_english'):
        for kw in extract_keywords(anime['title_english']):
            queries.append(('English keyword', kw))
    
    # Test each query on Sokuja
    print(f"\nTesting on SOKUJA:")
    for search_type, query in queries[:5]:  # Test first 5
        print(f"\n  Trying ({search_type}): {query}")
        results = sokuja_scraper.search_anime(query)
        if results:
            print(f"    ✓ Found {len(results)} results:")
            for r in results[:2]:
                print(f"      - {r['title']}")
        else:
            print(f"    ✗ No results")
    
    # Test on Otakudesu
    print(f"\nTesting on OTAKUDESU:")
    for search_type, query in queries[:5]:
        print(f"\n  Trying ({search_type}): {query}")
        results = otakudesu_scraper.search_anime(query)
        if results:
            print(f"    ✓ Found {len(results)} results:")
            for r in results[:2]:
                print(f"      - {r['title']}")
        else:
            print(f"    ✗ No results")
