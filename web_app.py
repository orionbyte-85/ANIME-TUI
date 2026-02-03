#!/usr/bin/env python3
"""
Anime Streaming Web Application
Flask-based web interface for anime streaming
"""

from flask import Flask, render_template, jsonify, request, Response
from flask_cors import CORS
import sys

# Import scrapers
from scrapers import samehadaku_scraper, otakudesu_scraper, sokuja_scraper, nyaa_scraper
from utils import stream_proxy

app = Flask(__name__)
CORS(app)  # Enable CORS for API

# Provider configuration
PROVIDERS = {
    'samehadaku': {
        'name': 'Samehadaku',
        'icon': '🎬',
        'module': samehadaku_scraper
    },
    'otakudesu': {
        'name': 'Otakudesu',
        'icon': '🔵',
        'module': otakudesu_scraper
    },
    'sokuja': {
        'name': 'Sokuja',
        'icon': '🟡',
        'module': sokuja_scraper
    },
    'torrent': {
        'name': 'Torrent (Nyaa)',
        'icon': '🎲',
        'module': nyaa_scraper
    }
}

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/providers')
def get_providers():
    """Get list of available providers"""
    providers = [
        {
            'id': key,
            'name': val['name'],
            'icon': val['icon']
        }
        for key, val in PROVIDERS.items()
    ]
    return jsonify(providers)

@app.route('/api/search')
def search_anime():
    """Search anime across provider"""
    provider_id = request.args.get('provider')
    query = request.args.get('query')
    
    if not provider_id or not query:
        return jsonify({'error': 'Missing provider or query'}), 400
    
    if provider_id not in PROVIDERS:
        return jsonify({'error': 'Invalid provider'}), 400
    
    try:
        provider = PROVIDERS[provider_id]
        results = provider['module'].search_anime(query)
        
        return jsonify({
            'provider': provider_id,
            'query': query,
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/episodes')
def get_episodes():
    """Get episodes for an anime"""
    provider_id = request.args.get('provider')
    url = request.args.get('url')
    
    if not provider_id or not url:
        return jsonify({'error': 'Missing provider or url'}), 400
    
    if provider_id not in PROVIDERS:
        return jsonify({'error': 'Invalid provider'}), 400
    
    try:
        provider = PROVIDERS[provider_id]
        episodes = provider['module'].get_anime_episodes(url)
        
        return jsonify({
            'provider': provider_id,
            'episodes': episodes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/servers')
def get_servers():
    """Get video servers for an episode (organized by resolution)"""
    provider_id = request.args.get('provider')
    url = request.args.get('url')
    
    if not provider_id or not url:
        return jsonify({'error': 'Missing provider or url'}), 400
    
    if provider_id not in PROVIDERS:
        return jsonify({'error': 'Invalid provider'}), 400
    
    try:
        provider = PROVIDERS[provider_id]
        
        # Get video links based on provider
        if provider_id == 'samehadaku':
            servers = samehadaku_scraper.get_all_video_links(url)
        elif provider_id == 'otakudesu':
            servers = otakudesu_scraper.get_video_links(url)
        elif provider_id == 'sokuja':
            servers = sokuja_scraper.get_video_links(url)
        else:
            servers = []
        
        # Organize servers by resolution
        organized = {}
        for server in servers:
            resolution = server.get('resolution', 'Unknown').upper()
            
            if resolution not in organized:
                organized[resolution] = {
                    'streaming': [],
                    'download': []
                }
            
            # Categorize by type
            server_type = server.get('type', 'download')
            if server_type == 'stream':
                organized[resolution]['streaming'].append(server)
            else:
                organized[resolution]['download'].append(server)
        
        # Sort resolutions (higher first)
        resolution_order = ['1080P', '720P', '480P', '360P', 'UNKNOWN']
        sorted_resolutions = sorted(
            organized.keys(),
            key=lambda x: resolution_order.index(x) if x in resolution_order else 999
        )
        
        return jsonify({
            'provider': provider_id,
            'servers': servers,  # Original flat list
            'organized': {res: organized[res] for res in sorted_resolutions}  # Organized by resolution
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stream')
def proxy_stream():
    """Proxy video stream (for Google Video URLs)"""
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({'error': 'Missing url'}), 400
    
    try:
        # Start proxy if not already running
        if not hasattr(app, 'proxy_port'):
            app.proxy_server, app.proxy_port = stream_proxy.start_server(0)
        
        # Create proxy URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.blogger.com/'
        }
        
        proxy_url = stream_proxy.create_proxy_url(app.proxy_port, video_url, headers)
        
        return jsonify({'proxy_url': proxy_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/resolve')
def resolve_url():
    """Resolve embed URL to direct stream URL"""
    video_url = request.args.get('url')
    server_name = request.args.get('server', '')
    
    if not video_url:
        return jsonify({'error': 'Missing url'}), 400
    
    try:
        from utils.embed_resolvers import resolve_embed_url
        from scrapers import samehadaku_scraper, otakudesu_scraper
        
        direct_url = None
        
        # Handle special URLs
        if video_url.startswith('ajax:'):
            # Samehadaku AJAX URL
            result = samehadaku_scraper.get_streaming_url(video_url)
            if isinstance(result, dict):
                direct_url = result['url']
            else:
                direct_url = result
        
        elif video_url.startswith('otakudesu:'):
            # Otakudesu special URL
            result = otakudesu_scraper.resolve_otakudesu_url(video_url)
            if isinstance(result, dict):
                direct_url = result['url']
            else:
                direct_url = result
        
        elif 'desustream.com/safelink' in video_url:
            # Unwrap safelink
            from utils.embed_resolvers import unwrap_safelink
            direct_url = unwrap_safelink(video_url)
        
        else:
            # Try embed resolver
            direct_url = resolve_embed_url(video_url, server_name)
        
        if not direct_url:
            return jsonify({'error': 'Could not resolve URL'}), 400
        
        # Check if resolved URL needs proxy (Google Video)
        if 'googlevideo.com' in direct_url or 'blogger.com' in direct_url:
            if not hasattr(app, 'proxy_port'):
                app.proxy_server, app.proxy_port = stream_proxy.start_server(0)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.blogger.com/'
            }
            
            proxy_url = stream_proxy.create_proxy_url(app.proxy_port, direct_url, headers)
            
            return jsonify({
                'resolved_url': proxy_url,
                'needs_proxy': True
            })
        
        return jsonify({
            'resolved_url': direct_url,
            'needs_proxy': False
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🌐 Starting Anime Streaming Web Server...")
    print("📺 Open http://localhost:5000 in your browser")
    app.run(host='0.0.0.0', port=5000, debug=True)
