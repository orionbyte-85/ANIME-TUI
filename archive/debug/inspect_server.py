import requests
from bs4 import BeautifulSoup
import sys

import subprocess

url = "https://v1.samehadaku.how/one-piece-fan-letter-episode-1/"
cmd = [
    'curl', '-s',
    '-A', "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    url
]

try:
    html = subprocess.check_output(cmd).decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

server_div = soup.find('div', id='server')
if server_div:
    print("Found #server div")
    print(server_div.prettify())
else:
    print("No #server div found")
