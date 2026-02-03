#!/usr/bin/env python3
"""
Scrape Blogger video page to get direct Google Video URL
"""

import requests
import re
from bs4 import BeautifulSoup

def scrape_blogger_direct_url(blogger_url):
    """
    Scrape Blogger video page to extract direct Google Video stream URL
    
    Args:
        blogger_url: URL like https://www.blogger.com/video.g?token=...
        
    Returns:
        Direct Google Video URL or None
    """
    try:
        print(f"[blogger] Scraping: {blogger_url[:80]}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://v1.samehadaku.how/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        resp = requests.get(blogger_url, headers=headers, timeout=10)
        
        if resp.status_code != 200:
            print(f"[blogger] HTTP {resp.status_code}")
            return None
        
        # Method 1: Look for direct video URL in HTML
        # Blogger usually has: <video src="https://...googlevideo.com/...">
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Try <video> tag
        video_tag = soup.find('video')
        if video_tag and video_tag.get('src'):
            url = video_tag['src']
            print(f"[blogger] Found in <video> tag: {url[:80]}...")
            return url
        
        # Try <source> tag inside <video>
        source_tag = soup.find('source', src=True)
        if source_tag:
            url = source_tag['src']
            print(f"[blogger] Found in <source> tag: {url[:80]}...")
            return url
        
        # Method 2: Look in JavaScript/JSON
        # Blogger embeds video info in scripts
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for googlevideo.com URLs
                matches = re.findall(r'(https://[^"\']+googlevideo\.com/[^"\']+)', script.string)
                if matches:
                    # Get the longest URL (usually the full one)
                    url = max(matches, key=len)
                    # Unescape if needed
                    url = url.replace('\\u003d', '=').replace('\\u0026', '&')
                    print(f"[blogger] Found in script: {url[:80]}...")
                    return url
        
        # Method 3: Look in page source directly
        matches = re.findall(r'(https://[^"\']+googlevideo\.com/videoplayback[^"\']+)', resp.text)
        if matches:
            url = max(matches, key=len)
            url = url.replace('\\u003d', '=').replace('\\u0026', '&')
            print(f"[blogger] Found in page source: {url[:80]}...")
            return url
        
        print(f"[blogger] ⚠️  Could not find direct URL")
        return None
        
    except Exception as e:
        print(f"[blogger] Error: {e}")
        return None

# Test
if __name__ == "__main__":
    # Test URL from user's log
    test_url = "https://www.blogger.com/video.g?token=AD6v5dy03FKctdBVG5CMf4_8j8Lz1K4LRAmjckIBnSWyTcFTt9UiyT0y6Fn1NbWw-ug_JQ5DS9SEdg1FDuNRUuu0KDUEscBlpAa9OGibQB7HkQ6PiLRQCNhsn-nilYHRHODFpGzQUKs"
    
    print("Testing Blogger scraper...")
    print(f"URL: {test_url}\n")
    
    direct_url = scrape_blogger_direct_url(test_url)
    
    if direct_url:
        print(f"\n✓ SUCCESS!")
        print(f"Direct URL: {direct_url[:120]}...")
    else:
        print(f"\n❌ FAILED")
