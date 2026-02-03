import requests
from bs4 import BeautifulSoup

url = "https://otakudesu.best/episode/boruto-naruto-next-generations-episode-1-subtitle-indonesia/"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

print(f"Analyzing: {url}")
resp = requests.get(url, headers=headers)
print(f"Status: {resp.status_code}")
print(f"Content snippet: {resp.text[:500]}")
soup = BeautifulSoup(resp.text, 'html.parser')

# 1. Mirror Stream
print("\n--- Mirror Stream ---")
mirror_div = soup.find('div', class_='mirrorstream')
if mirror_div:
    # Usually a ul with class 'm360p', 'm480p', 'm720p'
    for ul in mirror_div.find_all('ul'):
        cls = ul.get('class', [''])[0]
        print(f"Quality Class: {cls}")
        for li in ul.find_all('li'):
            a = li.find('a')
            if a:
                print(f"  - {a.get_text(strip=True)}: {a['data-content']}") # They often use data-content for the embed code

# 2. Download Links
print("\n--- Download Links ---")
download_div = soup.find('div', class_='download')
if download_div:
    # Just print the first few to verify structure
    h4s = download_div.find_all('h4')
    for h4 in h4s[:3]:
        print(f"Header: {h4.get_text(strip=True)}")
        ul = h4.find_next_sibling('ul')
        if ul:
            for li in ul.find_all('li'):
                a = li.find('a')
                if a:
                    print(f"  - {a.get_text(strip=True)}: {a['href']}")

# 3. Stream Div (Default player)
print("\n--- Default Stream ---")
stream_div = soup.find('div', class_='stream')
if stream_div:
    iframe = stream_div.find('iframe')
    if iframe:
        print(f"Iframe Src: {iframe.get('src')}")
