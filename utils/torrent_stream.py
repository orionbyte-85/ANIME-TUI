#!/usr/bin/env python3
"""
Torrent Streaming Helper
Handles torrent streaming via webtorrent-cli or peerflix
"""

import subprocess
import re
import os
import time

def check_dependencies():
    """
    Check if webtorrent-cli or peerflix is installed
    Returns: (tool_name, tool_path) or (None, None)
    """
    # Try webtorrent first (recommended)
    try:
        result = subprocess.run(['which', 'webtorrent'], capture_output=True, text=True)
        if result.returncode == 0:
            return ('webtorrent', result.stdout.strip())
    except:
        pass
    
    # Try peerflix as fallback
    try:
        result = subprocess.run(['which', 'peerflix'], capture_output=True, text=True)
        if result.returncode == 0:
            return ('peerflix', result.stdout.strip())
    except:
        pass
    
    return (None, None)

def stream_torrent(magnet_link, subtitle_path=None):
    """
    Stream torrent and return localhost URL for MPV
    
    Args:
        magnet_link: Magnet link or torrent URL
        subtitle_path: Optional path to subtitle file
    
    Returns:
        dict with 'url' and optionally 'subtitle_path', or None if failed
    """
    tool, tool_path = check_dependencies()
    
    if not tool:
        print("❌ Error: No torrent streaming tool found!")
        print("💡 Please install one of:")
        print("   npm install -g webtorrent-cli")
        print("   npm install -g peerflix")
        return None
    
    print(f"✓ Found {tool}: {tool_path}")
    
    try:
        if tool == 'webtorrent':
            return stream_with_webtorrent(magnet_link, subtitle_path)
        elif tool == 'peerflix':
            return stream_with_peerflix(magnet_link, subtitle_path)
    except Exception as e:
        print(f"❌ Streaming error: {e}")
        return None

def stream_with_webtorrent(magnet_link, subtitle_path=None):
    """Stream using webtorrent-cli"""
    print("🔄 Starting webtorrent stream...")
    print(f"🔗 Magnet: {magnet_link[:60]}...")
    
    # Start webtorrent in background
    # Format: webtorrent download "magnet:..." --select 0 --stdout | mpv -
    # But we want to get the HTTP URL instead
    
    # webtorrent has a --port option to specify HTTP server port
    port = 8888  # Default port
    
    cmd = ['webtorrent', 'download', magnet_link, '--port', str(port), '--select', '0']
    
    # Start process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start and extract URL
    # webtorrent outputs: "Server running at: http://localhost:8888/"
    timeout = 30
    start_time = time.time()
    server_url = None
    
    while time.time() - start_time < timeout:
        line = process.stderr.readline()
        if line:
            print(f"  [webtorrent] {line.strip()}")
            
            # Look for server URL
            match = re.search(r'Server running at:\s+(http://[^\s]+)', line)
            if match:
                server_url = match.group(1)
                break
        
        # Check if process died
        if process.poll() is not None:
            print("❌ Webtorrent process died")
            return None
        
        time.sleep(0.5)
    
    if not server_url:
        print("❌ Could not get server URL")
        process.kill()
        return None
    
    print(f"✓ Stream ready at: {server_url}")
    
    result = {'url': server_url, 'process': process}
    
    if subtitle_path:
        result['subtitle_path'] = subtitle_path
    
    return result

def stream_with_peerflix(magnet_link, subtitle_path=None):
    """Stream using peerflix"""
    print("🔄 Starting peerflix stream...")
    print(f"🔗 Magnet: {magnet_link[:60]}...")
    
    # peerflix automatically starts HTTP server
    # Format: peerflix "magnet:..." --port 8888
    port = 8888
    
    cmd = ['peerflix', magnet_link, '--port', str(port)]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    timeout = 30
    start_time = time.time()
    server_url = None
    
    while time.time() - start_time < timeout:
        line = process.stdout.readline()
        if line:
            print(f"  [peerflix] {line.strip()}")
            
            # Look for "server running on port" or similar
            if 'http://' in line.lower():
                match = re.search(r'(http://[^\s]+)', line)
                if match:
                    server_url = match.group(1)
                    break
            
            # Peerflix format: "server is running on port 8888"
            if 'port' in line.lower() and str(port) in line:
                server_url = f"http://localhost:{port}"
                break
        
        if process.poll() is not None:
            print("❌ Peerflix process died")
            return None
        
        time.sleep(0.5)
    
    if not server_url:
        # Default fallback
        server_url = f"http://localhost:{port}"
        print(f"⚠️  Assuming default URL: {server_url}")
    
    print(f"✓ Stream ready at: {server_url}")
    
    result = {'url': server_url, 'process': process}
    
    if subtitle_path:
        result['subtitle_path'] = subtitle_path
    
    return result

def download_subtitle(url, dest_path):
    """
    Download subtitle file from URL
    
    Args:
        url: Subtitle download URL
        dest_path: Destination file path
    
    Returns:
        True if successful, False otherwise
    """
    import requests
    
    try:
        print(f"📥 Downloading subtitle...")
        print(f"🔗 URL: {url[:60]}...")
        
        resp = requests.get(url, timeout=30)
        
        if resp.status_code == 200:
            with open(dest_path, 'wb') as f:
                f.write(resp.content)
            
            print(f"✓ Subtitle saved: {dest_path}")
            return True
        else:
            print(f"❌ Download failed: {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading subtitle: {e}")
        return False

if __name__ == "__main__":
    # Test dependency check
    tool, path = check_dependencies()
    if tool:
        print(f"✓ Found {tool}: {path}")
    else:
        print("❌ No torrent streaming tool found")
