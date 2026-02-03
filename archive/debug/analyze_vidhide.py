import requests
from bs4 import BeautifulSoup
import re

# Example Vidhide URL from the error
url = "https://odvidhide.com/embed/n87x8jeevpnp"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://v1.samehadaku.how/"
}

try:
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    print(f"Response length: {len(resp.text)}")
    
    # Look for video sources in scripts
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', resp.text, re.DOTALL)
    for i, script in enumerate(scripts):
        if 'sources' in script or 'file' in script or 'm3u8' in script or 'mp4' in script:
            print(f"\n--- Script {i} with video data ---")
            print(script[:1000])
    
    # Look for source URLs
    sources = re.findall(r'(?:file|src|source)["\':\s]+(["\'])(https?://[^"\']+\.(?:m3u8|mp4)[^"\']*)\1', resp.text)
    if sources:
        print("\n--- Found video sources ---")
        for src in sources:
            print(f"  {src[1]}")
    
    # Save full response for inspection
    with open('vidhide_embed.html', 'w', encoding='utf-8') as f:
        f.write(resp.text)
    print("\nSaved full response to vidhide_embed.html")
    
except Exception as e:
    print(f"Error: {e}")
