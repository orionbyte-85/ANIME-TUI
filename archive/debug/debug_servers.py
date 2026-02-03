import requests
from bs4 import BeautifulSoup
import subprocess

# 1. Test AJAX Blogspot
print("--- Testing AJAX Blogspot ---")
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
    print(f"Response: {resp.text[:500]}...") # Print first 500 chars
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    iframe = soup.find('iframe')
    if iframe:
        print(f"Iframe Src: {iframe.get('src')}")
    else:
        print("No iframe found")
except Exception as e:
    print(f"Error: {e}")

# 2. Test yt-dlp on Acefile/Racaty
print("\n--- Testing yt-dlp support ---")
test_links = [
    ("Acefile", "https://acefile.co/f/92093398/mgnf-s2-1-1080p-samehadaku-care-mkv"),
    ("Racaty", "https://racaty.io/01gtheihgxin")
]

for name, link in test_links:
    print(f"Testing {name}: {link}")
    try:
        # Run yt-dlp -g (get url) to see if it works
        result = subprocess.run(['yt-dlp', '-g', link], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"SUCCESS! Direct URL: {result.stdout.strip()[:100]}...")
        else:
            print(f"FAILED. Error: {result.stderr.strip()[:100]}...")
    except Exception as e:
        print(f"Error running yt-dlp: {e}")
