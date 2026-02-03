import requests
from bs4 import BeautifulSoup
import sys

def print_structure(element, depth=0):
    if depth > 3: return
    indent = "  " * depth
    if element.name:
        print(f"{indent}<{element.name} class='{element.get('class', [])}'>")
        for child in element.children:
            if child.name:
                print_structure(child, depth + 1)

print("--- Searching for 'one piece' ---")
url = "https://otakudesu.best/?s=one+piece&post_type=anime"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

try:
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Find search results container
    # Usually it's a ul or div with class 'chivsrc' or similar based on common themes, but let's look for 'ul' with class 'chivsrc' or just inspect the main content
    
    # Let's try to find the list of anime
    ul = soup.find('ul', class_='chivsrc')
    if ul:
        print("Found 'ul.chivsrc'")
        first_li = ul.find('li')
        if first_li:
            print("First item structure:")
            print(first_li.prettify())
            
            # Get the link to the first anime to test details
            link = first_li.find('a', href=True)
            if link:
                anime_url = link['href']
                print(f"\n--- Analyzing Anime Details: {anime_url} ---")
                resp_anime = requests.get(anime_url, headers=headers)
                soup_anime = BeautifulSoup(resp_anime.text, 'html.parser')
                
                # Find episode list
                # Sometimes there are multiple lists (Batch vs Regular)
                ep_lists = soup_anime.find_all('div', class_='episodelist')
                print(f"Found {len(ep_lists)} 'div.episodelist' elements")
                
                for i, ep_list_div in enumerate(ep_lists):
                    print(f"--- List {i+1} ---")
                    # Find all episodes
                    episodes = ep_list_div.find_all('li')
                    print(f"Found {len(episodes)} items in this list")
                    
                    if len(episodes) > 0:
                        print(f"First item: {episodes[0].get_text(strip=True)}")
                    
                    target_ep = None
                    for ep in episodes:
                        link = ep.find('a', href=True)
                        if link:
                            text = link.get_text(strip=True)
                            if "BATCH" not in text and "Batch" not in text:
                                target_ep = ep
                                print(f"Found regular episode: {text}")
                                break
                    
                    if target_ep:
                        # Get link to first episode
                        ep_link = target_ep.find('a', href=True)
                        if ep_link:
                            ep_url = ep_link['href']
                            print(f"\n--- Analyzing Episode Page: {ep_url} ---")
                            resp_ep = requests.get(ep_url, headers=headers)
                            soup_ep = BeautifulSoup(resp_ep.text, 'html.parser')
                            
                            # Find download/streaming links
                            # Usually in 'download' div or 'mirror-stream'
                            download_div = soup_ep.find('div', class_='download')
                            if download_div:
                                print("Found 'div.download'")
                                # print(download_div.prettify()[:1000]) 
                                
                                # Print structure of download links
                                for h4 in download_div.find_all('h4'):
                                    print(f"Quality: {h4.get_text(strip=True)}")
                                    ul = h4.find_next_sibling('ul')
                                    if ul:
                                        for li in ul.find_all('li'):
                                            a = li.find('a')
                                            if a:
                                                print(f"  - {a.get_text(strip=True)}: {a['href']}")
                            
                            stream_div = soup_ep.find('div', class_='stream')
                            if stream_div:
                                print("Found 'div.stream'")
                            
                            # Look for 'mirror-stream' or similar
                            # Otakudesu often uses a select box or list for mirrors
                            mirror_div = soup_ep.find('div', class_='mirrorstream')
                            if mirror_div:
                                print("Found 'div.mirrorstream'")
                                print(mirror_div.prettify()[:1000])

    else:
        print("Could not find search results list. Dumping main content structure...")
        main = soup.find('div', id='content') or soup.find('main')
        if main:
            print(main.prettify()[:1000])

except Exception as e:
    print(f"Error: {e}")
