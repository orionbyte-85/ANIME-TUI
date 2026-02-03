#!/usr/bin/env python3
"""
Database Manager untuk Anime TUI
Handles: watch history, favorites, search history, server health cache
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    def __init__(self):
        # Database path: ~/.config/anime-tui/history.db
        config_dir = Path.home() / '.config' / 'anime-tui'
        config_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = config_dir / 'history.db'
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Watch history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watch_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anime_url TEXT NOT NULL,
                anime_title TEXT NOT NULL,
                episode_num INTEGER NOT NULL,
                episode_title TEXT,
                timestamp REAL DEFAULT 0,
                last_watched DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(anime_url, episode_num)
            )
        ''')
        
        # Favorites table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anime_url TEXT UNIQUE NOT NULL,
                anime_title TEXT NOT NULL,
                thumbnail TEXT,
                provider TEXT,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Search history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                provider TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Server health cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS server_health (
                server_url TEXT PRIMARY KEY,
                status INTEGER DEFAULT 1,
                last_checked DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ==================== WATCH HISTORY ====================
    
    def save_watch_progress(self, anime_url, anime_title, episode_num, episode_title='', timestamp=0):
        """Save or update watch progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO watch_history 
            (anime_url, anime_title, episode_num, episode_title, timestamp, last_watched)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (anime_url, anime_title, episode_num, episode_title, timestamp))
        
        conn.commit()
        conn.close()
    
    def get_recent_history(self, limit=10):
        """Get recent watch history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT anime_url, anime_title, episode_num, episode_title, timestamp, last_watched
            FROM watch_history
            ORDER BY last_watched DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'anime_url': r[0],
            'anime_title': r[1],
            'episode_num': r[2],
            'episode_title': r[3],
            'timestamp': r[4],
            'last_watched': r[5]
        } for r in results]
    
    def get_anime_progress(self, anime_url):
        """Get last watched episode for an anime"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT episode_num, timestamp
            FROM watch_history
            WHERE anime_url = ?
            ORDER BY last_watched DESC
            LIMIT 1
        ''', (anime_url,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {'episode_num': result[0], 'timestamp': result[1]}
        return None
    
    def clear_history(self):
        """Clear all watch history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM watch_history')
        conn.commit()
        conn.close()
    
    # ==================== FAVORITES ====================
    
    def add_favorite(self, anime_url, anime_title, thumbnail='', provider=''):
        """Add anime to favorites"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO favorites (anime_url, anime_title, thumbnail, provider)
                VALUES (?, ?, ?, ?)
            ''', (anime_url, anime_title, thumbnail, provider))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Already in favorites
        finally:
            conn.close()
    
    def remove_favorite(self, anime_url):
        """Remove anime from favorites"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM favorites WHERE anime_url = ?', (anime_url,))
        affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def is_favorite(self, anime_url):
        """Check if anime is in favorites"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM favorites WHERE anime_url = ? LIMIT 1', (anime_url,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def get_all_favorites(self):
        """Get all favorite anime"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT anime_url, anime_title, thumbnail, provider, added_date
            FROM favorites
            ORDER BY added_date DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'anime_url': r[0],
            'anime_title': r[1],
            'thumbnail': r[2],
            'provider': r[3],
            'added_date': r[4]
        } for r in results]
    
    # ==================== SEARCH HISTORY ====================
    
    def add_search_history(self, query, provider=''):
        """Add search query to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete if already exists (to update timestamp)
        cursor.execute('DELETE FROM search_history WHERE query = ? AND provider = ?', (query, provider))
        
        # Insert new
        cursor.execute('''
            INSERT INTO search_history (query, provider)
            VALUES (?, ?)
        ''', (query, provider))
        
        # Keep only last 20
        cursor.execute('''
            DELETE FROM search_history
            WHERE id NOT IN (
                SELECT id FROM search_history
                ORDER BY timestamp DESC
                LIMIT 20
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_search_history(self, limit=10):
        """Get recent search queries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT query
            FROM search_history
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [r[0] for r in results]
    
    # ==================== SERVER HEALTH ====================
    
    def update_server_health(self, server_url, status):
        """Update server health status (1=online, 0=offline)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO server_health (server_url, status, last_checked)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (server_url, status))
        
        conn.commit()
        conn.close()
    
    def get_server_health(self, server_url, max_age_minutes=5):
        """Get cached server health (None if expired)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT status, last_checked
            FROM server_health
            WHERE server_url = ?
            AND datetime(last_checked) > datetime('now', '-' || ? || ' minutes')
        ''', (server_url, max_age_minutes))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return bool(result[0])
        return None

# Global instance
db = DatabaseManager()
