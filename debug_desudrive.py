import sys
import os
sys.path.append(os.getcwd())
from scrapers import otakudesu_scraper
import requests
from bs4 import BeautifulSoup

def debug_desudrive():
    print("Searching for anime...")
    results = otakudesu_scraper.search_anime("Maou Gakuin no Futekigousha")
    if not results:
        print("Anime not found")
        return

    anime_url = None
    for res in results:
        print(f"Found: {res['title']}")
        # Try to find the one that is NOT Season 2
        if "Season 2" not in res['title'] and "Gakuin" in res['title']:
            anime_url = res['url']
            print(f"Selected: {res['title']}")
            break
            
    if not anime_url:
        print("Could not find Season 1, using first result")
        anime_url = results[0]['url']

    print("Fetching episodes...")
    episodes = otakudesu_scraper.get_anime_episodes(anime_url)
    target_ep = None
    for ep in episodes:
        if "Episode 13" in ep['title']:
            target_ep = ep
            break
    
    if not target_ep:
        print("Episode 13 not found")
        return

    print(f"Fetching links for: {target_ep['title']}")
    links = otakudesu_scraper.get_video_links(target_ep['url'])
    
    desudrive_url = None
    for link in links:
        if "yourupload" in link['server'].lower():
            print(f"Found YourUpload link: {link['url']}")
            desudrive_url = link['url']
            break
            
    if not desudrive_url:
        print("No YourUpload link found")
        return

    # Now resolve the desudrive URL if it's a special otakudesu: URL
    if desudrive_url.startswith('otakudesu:'):
        print("Resolving otakudesu: URL...")
        resolved = otakudesu_scraper.resolve_otakudesu_url(desudrive_url)
        if isinstance(resolved, dict):
            desudrive_url = resolved['url']
        else:
            desudrive_url = resolved
        print(f"Resolved to: {desudrive_url}")

    # Now resolve the desudrive URL using our new resolver
    print(f"\nTesting resolver on: {desudrive_url}")
    try:
        from utils.embed_resolvers import resolve_embed_url
        direct_url = resolve_embed_url(desudrive_url, "DesuDrive")
        print(f"Result: {direct_url}")
        
        if direct_url and direct_url != desudrive_url:
            print("✅ SUCCESS: Resolved to direct URL")
        else:
            print("❌ FAILED: Could not resolve")
            
    except Exception as e:
        print(f"Error resolving: {e}")

if __name__ == "__main__":
    debug_desudrive()
