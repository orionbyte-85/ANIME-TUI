from otakudesu_scraper import search_anime, get_anime_episodes, get_video_links

print("--- Testing Search ---")
results = search_anime("one piece")
print(f"Found {len(results)} results")
if results:
    first = results[0]
    print(f"First result: {first['title']}")
    print(f"URL: {first['url']}")
    
    print("\n--- Testing Episodes ---")
    episodes = get_anime_episodes(first['url'])
    print(f"Found {len(episodes)} episodes")
    
    if episodes:
        # Pick a middle episode to avoid batch links if any slipped through
        ep = episodes[min(5, len(episodes)-1)]
        print(f"Testing Episode: {ep['title']}")
        print(f"URL: {ep['url']}")
        
        print("\n--- Testing Video Links ---")
        links = get_video_links(ep['url'])
        print(f"Found {len(links)} links")
        for link in links:
            print(f"[{link.get('type')}] {link['quality']} - {link['server']}: {link['url'][:50]}...")
            
        # Test resolution for first stream link
        stream_links = [l for l in links if l.get('type') == 'stream']
        if stream_links:
            print("\n--- Testing Resolution ---")
            target = stream_links[0]
            print(f"Resolving: {target['url'][:50]}...")
            from otakudesu_scraper import resolve_otakudesu_url
            real_url = resolve_otakudesu_url(target['url'])
            print(f"Resolved URL: {real_url}")
