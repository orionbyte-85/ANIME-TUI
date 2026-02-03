#!/usr/bin/env python3
"""Verify AJAX player extraction"""

import requests
from bs4 import BeautifulSoup

# Parameters found from previous step
url = "https://v1.samehadaku.how/wp-admin/admin-ajax.php"
post_id = "22149"
nume = "1"
type_ = "schtml"
action = "player_ajax"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://v1.samehadaku.how",
    "Referer": "https://v1.samehadaku.how/maou-gakuin-no-futekigousha-season-2-episode-1/"
}

data = {
    "action": action,
    "post": post_id,
    "nume": nume,
    "type": type_
}

print(f"Sending POST to {url}")
print(f"Data: {data}")

try:
    resp = requests.post(url, headers=headers, data=data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}...")
    
    # Check if response contains iframe
    if '<iframe' in resp.text:
        soup = BeautifulSoup(resp.text, 'html.parser')
        iframe = soup.find('iframe')
        print(f"\nFound iframe src: {iframe['src']}")
except Exception as e:
    print(f"Error: {e}")
