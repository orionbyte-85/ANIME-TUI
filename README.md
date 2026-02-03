# Anime Streaming TUI

A terminal-based anime streaming application with multi-provider support.

## Features

- **Multi-Provider Support**:
  - 🎬 Samehadaku
  - 🔵 Otakudesu
  - 🎲 Torrent (Nyaa.si)
  
- **Smart Streaming**:
  - Local proxy for Google Video streams
  - Automatic header handling
  - Torrent streaming via peerflix
  
- **Server Verification**:
  - Blacklist for dead servers
  - Whitelist for trusted servers
  - Fast concurrent verification

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install torrent streaming (optional, for Torrent provider)
npm install -g peerflix
```

## Usage

```bash
python3 anime_tui.py
```

### Navigation
- `↑↓` - Navigate
- `⏎` - Select
- `/` - Search
- `b` - Back
- `q` - Quit

## Project Structure

```
samehadaku-addon/
├── anime_tui.py          # Main TUI application
├── requirements.txt      # Python dependencies
├── manifest.json         # App metadata
│
├── scrapers/             # Scraper modules
│   ├── samehadaku_scraper.py
│   ├── otakudesu_scraper.py
│   ├── nyaa_scraper.py   # Torrent scraper
│   ├── subscene_scraper.py
│   └── sokuja_scraper.py
│
├── utils/                # Helper modules
│   ├── embed_resolvers.py  # Extract direct URLs from embeds
│   ├── stream_proxy.py     # Local streaming proxy
│   ├── torrent_stream.py   # Torrent streaming helper
│   └── link_verifier.py    # Server verification
│
└── archive/              # Old test/debug files
    ├── tests/
    └── debug/
```

## How It Works

### Streaming Flow

1. **Search** - Search anime across providers
2. **Select** - Choose anime and episode
3. **Scrape** - Get video servers
4. **Resolve** - Extract direct stream URLs (if embed)
5. **Proxy** - Route Google Video streams through local proxy
6. **Play** - Stream in MPV

### Torrent Flow

1. **Search** - Search Nyaa.si for torrents
2. **Filter** - Show seeders, resolution, size
3. **Stream** - Stream via peerflix to localhost
4. **Play** - Stream in MPV

## Credits

- Scrapers: Samehadaku, Otakudesu, Nyaa.si, Subscene
- Torrent: peerflix
- Player: MPV
# NONTON-ANIME-STREMIO
