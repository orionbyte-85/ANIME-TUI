import requests
from bs4 import BeautifulSoup

url = "https://v1.samehadaku.how/one-piece-fan-letter-episode-1/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0',
}

session = requests.Session()
response = session.get(url, headers=headers, timeout=10)

print(f"Status: {response.status_code}")
print(f"HTML length: {len(response.text)}")
print(f"Contains 'server': {'id=\"server\"' in response.text}")
print(f"First 500 chars: {response.text[:500]}")

soup = BeautifulSoup(response.text, 'html.parser')
server_div = soup.find('div', id='server')
if server_div:
    options = server_div.find_all('div', class_='east_player_option')
    print(f"\nFound {len(options)} streaming options:")
    for opt in options:
        label = opt.get_text(strip=True)
        print(f"  - {label}")
else:
    print("\nNo server div found")
