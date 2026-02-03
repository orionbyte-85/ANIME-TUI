import requests
from bs4 import BeautifulSoup

def inspect_search(query):
    url = f"https://samehadaku.how/?s={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers)
        print(f"Status: {resp.status_code}")
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Try to find search results container
        # Usually it's 'main' or specific class
        main_content = soup.find('main', id='main')
        if main_content:
            print("Found main content")
            articles = main_content.find_all('article')
            print(f"Found {len(articles)} articles")
            for i, art in enumerate(articles[:3]):
                title = art.find('h3', class_='entry-title')
                link = art.find('a', href=True)
                print(f"[{i}] Title: {title.get_text() if title else 'N/A'}")
                print(f"    Link: {link['href'] if link else 'N/A'}")
                print(f"    HTML snippet: {str(art)[:500]}...")
        else:
            print("Main content not found. Dumping partial body...")
            print(soup.body.prettify()[:1000])

    except Exception as e:
        print(f"Error: {e}")

def inspect_anime_details(url):
    print(f"Inspecting: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Try multiple patterns for episode list
        patterns = [
            ('div', 'lstep'),
            ('div', 'eplister'),
            ('ul', 'eplist'),
            ('div', 'episode-list')
        ]
        
        found = False
        for tag, cls in patterns:
            container = soup.find(tag, class_=cls)
            if container:
                print(f"Found {tag}.{cls} (episode list container)")
                found = True
                # Find all episode links
                links = container.find_all('a', href=True)
                print(f"Found {len(links)} episode links")
                for i, link in enumerate(links[:5]):
                    print(f"[{i}] {link.get_text(strip=True)}: {link['href']}")
                break
        
        if not found:
            # Search for any links that might be episodes
            print("No standard episode container found. Searching for episode links...")
            all_links = soup.find_all('a', href=True)
            episode_links = [a for a in all_links if '/episode' in a['href'].lower() or 'eps' in a.get_text().lower()]
            print(f"Found {len(episode_links)} potential episode links")
            for i, link in enumerate(episode_links[:5]):
                print(f"[{i}] {link.get_text(strip=True)}: {link['href']}")
            
            # Also dump main content area
            print("\nSearching for main content area...")
            main = soup.find('main', id='main') or soup.find('div', class_='site-content')
            if main:
                print(f"Main content HTML (first 2000 chars):\n{str(main)[:2000]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_search("naruto")
    print("-" * 20)
    inspect_anime_details("https://v1.samehadaku.how/anime/naruto-kecil/")
