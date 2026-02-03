import requests

url = "https://vidcache.net:8161/a20251127d6wnK8LAgyO/video.mp4" # URL from user log

headers_list = [
    {}, # No headers
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.yourupload.com/'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://desudrive.com/'
    }
]

print(f"Testing URL: {url}\n")

for i, headers in enumerate(headers_list):
    print(f"--- Test {i+1} ---")
    print(f"Headers: {headers}")
    try:
        # Use stream=True to avoid downloading the whole file if it works
        resp = requests.get(url, headers=headers, stream=True, timeout=10)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print("SUCCESS! This header combination works.")
            break
        else:
            print("Failed.")
    except Exception as e:
        print(f"Error: {e}")
    print("\n")
