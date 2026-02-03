import requests

url = "https://v1.samehadaku.how/one-piece-fan-letter-episode-1/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none"
}

session = requests.Session()
resp = session.get(url, headers=headers, timeout=30)

with open('samehadaku_response.html', 'w', encoding='utf-8') as f:
    f.write(resp.text)

print(f"Saved {len(resp.text)} bytes to samehadaku_response.html")
print(f"Status: {resp.status_code}")
print(f"First 1000 chars:")
print(resp.text[:1000])
