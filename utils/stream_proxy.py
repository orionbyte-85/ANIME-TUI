import http.server
import socketserver
import threading
import urllib.parse
import requests
import json
import base64
import socket

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse URL
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        
        if 'data' not in query:
            self.send_error(400, "Missing data param")
            return
            
        try:
            # Decode data
            data_str = base64.b64decode(query['data'][0]).decode('utf-8')
            data = json.loads(data_str)
            target_url = data['url']
            custom_headers = data.get('headers', {}) # Renamed to avoid conflict with request headers
            
            # Create request to actual URL
            # Filter headers to avoid issues
            request_headers = {}
            for key, value in self.headers.items():
                # Skip hop-by-hop headers and headers that might cause issues with requests library or target server
                if key.lower() not in ['host', 'connection', 'upgrade-insecure-requests', 'transfer-encoding', 'keep-alive', 'proxy-authenticate', 'proxy-authorization', 'te', 'trailers', 'upgrade']:
                    request_headers[key] = value
            
            # Add custom headers passed in query param
            if custom_headers:
                request_headers.update(custom_headers)
            
            # Log request
            print(f"[Proxy] Fetching: {target_url[:60]}...")
            
            # Stream the response
            with requests.get(target_url, headers=request_headers, stream=True, timeout=30, allow_redirects=True) as r:
                # Send response headers
                self.send_response(r.status_code)
                
                # Add CORS headers
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', '*')
                
                # Forward content headers
                for key, value in r.headers.items():
                    # Only forward specific content-related headers to avoid issues and simplify
                    if key.lower() in ['content-type', 'content-length', 'accept-ranges', 'content-range', 'last-modified', 'etag']:
                        self.send_header(key, value)
                
                self.end_headers()
                
                # Pipe data (Forwarding)
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        self.wfile.write(chunk)
                        
        except Exception as e:
            print(f"[Proxy] Error: {e}")
            # If headers not sent, send error
            self.send_error(500, str(e))
            
    def do_OPTIONS(self):
        """Handle OPTIONS request for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

def start_server(port=0):
    """Start the proxy server in a background thread. Returns (server, port)."""
    server = ThreadedHTTPServer(('127.0.0.1', port), ProxyHandler)
    actual_port = server.server_address[1]
    
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    
    return server, actual_port

def create_proxy_url(port, target_url, headers=None):
    """Helper to create a localhost URL for the proxy"""
    data = {
        'url': target_url,
        'headers': headers or {}
    }
    data_b64 = base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')
    return f"http://127.0.0.1:{port}/stream?data={urllib.parse.quote(data_b64)}"

if __name__ == "__main__":
    # Test run
    server, port = start_server(8080)
    print(f"Proxy running on port {port}")
    import time
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        server.shutdown()
