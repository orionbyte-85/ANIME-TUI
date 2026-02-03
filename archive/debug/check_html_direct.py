import subprocess
from bs4 import BeautifulSoup

url = "https://v1.samehadaku.how/one-piece-fan-letter-episode-1/"
cmd = ['curl', '-s', '-A', 'Mozilla/5.0', url]

html = subprocess.check_output(cmd).decode('utf-8')
print(f"HTML length: {len(html)}")
print(f"Contains 'server': {'id=\"server\"' in html}")
print(f"First 500 chars: {html[:500]}")
soup = BeautifulSoup(html, 'html.parser')

server_div = soup.find('div', id='server')
if server_div:
    options = server_div.find_all('div', class_='east_player_option')
    print(f"Found {len(options)} streaming options:")
    for opt in options:
        post_id = opt.get('data-post')
        nume = opt.get('data-nume')
        type_ = opt.get('data-type')
        label = opt.get_text(strip=True)
        print(f"  - {label} (post={post_id}, nume={nume}, type={type_})")
else:
    print("No server div found")
