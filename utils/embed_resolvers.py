#!/usr/bin/env python3
"""
Embed URL Resolvers - Extract direct video URLs from embed pages
Complex scraping to get direct MP4 URLs for MPV playback
"""

import requests
import re
import json
from bs4 import BeautifulSoup
import time

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

def unwrap_safelink(safelink_url):
    """
    Unwrap desustream.com/safelink URLs to get actual destination
    
    Args:
        safelink_url: URL like https://desustream.com/safelink/link/?id=...
        
    Returns:
        Actual destination URL or None if failed
    """
    try:
        print(f"  [safelink] Unwrapping...")
        
        # Fetch the safelink page
        resp = requests.get(safelink_url, headers=get_headers(), timeout=10, allow_redirects=True)
        
        # Method 1: Check if we were redirected
        if resp.url != safelink_url:
            print(f"  [safelink] Redirected to: {resp.url[:80]}...")
            return resp.url
        
        # Method 2: Parse HTML for redirect URL
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Look for meta refresh
        meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta_refresh and meta_refresh.get('content'):
            content = meta_refresh['content']
            # Format: "0;URL=http://example.com"
            match = re.search(r'url=([^"\']+)', content, re.I)
            if match:
                url = match.group(1)
                print(f"  [safelink] Found in meta refresh: {url[:80]}...")
                return url
        
        # Look for JavaScript redirect
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for window.location patterns
                patterns = [
                    r'window\.location\s*=\s*["\']([^"\']+)["\']',
                    r'location\.href\s*=\s*["\']([^"\']+)["\']',
                    r'window\.location\.replace\(["\']([^"\']+)["\']\)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, script.string)
                    if match:
                        url = match.group(1)
                        print(f"  [safelink] Found in JS: {url[:80]}...")
                        return url
        
        # Look for direct link in page
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            text = link.get_text(strip=True).lower()
            # Skip internal links
            if href.startswith('http') and 'desustream' not in href:
                print(f"  [safelink] Found link: {href[:80]}...")
                return href
        
        print(f"  [safelink] ⚠️  Could not unwrap")
        return None
        
    except Exception as e:
        print(f"  [safelink] Error: {e}")
        return None


def resolve_pixeldrain(embed_url):
    """
    Resolve Pixeldrain embed URL to direct stream
    Example: https://pixeldrain.com/u/XXXXX -> direct MP4
    """
    try:
        # Extract file ID from URL
        match = re.search(r'pixeldrain\.com/u/([a-zA-Z0-9_-]+)', embed_url)
        if not match:
            return None
        
        file_id = match.group(1)
        
        # Direct download URL format (this works with MPV)
        direct_url = f"https://pixeldrain.com/api/file/{file_id}"
        
        print(f"  [pixeldrain] Extracted file ID: {file_id}")
        print(f"  [pixeldrain] Direct URL: {direct_url}")
        
        return direct_url
    except Exception as e:
        print(f"  [pixeldrain] Error: {e}")
        return None

def resolve_mega(embed_url):
    """
    Resolve Mega embed URL to direct stream
    Note: Mega.nz is not supported by yt-dlp or simple HTTP requests
    Requires browser playback or mega.py library (not installed)
    Resolve Mega.nz embed URL to direct download link using mega.py library
    """
    try:
        from mega import Mega
    except (ImportError, AttributeError) as e:
        # AttributeError can happen due to tenacity incompatibility with Python 3.13
        print(f"  [mega] ⚠️  'mega.py' library issue: {e}")
        print(f"  [mega] Falling back to browser...")
        return None

    try:
        print(f"  [mega] Resolving: {embed_url[:60]}...")
        
        # Initialize Mega
        mega = Mega()
        m = mega.login() # Login as anonymous
        
        # Handle different URL formats
        # https://mega.nz/file/ID#KEY
        # https://mega.nz/embed/ID#KEY
        
        file_url = embed_url.replace('/embed/', '/file/')
        
        try:
            # Get file info
            file_info = m.get_public_url_info(file_url)
            file_name = file_info.get('name', 'mega_video.mp4')
            print(f"  [mega] Found file: {file_name}")
            
            # Get direct download link
            direct_url = m.get_public_url(file_url)
            
            if direct_url:
                print(f"  [mega] ✓ Got direct URL")
                return direct_url
                
        except Exception as e:
            print(f"  [mega] API Error: {e}")
            
    except Exception as e:
        print(f"  [mega] Error: {e}")
        
    return None

def resolve_krakenfiles(embed_url):
    """
    Resolve Krakenfiles embed URL to direct stream
    Complex scraping to find the actual video file
    """
    try:
        print(f"  [krakenfiles] Fetching embed page...")
        
        # First, get the embed page
        resp = requests.get(embed_url, headers=get_headers(), allow_redirects=True)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Method 1: Look for video tag with source
        video_tag = soup.find('video')
        if video_tag:
            source = video_tag.find('source')
            if source and source.get('src'):
                video_url = source['src']
                if not video_url.startswith('http'):
                    video_url = 'https:' + video_url if video_url.startswith('//') else 'https://krakenfiles.com' + video_url
                print(f"  [krakenfiles] Found video source: {video_url}")
                return video_url
        
        # Method 2: Look for download button/link
        download_links = soup.find_all('a', href=True)
        for link in download_links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()
            
            # Look for download-related links
            if 'download' in text or 'download' in href:
                if href.startswith('http') and ('.mp4' in href or 'krakenfiles' in href):
                    print(f"  [krakenfiles] Found download link: {href}")
                    return href
        
        # Method 3: Look in JavaScript for file URL
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for video URL patterns
                patterns = [
                    r'"(https://[^"]+\.mp4[^"]*)"',
                    r"'(https://[^']+\.mp4[^']*)'",
                    r'url:\s*["\']([^"\']+)["\']',
                    r'file:\s*["\']([^"\']+)["\']',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, script.string)
                    for match in matches:
                        if 'kraken' in match.lower() or '.mp4' in match.lower():
                            print(f"  [krakenfiles] Found in JS: {match}")
                            return match
        
        # Method 4: Try to find the actual file page
        # Krakenfiles embed might redirect to file page
        file_match = re.search(r'krakenfiles\.com/view/([^/]+)', embed_url)
        if file_match:
            file_id = file_match.group(1)
            # Try direct file URL
            direct_url = f"https://krakenfiles.com/getfile/{file_id}"
            print(f"  [krakenfiles] Trying direct URL: {direct_url}")
            return direct_url
        
        print(f"  [krakenfiles] ⚠️  Could not find direct video URL")
        return None
        
    except Exception as e:
        print(f"  [krakenfiles] Error: {e}")
        return None

def resolve_gdrive(embed_url):
    """
    Resolve Google Drive embed URL to direct stream
    """
    try:
        # Extract file ID
        match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', embed_url)
        if not match:
            match = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', embed_url)
        
        if not match:
            print(f"  [gdrive] Could not extract file ID")
            return None
        
        file_id = match.group(1)
        print(f"  [gdrive] File ID: {file_id}")
        
        # Try direct download URL
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        print(f"  [gdrive] Direct URL: {direct_url}")
        
        # Note: Large files may require confirmation token
        # For now, return the basic URL
        return direct_url
        
    except Exception as e:
        print(f"  [gdrive] Error: {e}")
        return None

def resolve_vidhide(embed_url):
    """
    Resolve Vidhide/odvidhide embed URL to direct stream
    Extracts m3u8 or mp4 URL from obfuscated JavaScript
    """
    try:
        print(f"  [vidhide] Fetching embed page...")
        
        headers = get_headers()
        headers['Referer'] = 'https://v1.samehadaku.how/'
        
        resp = requests.get(embed_url, headers=headers, timeout=10)
        html = resp.text
        
        # Method 1: Look for obfuscated object with video sources
        # Pattern: b o={"1k":"url1","1l":"url2","1t":"url3"};
        obj_pattern = r'b\s+o\s*=\s*\{([^}]+)\}'
        obj_match = re.search(obj_pattern, html)
        
        if obj_match:
            obj_content = obj_match.group(1)
            # Extract all URLs from the object
            url_pairs = re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', obj_content)
            
            # Look for URLs (they might be obfuscated but still contain :// or start with /)
            for key, value in url_pairs:
                # Check if it looks like a URL
                if '://' in value or value.startswith('/'):
                    # Prefer URLs with .m3u8 or .mp4 extensions (even if obfuscated like .82 or .fg)
                    if '.82' in value or '.m3u8' in value or 'm3u8' in value:
                        print(f"  [vidhide] Found m3u8 URL (key={key}): {value[:80]}...")
                        return value
                    elif '.fg' in value or '.mp4' in value or 'mp4' in value:
                        print(f"  [vidhide] Found mp4 URL (key={key}): {value[:80]}...")
                        return value
            
            # If no specific format found, return first URL-like value
            for key, value in url_pairs:
                if '://' in value:
                    print(f"  [vidhide] Found URL (key={key}): {value[:80]}...")
                    return value
        
        # Method 2: Look for sources array in jwplayer setup
        sources_pattern = r'sources\s*:\s*\[([^\]]+)\]'
        sources_match = re.search(sources_pattern, html)
        if sources_match:
            sources_str = sources_match.group(1)
            # Extract file URL
            file_match = re.search(r'file\s*:\s*["\']([^"\']+)["\']', sources_str)
            if file_match:
                video_url = file_match.group(1)
                print(f"  [vidhide] Found in sources: {video_url[:80]}...")
                return video_url
        
        # Method 3: Direct pattern matching for video URLs
        video_patterns = [
            r'(https?://[^"\']+\.m3u8[^"\']*)',
            r'(https?://[^"\']+\.mp4[^"\']*)',
            r'file["\':\s]+["\']([^"\']+)["\']',
        ]
        
        for pattern in video_patterns:
            matches = re.findall(pattern, html)
            if matches:
                video_url = matches[0]
                print(f"  [vidhide] Found with pattern: {video_url[:80]}...")
                return video_url
        
        print(f"  [vidhide] ⚠️  Could not find video URL")
        return None
        
    except Exception as e:
        print(f"  [vidhide] Error: {e}")
        return None

def resolve_embed_url(url, server_name=""):
    """
    Main resolver - detect server type and resolve to direct URL
    Returns direct MP4 URL that can be played with MPV
    """
    url_lower = url.lower()
    server_lower = server_name.lower()
    
    print(f"\n🔍 Resolving: {server_name}")
    print(f"   URL: {url[:80]}...")
    
    # DesuDrive (Otakudesu wrapper) - Check FIRST because server name might be "YourUpload"
    if 'desudrive' in url_lower:
        return resolve_desudrive(url)

    # Vidhide
    if 'vidhide' in url_lower or 'vidhide' in server_lower:
        return resolve_vidhide(url)
    
    # Pixeldrain
    elif 'pixeldrain' in url_lower or 'pdrain' in server_lower:
        return resolve_pixeldrain(url)
    
    # Mega
    elif 'mega.nz' in url_lower or 'mega' in server_lower:
        return resolve_mega(url)
    
    # Krakenfiles
    elif 'krakenfiles' in url_lower or 'kraken' in server_lower:
        return resolve_krakenfiles(url)
    
    # Streamwish
    elif 'streamwish' in url_lower or 'streamwish' in server_lower:
        return resolve_streamwish(url) # Assuming resolve_streamwish function exists
    
    # Google Drive
    elif 'drive.google' in url_lower or 'gdrive' in server_lower:
        return resolve_gdrive(url)
        
    # YourUpload
    elif 'yourupload' in url_lower or 'yourupload' in server_lower:
        return resolve_yourupload(url)
    
    # Dood.to (not supported by yt-dlp, return None to trigger browser)
    elif 'dood.' in url_lower or 'dood' in server_lower:
        print(f"  [dood] Not supported by MPV (yt-dlp blocked)")
        print(f"  [dood] Will open in browser...")
        return None

    # Unknown - return None (will fallback to browser)
    print(f"  [unknown] No resolver for this server type")
    return None

def resolve_yourupload(embed_url):
    """
    Resolve YourUpload embed URL to direct stream using yt-dlp
    """
    try:
        print(f"  [yourupload] Resolving with yt-dlp...")
        import subprocess
        
        # Use yt-dlp to get direct URL
        cmd = ['yt-dlp', '-g', '-f', 'best', embed_url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            direct_url = result.stdout.strip()
            print(f"  [yourupload] Direct URL: {direct_url[:80]}...")
            return direct_url
        else:
            print(f"  [yourupload] yt-dlp failed: {result.stderr}")
            print(f"  [yourupload] Trying manual scraping...")
            
            # Manual scraping fallback
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://www.yourupload.com/'
            }
            resp = requests.get(embed_url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Try og:video
            og_video = soup.find('meta', property='og:video')
            if og_video and og_video.get('content'):
                direct_url = og_video['content']
                print(f"  [yourupload] Found og:video: {direct_url[:80]}...")
                
                # Return dict with headers required for playback
                return {
                    'url': direct_url,
                    'headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Referer': 'https://www.yourupload.com/'
                    }
                }
                
            print(f"  [yourupload] Manual scraping failed")
            return None
            
    except Exception as e:
        print(f"  [yourupload] Error: {e}")
        return None

def resolve_desudrive(embed_url):
    """
    Resolve DesuDrive embed URL to direct stream
    Extracts iframe src which usually points to the real host (YourUpload, etc)
    """
    try:
        print(f"  [desudrive] Fetching embed page...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://otakudesu.best/'
        }
        resp = requests.get(embed_url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Look for iframe
        iframe = soup.find('iframe')
        if iframe and iframe.get('src'):
            real_url = iframe['src']
            print(f"  [desudrive] Found iframe: {real_url}")
            
            # Recursively resolve the new URL
            return resolve_embed_url(real_url, "Recursive")
            
        print(f"  [desudrive] ⚠️  Could not find iframe")
        return None
        
    except Exception as e:
        print(f"  [desudrive] Error: {e}")
        return None

# Test
if __name__ == "__main__":
    print("Testing embed resolvers...")
    
    # Test Pixeldrain
    print("\n" + "="*60)
    test_url = "https://pixeldrain.com/u/abc123"
    result = resolve_embed_url(test_url, "Pixeldrain")
    print(f"Result: {result}\n")
    
    # Test Krakenfiles
    print("="*60)
    test_url = "https://krakenfiles.com/view/abc123/file.html"
    result = resolve_embed_url(test_url, "Krakenfiles")
    print(f"Result: {result}\n")
    
    # Test GDrive
    print("="*60)
    test_url = "https://drive.google.com/file/d/1ABC123/preview"
    result = resolve_embed_url(test_url, "Google Drive")
    print(f"Result: {result}\n")
