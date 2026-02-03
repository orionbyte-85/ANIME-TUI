#!/usr/bin/env python3
"""
Config Manager untuk Anime TUI
Handles configuration file di ~/.config/anime-tui/config.json
"""

import json
import os
from pathlib import Path

class ConfigManager:
    DEFAULT_CONFIG = {
        "bahasa": "id",
        "provider_default": "otakudesu",
        "kualitas_default": "720p",
        "auto_play_berikutnya": True,
        "countdown_detik": 5,
        "mpv_args": "--sub-auto=fuzzy --volume=70",
        "lokasi_download": "~/Downloads/Anime",
        "max_riwayat": 10,
        "max_riwayat_pencarian": 20,
        "cache_server_menit": 5,
        "server_check_timeout": 3,
        "subtitle_otomatis": True,
        "subtitle_bahasa": "indonesian"
    }
    
    def __init__(self):
        # Config path: ~/.config/anime-tui/config.json
        self.config_dir = Path.home() / '.config' / 'anime-tui'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_path = self.config_dir / 'config.json'
        self.config = self.load_config()
    
    def load_config(self):
        """Load config dari file, create default jika belum ada"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                
                # Merge dengan default (untuk key baru)
                config = self.DEFAULT_CONFIG.copy()
                config.update(loaded)
                
                return config
            except:
                # Jika corrupt, gunakan default
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self, config=None):
        """Save config ke file"""
        if config is None:
            config = self.config
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def get(self, key, default=None):
        """Get config value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set config value dan save"""
        self.config[key] = value
        self.save_config()
    
    def reset_to_defaults(self):
        """Reset semua ke default"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
    
    def get_download_path(self):
        """Get absolute download path"""
        path = self.get('lokasi_download', '~/Downloads/Anime')
        return Path(path).expanduser()
    
    def ensure_download_path(self):
        """Create download directory jika belum ada"""
        path = self.get_download_path()
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_mpv_args(self):
        """Get MPV arguments as list"""
        args_str = self.get('mpv_args', '')
        if not args_str:
            return []
        return args_str.split()

# Global instance
config = ConfigManager()
