#!/usr/bin/env python3
"""Debug script to test specific episode URLs and TUI filtering"""

import requests
from bs4 import BeautifulSoup
import scraper as samehadaku_scraper
import otakudesu_scraper
import sokuja_scraper
import anime_tui

# Mock TUI class to access filtering logic
class MockTUI:
    def __init__(self):
        pass
    
    # Copying relevant methods from anime_tui.py to ensure exact logic match
    def mark_streamable_servers(self, links):
        """Mark servers that have embed players as streamable"""
        # Servers that work with MPV (have resolvers or yt-dlp support)
        mpv_streamable_keywords = [
            'sokuja',      # SOKUJA direct MP4
            'vidhide',     # Vidhide works with yt-dlp
            'streamhd',    # StreamHD works with yt-dlp
            'filemoon',    # Filemoon works with yt-dlp
            'pixeldrain',  # Pixeldrain - we have resolver!
            'pdrain',      # Pixeldrain (short name) - we have resolver!
            'kraken',      # Krakenfiles - we have resolver!
            'gdrive',      # Google Drive - we have resolver!
            'drive',       # Google Drive
        ]
        
        # Servers that need browser (no resolver yet)
        browser_embed_keywords = [
            'mega',        # Mega - complex encryption, no resolver yet
            'acefile',     # File host
            'racaty',      # File host
            'mirrorupload',# File host
            'wibufile',    # File host
            'yourupload',  # File host
            'zippyshare',  # Often dead but sometimes proxied
        ]
        
        # Blacklist of known broken servers (very limited - only truly broken ones)
        blacklist_keywords = [
            'desudrive',   # Unsupported by yt-dlp
        ]
        
        processed = []
        
        for link in links:
            url = link.get('url', '').lower()
            server = link.get('server', '').lower()
            
            # Check if blacklisted
            is_blacklisted = any(keyword in url or keyword in server 
                                for keyword in blacklist_keywords)
            
            if is_blacklisted:
                print(f"  [BLOCKED] {server} ({url})")
                continue  # Skip blacklisted servers
            
            # Check if MPV streamable (has resolver or yt-dlp support)
            is_mpv_streamable = any(keyword in url or keyword in server 
                                   for keyword in mpv_streamable_keywords)
            
            # Check if browser embed (no resolver)
            is_browser_embed = any(keyword in url or keyword in server 
                                  for keyword in browser_embed_keywords)
            
            # Mark MPV streamable (will be resolved to direct URL)
            if is_mpv_streamable:
                link['stream_ready'] = True
                link['type'] = 'stream'
            # Mark browser embed
            elif is_browser_embed:
                link['type'] = 'browser_embed'
            else:
                link['type'] = 'download' # Default to download/unknown
                
            processed.append(link)
            
        return processed

    def organize_server_list(self, links):
        """Organize servers into categories"""
        if not links:
            return []
            
        # Filter and mark streamable servers
        processed = self.mark_streamable_servers(links)
        
        # Separate into 3 categories
        mpv_streaming = []
        browser_embeds = []
        downloads = []
        
        for link in processed:
            if link.get('type') == 'browser_embed':
                browser_embeds.append(link)
            elif link.get('stream_ready', False) or link.get('type') == 'stream':
                mpv_streaming.append(link)
            else:
                downloads.append(link)
        
        # Combine: MPV streaming first, browser embeds, then downloads
        organized = mpv_streaming + browser_embeds + downloads
        
        return organized

tui = MockTUI()

def test_url(provider, url, scraper_func):
    print(f"\nTesting {provider} URL: {url}")
    try:
        links = scraper_func(url)
        print(f"Raw links found: {len(links)}")
        for l in links:
            print(f"  - {l['server']} ({l['url']})")
            
        organized = tui.organize_server_list(links)
        print(f"Organized links (TUI view): {len(organized)}")
        for l in organized:
            print(f"  - [{l.get('type', '?')}] {l['server']}")
            
        if not organized:
            print("❌ FAILURE: No servers would be shown in TUI")
        else:
            print("✅ SUCCESS: Servers would be shown")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

# 1. Samehadaku S1 Ep 13
test_url("Samehadaku", 
         "https://v1.samehadaku.how/maou-gakuin-no-futekigousha-episode-13/", 
         samehadaku_scraper.get_all_video_links)

# 2. Otakudesu Ep 13
test_url("Otakudesu", 
         "https://otakudesu.best/episode/maogkn-ftkg-episode-13-sub-indo/", 
         otakudesu_scraper.get_video_links)

# 3. Sokuja (Try finding a valid URL first)
print("\nSearching Sokuja for URL...")
results = sokuja_scraper.search_anime("Maou Gakuin")
if results:
    episodes = sokuja_scraper.get_anime_episodes(results[0]['url'])
    if episodes:
        test_url("Sokuja", episodes[0]['url'], sokuja_scraper.get_video_links)
