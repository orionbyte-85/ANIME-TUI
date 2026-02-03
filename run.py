#!/usr/bin/env python3
"""
Unified launcher for Anime Streaming App
Supports both TUI and Web modes
"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='Anime Streaming Application')
    parser.add_argument('--mode', choices=['tui', 'web'], default='tui',
                       help='Interface mode: tui (terminal) or web (browser)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port for web server (default: 5000)')
    
    args = parser.parse_args()
    
    if args.mode == 'web':
        try:
            import flask
        except ImportError:
            print("❌ Flask not installed!")
            print("💡 Install: pip install flask flask-cors --break-system-packages")
            print("💡 Or use: pacman -S python-flask")
            sys.exit(1)
        
        print(f"🌐 Starting Web Server on port {args.port}...")
        from web_app import app
        app.run(host='0.0.0.0', port=args.port, debug=True)
    else:
        print("🎬 Starting TUI Mode...")
        import curses
        from anime_tui import AnimeTUI
        curses.wrapper(lambda stdscr: AnimeTUI(stdscr).run())

if __name__ == '__main__':
    main()
