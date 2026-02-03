import requests
from bs4 import BeautifulSoup
import subprocess
import sys

print("--- START DEBUG ---")

# 1. Test AJAX Blogspot
print("\n--- Testing AJAX Blogspot ---")
# Using the params found in test_all_servers.py output: ajax:22149:1:schtml
url = "https://v1.samehadaku.how/wp-admin/admin-ajax.php"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://v1.samehadaku.how"
}
data = {
    "action": "player_ajax",
    "post": "22149",
    "nume": "1",
    "type": "schtml"
}

try:
    resp = requests.post(url, headers=headers, data=data)
    print(f"Status: {resp.status_code}")
    print(f"Response len: {len(resp.text)}")
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    iframe = soup.find('iframe')
    if iframe:
        src = iframe.get('src')
        print(f"Iframe Src: {src}")
        
        # If it's a blogger link, try to see if yt-dlp supports it
        if 'blogger.com' in src or 'googleusercontent' in src:
            print("Found Blogger/Google link!")
    else:
        print("No iframe found in AJAX response")
        print(f"Full response: {resp.text[:200]}...")
except Exception as e:
    print(f"Error in AJAX test: {e}")

# 2. Test yt-dlp on Acefile/Racaty
print("\n--- Testing yt-dlp support ---")
test_links = [
    ("Acefile", "https://acefile.co/f/92093398/mgnf-s2-1-1080p-samehadaku-care-mkv"),
    ("Racaty", "https://racaty.io/01gtheihgxin")
]

for name, link in test_links:
    print(f"Testing {name}: {link}")
    try:
        # Run yt-dlp -g (get url)
        # We use a timeout to avoid hanging
        cmd = ['yt-dlp', '-g', link]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            direct_url = result.stdout.strip()
            print(f"SUCCESS! Direct URL found (len={len(direct_url)})")
            print(f"URL start: {direct_url[:50]}...")
        else:
            print(f"FAILED. Return code: {result.returncode}")
            print(f"Error output: {result.stderr.strip()[:200]}...")
    except subprocess.TimeoutExpired:
        print("TIMEOUT: yt-dlp took too long")
    except Exception as e:
        print(f"Error running yt-dlp: {e}")

print("\n--- END DEBUG ---")
