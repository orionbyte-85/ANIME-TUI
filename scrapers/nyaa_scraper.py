#!/usr/bin/env python3
"""
Nyaa.si Torrent Scraper
Scrapes anime torrents from Nyaa.si with metadata
"""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://nyaa.si"

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

def search_anime(query):
    """
    Search for anime on Nyaa.si
    
    Args:
        query: Anime title to search
    
    Returns:
        List of search results with metadata
    """
    try:
        # Nyaa.si search URL with anime category filter
        # Category: 1_2 = Anime - English-translated
        url = f"{BASE_URL}/?f=0&c=1_2&q={query}"
        
        print(f"[nyaa] Searching: {query}")
        print(f"[nyaa] URL: {url}")
        
        resp = requests.get(url, headers=get_headers())
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        results = []
        
        # Find all torrent rows in table
        torrent_list = soup.find('table', class_='torrent-list')
        if not torrent_list:
            print("[nyaa] No results found")
            return []
        
        rows = torrent_list.find('tbody').find_all('tr')
        
        for row in rows:
            try:
                # Extract data from columns
                cols = row.find_all('td')
                
                if len(cols) < 6:
                    continue
                
                # Column 0: Category
                # Column 1: Title + Links
                # Column 2: Torrent links (magnet, torrent file)
                # Column 3: Size
                # Column 4: Date
                # Column 5: Seeders
                # Column 6: Leechers
                # Column 7: Downloads
                
                # Title and page URL
                title_col = cols[1]
                title_link = title_col.find('a', href=True)
                if not title_link:
                    continue
                
                title = title_link.get_text(strip=True)
                page_url = BASE_URL + title_link['href']
                
                # Magnet link
                links_col = cols[2]
                magnet_link = links_col.find('a', href=lambda x: x and x.startswith('magnet:'))
                magnet = magnet_link['href'] if magnet_link else None
                
                # Torrent file link
                torrent_link = links_col.find('a', href=lambda x: x and x.endswith('.torrent'))
                torrent_url = BASE_URL + torrent_link['href'] if torrent_link else None
                
                # Size
                size = cols[3].get_text(strip=True)
                
                # Seeders and Leechers
                seeders = int(cols[5].get_text(strip=True))
                leechers = int(cols[6].get_text(strip=True))
                downloads = int(cols[7].get_text(strip=True))
                
                # Extract resolution from title
                resolution = extract_resolution(title)
                
                # Extract group/release from title
                release_group = extract_release_group(title)
                
                results.append({
                    'title': title,
                    'magnet': magnet,
                    'torrent_url': torrent_url,
                    'page_url': page_url,
                    'size': size,
                    'seeders': seeders,
                    'leechers': leechers,
                    'downloads': downloads,
                    'resolution': resolution,
                    'release_group': release_group,
                    'source': 'nyaa'
                })
                
            except Exception as e:
                print(f"[nyaa] Error parsing row: {e}")
                continue
        
        print(f"[nyaa] Found {len(results)} torrents")
        return results
        
    except Exception as e:
        print(f"[nyaa] Search error: {e}")
        return []

def extract_resolution(title):
    """Extract resolution from title (e.g., 1080p, 720p)"""
    # Common patterns: 1080p, 720p, 480p, 360p, 2160p (4K)
    match = re.search(r'(\d{3,4}p)', title, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    # Alternative patterns: FHD, HD, SD
    if 'FHD' in title.upper() or '1920x1080' in title:
        return '1080P'
    elif 'HD' in title.upper() or '1280x720' in title:
        return '720P'
    
    return 'Unknown'

def extract_release_group(title):
    """Extract release group from title (e.g., [SubsPlease], [HorribleSubs])"""
    # Pattern: [GroupName]
    match = re.search(r'\[([^\]]+)\]', title)
    if match:
        return match.group(1)
    
    return 'Unknown'

def filter_torrents(torrents, min_seeders=0, resolution=None):
    """
    Filter torrent results
    
    Args:
        torrents: List of torrent dicts
        min_seeders: Minimum number of seeders
        resolution: Filter by resolution (e.g., '1080P', '720P')
    
    Returns:
        Filtered list
    """
    filtered = torrents
    
    # Filter by seeders
    if min_seeders > 0:
        filtered = [t for t in filtered if t['seeders'] >= min_seeders]
    
    # Filter by resolution
    if resolution:
        filtered = [t for t in filtered if t['resolution'] == resolution.upper()]
    
    return filtered

def sort_torrents(torrents, by='seeders'):
    """
    Sort torrents
    
    Args:
        torrents: List of torrent dicts
        by: Sort key ('seeders', 'size', 'resolution')
    
    Returns:
        Sorted list
    """
    if by == 'seeders':
        return sorted(torrents, key=lambda x: x['seeders'], reverse=True)
    elif by == 'size':
        # Sort by size (requires parsing size string)
        return torrents
    elif by == 'resolution':
        # Sort by resolution (1080p > 720p > 480p)
        resolution_priority = {'2160P': 0, '1080P': 1, '720P': 2, '480P': 3, '360P': 4, 'Unknown': 999}
        return sorted(torrents, key=lambda x: resolution_priority.get(x['resolution'], 999))
    
    return torrents

if __name__ == "__main__":
    # Test search
    results = search_anime("Maou Gakuin")
    
    if results:
        print(f"\nFound {len(results)} torrents")
        print("\nTop 5 by seeders:")
        
        sorted_results = sort_torrents(results, by='seeders')
        
        for i, torrent in enumerate(sorted_results[:5], 1):
            print(f"\n{i}. {torrent['title']}")
            print(f"   Resolution: {torrent['resolution']}")
            print(f"   Size: {torrent['size']}")
            print(f"   Seeders: {torrent['seeders']}")
            print(f"   Group: {torrent['release_group']}")
