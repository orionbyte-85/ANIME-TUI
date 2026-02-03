import requests

# URL from user log (truncated, so this exact one might fail, but I need to test the concept)
# I will use a placeholder or try to get a fresh one if possible. 
# Since I can't get a fresh one easily without running the scraper, I'll use the scraper to get one.

import otakudesu_scraper

def test_fetch():
    print("Fetching fresh Otakudesu link...")
    # Use the episode from the log: Maou Gakuin Ep 1
    url = "https://otakudesu.best/episode/maogkn-ftkg-episode-1-sub-indo/"
    
    links = otakudesu_scraper.get_video_links(url)
    target_link = None
    
    # Find desudrive
    for link in links:
        if 'desudrive' in link['server'].lower():
            target_link = link
            break
            
    if not target_link:
        print("Could not find desudrive link")
        return

    print(f"Resolving {target_link['url']}...")
    resolved = otakudesu_scraper.resolve_otakudesu_url(target_link['url'])
    
    if not resolved:
        print("Failed to resolve")
        return
        
    if isinstance(resolved, dict):
        video_url = resolved['url']
        headers = resolved.get('headers', {})
    else:
        video_url = resolved
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://desustream.info/'}
        
    print(f"Video URL: {video_url[:60]}...")
    print(f"Headers: {headers}")
    
    print("\nAttempting download with requests...")
    try:
        r = requests.get(video_url, headers=headers, stream=True)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            print("✅ Success! Stream is accessible with headers.")
            ct = r.headers.get('Content-Type', '')
            print(f"Content-Type: {ct}")
            
            if 'video' in ct or 'application/octet-stream' in ct:
                print("Detected video stream!")
                chunk = next(r.iter_content(1024))
                print(f"Received chunk of size: {len(chunk)}")
                print("First 50 bytes hex:", chunk[:50].hex())
            else:
                content = r.content
                print(f"Total size: {len(content)}")
                print("--- Content Start ---")
                print(content.decode('utf-8', errors='ignore')[:2000])
                print("--- Content End ---")
        else:
            print("❌ Failed with status code")
            print(r.text[:200])
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_fetch()
