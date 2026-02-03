#!/usr/bin/env python3
"""Debug script to test episode and server fetching"""

from scraper import search_anime as search_samehadaku, get_anime_episodes as get_episodes_samehadaku, get_all_video_links as get_links_samehadaku
import otakudesu_scraper
import sokuja_scraper

# Test search
print("Testing Otakudesu search...")
results = otakudesu_scraper.search_anime("maou gakuin")
if results:
    print(f"✓ Found {len(results)} results")
    anime = results[0]
    print(f"  Title: {anime['title']}")
    print(f"  URL: {anime['url']}")
    
    # Test get episodes
    print("\nTesting get episodes...")
    try:
        episodes = otakudesu_scraper.get_anime_episodes(anime['url'])
        print(f"✓ Found {len(episodes)} episodes")
        if episodes:
            ep = episodes[0]
            print(f"  Episode 1: {ep['title']}")
            print(f"  URL: {ep['url']}")
            
            # Test get video links
            print("\nTesting get video links...")
            try:
                links = otakudesu_scraper.get_video_links(ep['url'])
                print(f"✓ Found {len(links)} links")
                for link in links[:3]:
                    print(f"  - {link['server']} ({link['quality']})")
            except Exception as e:
                print(f"✗ Error getting links: {e}")
                import traceback
                traceback.print_exc()
    except Exception as e:
        print(f"✗ Error getting episodes: {e}")
        import traceback
        traceback.print_exc()
else:
    print("✗ No results found")
