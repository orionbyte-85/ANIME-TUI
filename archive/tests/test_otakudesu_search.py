#!/usr/bin/env python3
from otakudesu_scraper import search_anime, get_anime_episodes, get_video_links

query = "Maou Gakuin"
print(f"Searching for: {query}")

results = search_anime(query)
print(f"Found {len(results)} results")

if results:
    for i, anime in enumerate(results):
        print(f"[{i}] {anime['title']}")
        print(f"    URL: {anime['url']}")
    
    # Try to find Season 1 (usually the one without "Season 2" in title)
    target_anime = results[0]
    for anime in results:
        if "Season 2" not in anime['title']:
            target_anime = anime
            break
            
    print(f"\nChecking episodes for: {target_anime['title']}")
    print(f"URL: {target_anime['url']}")
    
    episodes = get_anime_episodes(target_anime['url'])
    print(f"Found {len(episodes)} episodes")
    
    if episodes:
        # Check Episode 5 if available, or just the first few
        for ep in episodes[:5]:
            print(f"- {ep['title']}")
            print(f"  URL: {ep['url']}")
            
        # Test scraping the first episode found
        test_ep = episodes[0]
        print(f"\nTesting scraping for: {test_ep['title']}")
        links = get_video_links(test_ep['url'])
        print(f"Found {len(links)} links")
        for link in links:
            print(f"- {link['server']}")
