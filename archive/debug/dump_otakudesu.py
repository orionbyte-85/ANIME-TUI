#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

url = "https://otakudesu.best/maou-gakuin-no-futekigousha-episode-1-subtitle-indonesia/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

resp = requests.get(url, headers=headers)
print(f"Status: {resp.status_code}")
print(f"Length: {len(resp.text)}")

with open("otakudesu_debug.html", "w") as f:
    f.write(resp.text)

soup = BeautifulSoup(resp.text, 'html.parser')
mirror = soup.find('div', class_='mirrorstream')
print(f"Mirror div found: {mirror is not None}")

download = soup.find('div', class_='download')
print(f"Download div found: {download is not None}")
