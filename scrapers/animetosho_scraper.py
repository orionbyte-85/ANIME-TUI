#!/usr/bin/env python3
"""
AnimeTosho Scraper
Anime torrent tracker with JSON API
"""

import requests
import re

BASE_URL = "https://feed.animetosho.org"

def search_anime(query, limit=10):
    """
    Search AnimeTosho for anime torrents
    
    Args:
        query: Anime title + episode number
        limit: Max results
    
    Returns:
        List of torrent dicts with info_hash, seeders, size, etc
    """
    try:
        # API endpoint
        url = f"{BASE_URL}/json"
        params = {
            'q': query,
            'qx': '1'  # Only exact matches
        }
        
        print(f"[animetosho] Searching: {query}")
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"[animetosho] HTTP error: {response.status_code}")
            return []
        
        data = response.json()
        results = []
        
        for item in data[:limit]:
            # Extract info
            title = item.get('title', '')
            torrent_url = item.get('torrent_url', '')
            magnet = item.get('magnet_uri', '')
            size = item.get('total_size', 0)
            seeders = item.get('seeders', 0)
            
            # Extract info_hash from magnet
            info_hash = extract_info_hash(magnet)
            if not info_hash:
                continue
            
            # Extract resolution
            resolution = extract_resolution(title)
            
            # Extract release group
            release_group = extract_release_group(title)
            
            # Format size
            size_formatted = format_size(size)
            
            results.append({
                'title': title,
                'magnet': magnet,
                'info_hash': info_hash,
                'torrent_url': torrent_url,
                'size': size_formatted,
                'seeders': seeders,
                'leechers': 0,  # AnimeTosho doesn't provide this
                'resolution': resolution,
                'release_group': release_group,
                'source': 'animetosho'
            })
        
        print(f"[animetosho] Found {len(results)} torrents")
        return results
        
    except Exception as e:
        print(f"[animetosho] Error: {e}")
        return []

def extract_info_hash(magnet_url):
    """Extract info hash from magnet URI"""
    if not magnet_url:
        return None
    match = re.search(r'btih:([a-fA-F0-9]{40})', magnet_url)
    if match:
        return match.group(1).lower()
    return None

def extract_resolution(title):
    """Extract resolution from title"""
    match = re.search(r'(\d{3,4}p)', title, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    if 'FHD' in title.upper() or '1920x1080' in title:
        return '1080P'
    elif 'HD' in title.upper() or '1280x720' in title:
        return '720P'
    
    return 'Unknown'

def extract_release_group(title):
    """Extract release group from title"""
    match = re.search(r'\[([^\]]+)\]', title)
    if match:
        return match.group(1)
    return 'Unknown'

def format_size(bytes_size):
    """Format bytes to human readable"""
    if bytes_size < 1024:
        return f"{bytes_size}B"
    elif bytes_size < 1024**2:
        return f"{bytes_size/1024:.1f}KB"
    elif bytes_size < 1024**3:
        return f"{bytes_size/(1024**2):.1f}MB"
    else:
        return f"{bytes_size/(1024**3):.2f}GB"

if __name__ == "__main__":
    # Test
    results = search_anime("Maou Gakuin 01")
    for i, t in enumerate(results[:3], 1):
        print(f"\n{i}. {t['title']}")
        print(f"   Resolution: {t['resolution']}")
        print(f"   Size: {t['size']}")
        print(f"   Seeders: {t['seeders']}")
        print(f"   Group: {t['release_group']}")
