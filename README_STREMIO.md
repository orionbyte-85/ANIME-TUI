# Stremio Addon - Indonesian Anime (Multi-Provider)

Stream anime from Indonesian sources directly in Stremio!

## Features

- 🟢 **Samehadaku** - 360p-1080p (Blogspot, Mega, Vidhide, Pixeldrain)
- 🔵 **Otakudesu** - 360p-720p (35+ servers including Google Video, Mega, Vidhide)
- 🟡 **Sokuja** - 480p-720p (Fast direct streaming)
- 🎲 **Nyaa Torrents** - 720p-1080p (P2P with seeders info)

## Installation

### Local Testing

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get TMDB API key (free):
   - Visit https://www.themoviedb.org/settings/api
   - Copy your API key
   - Replace `YOUR_TMDB_API_KEY_HERE` in `utils/tmdb_helper.py`

3. Run server:
```bash
python stremio_addon.py
```

4. Add to Stremio:
   - Open Stremio
   - Go to Addons → Install from URL
   - Enter: `http://localhost:7000/manifest.json`

### Deploy to Vercel (FREE)

1. Push to GitHub
2. Connect to Vercel
3. Add environment variable:
   - Name: `TMDB_API_KEY`
   - Value: Your TMDB API key
4. Deploy!
5. Add to Stremio: `https://your-addon.vercel.app/manifest.json`

## How It Works

When you open an anime episode in Stremio:

1. Stremio sends request with IMDb ID + season + episode
2. Addon converts IMDb ID → Anime title (via TMDB)
3. Searches all providers (Samehadaku, Otakudesu, etc)
4. Matches season & episode
5. Returns streaming links

## Supported Formats

- **Direct Stream** (`url`) - Play immediately
- **External URL** (`externalUrl`) - Opens in browser (for Mega, Dood.to)
- **Torrent** (`infoHash`) - P2P streaming

## Notes

- Some streams require opening in browser (Mega.nz, Dood.to)
- Torrent streams require seeders to be available
- First request may be slow (searching multiple providers)
- Results are cached for 1 hour

## Disclaimer

This addon only provides links from publicly available sources.
All content is hosted by third parties.
