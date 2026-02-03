import requests
from bs4 import BeautifulSoup

url = "https://v1.samehadaku.how/one-piece-fan-letter-episode-1/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1"
}

s = requests.Session()
resp = s.get(url, headers=headers)
print(f"Status: {resp.status_code}")
print(f"Response Headers: {resp.headers}")

soup = BeautifulSoup(resp.text, 'html.parser')
server_div = soup.find('div', id='server')
if server_div:
    options = server_div.find_all('div', class_='east_player_option')
    print(f"Found {len(options)} options")
    for opt in options:
        print(f" - {opt.get_text(strip=True)}")
else:
    print("No #server div found")
