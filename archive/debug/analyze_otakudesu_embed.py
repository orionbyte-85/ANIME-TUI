#!/usr/bin/env python3
"""
Analyze Otakudesu episode page to find embed player structure
"""

import requests
from bs4 import BeautifulSoup
import re

# Use the One Piece episode URL from the user's browser
url = "https://otakudesu.best/episode/wpoiec-episode-1150-sub-indo/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print(f"Fetching: {url}\n")
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

# Look for video player sections
print("=" * 60)
print("Looking for video player sections...")
print("=" * 60)

# Check for mirrorstream div (streaming options)
mirror_div = soup.find('div', class_='mirrorstream')
if mirror_div:
    print("\n✓ Found mirrorstream div")
    print(f"  Content preview: {str(mirror_div)[:200]}...")
    
    # Look for UL elements (quality groups)
    uls = mirror_div.find_all('ul')
    print(f"\n  Found {len(uls)} quality groups:")
    
    for ul in uls:
        quality_class = ul.get('class', [''])[0]
        print(f"\n  Quality: {quality_class}")
        
        # Look for LI elements (server options)
        lis = ul.find_all('li')
        print(f"    Servers: {len(lis)}")
        
        for li in lis[:3]:  # Show first 3
            a = li.find('a')
            if a:
                server_name = a.get_text(strip=True)
                data_content = a.get('data-content')
                print(f"      - {server_name}")
                if data_content:
                    print(f"        data-content: {data_content[:50]}...")
else:
    print("\n❌ No mirrorstream div found")

# Check for venutama div (main player)
venutama = soup.find('div', class_='venutama')
if venutama:
    print("\n✓ Found venutama div (main player area)")
    
    # Look for iframes
    iframes = venutama.find_all('iframe')
    print(f"  Iframes found: {len(iframes)}")
    for iframe in iframes:
        src = iframe.get('src', '')
        print(f"    - {src[:80]}...")
else:
    print("\n❌ No venutama div found")

# Look for any iframes on the page
all_iframes = soup.find_all('iframe')
print(f"\n\nTotal iframes on page: {len(all_iframes)}")
for i, iframe in enumerate(all_iframes[:5], 1):
    src = iframe.get('src', 'No src')
    print(f"  {i}. {src[:80]}...")

# Look for AJAX scripts
print("\n" + "=" * 60)
print("Looking for AJAX action hashes...")
print("=" * 60)

scripts = soup.find_all('script')
for script in scripts:
    if script.string and 'admin-ajax.php' in script.string:
        # Look for action hashes
        matches = re.findall(r'action\s*:\s*["\']([a-f0-9]{32})["\']', script.string)
        if matches:
            print(f"\n✓ Found action hashes: {matches}")
            break
