from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

url = "https://v1.samehadaku.how/one-piece-fan-letter-episode-1/"

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(options=options)
try:
    driver.get(url)
    # Wait for Cloudflare to pass
    time.sleep(5)
    
    html = driver.page_source
    print(f"HTML length: {len(html)}")
    print(f"Contains 'server': {'id=\"server\"' in html}")
    
    soup = BeautifulSoup(html, 'html.parser')
    server_div = soup.find('div', id='server')
    if server_div:
        options = server_div.find_all('div', class_='east_player_option')
        print(f"Found {len(options)} streaming options:")
        for opt in options:
            label = opt.get_text(strip=True)
            print(f"  - {label}")
    else:
        print("No server div found")
finally:
    driver.quit()
