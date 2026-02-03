#!/usr/bin/env python3
"""
Sokuja Scraper - https://x3.sokuja.uk/
"""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://x3.sokuja.uk"

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

def search_anime(query):
    """Search for anime on Sokuja"""
    url = f"{BASE_URL}/?s={query}"
    try:
        resp = requests.get(url, headers=get_headers())
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        results = []
        # Find search results
        articles = soup.find_all('article', class_='bs')
        
        for art in articles:
            link = art.find('a', href=True)
            if link:
                title = link.get('title', link.get_text(strip=True))
                url = link['href']
                
                # Get thumbnail
                img = art.find('img', src=True)
                thumbnail = img['src'] if img else None
                
                results.append({
                    'title': title,
                    'url': url,
                    'thumbnail': thumbnail,
                    'source': 'sokuja'
                })
        
        return results
    except Exception as e:
        print(f"[sokuja] Search error: {e}")
        return []

def get_anime_episodes(anime_url):
    """Get episodes for an anime"""
    try:
        resp = requests.get(anime_url, headers=get_headers())
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        episodes = []
        # Find episode list in eplister div
        eplister = soup.find('div', class_='eplister')
        
        if eplister:
            lis = eplister.find_all('li')
            for li in lis:
                link = li.find('a', href=True)
                if link:
                    # Try to get clean title from div.epl-title
                    title_div = link.find('div', class_='epl-title')
                    if title_div:
                        title = title_div.get_text(strip=True)
                    else:
                        title = link.get_text(strip=True)
                        
                    url = link['href']
                    
                    # Extract episode number
                    ep_num = '?'
                    match = re.search(r'Episode\s+(\d+)', title, re.IGNORECASE)
                    if match:
                        ep_num = match.group(1)
                    
                    episodes.append({
                        'title': title,
                        'url': url,
                        'episode_number': ep_num,
                        'source': 'sokuja'
                    })
        
        # Reverse to get ascending order (or keep descending?)
        # Site lists newest first. Let's keep it that way for consistency with others.
        # episodes.reverse() 
        
        return episodes
    except Exception as e:
        print(f"[sokuja] Episode list error: {e}")
        return []

def get_video_links(episode_url):
    """Get video links from episode page"""
    try:
        resp = requests.get(episode_url, headers=get_headers())
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        links = []
        
        # Look for select dropdown with video options
        select = soup.find('select', {'name': 'mirror'})
        if select:
            options = select.find_all('option')
            priority = 0
            
            for opt in options:
                value = opt.get('value')
                text = opt.get_text(strip=True)
                
                # Skip placeholder option
                if not value or 'Pilih' in text:
                    continue
                
                # Decode base64 value to get video HTML
                try:
                    import base64
                    decoded = base64.b64decode(value).decode('utf-8')
                    
                    # Extract src URL from decoded HTML
                    # Format: <video controls preload="none"><source src="URL" type="video/mp4"></video>
                    match = re.search(r'src="([^"]+)"', decoded)
                    if match:
                        video_url = match.group(1)
                        
                        # Extract quality from text (e.g., "SOKUJA 480p")
                        quality = 'Unknown'
                        quality_match = re.search(r'(360p|480p|720p|1080p)', text)
                        if quality_match:
                            quality = quality_match.group(1)
                        
                        links.append({
                            'server': f'🎬 SOKUJA',
                            'url': video_url,
                            'resolution': quality,
                            'type': 'stream',
                            'stream_ready': True,
                            'priority': priority
                        })
                        priority += 1
                except Exception as e:
                    print(f"[sokuja] Error decoding option: {e}")
        
        # Sort by priority (720p first, then 480p, etc.)
        links.sort(key=lambda x: x.get('priority', 999))
        
        return links
    except Exception as e:
        print(f"[sokuja] Video links error: {e}")
        return []

if __name__ == "__main__":
    # Test
    print("Testing Sokuja scraper...")
    print("=" * 60)
    
    # Test search
    print("\\nSearching for 'Naruto'...")
    results = search_anime("Naruto")
    print(f"Found {len(results)} results:")
    for i, anime in enumerate(results[:3], 1):
        print(f"{i}. {anime['title']}")
        print(f"   {anime['url']}")
    
    # Test episodes
    if results:
        print(f"\\n{'=' * 60}")
        print(f"Getting episodes for: {results[0]['title']}")
        episodes = get_anime_episodes(results[0]['url'])
        print(f"Found {len(episodes)} episodes")
        if episodes:
            print(f"First 5:")
            for ep in episodes[:5]:
                print(f"  [{ep['episode_number']}] {ep['title']}")
            
            # Test video links
            print(f"\\n{'=' * 60}")
            print(f"Getting video links for: {episodes[0]['title']}")
            links = get_video_links(episodes[0]['url'])
            print(f"Found {len(links)} links:")
            for link in links[:5]:
                print(f"  [{link['quality']}] {link['server']}")
