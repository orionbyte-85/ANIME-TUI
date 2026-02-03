import requests
from bs4 import BeautifulSoup
import sys

# URL obtained from previous step (Otakudesu resolution)
url = "https://desustream.info/dstream/ondesu/v5/index.php?id=NXA1Z0JiQklTSzNld2xJbUppdWJpTHhXQWhpQXRJN3gvbG1PYTdiZXFQRT0="

print(f"Inspecting: {url}")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://otakudesu.best/"
}

try:
    resp = requests.get(url, headers=headers)
    print(f"Status: {resp.status_code}")
    
    # Print full response to see what we're dealing with
    print("\n--- Full Response ---")
    print(resp.text[:2000])
    print("\n--- End Response ---")
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Look for scripts that might contain sources
    scripts = soup.find_all('script')
    for i, s in enumerate(scripts):
        if s.string and ('sources' in s.string or 'file' in s.string or 'm3u8' in s.string):
            print(f"\n--- Script {i} with video data ---")
            print(s.string)
            
    # Look for video tag
    video = soup.find('video')
    if video:
        print("Found <video> tag")
        print(video.prettify())
        
except Exception as e:
    print(f"Error: {e}")
