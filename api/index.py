"""
Stremio Addon for Indonesian Anime Streaming
Supports: Samehadaku, Otakudesu, Sokuja, Nyaa Torrents
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import re
import logging
from functools import lru_cache
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import existing scrapers
from scrapers import samehadaku_scraper, otakudesu_scraper, sokuja_scraper, nyaa_scraper
from scrapers import animetosho_scraper  # NEW: AnimeTosho torrents
from utils.tmdb_helper import TMDBHelper
from utils.anilist_helper import AniListHelper

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize helpers
tmdb = TMDBHelper()
anilist = AniListHelper()

# Addon metadata
MANIFEST = {
    "id": "community.anime.indonesian.multi",
    "version": "2.0.0",
    "name": "Indonesian Anime Streams",
    "description": "Fast & reliable anime streams: Sokuja (direct) + 15 torrents (Nyaa & AnimeTosho)",
    "resources": ["stream"],
    "types": ["series"],
    "idPrefixes": ["tt", "tmdb"],
    "catalogs": []
}

@app.route('/')
def index():
    return jsonify({
        "addon": MANIFEST['name'],
        "version": MANIFEST['version'],
        "endpoints": {
            "manifest": "/manifest.json",
            "stream": "/stream/{type}/{id}.json"
        }
    })

@app.route('/manifest.json')
def manifest():
    """Stremio addon manifest"""
    return jsonify(MANIFEST)

@app.route('/stream/<type>/<id>.json')
def stream(type, id):
    """
    Main stream endpoint
    ID format: {imdb_id}:{season}:{episode}
    Example: tt0409591:1:1 (Naruto S01E01)
    """
    try:
        logger.info(f"Stream request: {type}/{id}")
        
        # Parse video ID
        parts = id.split(':')
        if len(parts) < 3:
            return jsonify({"streams": []})
        
        imdb_id, season, episode = parts[0], int(parts[1]), int(parts[2])
        
        # Step 1: Get basic info from TMDB
        tmdb_metadata = tmdb.get_anime_metadata(imdb_id, season, episode)
        if not tmdb_metadata:
            logger.warning(f"No TMDB metadata found for {imdb_id}")
            return jsonify({"streams": []})
        
        tmdb_title = tmdb_metadata['title']
        
        # Step 2: Search AniList with TMDB title to get romaji
        anime_data = anilist.search_anime(tmdb_title)
        
        if anime_data:
            # Use AniList titles (more accurate for anime)
            all_titles = anime_data['all_titles']
            logger.info(f"AniList titles: {all_titles}")
            
            # IMPORTANT: Prioritize SHORT titles (Indonesian sites use short names)
            # Sort by length: shorter titles first
            all_titles_sorted = sorted([t for t in all_titles if t], key=lambda x: len(x))
            
            # Also try extracting short version from long titles
            # e.g., "Maou Gakuin no Futekigousha: Shijou..." → "Maou Gakuin"
            short_versions = []
            for title in all_titles_sorted:
                # Extract before colon/subtitle
                if ':' in title:
                    short_versions.append(title.split(':')[0].strip())
                # Extract first keywords (first 2-3 words for romaji)
                if any(c.isalpha() and ord(c) < 128 for c in title):  # Latin alphabet
                    words = title.split()
                    if len(words) >= 2:
                        short_versions.append(' '.join(words[:3]))  # First 3 words
            
            # Combine: short titles first, then originals
            all_titles = short_versions + all_titles_sorted
            
            # Remove duplicates while preserving order
            seen = set()
            all_titles = [t for t in all_titles if t and t not in seen and not seen.add(t)]
            
            logger.info(f"Prioritized titles (short first): {all_titles[:5]}...")  # Show first 5
        else:
            # Fallback to TMDB if AniList fails
            all_titles = tmdb_metadata.get('all_titles', [tmdb_title])
            logger.warning(f"AniList failed, using TMDB titles: {all_titles}")
        
        logger.info(f"Searching for S{season:02d}E{episode:02d} with {len(all_titles)} title variations")
        
        # Parallel scraping for SPEED!
        # Using ONLY fast & reliable providers: Sokuja + Torrents
        streams = []
        
        # Try each title variation
        for title in all_titles:
            if not title:
                continue
                
            logger.info(f"Trying title: {title}")
            
            # Scrape FAST providers in PARALLEL
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = {
                    executor.submit(get_sokuja_streams, title, season, episode): "Sokuja",
                    executor.submit(get_nyaa_streams, title, season, episode): "Torrents"
                }
                
                # Process results as they complete
                try:
                    for future in as_completed(futures, timeout=10):  # 10s sufficient for 2 providers
                        provider = futures[future]
                        try:
                            results = future.result(timeout=5)  # 5s per provider
                            if results:
                                logger.info(f"  └─ {provider}: {len(results)} streams")
                                streams.extend(results)
                        except Exception as e:
                            logger.warning(f"  └─ {provider}: error - {type(e).__name__}")
                except TimeoutError:
                    logger.warning(f"  └─ Timeout, using partial results ({len(streams)} streams)")
            
            # If we found streams with this title, stop trying other titles
            if streams:
                logger.info(f"Found {len(streams)} streams with title: {title}")
                break
        
        # Remove duplicates (same server/resolution combo)
        seen = set()
        unique_streams = []
        for stream in streams:
            key = stream.get('name', '')
            if key not in seen:
                seen.add(key)
                unique_streams.append(stream)
        
        # Prioritize reliable sources (direct streams first, embeds last)
        def stream_priority(stream):
            name = stream.get('name', '').lower()
            description = stream.get('description', '').lower()
            
            # Priority 1: Torrents (most reliable)
            if 'torrent' in name or 'infoHash' in stream:
                return 0
            
            # Priority 2: Direct streams (Sokuja, stream_ready)
            if 'sokuja' in name or stream.get('url'):
                return 1
            
            # Priority 3: External/Browser (Mega, Dood, etc - less reliable)
            if stream.get('externalUrl'):
                return 2
            
            return 3  # Unknown
        
        unique_streams.sort(key=stream_priority)
        
        logger.info(f"Total unique streams: {len(unique_streams)} (sorted by reliability)")
        return jsonify({"streams": unique_streams})
        
    except Exception as e:
        logger.error(f"Stream error: {e}", exc_info=True)
        return jsonify({"streams": []})

@lru_cache(maxsize=100)
def get_samehadaku_streams(title, season, episode):
    """Get streams from Samehadaku"""
    streams = []
    try:
        # Search anime
        results = samehadaku_scraper.search_anime(title)
        if not results:
            return streams
        
        # Match season/episode
        anime = match_season(results, season)
        if not anime:
            return streams
        
        # Get episodes
        episodes = samehadaku_scraper.get_anime_episodes(anime['url'])
        ep_data = match_episode(episodes, episode)
        if not ep_data:
            return streams
        
        # Get video links
        links = samehadaku_scraper.get_all_video_links(ep_data['url'])
        
        for link in links:
            # ONLY direct playable streams (no browser embeds)
            if not link.get('stream_ready'):
                continue
            
            server = link.get('server', 'Unknown')
            resolution = link.get('resolution', 'Unknown')
            url = link['url']
            
            # Resolve special AJAX URLs if needed (similar to Otakudesu)
            # Samehadaku might have ajax: prefix URLs
            if url.startswith('ajax:'):
                try:
                    from scrapers.samehadaku_scraper import get_streaming_url
                    resolved_url = get_streaming_url(url)
                    if not resolved_url:
                        continue
                    url = resolved_url
                except Exception as e:
                    logger.warning(f"Failed to resolve Samehadaku URL: {e}")
                    continue
            
            stream = {
                "name": f"🟢 Samehadaku - {server} {resolution}",
                "url": url,
                "description": f"Direct stream | {link.get('type', 'stream')}"
            }
            streams.append(stream)
    
    except Exception as e:
        logger.error(f"Samehadaku error: {e}")
    
    return streams

@lru_cache(maxsize=100)
def get_otakudesu_streams(title, season, episode):
    """Get streams from Otakudesu"""
    streams = []
    try:
        results = otakudesu_scraper.search_anime(title)
        if not results:
            return streams
        
        anime = match_season(results, season)
        if not anime:
            return streams
        
        episodes = otakudesu_scraper.get_anime_episodes(anime['url'])
        ep_data = match_episode(episodes, episode)
        if not ep_data:
            return streams
        
        links = otakudesu_scraper.get_video_links(ep_data['url'])
        
        for link in links:
            # ONLY direct playable streams (no browser embeds)
            if not link.get('stream_ready'):
                continue
            
            server = link.get('server', 'Unknown')
            resolution = link.get('resolution', 'Unknown')
            url = link['url']
            
            # Resolve special otakudesu URLs (AJAX)
            if url.startswith('otakudesu:'):
                try:
                    resolved_url = otakudesu_scraper.resolve_otakudesu_url(url)
                    if not resolved_url:
                        continue  # Skip if resolution failed
                    url = resolved_url
                except Exception as e:
                    logger.warning(f"Failed to resolve Otakudesu URL: {e}")
                    continue
            
            stream = {
                "name": f"🔵 Otakudesu - {server} {resolution}",
                "url": url,
                "description": f"Direct stream | {server}"
            }
            streams.append(stream)
    
    except Exception as e:
        logger.error(f"Otakudesu error: {e}")
    
    return streams

@lru_cache(maxsize=100)
def get_sokuja_streams(title, season, episode):
    """Get streams from Sokuja"""
    streams = []
    try:
        results = sokuja_scraper.search_anime(title)
        if not results:
            return streams
        
        anime = match_season(results, season)
        if not anime:
            return streams
        
        episodes = sokuja_scraper.get_anime_episodes(anime['url'])
        ep_data = match_episode(episodes, episode)
        if not ep_data:
            return streams
        
        links = sokuja_scraper.get_video_links(ep_data['url'])
        
        for link in links:
            stream = {
                "name": f"🟡 Sokuja - {link.get('resolution', '720p')}",
                "url": link['url'],
                "description": "Provider: Sokuja | Fast streaming"
            }
            streams.append(stream)
    
    except Exception as e:
        logger.error(f"Sokuja error: {e}")
    
    return streams

@lru_cache(maxsize=100)
def get_nyaa_streams(title, season, episode):
    """Get torrents from Nyaa.si + AnimeTosho"""
    streams = []
    try:
        # Search with episode number
        query = f"{title} {episode:02d}"
        
        # Get from both sources
        nyaa_results = nyaa_scraper.search_anime(query)
        animetosho_results = animetosho_scraper.search_anime(query, limit=10)
        
        # Combine and dedupe by info_hash
        all_torrents = {}
        for torrent in nyaa_results + animetosho_results:
            info_hash = torrent.get('info_hash')
            if info_hash and torrent.get('seeders', 0) > 0:
                # Keep the one with more seeders if duplicate
                if info_hash not in all_torrents or torrent['seeders'] > all_torrents[info_hash]['seeders']:
                    all_torrents[info_hash] = torrent
        
        # Sort by seeders
        sorted_torrents = sorted(all_torrents.values(), key=lambda x: x.get('seeders', 0), reverse=True)
        
        # Take top 15 (increased from 5)
        for torrent in sorted_torrents[:15]:
            # Extract info_hash from magnet link
            magnet = torrent.get('magnet', '')
            info_hash = extract_info_hash(magnet)
            
            if not info_hash:
                continue  # Skip if no valid hash
            
            source_icon = "🎲" if torrent.get('source') == 'nyaa' else "🌸"  # Nyaa vs AnimeTosho
            
            stream = {
                "name": f"{source_icon} Torrent - {torrent.get('resolution', '1080p')} [{torrent.get('release_group', 'Unknown')}]",
                "infoHash": info_hash,
                "description": f"👥 {torrent.get('seeders', 0)} seeders | 💾 {torrent.get('size', 'Unknown')} | {torrent.get('source', 'unknown').title()}",
            }
            
            streams.append(stream)
    
    except Exception as e:
        logger.error(f"Torrent search error: {e}")
    
    return streams

def extract_info_hash(magnet_url):
    """Extract info hash from magnet URI"""
    if not magnet_url:
        return None
    
    # Magnet format: magnet:?xt=urn:btih:HASH&...
    match = re.search(r'btih:([a-fA-F0-9]{40})', magnet_url)
    if match:
        return match.group(1).lower()
    
    return None

def match_season(results, season):
    """Match anime by season number"""
    if season == 1:
        # First season usually doesn't have "Season" in title
        for result in results:
            title_lower = result['title'].lower()
            if 'season 2' not in title_lower and 's2' not in title_lower:
                return result
    else:
        # Look for "Season X" or "SX" in title
        patterns = [
            f"season {season}",
            f"s{season}",
            f"part {season}",
            f"{season}st" if season == 1 else f"{season}nd" if season == 2 else f"{season}rd" if season == 3 else f"{season}th"
        ]
        for result in results:
            title_lower = result['title'].lower()
            if any(p in title_lower for p in patterns):
                return result
    
    # Fallback: return first result
    return results[0] if results else None

def match_episode(episodes, episode_number):
    """Match episode by number"""
    for ep in episodes:
        ep_num = ep.get('episode_number', '?')
        # Try to convert to int
        try:
            if int(ep_num) == episode_number:
                return ep
        except:
            # Try regex match from title
            match = re.search(r'episode\s+(\d+)', ep.get('title', '').lower())
            if match and int(match.group(1)) == episode_number:
                return ep
    
    return None

if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=7000, debug=True)
