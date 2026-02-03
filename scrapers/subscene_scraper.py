#!/usr/bin/env python3
"""
Subscene Subtitle Scraper
Scrapes Indonesian subtitles from Subscene
"""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://subscene.com"

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

def search_subtitles(query):
    """
    Search for subtitles on Subscene
    
    Args:
        query: Anime title to search
    
    Returns:
        List of results with metadata
    """
    try:
        # Subscene search URL
        url = f"{BASE_URL}/subtitles/searchbytitle"
        
        print(f"[subscene] Searching: {query}")
        
        # Subscene requires POST for search
        data = {'query': query}
        resp = requests.post(url, data=data, headers=get_headers())
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        results = []
        
        # Find search results
        result_divs = soup.find_all('div', class_='title')
        
        for div in result_divs:
            link = div.find('a', href=True)
            if link:
                title = link.get_text(strip=True)
                url = BASE_URL + link['href']
                
                results.append({
                    'title': title,
                    'url': url,
                    'source': 'subscene'
                })
        
        print(f"[subscene] Found {len(results)} title matches")
        return results
        
    except Exception as e:
        print(f"[subscene] Search error: {e}")
        return []

def get_subtitle_downloads(page_url):
    """
    Get all Indonesian subtitle download links from a title page
    
    Args:
        page_url: Subscene title page URL
    
    Returns:
        List of subtitle options with metadata
    """
    try:
        print(f"[subscene] Fetching subtitles from: {page_url}")
        
        resp = requests.get(page_url, headers=get_headers())
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        subtitles = []
        
        # Find all subtitle rows
        table = soup.find('table')
        if not table:
            print("[subscene] No subtitle table found")
            return []
        
        rows = table.find('tbody').find_all('tr')
        
        for row in rows:
            try:
                # Check language
                lang_cell = row.find('td', class_='a1')
                if not lang_cell:
                    continue
                
                lang_spans = lang_cell.find_all('span')
                language = lang_spans[0].get_text(strip=True) if lang_spans else ''
                
                # Filter for Indonesian only
                if 'indonesian' not in language.lower():
                    continue
                
                # Get subtitle link and info
                link_cell = row.find('td', class_='a1')
                link = link_cell.find('a', href=True)
                if not link:
                    continue
                
                subtitle_url = BASE_URL + link['href']
                subtitle_name = link.find('span', class_=['', None])
                subtitle_name = subtitle_name.get_text(strip=True) if subtitle_name else 'Unknown'
                
                # Get hearing impaired info
                hi_icon = lang_cell.find('span', class_='l r neutral-icon')
                hearing_impaired = hi_icon is not None
                
                # Get uploader
                uploader_cell = row.find('td', class_='a5')
                uploader = uploader_cell.get_text(strip=True) if uploader_cell else 'Unknown'
                
                # Get comment (often has quality info)
                comment_cell = row.find('td', class_='a6')
                comment = comment_cell.get_text(strip=True) if comment_cell else ''
                
                subtitles.append({
                    'name': subtitle_name,
                    'url': subtitle_url,
                    'language': language,
                    'uploader': uploader,
                    'hearing_impaired': hearing_impaired,
                    'comment': comment,
                    'source': 'subscene'
                })
                
            except Exception as e:
                print(f"[subscene] Error parsing row: {e}")
                continue
        
        print(f"[subscene] Found {len(subtitles)} Indonesian subtitles")
        return subtitles
        
    except Exception as e:
        print(f"[subscene] Error getting subtitles: {e}")
        return []

def get_download_link(subtitle_url):
    """
    Get the actual download link from a subtitle page
    
    Args:
        subtitle_url: Subscene subtitle page URL
    
    Returns:
        Direct download URL or None
    """
    try:
        print(f"[subscene] Getting download link...")
        
        resp = requests.get(subtitle_url, headers=get_headers())
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find download button
        download_button = soup.find('a', id='downloadButton')
        if download_button and download_button.get('href'):
            download_url = BASE_URL + download_button['href']
            print(f"[subscene] ✓ Got download link")
            return download_url
        
        print(f"[subscene] ⚠️  Could not find download link")
        return None
        
    except Exception as e:
        print(f"[subscene] Error getting download link: {e}")
        return None

if __name__ == "__main__":
    # Test search
    results = search_subtitles("Maou Gakuin")
    
    if results:
        print(f"\nFound {len(results)} title matches")
        print("\nFirst result:")
        first = results[0]
        print(f"  Title: {first['title']}")
        print(f"  URL: {first['url']}")
        
        # Get subtitles for first result
        print("\nGetting subtitles...")
        subtitles = get_subtitle_downloads(first['url'])
        
        if subtitles:
            print(f"\nFound {len(subtitles)} Indonesian subtitles")
            print("\nTop 3:")
            for i, sub in enumerate(subtitles[:3], 1):
                print(f"\n{i}. {sub['name']}")
                print(f"   Uploader: {sub['uploader']}")
                print(f"   HI: {sub['hearing_impaired']}")
                if sub['comment']:
                    print(f"   Comment: {sub['comment']}")
