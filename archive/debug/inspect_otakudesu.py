import requests
from bs4 import BeautifulSoup

url = "https://otakudesu.best/episode/wpoiec-episode-1150-sub-indo/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

print("--- Mirror Stream Section ---")
mirror_div = soup.find('div', class_='mirrorstream')
if mirror_div:
    print(mirror_div.prettify())
else:
    print("No mirrorstream div found")

print("--- Download Section ---")
download_div = soup.find('div', class_='download')
if download_div:
    print(download_div.prettify())
else:
    print("No download div found")
