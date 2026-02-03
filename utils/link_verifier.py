#!/usr/bin/env python3
"""
Link Verification Module
Verifies if links are accessible and filters out dead servers
"""

import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Callable, Optional
import hashlib
import json
from datetime import datetime, timedelta

# Cache for verification results (5 minute TTL)
_verification_cache = {}
_cache_ttl = timedelta(minutes=5)

def _get_cache_key(url: str) -> str:
    """Generate cache key from URL"""
    return hashlib.md5(url.encode()).hexdigest()

def _get_cached_result(url: str) -> Optional[Dict]:
    """Get cached verification result if still valid"""
    key = _get_cache_key(url)
    if key in _verification_cache:
        cached = _verification_cache[key]
        if datetime.now() - cached['timestamp'] < _cache_ttl:
            return cached['result']
        else:
            # Expired, remove from cache
            del _verification_cache[key]
    return None

def _cache_result(url: str, result: Dict):
    """Cache verification result"""
    key = _get_cache_key(url)
    _verification_cache[key] = {
        'result': result,
        'timestamp': datetime.now()
    }

def verify_link(url: str, timeout: int = 2) -> Dict:
    """
    Verify if a link is accessible
    
    Args:
        url: URL to verify
        timeout: Request timeout in seconds (default 2s for speed)
        
    Returns:
        {
            'status': 'working'|'dead'|'needs_scraping',
            'final_url': str,
            'status_code': int or None,
            'error': str or None
        }
    """
    # Check cache first
    cached = _get_cached_result(url)
    if cached:
        return cached
    
    result = {
        'status': 'dead',
        'final_url': url,
        'status_code': None,
        'error': None
    }
    
    # Known dead hosts - auto-fail without checking
    dead_hosts = [
        'zippyshare.com',   # Service shut down
        'racaty.net',       # Often dead/slow
        'racaty.io',
        'solidfiles.com',   # SSL issues
        'letsupload.org',   # Often dead
        'letsupload.io',
        'gdriveplayer.me',  # Broken wrapper, returns 404
        'dood.to',          # Not supported by yt-dlp (piracy blacklist)
        'dood.la',
        'dood.ws',
    ]
    
    url_lower = url.lower()
    for dead_host in dead_hosts:
        if dead_host in url_lower:
            result['status'] = 'dead'
            result['error'] = f'Known dead host: {dead_host}'
            _cache_result(url, result)
            return result
    
    # Known working hosts - skip verification for speed
    trusted_hosts = [
        'googlevideo.com',      # Google/Blogger video
        'googleapis.com',       # Google Drive API
        'blogger.com',          # Blogger
        'storages.sokuja.id',   # Sokuja direct
    ]
    
    for trusted_host in trusted_hosts:
        if trusted_host in url_lower:
            result['status'] = 'working'
            result['status_code'] = 200
            _cache_result(url, result)
            return result
    
    try:
        # Skip verification for special URL formats
        if url.startswith('otakudesu:') or url.startswith('ajax:'):
            result['status'] = 'needs_scraping'
            _cache_result(url, result)
            return result
        
        # Send HEAD request (faster than GET)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
        }
        
        response = requests.head(
            url,
            headers=headers,
            timeout=timeout,
            allow_redirects=True
        )
        
        result['status_code'] = response.status_code
        result['final_url'] = response.url
        
        # For file hosts, be stricter - check content-length
        file_hosts = ['mega.nz', 'drive.google', 'pixeldrain.com', 'krakenfiles.com']
        is_file_host = any(host in url_lower for host in file_hosts)
        
        if is_file_host:
            # Must have content-length header for file hosts
            content_length = response.headers.get('content-length', '0')
            if int(content_length) > 1000:  # At least 1KB
                result['status'] = 'working'
            else:
                result['status'] = 'dead'
                result['error'] = 'No file content'
        else:
            # Consider 2xx and 3xx as working
            if 200 <= response.status_code < 400:
                result['status'] = 'working'
            # 403/401 might still be accessible (just needs auth)
            elif response.status_code in [401, 403]:
                result['status'] = 'needs_scraping'
            else:
                result['status'] = 'dead'
                result['error'] = f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        result['status'] = 'dead'
        result['error'] = 'Timeout'
    except requests.exceptions.ConnectionError:
        result['status'] = 'dead'
        result['error'] = 'Connection failed'
    except requests.exceptions.TooManyRedirects:
        result['status'] = 'dead'
        result['error'] = 'Too many redirects'
    except Exception as e:
        result['status'] = 'dead'
        result['error'] = str(e)[:50]
    
    # Cache the result
    _cache_result(url, result)
    return result

def verify_links_batch(
    links: List[Dict],
    max_workers: int = 10,  # Increased from 5 for faster verification
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> List[Dict]:
    """
    Verify multiple links in parallel
    
    Args:
        links: List of link dicts with 'url' key
        max_workers: Number of parallel workers
        progress_callback: Optional callback(completed, total)
        
    Returns:
        List of links with added 'verification' key containing result
    """
    total = len(links)
    completed = 0
    
    # Create a copy to avoid modifying original
    verified_links = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all verification tasks
        future_to_link = {
            executor.submit(verify_link, link['url']): link
            for link in links
        }
        
        # Process results as they complete
        for future in as_completed(future_to_link):
            link = future_to_link[future]
            try:
                verification = future.result()
                link_copy = link.copy()
                link_copy['verification'] = verification
                verified_links.append(link_copy)
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, total)
                    
            except Exception as e:
                # If verification itself fails, mark as dead
                link_copy = link.copy()
                link_copy['verification'] = {
                    'status': 'dead',
                    'final_url': link['url'],
                    'status_code': None,
                    'error': f'Verification error: {str(e)[:30]}'
                }
                verified_links.append(link_copy)
                completed += 1
                if progress_callback:
                    progress_callback(completed, total)
    
    return verified_links

def filter_working_links(verified_links: List[Dict]) -> List[Dict]:
    """
    Filter to only working links
    
    Args:
        verified_links: Links with 'verification' key
        
    Returns:
        List of links where status is 'working' or 'needs_scraping'
    """
    return [
        link for link in verified_links
        if link.get('verification', {}).get('status') in ['working', 'needs_scraping']
    ]

def clear_cache():
    """Clear the verification cache"""
    global _verification_cache
    _verification_cache = {}

# Test
if __name__ == "__main__":
    print("Testing link verifier...\n")
    
    # Test individual verification
    test_urls = [
        "https://www.google.com",  # Should work
        "https://dead-server-12345.example.com",  # Should fail
        "https://httpstat.us/404",  # Should fail (404)
    ]
    
    for url in test_urls:
        print(f"Testing: {url}")
        result = verify_link(url, timeout=3)
        print(f"  Status: {result['status']}")
        print(f"  Code: {result['status_code']}")
        print(f"  Error: {result['error']}")
        print()
    
    # Test batch verification
    print("\nTesting batch verification...")
    links = [{'url': url, 'server': f'Server {i}'} for i, url in enumerate(test_urls)]
    
    def progress(completed, total):
        print(f"  Progress: {completed}/{total}")
    
    verified = verify_links_batch(links, progress_callback=progress)
    working = filter_working_links(verified)
    
    print(f"\nResults: {len(working)}/{len(links)} working")
    for link in working:
        print(f"  ✓ {link['url']}: {link['verification']['status']}")
