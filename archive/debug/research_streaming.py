#!/usr/bin/env python3
"""Research streaming sources extraction"""

import requests
from bs4 import BeautifulSoup
import re
import json

url = "https://v1.samehadaku.how/maou-gakuin-no-futekigousha-season-2-episode-1/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

print(f"Fetching: {url}")
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

# 1. Look for the 'server' variable in scripts which usually contains streaming data
print("\n=== Searching for 'server' variable in scripts ===")
scripts = soup.find_all('script')
for script in scripts:
    if script.string and 'server' in script.string:
        # Try to find JSON-like structures or array definitions
        # Look for something like: var server = [...] or window.server = [...]
        matches = re.findall(r'(?:var|let|const|window\.)\s*server\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
        if matches:
            print("Found server data!")
            try:
                # Clean up the JS array to make it valid JSON if possible
                # This is a rough attempt
                data = matches[0]
                print(f"Data snippet: {data[:200]}...")
            except:
                pass

# 2. Look for the .player-area or similar divs
print("\n=== Searching for player area ===")
player_area = soup.find('div', id='server')
if player_area:
    print("Found div#server")
    print(player_area.prettify()[:500])

# 3. Look for post_id and nonce which might be needed for AJAX requests
print("\n=== Searching for AJAX parameters ===")
post_id = None
nonce = None

# Try to find post ID
article = soup.find('article', id=re.compile(r'post-\d+'))
if article:
    post_id = article['id'].replace('post-', '')
    print(f"Found Post ID: {post_id}")

# Try to find nonce
for script in scripts:
    if script.string and 'nonce' in script.string:
        nonce_match = re.search(r'"nonce":"([^"]+)"', script.string)
        if nonce_match:
            nonce = nonce_match.group(1)
            print(f"Found Nonce: {nonce}")
            break

if post_id and nonce:
    print("\n=== Attempting to simulate AJAX request for streaming links ===")
    # Samehadaku usually uses admin-ajax.php with action='player_ajax'
    ajax_url = "https://v1.samehadaku.how/wp-admin/admin-ajax.php"
    
    # We need to guess the action name, common ones: 'player_ajax', 'get_player', etc.
    # Let's try to find the action name in the scripts
    action = 'player_ajax' # Default guess
    
    data = {
        'action': action,
        'post': post_id,
        'nume': '1', # Episode index?
        'type': 'schtml' # specific type?
    }
    
    print(f"POST to {ajax_url} with data: {data}")
    # Note: This might fail without proper cookies/headers/nonce
