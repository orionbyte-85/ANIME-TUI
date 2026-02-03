import re
from bs4 import BeautifulSoup
import requests


def get_samehadaku_video(episode_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    try:
        # Use requests.Session() with proper headers
        session = requests.Session()
        resp = session.get(episode_url, headers=headers, timeout=10)
        resp.raise_for_status()  # Raise an exception for HTTP errors
        html = resp.text
            
        soup = BeautifulSoup(html, 'html.parser')

        # Cari div class="download-eps"
        dl_section = soup.find('div', {'class': 'download-eps'})
        if not dl_section:
            return None

        # Prioritas kualitas (dari tinggi ke rendah)
        qualities = ['1080p', '720p', 'x265', 'MP4HD', '480p', '360p']

        # Server yang didukung (prioritas dari yang paling reliable untuk streaming)
        servers = [
            {'name': 'pixeldrain', 'pattern': r'pixeldrain\.com/u/([a-zA-Z0-9]+)', 'fmt': 'https://pixeldrain.com/api/file/{}'},
            {'name': 'gdrive', 'pattern': r'gdriveplayer\.me/download\.php\?link=([^"\'&]+)', 'fmt': 'https://gdriveplayer.me/download.php?link={}'},
            {'name': 'acefile', 'pattern': r'acefile\.co/f/([a-zA-Z0-9]+/[^/\s"\']+)', 'fmt': 'https://acefile.co/f/{}'},
            {'name': 'wibufile', 'pattern': r'wibufile\.com/([a-zA-Z0-9]+/watch)', 'fmt': 'https://wibufile.com/{}'},
            {'name': 'mirrorupload', 'pattern': r'mir\.cr/([a-zA-Z0-9]+)', 'fmt': 'https://mir.cr/{}'},
            {'name': 'racaty', 'pattern': r'racaty\.io/([a-zA-Z0-9]+)', 'fmt': 'https://racaty.io/{}'},
            {'name': 'krakenfiles', 'pattern': r'krakenfiles\.com/view/([a-zA-Z0-9]+)', 'fmt': 'https://krakenfiles.com/{}'},
            {'name': 'gofile', 'pattern': r'gofile\.io/d/([a-zA-Z0-9]+)', 'fmt': 'https://gofile.io/d/{}'},
            {'name': 'zippyshare', 'pattern': r'zippyshare\.com/v/([a-zA-Z0-9]+)', 'fmt': 'https://www.zippyshare.com/v/{}'},
            {'name': 'reupload', 'pattern': r'reupload\.org/([a-zA-Z0-9]+)', 'fmt': 'https://reupload.org/{}'},
        ]

        for q in qualities:
            # Cari <li> yang mengandung kualitas
            items = dl_section.find_all('li')
            for li in items:
                if q in li.get_text():
                    for s in servers:
                        link = li.find('a', href=re.compile(s['pattern']))
                        if link:
                            match = re.search(s['pattern'], link['href'])
                            if match:
                                url = s['fmt'].format(match.group(1))
                                print(f"[scraper] Found {s['name']} link for {q}: {url}")
                                return url
        return None
    except Exception as e:
        print(f"[scraper] Error: {e}")
        return None


def get_all_video_links(episode_url):
    """Get all available video links with quality and server info"""
    try:
        # Use Selenium to bypass Cloudflare protection
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options
        import time
        
        options = Options()
        options.add_argument('--headless')
        options.set_preference('general.useragent.override', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Firefox(options=options)
        try:
            driver.get(episode_url)
            # Wait for Cloudflare to pass and content to load
            time.sleep(7)
            
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
        finally:
            driver.quit()

        # Cari div class="download-eps"
        dl_section = soup.find('div', {'class': 'download-eps'})
        if not dl_section:
            return []

        # Server yang didukung (dengan prioritas dan stream_ready flag)
        # stream_ready = True: bisa langsung streaming di MPV
        # stream_ready = False: perlu download atau extract URL dulu
        servers = [
            {'name': 'Pixeldrain', 'pattern': r'pixeldrain\.com/u/([a-zA-Z0-9]+)', 'fmt': 'https://pixeldrain.com/api/file/{}', 'stream_ready': True},
            {'name': 'Google Drive', 'pattern': r'gdriveplayer\.me/download\.php\?link=([^"\'&]+)', 'fmt': 'https://gdriveplayer.me/download.php?link={}', 'stream_ready': True},
            {'name': 'Acefile', 'pattern': r'acefile\.co/f/([a-zA-Z0-9]+/[^/\s"\']+)', 'fmt': 'https://acefile.co/f/{}', 'stream_ready': False},
            {'name': 'Wibufile', 'pattern': r'wibufile\.com/([a-zA-Z0-9]+/watch)', 'fmt': 'https://wibufile.com/{}', 'stream_ready': False},
            {'name': 'MirrorUpload', 'pattern': r'mir\.cr/([a-zA-Z0-9]+)', 'fmt': 'https://mir.cr/{}', 'stream_ready': False},
            {'name': 'Racaty', 'pattern': r'racaty\.io/([a-zA-Z0-9]+)', 'fmt': 'https://racaty.io/{}', 'stream_ready': False},
            {'name': 'Krakenfiles', 'pattern': r'krakenfiles\.com/view/([a-zA-Z0-9]+)', 'fmt': 'https://krakenfiles.com/{}', 'stream_ready': False},
            {'name': 'Gofile', 'pattern': r'gofile\.io/d/([a-zA-Z0-9]+)', 'fmt': 'https://gofile.io/d/{}', 'stream_ready': True},
            {'name': 'Zippyshare', 'pattern': r'zippyshare\.com/v/([a-zA-Z0-9]+)', 'fmt': 'https://www.zippyshare.com/v/{}', 'stream_ready': False},
            {'name': 'Reupload', 'pattern': r'reupload\.org/([a-zA-Z0-9]+)', 'fmt': 'https://reupload.org/{}', 'stream_ready': False},
        ]

        results = []

        # Find all <li> items
        items = dl_section.find_all('li')
        for li in items:
            text = li.get_text()

            # Try to extract quality
            quality = None
            quality_patterns = ['1080p', '720p', 'x265', 'MP4HD', '480p', '360p', '240p']
            for q in quality_patterns:
                if q in text:
                    quality = q
                    break

            if not quality:
                continue  # Skip if we can't determine quality

            # Find all links in this <li>
            links = li.find_all('a', href=True)
            for link in links:
                href = link['href']
                link_text = link.get_text(strip=True)

                # Try to match against known servers
                for s in servers:
                    match = re.search(s['pattern'], href)
                    if match:
                        url = s['fmt'].format(match.group(1))
                        results.append({
                            'resolution': quality,
                            'server': s['name'],
                            'url': url,
                            'type': 'download',
                            'stream_ready': s.get('stream_ready', False),
                            'priority': quality_patterns.index(quality) if quality in quality_patterns else 999
                        })
                        break  # Found match for this link, move to next

        # Sort by: 1) quality priority, 2) stream-ready servers first
        results.sort(key=lambda x: (x['priority'], not x['stream_ready']))

        # --- Extract Streaming Options (AJAX) - PRIORITIZED ---
        # Cari div id="server" -> ul -> li -> div.east_player_option
        server_div = soup.find('div', id='server')
        streaming_options = []

        if server_div:
            options = server_div.find_all('div', class_='east_player_option')
            for opt in options:
                # Extract attributes needed for AJAX
                post_id = opt.get('data-post')
                nume = opt.get('data-nume')
                type_ = opt.get('data-type')

                # Get label text (e.g., "Blogspot 480p")
                label = opt.get_text(strip=True)

                if post_id and nume and type_:
                    # Determine quality from label
                    quality = 'Unknown'
                    quality_priority = 999
                    for idx, q in enumerate(['1080p', '720p', '480p', '360p']):
                        if q in label:
                            quality = q
                            quality_priority = idx
                            break

                    # Add to streaming options with high priority
                    streaming_options.append({
                        'resolution': quality,
                        'server': f"🎬 {label.replace(quality, '').strip()}",
                        'url': f"ajax:{post_id}:{nume}:{type_}",
                        'stream_ready': True,
                        'priority': quality_priority  # Sort by quality within streaming options
                    })

        # Sort streaming options by quality
        streaming_options.sort(key=lambda x: x['priority'])

        # Sort download options by quality and stream-ready status
        results.sort(key=lambda x: (x['priority'], not x['stream_ready']))

        # Combine: streaming options first, then download options
        results = streaming_options + results

        return results
    except Exception as e:
        print(f"[scraper] Error getting all links: {e}")
        return []


def get_streaming_url(ajax_params):
    """Fetch actual streaming URL using AJAX params"""
    # params format: ajax:post_id:nume:type
    try:
        _, post_id, nume, type_ = ajax_params.split(':')

        url = "https://v1.samehadaku.how/wp-admin/admin-ajax.php"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://v1.samehadaku.how"
        }

        data = {
            "action": "player_ajax",
            "post": post_id,
            "nume": nume,
            "type": type_
        }

        resp = requests.post(url, headers=headers, data=data)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            iframe = soup.find('iframe')
            if iframe and iframe.get('src'):
                src = iframe['src']
                
                # If it's a blogger link, scrape to get direct Google Video URL
                if 'blogger.com' in src or 'googleusercontent' in src or 'googlevideo.com' in src:
                    print(f"  [blogger] Scraping for direct URL...")
                    
                    try:
                        # Scrape Blogger page for direct video URL
                        blogger_resp = requests.get(src, headers=headers, timeout=10)
                        
                        if blogger_resp.status_code == 200:
                            # Look for direct googlevideo.com URL in page source
                            matches = re.findall(
                                r'(https://[^"\']+googlevideo\.com/videoplayback[^"\']+)', 
                                blogger_resp.text
                            )
                            
                            if matches:
                                # Get the longest URL (usually the full one)
                                direct_url = max(matches, key=len)
                                # Unescape
                                direct_url = direct_url.replace('\\u003d', '=').replace('\\u0026', '&')
                                
                                print(f"  [blogger] ✓ Found direct URL")
                                
                                # Return with headers for proxy
                                return {
                                    'url': direct_url,
                                    'headers': {
                                        'User-Agent': headers['User-Agent'],
                                        'Referer': 'https://v1.samehadaku.how/'
                                    }
                                }
                    except Exception as e:
                        print(f"  [blogger] Scraping error: {e}")
                    
                    # Fallback: return Blogger URL with headers
                    print(f"  [blogger] ⚠️  Using Blogger embed URL (fallback)")
                    return {
                        'url': src,
                        'headers': {
                            'User-Agent': headers['User-Agent'],
                            'Referer': 'https://v1.samehadaku.how/'
                        }
                    }
                    
                # If it's youtube, also playable
                if 'youtube.com' in src or 'youtu.be' in src:
                    return src
                
                # Try to resolve embed URLs to direct video
                try:
                    from utils.embed_resolvers import resolve_embed_url
                    
                    # Determine server name from URL
                    server_name = ""
                    if 'vidhide' in src.lower():
                        server_name = "Vidhide"
                    elif 'pixeldrain' in src.lower():
                        server_name = "Pixeldrain"
                    elif 'mega' in src.lower():
                        server_name = "Mega"
                    elif 'krakenfiles' in src.lower():
                        server_name = "Krakenfiles"
                    
                    if server_name:
                        resolved = resolve_embed_url(src, server_name)
                        if resolved:
                            return resolved
                except ImportError:
                    pass  # embed_resolvers not available
                except Exception as e:
                    print(f"[scraper] Resolver error: {e}")

                # Return embed URL as fallback (yt-dlp might handle it)
                return src
    except Exception as e:
        print(f"[scraper] Error fetching stream URL: {e}")

    return None


def resolve_gofile_url(gofile_url):
    # Placeholder for Gofile resolver
    # Implement actual logic here if needed, e.g., using requests to get the direct link
    print(f"[scraper] Warning: Gofile resolver not implemented yet. Returning original URL: {gofile_url}")
    return gofile_url


def search_anime(query):
    """Search for anime on Samehadaku and return list of results"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    try:
        url = f"https://samehadaku.how/?s={query}"
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')

        results = []
        main_content = soup.find('main', id='main')
        if main_content:
            articles = main_content.find_all('article', class_='animpost')
            for art in articles:
                link_tag = art.find('a', href=True)
                if link_tag:
                    # Extract title from alt attribute or text
                    title = link_tag.get('alt', link_tag.get_text(strip=True))
                    url = link_tag['href']

                    # Try to get thumbnail
                    img = art.find('img', src=True)
                    thumbnail = img['src'] if img else None

                    results.append({
                        'title': title,
                        'url': url,
                        'thumbnail': thumbnail
                    })

        return results
    except Exception as e:
        print(f"[scraper] Search error: {e}")
        return []


def get_anime_episodes(anime_url):
    """Get list of episodes from an anime detail page"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(anime_url, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')

        episodes = []
        
        # Method 1: Check for div.lstepsiode (Standard layout)
        lstepsiode = soup.find('div', class_='lstepsiode')
        if lstepsiode:
            # Check for ul inside
            ul = lstepsiode.find('ul')
            if ul:
                for li in ul.find_all('li'):
                    # Title and URL are usually in div.epsleft span.lchx a
                    epsleft = li.find('div', class_='epsleft')
                    if epsleft:
                        link = epsleft.find('a', href=True)
                        if link:
                            title = link.get_text(strip=True)
                            url = link['href']
                            
                            # Extract episode number
                            ep_num = '?'
                            # Try to find number in div.epsright first (sometimes contains just the number)
                            epsright = li.find('div', class_='epsright')
                            if epsright:
                                num_link = epsright.find('a')
                                if num_link:
                                    ep_num = num_link.get_text(strip=True)
                            
                            # If not found or not digit, try regex on title
                            if not ep_num or not ep_num.isdigit():
                                match = re.search(r'Episode\s+(\d+)', title, re.IGNORECASE)
                                if match:
                                    ep_num = match.group(1)
                            
                            episodes.append({
                                'title': title,
                                'url': url,
                                'episode_number': ep_num,
                                'source': 'samehadaku'
                            })
                            continue

        # Method 2: Check for div.listeps (Alternative layout)
        if not episodes:
            listeps = soup.find('div', class_='listeps')
            if listeps:
                ul = listeps.find('ul')
                if ul:
                    for li in ul.find_all('li'):
                        # Similar structure usually
                        epsleft = li.find('div', class_='epsleft')
                        if epsleft:
                            link = epsleft.find('a', href=True)
                            if link:
                                title = link.get_text(strip=True)
                                url = link['href']
                                
                                ep_num = '?'
                                match = re.search(r'Episode\s+(\d+)', title, re.IGNORECASE)
                                if match:
                                    ep_num = match.group(1)
                                
                                episodes.append({
                                    'title': title,
                                    'url': url,
                                    'episode_number': ep_num,
                                    'source': 'samehadaku'
                                })

        # Sort by episode number (descending usually, reverse if needed)
        # Samehadaku usually lists newest first (descending).
        # We want newest first usually, so keep as is.
        
        return episodes
    except Exception as e:
        print(f"[scraper] Episode list error: {e}")
        return []
