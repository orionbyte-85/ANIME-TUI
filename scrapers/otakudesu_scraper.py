import requests
from bs4 import BeautifulSoup
import re
import base64
import json

BASE_URL = "https://otakudesu.best"

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

def search_anime(query):
    """Search for anime on Otakudesu"""
    url = f"{BASE_URL}/?s={query}&post_type=anime"
    try:
        resp = requests.get(url, headers=get_headers())
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        results = []
        ul = soup.find('ul', class_='chivsrc')
        if ul:
            for li in ul.find_all('li'):
                link = li.find('a', href=True)
                if link:
                    # Get title from h2 tag inside the link
                    h2 = link.find('h2')
                    if h2:
                        title = h2.get_text(strip=True)
                    else:
                        # Fallback to link text
                        title = link.get_text(strip=True)
                    
                    url = link['href']
                    img = li.find('img', src=True)
                    thumbnail = img['src'] if img else None
                    
                    # Status/Rating/Genres are in div.set
                    status = "Unknown"
                    rating = "?"
                    for div in li.find_all('div', class_='set'):
                        text = div.get_text(strip=True)
                        if "Status" in text:
                            status = text.replace("Status", "").replace(":", "").strip()
                        elif "Rating" in text:
                            rating = text.replace("Rating", "").replace(":", "").strip()
                            
                    results.append({
                        'title': title,
                        'url': url,
                        'thumbnail': thumbnail,
                        'status': status,
                        'rating': rating,
                        'source': 'otakudesu'
                    })
        return results
    except Exception as e:
        print(f"[otakudesu] Search error: {e}")
        return []

def get_anime_episodes(anime_url):
    """Get list of episodes for an anime"""
    try:
        resp = requests.get(anime_url, headers=get_headers())
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        episodes = []
        
        # Find all episode lists (there might be multiple divs)
        ep_lists = soup.find_all('div', class_='episodelist')
        
        for episode_list in ep_lists:
            for li in episode_list.find_all('li'):
                link = li.find('a', href=True)
                if link:
                    url = link['href']
                    
                    # Skip batch/collection episodes (lengkap URLs)
                    if '/lengkap/' in url or 'batch' in url.lower():
                        continue
                    
                    title = link.get_text(strip=True)
                    
                    # Extract episode number
                    ep_num_match = re.search(r'Episode\s+(\d+)', title, re.IGNORECASE)
                    if ep_num_match:
                        ep_num = int(ep_num_match.group(1))
                    else:
                        ep_num = len(episodes) + 1
                    
                    episodes.append({
                        'title': title,
                        'url': url,
                        'episode_number': ep_num,
                        'source': 'otakudesu'
                    })
        
        return episodes
    except Exception as e:
        print(f"[otakudesu] Error getting episodes: {e}")
        return []

def get_video_links(episode_url):
    """Get video links - prioritize streaming mirrors (360p, 480p, 720p)"""
    try:
        resp = requests.get(episode_url, headers=get_headers())
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        links = []
        
        # PRIORITY: Extract streaming mirrors (AJAX-based)
        # User wants 360p, 480p, 720p streaming mirrors as main options
        mirror_div = soup.find('div', class_='mirrorstream')
        if mirror_div:
            # Extract AJAX action hashes from scripts
            action_video = None
            action_nonce = None
            
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'admin-ajax.php' in script.string:
                    matches = re.findall(r'action\s*:\s*["\']([a-f0-9]{32})["\']', script.string)
                    if len(matches) >= 2:
                        action_video = matches[0]
                        action_nonce = matches[1]
                        break
            
            if action_video and action_nonce:
                # Get Nonce
                nonce = None
                try:
                    nonce_resp = requests.post(
                        f"{BASE_URL}/wp-admin/admin-ajax.php",
                        headers=get_headers(),
                        data={"action": action_nonce}
                    )
                    if nonce_resp.status_code == 200:
                        nonce_data = nonce_resp.json()
                        if 'data' in nonce_data:
                            nonce = nonce_data['data']
                except Exception as e:
                    print(f"[otakudesu] Error getting nonce: {e}")

                if nonce:
                    # Priority order: 720p, 480p, 360p
                    quality_priority = {'m720p': 0, 'm480p': 1, 'm360p': 2}
                    
                    for ul in mirror_div.find_all('ul'):
                        quality_class = ul.get('class', [''])[0]
                        quality = quality_class.replace('m', '') if quality_class.startswith('m') else 'Unknown'
                        base_priority = quality_priority.get(quality_class, 999) * 100
                        
                        server_priority = 0
                        for li in ul.find_all('li'):
                            a = li.find('a')
                            if a:
                                server_name = a.get_text(strip=True)
                                content = a.get('data-content')
                                if content:
                                    try:
                                        original_payload = json.loads(base64.b64decode(content).decode('utf-8'))
                                        original_payload_b64 = base64.b64encode(json.dumps(original_payload).encode()).decode()
                                        
                                        special_url = f"otakudesu:{action_video}:{nonce}:{original_payload_b64}"
                                        
                                        # Rename ondesu to Sokuja for clarity
                                        if 'ondesu' in server_name.lower():
                                            server_name = 'Sokuja (ondesu)'
                                        
                                        links.append({
                                            'server': f"🎬 {server_name}",
                                            'url': special_url,
                                            'resolution': quality,
                                            'type': 'stream',
                                            'stream_ready': True,
                                            'priority': base_priority + server_priority
                                        })
                                        server_priority += 1
                                    except Exception as e:
                                        print(f"[otakudesu] Error parsing mirror: {e}")

        # Download Links as fallback (much lower priority)
        download_div = soup.find('div', class_='download')
        if download_div:
            ul = download_div.find('ul')
            if ul:
                priority = 1000  # Much lower priority
                for li in ul.find_all('li'):
                    text = li.get_text(strip=True)
                    quality = 'Unknown'
                    match = re.search(r'(360p|480p|720p|1080p)', text)
                    if match:
                        quality = match.group(1)
                    
                    for a in li.find_all('a'):
                        server = a.get_text(strip=True)
                        url = a['href']
                        links.append({
                            'server': server,
                            'url': url,
                            'resolution': quality,
                            'type': 'download',
                            'stream_ready': False,
                            'priority': priority
                        })
                        priority += 1
        
        # Sort by priority
        links.sort(key=lambda x: x.get('priority', 999))
                             
        return links
    except Exception as e:
        print(f"[otakudesu] Video links error: {e}")
        return []



def resolve_otakudesu_url(special_url):
    """Resolve otakudesu:ACTION:NONCE:PAYLOAD url to real stream URL"""
    try:
        if not special_url.startswith('otakudesu:'):
            return special_url
            
        parts = special_url.split(':')
        if len(parts) != 4:
            return None
            
        _, action, nonce, payload_b64 = parts
        
        payload = json.loads(base64.b64decode(payload_b64).decode('utf-8'))
        
        # Add required fields
        payload['action'] = action
        payload['nonce'] = nonce
        
        # Request
        resp = requests.post(
            f"{BASE_URL}/wp-admin/admin-ajax.php",
            headers=get_headers(),
            data=payload
        )
        
        if resp.status_code == 200:
            resp_json = resp.json()
            if 'data' in resp_json:
                html = base64.b64decode(resp_json['data']).decode('utf-8')
                # Extract iframe src (usually desustream URL)
                match = re.search(r'src="([^"]+)"', html)
                if match:
                    desustream_url = match.group(1)
                    
                    # Follow desustream URL to get actual video
                    try:
                        desu_resp = requests.get(desustream_url, headers=get_headers())
                        if desu_resp.status_code == 200:
                            # Look for Blogger iframe or direct video URL
                            blogger_match = re.search(r'<iframe[^>]+src="(https://www\.blogger\.com/video\.g\?token=[^"]+)"', desu_resp.text)
                            if blogger_match:
                                blogger_url = blogger_match.group(1)
                                
                                # Scrape Blogger page for direct Google Video URL
                                try:
                                    print(f"  [blogger] Scraping for direct URL...")
                                    blogger_resp = requests.get(blogger_url, headers=get_headers(), timeout=10)
                                    
                                    if blogger_resp.status_code == 200:
                                        # Look for direct googlevideo.com URL
                                        matches = re.findall(
                                            r'(https://[^"\']+googlevideo\.com/videoplayback[^"\']+)',
                                            blogger_resp.text
                                        )
                                        
                                        if matches:
                                            # Get the longest URL
                                            direct_url = max(matches, key=len)
                                            direct_url = direct_url.replace('\\u003d', '=').replace('\\u0026', '&')
                                            
                                            print(f"  [blogger] ✓ Found direct URL")
                                            
                                            # Return direct Google Video URL with headers
                                            return {
                                                'url': direct_url,
                                                'headers': {
                                                    'User-Agent': get_headers()['User-Agent'],
                                                    'Referer': 'https://desustream.info/'
                                                }
                                            }
                                except Exception as e:
                                    print(f"  [blogger] Scraping error: {e}")
                                
                                # Fallback: return Blogger URL with headers
                                print(f"  [blogger] ⚠️  Using Blogger embed URL (fallback)")
                                return {
                                    'url': blogger_url,
                                    'headers': {
                                        'User-Agent': get_headers()['User-Agent'],
                                        'Referer': 'https://desustream.info/'
                                    }
                                }
                            
                            # Fallback: look for any video source in scripts
                            video_match = re.search(r'file:\s*["\']([^"\']+\.m3u8[^"\']*)["\']', desu_resp.text)
                            if video_match:
                                return {
                                    'url': video_match.group(1),
                                    'headers': {
                                        'User-Agent': get_headers()['User-Agent'],
                                        'Referer': 'https://desustream.info/'
                                    }
                                }
                            
                            # Fallback 2: Look for <source src="..."> in HTML player
                            source_match = re.search(r'<source\s+src="([^"]+)"', desu_resp.text)
                            if source_match:
                                return {
                                    'url': source_match.group(1),
                                    'headers': {
                                        'User-Agent': get_headers()['User-Agent'],
                                        'Referer': 'https://desustream.info/'
                                    }
                                }
                                
                            # Fallback 3: Look for otakudesu('JSON') (Desudrive)
                            json_match = re.search(r"otakudesu\('([^']+)'\)", desu_resp.text)
                            if json_match:
                                try:
                                    data = json.loads(json_match.group(1))
                                    if 'file' in data:
                                        return {
                                            'url': data['file'],
                                            'headers': {
                                                'User-Agent': get_headers()['User-Agent'],
                                                'Referer': 'https://desustream.info/'
                                            }
                                        }
                                except:
                                    pass
                    except Exception as e:
                        print(f"[otakudesu] Error following desustream: {e}")
                    
                    # If we can't extract, return the desustream URL as fallback
                    # Only return dict with headers if it's Google/Blogger (needs proxy)
                    # For others (Vidhide, etc), return string so yt-dlp handles it
                    if 'googlevideo.com' in desustream_url or 'blogger.com' in desustream_url:
                        return {
                            'url': desustream_url,
                            'headers': {
                                'User-Agent': get_headers()['User-Agent'],
                                'Referer': 'https://desustream.info/'
                            }
                        }
                    else:
                        return desustream_url
                    
        return None
    except Exception as e:
        print(f"[otakudesu] Resolve error: {e}")
        return None
