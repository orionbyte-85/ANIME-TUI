#!/usr/bin/env python3
"""
Samehadaku TUI - Terminal User Interface for browsing and watching anime
Multi-provider support: Samehadaku, Otakudesu, Sokuja
"""

import curses
import subprocess
import sys
import webbrowser

# Import all providers
from scrapers import samehadaku_scraper
from scrapers import otakudesu_scraper
from scrapers import sokuja_scraper
import logging
from utils import stream_proxy
from utils.database import db
from utils.config import config

# Setup logging
logging.basicConfig(filename='tui_debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class AnimeTUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_view = 'SEARCH'  # SEARCH, RESULTS, EPISODES, SERVER_SELECT
        self.search_results = []  # Multi-provider results
        self.episodes = []  # Episodes from selected anime
        self.available_links = []  # Server/quality options for selected episode
        self.selected_index = 0
        self.search_query = ""
        self.selected_anime = None  # Selected anime with provider info
        self.selected_episode = None  # Selected episode
        self.selected_provider = config.get('provider_default', None)  # Load from config
        self.status_message = "🔍 Tekan / untuk cari anime | ❌ q untuk keluar"
        
        # Config and preferences
        self.default_quality = config.get('kualitas_default', '720p')
        self.auto_play_next = config.get('auto_play_berikutnya', True)
        
        # Indonesian status messages
        self.STATUS_MSG = {
            'searching': 'Mencari anime...',
            'loading': 'Memuat episode...',
            'fetching_servers': 'Mengambil daftar server...',
            'playing': 'Memutar video...',
            'saved_history': '📺 Tersimpan di riwayat',
            'added_favorite': '⭐ Ditambahkan ke favorit!',
            'removed_favorite': '❌ Dihapus dari favorit!',
        }
        
        # Start local stream proxy
        try:
            self.proxy_server, self.proxy_port = stream_proxy.start_server(0) # 0 = random port
            logging.info(f"Local stream proxy started on port {self.proxy_port}")
        except Exception as e:
            logging.error(f"Failed to start proxy: {e}")
            self.proxy_server = None
            self.proxy_port = 0
        
        # Setup modern color scheme
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)      # Headers/Title
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)     # Selected item
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # Section headers
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Normal text
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)       # Error
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_GREEN)     # Highlight background
        curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)      # Info text
        curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # Provider badges
        
        # Hide cursor
        curses.curs_set(0)
    
    def draw_box(self, y, x, width, title=""):
        """Draw a box with optional title using Unicode characters"""
        try:
            # Top line with title
            if title:
                title_text = f" {title} "
                left_width = (width - len(title_text)) // 2
                right_width = width - len(title_text) - left_width
                self.stdscr.addstr(y, x, "┌" + "─" * left_width + title_text + "─" * right_width + "┐", curses.color_pair(3))
            else:
                self.stdscr.addstr(y, x, "┌" + "─" * width + "┐", curses.color_pair(3))
        except:
            pass
    
    def draw_section_header(self, y, x, text, width):
        """Draw a section header with separator"""
        try:
            self.stdscr.addstr(y, x, f"━━━ {text} ━━━".ljust(width), curses.color_pair(3) | curses.A_BOLD)
        except:
            pass
    
    def draw_footer(self, height, width, hints):
        """Draw navigation hints footer"""
        try:
            separator = "━" * width
            self.stdscr.addstr(height - 2, 0, separator, curses.color_pair(3))
            footer_text = "💡 " + " │ ".join(hints)
            self.stdscr.addstr(height - 1, 2, footer_text[:width-4], curses.color_pair(7))
        except:
            pass
        
    def run(self):
        """Main event loop"""
        while True:
            self.draw()
            key = self.stdscr.getch()
            
            if key == ord('q') or key == ord('Q'):
                return False # Changed from break to return False
            
            # Global shortcuts
            if key == ord('?'):
                self.previous_view = self.current_view
                self.current_view = 'HELP'
                # return True # Removed this as it would exit the loop
                continue # Continue to redraw with HELP view
                
            if self.current_view == 'HELP':
                # Any key to close help
                self.current_view = self.previous_view
                # return True # Removed this as it would exit the loop
                continue # Continue to redraw with previous view
                
            if key == ord('b') or key == ord('B'): # Kept 'B' for consistency
                self.handle_back()
            elif key == ord('/'):
                self.handle_search_input()
            elif self.current_view == 'PROVIDER_SELECT':
                # Main Menu options
                options = ['samehadaku', 'otakudesu', 'sokuja', 'torrent', 'HISTORY', 'FAVORITES']
                if key == curses.KEY_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                elif key == curses.KEY_DOWN:
                    self.selected_index = min(len(options) - 1, self.selected_index + 1)
                elif key == curses.KEY_ENTER or key in [10, 13]:
                    choice = options[self.selected_index]
                    if choice == 'HISTORY':
                        self.current_view = 'HISTORY'
                        # Load history
                        history = db.get_recent_history(20)
                        self.search_results = history # Reuse list
                        self.selected_index = 0
                        if not history:
                            self.status_message = "Belum ada riwayat."
                    elif choice == 'FAVORITES':
                        self.status_message = "Fitur Favorit akan segera hadir!"
                    else:
                        self.selected_provider = choice
                        self.current_view = 'SEARCH'
                        self.status_message = self.STATUS_MSG['searching']
                        
            elif self.current_view == 'HISTORY':
                if key == curses.KEY_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                elif key == curses.KEY_DOWN:
                    self.selected_index = min(len(self.search_results) - 1, self.selected_index + 1)
                elif key == curses.KEY_ENTER or key in [10, 13]:
                    if self.search_results:
                        item = self.search_results[self.selected_index]
                        # Resume watching logic
                        self.selected_anime = {
                            'title': item['anime_title'],
                            'url': item['anime_url'],
                            'source': 'history' # Or try to infer provider
                        }
                        # Need to fetch episodes to get the correct episode object/url
                        # But we might not know the provider easily if not stored.
                        # Let's assume we can try to detect or just use the stored info if we had provider.
                        # For now, let's try to find provider from url or default
                        
                        # Simple heuristic for provider based on URL
                        provider = 'otakudesu' # Default
                        if 'samehadaku' in item['anime_url']:
                            provider = 'samehadaku'
                        elif 'sokuja' in item['anime_url']:
                            provider = 'sokuja'
                        
                        self.selected_provider = provider
                        self.status_message = f"Memuat episode {item['episode_num']}..."
                        
                        # Go to episodes view first to load context
                        self.current_view = 'EPISODES'
                        self.stdscr.clear()
                        self.stdscr.addstr(0, 0, self.STATUS_MSG['loading'])
                        self.stdscr.refresh()
                        
                        # Fetch episodes
                        try:
                            if provider == 'samehadaku':
                                self.episodes = samehadaku_scraper.get_anime_episodes(item['anime_url'])
                            elif provider == 'otakudesu':
                                self.episodes = otakudesu_scraper.get_anime_episodes(item['anime_url'])
                            elif provider == 'sokuja':
                                self.episodes = sokuja_scraper.get_anime_episodes(item['anime_url'])
                            
                            # Find the target episode index
                            target_ep = item['episode_num']
                            for i, ep in enumerate(self.episodes):
                                if ep.get('episode_number') == target_ep: # Use .get for safety
                                    self.selected_index = i
                                    self.selected_episode = ep
                                    break
                            else:
                                self.selected_index = 0
                                
                        except Exception as e:
                            self.status_message = f"Error: {e}"
                            self.current_view = 'HISTORY'
            elif key == curses.KEY_UP:
                self.move_selection(-1)
            elif key == curses.KEY_DOWN:
                self.move_selection(1)
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                self.handle_enter()
            elif key == ord('b') or key == ord('B'):
                self.go_back()
    
    def draw(self):
        """Draw the current view"""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        
        # Header
        header = "🎬 ANIME STREAMING TUI (Multi-Provider) 🎬"
        self.stdscr.addstr(0, (width - len(header)) // 2, header, curses.A_BOLD)
        
        # Provider selection view (if applicable)
        if self.current_view == 'PROVIDER_SELECT':
            self.stdscr.addstr(3, 2, "📺 Select a provider:", curses.A_BOLD)
            
            # Assuming self.PROVIDERS is defined elsewhere, e.g., in __init__
            # For now, using a placeholder list based on draw_provider_select_view
            providers_list = [
                {'name': 'Sokuja', 'id': 'sokuja', 'desc': '480p, 720p'},
                {'name': 'Otakudesu', 'id': 'otakudesu', 'desc': '360p, 480p, 720p (35+ servers)'},
                {'name': 'Samehadaku', 'id': 'samehadaku', 'desc': '360p Blogspot'}
            ]
            
            for i, provider_info in enumerate(providers_list):
                y = 5 + i
                display_name = provider_info['name']
                if i == self.selected_index:
                    self.stdscr.addstr(y, 4, f"▶ {display_name}", curses.A_REVERSE)
                else:
                    self.stdscr.addstr(y, 4, f"  {display_name}")
            
            # Instructions
            self.stdscr.addstr(height - 2, 2, "↑↓ navigate | ⏎ select | q quit", curses.A_DIM)
        
        # Draw view-specific content
        elif self.current_view == 'SEARCH':
            self.draw_search_view(height, width)
        elif self.current_view == 'RESULTS':
            self.draw_results_view(height, width)
        elif self.current_view == 'EPISODES':
            self.draw_episodes_view(height, width)
        elif self.current_view == 'SERVER_SELECT':
            self.draw_server_select_view(height, width)
        elif self.current_view == 'HISTORY':
            self.draw_history_view(height, width)
        elif self.current_view == 'HELP':
            # Draw underlying view first
            if self.previous_view == 'PROVIDER_SELECT':
                self.draw_provider_select_view(height, width)
            elif self.previous_view == 'SEARCH':
                self.draw_search_view(height, width)
            elif self.previous_view == 'RESULTS':
                self.draw_results_view(height, width)
            elif self.previous_view == 'EPISODES':
                self.draw_episodes_view(height, width)
            elif self.previous_view == 'SERVER_SELECT':
                self.draw_server_select_view(height, width)
            elif self.previous_view == 'HISTORY':
                self.draw_history_view(height, width)
            
            # Draw help overlay
            self.draw_help_view(height, width)
        
        # Draw status bar at bottom
        self.stdscr.attron(curses.color_pair(3))
        status_y = height - 1
        self.stdscr.addstr(status_y, 0, self.status_message[:width-1])
        self.stdscr.attroff(curses.color_pair(3))
        
        self.stdscr.refresh()
    
    def draw_search_view(self, height, width):
        """Draw the search input view"""
        y = 3
        self.stdscr.attron(curses.color_pair(4))
        self.stdscr.addstr(y, 2, "🌟 Search anime across all providers")
        y += 2
        self.stdscr.addstr(y, 2, "Press '/' to start searching")
        y += 2
        if self.search_query:
            self.stdscr.addstr(y, 2, f"Last search: {self.search_query}")
            y += 1
            self.stdscr.addstr(y, 2, f"Found {len(self.search_results)} results")
        self.stdscr.attroff(curses.color_pair(4))
    
    def draw_results_view(self, height, width):
        """Draw search results from all providers"""
        y = 2
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(y, 2, f"🔍 Search Results: {self.search_query}")
        self.stdscr.attroff(curses.color_pair(1))
        y += 1
        
        # Show provider summary
        providers_count = {}
        for result in self.search_results:
            prov = result.get('provider', 'unknown')
            providers_count[prov] = providers_count.get(prov, 0) + 1
        
        summary_parts = []
        if 'samehadaku' in providers_count:
            summary_parts.append(f"🟢 [Samehadaku] {providers_count['samehadaku']}")
        if 'otakudesu' in providers_count:
            summary_parts.append(f"🔵 [Otakudesu] {providers_count['otakudesu']}")
        if 'sokuja' in providers_count:
            summary_parts.append(f"🟡 [Sokuja] {providers_count['sokuja']}")
        
        if summary_parts:
            self.stdscr.attron(curses.color_pair(4))
            summary = f"   Found: {' | '.join(summary_parts)} results"
            self.stdscr.addstr(y, 2, summary)
            self.stdscr.attroff(curses.color_pair(4))
        y += 2
        
        # Calculate viewable area
        max_items = height - 8
        start_idx = max(0, self.selected_index - max_items + 1)
        end_idx = min(len(self.search_results), start_idx + max_items)
        
        for i in range(start_idx, end_idx):
            if i >= len(self.search_results):
                break
                
            result = self.search_results[i]
            prefix = "▶ " if i == self.selected_index else "  "
            
            # Get provider badge and color
            provider = result.get('provider', '')
            if provider == 'samehadaku':
                provider_badge = "🟢"
                provider_name = "SMH"  # Short name
            elif provider == 'otakudesu':
                provider_badge = "🔵"
                provider_name = "OTK"
            elif provider == 'sokuja':
                provider_badge = "🟡"
                provider_name = "SKJ"
            else:
                provider_badge = "⚪"
                provider_name = "???"
            
            if i == self.selected_index:
                self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            else:
                self.stdscr.attron(curses.color_pair(4))
            
            # Format: [Badge] Title
            title = result['title']
            # Truncate title if too long
            max_title_len = width - 10
            if len(title) > max_title_len:
                title = title[:max_title_len-3] + "..."
            
            line = f"{prefix}{provider_badge} {title}"
            
            try:
                self.stdscr.addstr(y, 2, line)
            except:
                pass
            
            if i == self.selected_index:
                self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                self.stdscr.attroff(curses.color_pair(4))
            
            y += 1
    
    def draw_episodes_view(self, height, width):
        """Draw episode list from selected anime"""
        y = 2
        self.stdscr.attron(curses.color_pair(1))
        
        # Get provider badge
        provider = self.selected_provider if self.selected_provider else ''
        if provider == 'samehadaku':
            provider_badge = "🟢 Samehadaku"
        elif provider == 'otakudesu':
            provider_badge = "🔵 Otakudesu"
        elif provider == 'sokuja':
            provider_badge = "🟡 Sokuja"
        else:
            provider_badge = ""
        
        title = self.selected_anime['title'] if self.selected_anime else "Episodes"
        header = f"{provider_badge} | {title[:width-30]}" if provider_badge else title[:width-15]
        self.stdscr.addstr(y, 2, header)
        self.stdscr.attroff(curses.color_pair(1))
        y += 2
        
        # Calculate viewable area
        max_items = height - 6
        start_idx = max(0, self.selected_index - max_items + 1)
        end_idx = min(len(self.episodes), start_idx + max_items)
        
        for i in range(start_idx, end_idx):
            if i >= len(self.episodes):
                break
                
            episode = self.episodes[i]
            prefix = "▶ " if i == self.selected_index else "  "
            
            if i == self.selected_index:
                self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            else:
                self.stdscr.attron(curses.color_pair(4))
            
            line = f"{prefix}{episode['title']}"
            if len(line) > width - 4:
                line = line[:width-7] + "..."
            
            try:
                self.stdscr.addstr(y, 2, line)
            except:
                pass
            
            if i == self.selected_index:
                self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                self.stdscr.attroff(curses.color_pair(4))
            
            y += 1
    
    def draw_provider_select_view(self, height, width):
        y = 2
        
        # Title box
        self.draw_box(y, 2, width - 4, "🎬 ANIME STREAMING TUI v2.0")
        y += 2
        
        self.stdscr.attron(curses.color_pair(4))
        self.stdscr.addstr(y, 4, "📺 Pilih Provider:")
        self.stdscr.attroff(curses.color_pair(4))
        y += 2
        
        providers = [
            {'name': 'Sokuja',     'id': 'sokuja',     'icon': '🟡', 'desc': '480p-720p │ Fast streaming'},
            {'name': 'Otakudesu',  'id': 'otakudesu',  'icon': '🔵', 'desc': '360p-720p │ 35+ servers'},
            {'name': 'Samehadaku', 'id': 'samehadaku', 'icon': '🟢', 'desc': '360p-1080p │ Mega, Vidhide'},
            {'name': 'Torrent',    'id': 'torrent',    'icon': '🎲', 'desc': '720p-1080p │ Nyaa.si Seeders'}
        ]
        
        for i, provider in enumerate(providers):
            prefix = "▶ " if i == self.selected_index else "  "
            
            if i == self.selected_index:
                self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            else:
                self.stdscr.attron(curses.color_pair(4))
            
            line = f"{prefix}{provider['icon']} {provider['name']:<12} │ {provider['desc']}"
            try:
                self.stdscr.addstr(y, 4, line[:width-8])
            except:
                pass
            
            if i == self.selected_index:
                self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                self.stdscr.attroff(curses.color_pair(4))
            
            y += 1
        
        # Footer with hints
        self.draw_footer(height, width, ["↑↓ Navigate", "Enter Select", "q Quit", "? Help"])
    
    
    def draw_help_view(self, height, width):
        """Draw help popup"""
        # Calculate popup dimensions
        popup_h = 16
        popup_w = 50
        start_y = (height - popup_h) // 2
        start_x = (width - popup_w) // 2
        
        # Draw box
        for y in range(start_y, start_y + popup_h):
            self.stdscr.addstr(y, start_x, " " * popup_w, curses.color_pair(4) | curses.A_REVERSE)
        
        # Draw border
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(start_y, start_x, "╔" + "═" * (popup_w - 2) + "╗")
        for y in range(start_y + 1, start_y + popup_h - 1):
            self.stdscr.addstr(y, start_x, "║")
            self.stdscr.addstr(y, start_x + popup_w - 1, "║")
        self.stdscr.addstr(start_y + popup_h - 1, start_x, "╚" + "═" * (popup_w - 2) + "╝")
        
        # Title
        title = " BANTUAN KEYBOARD "
        self.stdscr.addstr(start_y, start_x + (popup_w - len(title)) // 2, title)
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        
        # Content
        shortcuts = [
            ("/", "Cari Anime"),
            ("↑/↓", "Navigasi Menu"),
            ("⏎", "Pilih / Putar"),
            ("b", "Kembali"),
            ("q", "Keluar Aplikasi"),
            ("?", "Tampilkan Bantuan ini"),
            ("h", "Riwayat Tontonan"),
            ("f", "Tambah ke Favorit (Segera)"),
            ("d", "Download Episode (Segera)")
        ]
        
        for i, (key, desc) in enumerate(shortcuts):
            row = start_y + 2 + i
            self.stdscr.addstr(row, start_x + 4, f"{key:<5}", curses.color_pair(2) | curses.A_BOLD)
            self.stdscr.addstr(row, start_x + 12, desc, curses.color_pair(4) | curses.A_REVERSE)
            
        # Footer
        footer = "Tekan sembarang tombol untuk tutup"
        self.stdscr.addstr(start_y + popup_h - 2, start_x + (popup_w - len(footer)) // 2, footer, curses.color_pair(3) | curses.A_REVERSE)

    def draw_history_view(self, height, width):
        """Draw watch history"""
        title = "📺 RIWAYAT TONTONAN"
        self.stdscr.addstr(0, 2, title, curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(1, 0, "─" * width, curses.color_pair(3))
        
        if not self.search_results:  # Reusing search_results list for history items
            self.stdscr.addstr(3, 2, "Belum ada riwayat tontonan.", curses.color_pair(4))
            return

        # Calculate visible range
        max_items = height - 5
        start_idx = max(0, self.selected_index - max_items + 1)
        end_idx = min(len(self.search_results), start_idx + max_items)
        
        for i in range(start_idx, end_idx):
            item = self.search_results[i]
            row = 3 + (i - start_idx)
            
            prefix = "👉 " if i == self.selected_index else "   "
            style = curses.color_pair(2) if i == self.selected_index else curses.color_pair(4)
            
            # Format: Anime Title - Episode X (Time)
            # Parse timestamp if needed or just show relative time
            date_str = item.get('last_watched', '')
            try:
                # Simple parsing or just display
                display_date = date_str.split('.')[0] # Remove microseconds
            except:
                display_date = date_str
                
            label = f"{item['anime_title']} - Episode {item['episode_num']}"
            meta = f" [{display_date}]"
            
            # Truncate if too long
            max_len = width - len(meta) - 10
            if len(label) > max_len:
                label = label[:max_len-3] + "..."
                
            self.stdscr.addstr(row, 2, f"{prefix}{label}{meta}", style)
            
        self.draw_status_bar(height, width)

    def draw_server_select_view(self, height, width):
        """Draw server/quality selection with organized sections"""
        y = 2
        self.stdscr.attron(curses.color_pair(1))
        
        # Get provider badge
        provider = self.selected_provider if self.selected_provider else ''
        if provider == 'samehadaku':
            provider_badge = "🟢"
        elif provider == 'otakudesu':
            provider_badge = "🔵"
        elif provider == 'sokuja':
            provider_badge = "🟡"
        else:
            provider_badge = ""
        
        ep_title = self.selected_episode['title'][:width-50] if self.selected_episode else "Episode"
        title = f"{provider_badge} {provider.upper()} | {ep_title}" if provider else f"Select Server: {ep_title}"
        self.stdscr.addstr(y, 2, title)
        self.stdscr.attroff(curses.color_pair(1))
        y += 2
        
        if not self.available_links:
            self.stdscr.attron(curses.color_pair(5))
            self.stdscr.addstr(y, 2, "❌ No servers found for this episode.")
            self.stdscr.attroff(curses.color_pair(5))
            y += 2
            self.stdscr.attron(curses.color_pair(4))
            self.stdscr.addstr(y, 2, "Press 'b' to go back and try another provider")
            self.stdscr.attroff(curses.color_pair(4))
            return
        
        # Count server types
        mpv_count = sum(1 for link in self.available_links if link.get('stream_ready', False))
        browser_count = sum(1 for link in self.available_links if link.get('type') == 'browser_embed')
        download_count = len(self.available_links) - mpv_count - browser_count
        
        # Show summary
        self.stdscr.attron(curses.color_pair(4))
        summary = f"🎬 {mpv_count} MPV | 🌐 {browser_count} Browser | 💾 {download_count} Download"
        self.stdscr.addstr(y, 2, summary)
        self.stdscr.attroff(curses.color_pair(4))
        y += 2
        
        # Calculate viewable area
        max_items = height - 10
        start_idx = max(0, self.selected_index - max_items + 1)
        end_idx = min(len(self.available_links), start_idx + max_items)
        
        # Track section headers
        last_type = None
        
        for i in range(start_idx, end_idx):
            if i >= len(self.available_links):
                break
            
            link = self.available_links[i]
            link_type = link.get('type', 'download')
            
            # Add section header when type changes
            if last_type != link_type:
                if y < height - 3:
                    self.stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
                    if link_type == 'stream':
                        header = "━━━ 🎬 MPV STREAMING ━━━"
                    elif link_type == 'browser_embed':
                        header = "━━━ 🌐 BROWSER EMBED ━━━"
                    else:
                        header = "━━━ 💾 DOWNLOAD ━━━"
                    self.stdscr.addstr(y, 2, header)
                    self.stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
                    y += 1
                last_type = link_type
            
            prefix = "▶ " if i == self.selected_index else "  "
            
            if i == self.selected_index:
                self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            else:
                self.stdscr.attron(curses.color_pair(4))
            
            line = f"{prefix}[{link.get('resolution', 'Unknown'):>6}] {link['server']}"
            if len(line) > width - 4:
                line = line[:width-7] + "..."
            
            try:
                self.stdscr.addstr(y, 2, line)
            except:
                pass
            
            if i == self.selected_index:
                self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                self.stdscr.attroff(curses.color_pair(4))
            
            y += 1
    
    def handle_search_input(self):
        """Handle search input - searches all providers"""
        curses.curs_set(1)
        curses.echo()
        
        height, width = self.stdscr.getmaxyx()
        
        self.stdscr.clear()
        self.stdscr.addstr(height // 2, 2, "Search anime: ")
        self.stdscr.refresh()
        
        try:
            query = self.stdscr.getstr(height // 2, 16, 50).decode('utf-8').strip()
        except:
            query = ""
        
        curses.noecho()
        curses.curs_set(0)
        
        if query:
            self.search_query = query
            self.status_message = f"🔍 Searching all providers for '{query}'..."
            self.stdscr.refresh()
            
            # Search all providers
            all_results = []
            
            # Search Samehadaku
            try:
                results = samehadaku_scraper.search_anime(query)
                for r in results:
                    all_results.append({
                        'title': r['title'],
                        'url': r['url'],
                        'provider': 'samehadaku',
                        'provider_display': 'Samehadaku'
                    })
            except Exception as e:
                print(f"Samehadaku search error: {e}")
            
            # Search Otakudesu
            try:
                results = otakudesu_scraper.search_anime(query)
                for r in results:
                    all_results.append({
                        'title': r['title'],
                        'url': r['url'],
                        'provider': 'otakudesu',
                        'provider_display': 'Otakudesu'
                    })
            except Exception as e:
                print(f"Otakudesu search error: {e}")
            
            # Search Sokuja
            try:
                results = sokuja_scraper.search_anime(query)
                for r in results:
                    all_results.append({
                        'title': r['title'],
                        'url': r['url'],
                        'provider': 'sokuja',
                        'provider_display': 'Sokuja'
                    })
            except Exception as e:
                print(f"Sokuja search error: {e}")
            
            self.search_results = all_results
            self.selected_index = 0
            
        if self.selected_provider == 'torrent':
            from scrapers import nyaa_scraper
            self.search_results = [
                {
                    'title': f"[Nyaa] {result['title']}",
                    'url': result['magnet'],
                    'thumbnail': '',
                    'source': 'torrent',
                    'metadata': result  # Store full torrent metadata
                }
                for result in nyaa_scraper.search_anime(query)
            ]
        
        if self.search_results:
            self.current_view = 'RESULTS'
            self.status_message = f"✓ Found {len(self.search_results)} results | ↑↓ navigate | ⏎ select | b back"
        else:
                self.status_message = f"❌ No results for '{query}' | Press / to search again"
    
    def move_selection(self, delta):
        """Move selection up or down"""
        if self.current_view == 'RESULTS' and self.search_results:
            self.selected_index = (self.selected_index + delta) % len(self.search_results)
        elif self.current_view == 'EPISODES' and self.episodes:
            self.selected_index = (self.selected_index + delta) % len(self.episodes)
        elif self.current_view == 'SERVER_SELECT' and self.available_links:
            self.selected_index = (self.selected_index + delta) % len(self.available_links)
    
    def handle_enter(self):
        """Handle Enter key press"""
        # Provider selection
        if self.current_view == 'PROVIDER_SELECT':
            _, provider_key = self.PROVIDERS[self.selected_index]
            self.selected_provider = provider_key
            self.current_view = 'SEARCH'
            self.selected_index = 0
            self.status_message = f"✓ Selected {self.PROVIDERS[self.selected_index][0]} | Press / to search"
            return
        
        # Search results selection
        if self.current_view == 'RESULTS' and self.search_results:
            # Selected an anime from provider
            self.selected_anime = self.search_results[self.selected_index]
            self.selected_provider = self.selected_anime.get('provider', 'samehadaku')  # Default to samehadaku if not set
            
            provider_display = self.selected_anime.get('provider_display', '🟢 Samehadaku')
            self.status_message = f"📺 Loading episodes from {provider_display}..."
            self.stdscr.refresh()
            
            # Get episodes from provider
            try:
                if self.selected_provider == 'samehadaku':
                    self.episodes = samehadaku_scraper.get_anime_episodes(self.selected_anime['url'])
                elif self.selected_provider == 'otakudesu':
                    self.episodes = otakudesu_scraper.get_anime_episodes(self.selected_anime['url'])
                elif self.selected_provider == 'sokuja':
                    self.episodes = sokuja_scraper.get_anime_episodes(self.selected_anime['url'])
                else:
                    self.episodes = []
            except Exception as e:
                print(f"Error getting episodes: {e}")
                self.episodes = []
            
            self.selected_index = 0
            
            if self.episodes:
                self.current_view = 'EPISODES'
                self.status_message = f"✓ {len(self.episodes)} episodes | ↑↓ navigate | ⏎ select | b back"
            else:
                self.status_message = "❌ No episodes found | Press b to go back"
                
        # Episode selection
        if self.current_view == 'EPISODES' and self.episodes:
            self.selected_episode = self.episodes[self.selected_index]
            self.status_message = f"🔄 Loading servers from {self.selected_provider.upper()}..."
            self.stdscr.refresh()
            
            # Get video links from provider
            try:
                logging.info(f"Fetching links for {self.selected_provider} - {self.selected_episode['url']}")
                
                if self.selected_provider == 'samehadaku':
                        links = samehadaku_scraper.get_all_video_links(self.selected_episode['url'])
                elif self.selected_provider == 'otakudesu':
                    links = otakudesu_scraper.get_video_links(self.selected_episode['url'])
                elif self.selected_provider == 'sokuja':
                    links = sokuja_scraper.get_video_links(self.selected_episode['url'])
                else:
                    links = []
                
                logging.info(f"Raw links found: {len(links)}")
                for l in links:
                    logging.debug(f"Link: {l.get('server')} - {l.get('url')}")
                
                self.available_links = self.organize_server_list(links)
                logging.info(f"Organized links: {len(self.available_links)}")
                
            except Exception as e:
                logging.error(f"Error getting links: {e}", exc_info=True)
                print(f"Error getting links: {e}")
                self.available_links = []
            
            self.selected_index = 0
            
            if self.available_links:
                self.current_view = 'SERVER_SELECT'
                self.status_message = f"✓ {len(self.available_links)} servers | ↑↓ navigate | ⏎ play | b back"
            else:
                self.status_message = f"❌ No servers found | Press b to go back"
        
        elif self.current_view == 'SERVER_SELECT' and self.available_links:
            # Play with selected server
            link = self.available_links[self.selected_index]
            self.play_with_url(link, f"{self.selected_episode['title']} [{link.get('resolution', 'Unknown')} - {link['server']}]")

            # Restore terminal
            try:
                curses.reset_prog_mode()
            except Exception:
                pass
            try:
                self.stdscr.refresh()
            except Exception:
                pass
            self.status_message = "↑↓ navigate | ⏎ play | b back"
    
    def get_provider_links(self):
        """Get video links from selected provider with smart title matching"""
        try:
            # Get all title variants
            main_title = self.selected_anime['title']
            title_romaji = self.selected_anime.get('title_romaji')
            title_english = self.selected_anime.get('title_english')
            
            # Extract SHORT keywords - 2 words work best!
            def extract_short_keywords(title):
                if not title:
                    return []
                
                keywords = []
                
                # Split by colon and take first part
                parts = title.split(':')
                if len(parts) > 1:
                    first_part = parts[0].strip()
                    # Try 2-word combinations from first part
                    words = first_part.split()
                    if len(words) >= 2:
                        keywords.append(' '.join(words[:2]))  # First 2 words
                    keywords.append(first_part)
                
                # Try 2-word combinations from full title
                words = title.split()
                if len(words) >= 2:
                    keywords.append(' '.join(words[:2]))  # First 2 words
                if len(words) >= 3:
                    keywords.append(' '.join(words[:3]))  # First 3 words
                
                return keywords
            
            # Build search query list - PRIORITIZE 2-WORD QUERIES
            search_queries = []
            
            # Priority 1: Short romaji (BEST for Indonesian sites)
            if title_romaji:
                # Extract 2-word first
                short_keywords = extract_short_keywords(title_romaji)
                search_queries.extend(short_keywords)
            
            # Priority 2: Short english
            if title_english:
                short_keywords = extract_short_keywords(title_english)
                search_queries.extend(short_keywords)
            
            # Priority 3: Short main title
            short_keywords = extract_short_keywords(main_title)
            search_queries.extend(short_keywords)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_queries = []
            for q in search_queries:
                if q and q.lower() not in seen:
                    seen.add(q.lower())
                    unique_queries.append(q)
            
            ep_number = self.selected_episode['episode_number']
            
            # Show what we're searching for
            self.status_message = f"🔍 Searching {self.selected_provider.upper()}..."
            self.stdscr.refresh()
            
            # Try each search query
            for query in unique_queries:
                if not query or len(query) < 3:
                    continue
                
                # Update status to show current search
                self.status_message = f"🔍 Trying: {query[:40]}..."
                self.draw()
                
                try:
                    results = None
                    episodes = None

                    if self.selected_provider == 'sokuja':
                        results = sokuja_scraper.search_anime(query)
                        if results:
                            episodes = sokuja_scraper.get_anime_episodes(results[0]['url'])
                            for ep in episodes:
                                if ep['episode_number'] == ep_number:
                                    links = sokuja_scraper.get_video_links(ep['url'])
                                    if links:
                                        organized = self.organize_server_list(links)
                                        if organized:
                                            self.status_message = f"✓ Found: {query[:30]}"
                                            return organized
                    
                    elif self.selected_provider == 'otakudesu':
                        results = otakudesu_scraper.search_anime(query)
                        if results:
                            episodes = otakudesu_scraper.get_anime_episodes(results[0]['url'])
                            for ep in episodes:
                                if ep['episode_number'] == ep_number:
                                    links = otakudesu_scraper.get_video_links(ep['url'])
                                    if links:
                                        organized = self.organize_server_list(links)
                                        if organized:
                                            self.status_message = f"✓ Found: {query[:30]}"
                                            return organized
                    
                    elif self.selected_provider == 'samehadaku':
                        results = samehadaku_scraper.search_anime(query)
                        if results:
                            episodes = samehadaku_scraper.get_anime_episodes(results[0]['url'])
                            for ep in episodes:
                                if ep['episode_number'] == ep_number:
                                    links = samehadaku_scraper.get_all_video_links(ep['url'])
                                    if links:
                                        organized = self.organize_server_list(links)
                                        if organized:
                                            self.status_message = f"✓ Found: {query[:30]}"
                                            return organized
                except Exception as e:
                    # Log the error so failures are visible during debugging,
                    # then continue to the next search query.
                    print(f"Error searching {self.selected_provider} for '{query}': {e}")
                    continue
            
            self.status_message = f"❌ No results found on {self.selected_provider.upper()}"
            return []
        except Exception as e:
            print(f"Error getting provider links: {e}")
            self.status_message = f"❌ Error: {str(e)[:50]}"
            return []
    
    def organize_server_list(self, links):
        """Organize servers: MPV Streaming first, Browser Embeds, then Downloads"""
        # Filter and mark streamable servers
        processed = self.mark_streamable_servers(links)
        
        # Separate into 3 categories
        mpv_streaming = []
        browser_embeds = []
        downloads = []
        
        for link in processed:
            if link.get('type') == 'browser_embed':
                browser_embeds.append(link)
            elif link.get('stream_ready', False) or link.get('type') == 'stream':
                mpv_streaming.append(link)
            else:
                downloads.append(link)
        
        # Combine: MPV streaming first, browser embeds, then downloads
        organized = mpv_streaming + browser_embeds + downloads
        
        return organized if organized else processed
    
    def mark_streamable_servers(self, links):
        """Mark servers that have embed players as streamable"""
        # Servers that work with MPV (have resolvers or yt-dlp support)
        mpv_streamable_keywords = [
            'sokuja',      # SOKUJA direct MP4
            'vidhide',     # Vidhide works with yt-dlp
            'streamhd',    # StreamHD works with yt-dlp
            'filemoon',    # Filemoon works with yt-dlp
            'pixeldrain',  # Pixeldrain - we have resolver!
            'pdrain',      # Pixeldrain (short name) - we have resolver!
            'kraken',      # Krakenfiles - we have resolver!
            'gdrive',      # Google Drive - we have resolver!
            'drive',       # Google Drive
            'otakudesu:',  # Otakudesu special URLs
            'ajax:',       # Samehadaku AJAX URLs
        ]
        
        # Servers that need browser (no resolver available)
        browser_embed_keywords = [
            'mega',        # Mega.nz - not supported by yt-dlp, requires browser
            'acefile',     # File host
            'racaty',      # File host
            'mirrorupload',# File host
            'wibufile',    # File host
            'yourupload',  # File host
            'zippyshare',  # Often dead but sometimes proxied
        ]
        
        # Blacklist of known broken servers (very limited - only truly broken ones)
        blacklist_keywords = [
            # 'desudrive',   # Unsupported by yt-dlp (Removed, now supported via browser embed or direct)
        ]
        
        processed = []
        
        for link in links:
            url = link.get('url', '').lower()
            server = link.get('server', '').lower()
            
            # Check if blacklisted
            is_blacklisted = any(keyword in url or keyword in server 
                                for keyword in blacklist_keywords)
            
            if is_blacklisted:
                continue  # Skip blacklisted servers
            
            # Check if MPV streamable (has resolver or yt-dlp support)
            is_mpv_streamable = any(keyword in url or keyword in server 
                                   for keyword in mpv_streamable_keywords)
            
            # Check if browser embed (no resolver)
            is_browser_embed = any(keyword in url or keyword in server 
                                  for keyword in browser_embed_keywords)
            
            # Mark MPV streamable (will be resolved to direct URL)
            if is_mpv_streamable or link.get('type') == 'stream':
                link['stream_ready'] = True
                link['type'] = 'stream'
                if '🎬' not in link['server']:
                    link['server'] = f"🎬 {link['server']}"
            
            # Mark browser embeds (no resolver available)
            elif is_browser_embed:
                link['stream_ready'] = False
                link['type'] = 'browser_embed'
                if '🌐' not in link['server']:
                    link['server'] = f"🌐 {link['server']}"
            
            processed.append(link)
        
        return processed if processed else links
    
    def play_with_url(self, link_data, title):
        """Play video with MPV or open in browser"""
        video_url = link_data['url']
        server_name = link_data.get('server', 'Unknown')
        headers = {}  # Initialize headers for potential use later
        
        # Save to watch history
        if self.selected_anime and self.selected_episode:
            try:
                import logging
                import database as db
                db.save_watch_progress(
                    self.selected_anime['url'],
                    self.selected_anime['title'],
                    self.selected_episode['episode_number'],
                    self.selected_episode['title']
                )
                self.status_message = self.STATUS_MSG['saved_history']
            except Exception as e:
                logging.error(f"Failed to save history: {e}")

        import curses
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, f"{self.STATUS_MSG['playing']} {title}", curses.color_pair(1))
        self.stdscr.addstr(2, 0, f"Server: {server_name}", curses.color_pair(4))
        self.stdscr.refresh()
        
        link_type = link_data.get('type', 'download')
        provider_display = self.selected_anime.get('provider_display', 'Unknown')
        
        # Initialize MPV command
        mpv_cmd = [
            'mpv',
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        ]
        
        # Save terminal state
        curses.def_prog_mode()
        curses.endwin()
        
        # Get provider info
        provider = self.selected_provider if self.selected_provider else 'Unknown'
        if provider == 'samehadaku':
            provider_display = "🟢 Samehadaku"
        elif provider == 'otakudesu':
            provider_display = "🔵 Otakudesu"
        elif provider == 'sokuja':
            provider_display = "🟡 Sokuja"
        else:
            provider_display = provider
        
        # Resolve browser embeds to direct URLs if possible
        if link_type == 'browser_embed':
            print(f"\n🔄 Resolving embed URL: {title}")
            print(f"📺 Provider: {provider_display}")
            print(f"🎬 Server: {server_name}")
            print(f"🔗 Embed: {video_url[:80]}...")
            print("⏳ Extracting direct stream URL...\n")
            
            # Try to resolve to direct URL
            # First, check if it's an Otakudesu link that needs unwrapping
            if video_url.startswith('otakudesu:'):
                print(f"🔄 Unwrapping Otakudesu link...")
                resolved = otakudesu_scraper.resolve_otakudesu_url(video_url)
                if resolved:
                    if isinstance(resolved, dict):
                        video_url = resolved['url']
                        # We ignore headers here as embed resolvers usually handle their own
                    else:
                        video_url = resolved
                    print(f"✓ Unwrapped: {video_url[:60]}...")
            
            from utils.embed_resolvers import resolve_embed_url
            direct_url = resolve_embed_url(video_url, server_name)
            
            if direct_url and direct_url != video_url:
                print(f"\n✓ Found direct URL!")
                print(f"🔗 {direct_url[:80]}...")
                video_url = direct_url
                link_type = 'stream'  # Treat as stream now
            else:
                # Resolver returned None - open in browser instead
                print(f"\n🌐 Opening in browser instead...")
                print(f"🔗 URL: {video_url[:80]}...")
                webbrowser.open(video_url)
                input("\nPress Enter to return to menu...")
                curses.reset_prog_mode()
                self.stdscr.refresh()
                return
        
        # Handle AJAX streaming URLs (Samehadaku)
        if video_url.startswith('ajax:'):
            print(f"\n🔄 Fetching embed URL for {title}...")
            print(f"📺 Provider: {provider_display}")
            real_url = samehadaku_scraper.get_streaming_url(video_url)
            if real_url:
                # Check if it's a dict with headers (Blogger/Google Video)
                if isinstance(real_url, dict):
                    video_url = real_url['url']
                    headers = real_url.get('headers', {})
                    
                    # Use local proxy if headers are present
                    if headers and self.proxy_port > 0:
                        print(f"🔄 Routing through local proxy (Port {self.proxy_port})...")
                        video_url = stream_proxy.create_proxy_url(self.proxy_port, video_url, headers)
                        print(f"✓ Got proxy URL")
                    elif headers:
                        # Fallback to MPV headers if proxy not available
                        header_args = ",".join([f"{k}: {v}" for k, v in headers.items()])
                        mpv_cmd.append(f"--http-header-fields={header_args}")
                        print(f"✓ Got embed URL with headers (Direct)")
                else:
                    video_url = real_url
                    print(f"✓ Got embed URL: {video_url[:80]}...")
            else:
                print("✗ Failed to fetch embed URL.")
                print("💡 Try selecting a different server.")
                input("Press Enter to continue...")
                curses.reset_prog_mode()
                self.stdscr.refresh()
                return

        # Handle Otakudesu streaming URLs
        if video_url.startswith('otakudesu:'):
            print(f"\n🔄 Resolving Otakudesu stream for {title}...")
            print(f"📺 Provider: {provider_display}")
            resolved = otakudesu_scraper.resolve_otakudesu_url(video_url)
            
            if resolved:
                if isinstance(resolved, dict):
                    video_url = resolved['url']
                    headers = resolved.get('headers', {})
                    
                    # Use local proxy if headers are present
                    if headers and self.proxy_port > 0:
                        print(f"🔄 Routing through local proxy (Port {self.proxy_port})...")
                        video_url = stream_proxy.create_proxy_url(self.proxy_port, video_url, headers)
                        print(f"✓ Got proxy URL")
                    elif headers:
                        # Fallback to MPV headers if proxy failed
                        header_args = ",".join([f"{k}: {v}" for k, v in headers.items()])
                        mpv_cmd.append(f"--http-header-fields={header_args}")
                        print(f"✓ Got stream URL with headers (Direct)")
                else:
                    video_url = resolved
                    print(f"✓ Got stream URL: {video_url[:80]}...")
            else:
                print("✗ Failed to resolve Otakudesu URL.")
                print("💡 Try selecting a different server.")
                input("Press Enter to continue...")
                curses.reset_prog_mode()
                self.stdscr.refresh()
                return
        
        # Handle Safelinks (desustream.com/safelink/...)
        if 'desustream.com/safelink' in video_url:
            print(f"\n🔄 Unwrapping safelink...")
            print(f"🔗 URL: {video_url[:80]}...")
            
            from utils.embed_resolvers import unwrap_safelink
            unwrapped = unwrap_safelink(video_url)
            
            if unwrapped:
                video_url = unwrapped
                print(f"✓ Unwrapped: {video_url[:80]}...")
            else:
                print("✗ Failed to unwrap safelink.")
                print("💡 Try selecting a different server.")
                input("Press Enter to continue...")
                curses.reset_prog_mode()
                self.stdscr.refresh()
                return
        
        # Resolve embed URLs for MPV streamable servers
        # (Pixeldrain, Krakenfiles, GDrive need URL extraction)
        if link_type == 'stream' or link_data.get('stream_ready', False):
            server_lower = server_name.lower()
            
            # Check if this is a Google Video URL that needs proxy
            is_google_video = 'googlevideo.com' in video_url or 'blogger.com' in video_url
            
            if is_google_video and self.proxy_port > 0:
                # Google Video URLs MUST go through proxy
                print(f"\n🔄 Routing Google Video through proxy (Port {self.proxy_port})...")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://desustream.info/' if 'otakudesu' in provider.lower() else 'https://v1.samehadaku.how/'
                }
                video_url = stream_proxy.create_proxy_url(self.proxy_port, video_url, headers)
                print(f"✓ Got proxy URL")
            
            # Check if needs resolution (non-Google URLs)
            elif not is_google_video:
                # Skip resolution if it's already a local proxy URL
                if '127.0.0.1' in video_url or 'localhost' in video_url:
                    needs_resolution = False
                else:
                    # Check if this is a known embed host by server name OR URL pattern
                    needs_resolution = (
                        any(keyword in server_lower for keyword in ['pixeldrain', 'pdrain', 'kraken', 'gdrive', 'drive', 'vidhide', 'streamwish', 'desudrive', 'yourupload', 'mega', 'nakama', 'dood'])
                        or any(pattern in video_url for pattern in ['pixeldrain.com/', 'krakenfiles.com/', 'mega.nz/', 'vidhide.com/', 'desudrive.com/', 'dood.'])
                        or '/embed/' in video_url
                    )

                # Attempt resolution for embed URLs
                if needs_resolution:
                    print(f"\n🔄 Resolving embed URL: {title}")
                    print(f"🎬 Server: {server_name}")
                    print(f"🔗 Embed: {video_url[:80]}...")
                    print("⏳ Extracting direct stream URL...\n")

                    from utils.embed_resolvers import resolve_embed_url
                    direct_url = resolve_embed_url(video_url, server_name)
                    
                    if direct_url:
                        # Check if resolver returned dict with headers
                        if isinstance(direct_url, dict):
                            video_url = direct_url['url']
                            # Store headers for MPV
                            if 'headers' in direct_url:
                                headers = direct_url['headers']
                            print(f"✓ Got direct URL: {video_url[:80]}...")
                        else:
                            video_url = direct_url
                            print(f"✓ Got direct URL: {video_url[:80]}...")
                    else:
                        # Resolver returned None - open in browser instead
                        print("💡 Direct stream not available, opening in browser...")
                        import webbrowser
                        webbrowser.open(video_url)
                        input("\\nPress Enter to return to menu...")
                        curses.reset_prog_mode()
                        self.stdscr.refresh()
                        return

        # Play with MPV (all resolved URLs)
        if link_type == 'stream' or link_data.get('stream_ready', False):
            print(f"\n▶️  Playing: {title}")
            print(f"🎬 Server: {server_name}")
            print(f"🔗 URL: {video_url[:80]}...")
            print("⏳ Loading video...\n")
            
            # Add headers to MPV if they exist (from embed resolution)
            if headers:
                header_args = ",".join([f"{k}: {v}" for k, v in headers.items()])
                mpv_cmd.append(f"--http-header-fields={header_args}")
                print(f"🔑 Using custom headers for playback")
            
            # Add URL to command
            mpv_cmd.append(video_url)
            
            try:
                # Run MPV
                subprocess.run(mpv_cmd, check=False)
            except FileNotFoundError:
                print("❌ Error: MPV not found. Please install mpv.")
                input("Press Enter to continue...")
            except Exception as e:
                print(f"❌ Error playing video: {e}")
                input("Press Enter to continue...")
            
            input("\nPress Enter to return to menu...")
        else:
            # Download links - open in browser
            print(f"\n🌐 Opening in browser: {title}")
            print(f"🔗 URL: {video_url}")
            webbrowser.open(video_url)
            input("Press Enter to continue...")
        
        # Restore terminal
        curses.reset_prog_mode()
        self.stdscr.refresh()
    
    # Assuming this code is intended for the __init__ method of the class
    # and the instruction meant to place it there, along with necessary imports.
    # Since the class definition and __init__ are not provided,
    # I'm placing it here as per the exact insertion point in the instruction,
    # but noting that it's likely misplaced if it's meant for __init__.
    # For a syntactically correct file, this block needs to be inside a method or class.
    # Given the instruction "initialize in __init__", I'll assume the user wants
    # to add these lines to the __init__ method of the AnimeTUI class.
    # As the __init__ method is not in the provided snippet, I'll simulate
    # adding it by placing it before handle_back, assuming handle_back is
    # the next method in the class.
    # I'll also add dummy imports for 'config' and 'database' as requested.
    
    # Dummy imports for config and database (assuming they are needed)
    # from . import config # Example import, adjust as needed
    # from . import database # Example import, adjust as needed

    # App state (intended for __init__)
    # self.current_view = 'PROVIDER_SELECT'  # Start with provider selection
    # self.selected_provider = config.get('provider_default', None)
    # self.default_quality = config.get('kualitas_default', '720p')
    
    # Indonesian status messages (intended for __init__)
    # self.STATUS_MSG = {
    #     'searching': 'Mencari anime...',
    #     'loading': 'Memuat episode...',
    #     'fetching_servers': 'Mengambil daftar server...',
    #     'playing': 'Memutar video...',
    #     'saved_history': '📺 Tersimpan di riwayat',
    #     'added_favorite': '⭐ Ditambahkan ke favorit!',
    #     'removed_favorite': '❌ Dihapus dari favorit!',
    # }

    def handle_back(self):
        """Handle back navigation"""
        if self.current_view == 'SEARCH':
            self.current_view = 'PROVIDER_SELECT'
            self.selected_index = 0
            self.status_message = "Select a provider"
        elif self.current_view == 'SERVER_SELECT':
            self.current_view = 'EPISODES'
            # Restore episode selection
            for i, ep in enumerate(self.episodes):
                if ep == self.selected_episode:
                    self.selected_index = i
                    break
            self.status_message = "↑↓ navigate | ⏎ select | b back"
        elif self.current_view == 'EPISODES':
            self.current_view = 'RESULTS'
            self.selected_index = min(self.selected_index, len(self.search_results) - 1)
            self.status_message = "↑↓ navigate | ⏎ select | b back"
        elif self.current_view == 'RESULTS':
            self.current_view = 'SEARCH'
            self.status_message = "🔍 Press / to search | ❌ q to quit"

def main(stdscr):
    app = AnimeTUI(stdscr)
    app.run()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
