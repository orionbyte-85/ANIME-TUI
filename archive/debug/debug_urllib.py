import urllib.request
from bs4 import BeautifulSoup

url = "https://v1.samehadaku.how/one-piece-fan-letter-episode-1/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        server_div = soup.find('div', id='server')
        if server_div:
            options = server_div.find_all('div', class_='east_player_option')
            print(f"Found {len(options)} options")
            for opt in options:
                print(f" - {opt.get_text(strip=True)}")
        else:
            print("No #server div found")
except Exception as e:
    print(f"Error: {e}")
