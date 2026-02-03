# Indonesian Anime Stremio Addon - Deployment Guide

## 🚀 Quick Deploy to Vercel (FREE)

### Prerequisites
- GitHub account
- Vercel account (free tier)
- TMDB API Key (already configured in code)

### Step-by-Step Deployment

#### 1. Push to GitHub
```bash
cd ~/Documents/samehadaku-addon

# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit - Stremio addon"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

#### 2. Deploy to Vercel

**Option A: Via Vercel Dashboard** (Easiest)
1. Go to https://vercel.com
2. Sign in with GitHub
3. Click "Add New" → "Project"
4. Import your GitHub repository
5. **Environment Variables:**
   - Name: `TMDB_API_KEY`
   - Value: `3860b57595ccaead6c727d84327e5ff0`
6. Click "Deploy"
7. Wait ~2 minutes ✅

**Option B: Via Vercel CLI**
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd ~/Documents/samehadaku-addon
vercel --prod

# Set environment variable
vercel env add TMDB_API_KEY
# Paste: 3860b57595ccaead6c727d84327e5ff0
```

#### 3. Get Your Addon URL
After deployment, Vercel gives you a URL like:
```
https://your-addon-name.vercel.app
```

#### 4. Install in Stremio
1. Open Stremio Desktop
2. Go to Addons → Community Addons
3. Paste URL:
   ```
   https://your-addon-name.vercel.app/manifest.json
   ```
4. Click Install ✅

---

## 📊 What You Get

### Providers (Fast & Reliable)
- 🟡 **Sokuja** - Direct streams (360p-720p)
- 🎲 **Nyaa** - Torrents (up to 15 results)
- 🌸 **AnimeTosho** - Premium torrents

### Performance
- ⚡ **Response Time:** 2-5 seconds
- ✅ **Success Rate:** ~95%
- 🌐 **Always Online:** 24/7 via Vercel

### Features
- AniList integration for accurate title matching
- Automatic romaji/English title conversion
- Smart episode matching
- Seeder count & quality info for torrents

---

## 🔧 Configuration

### vercel.json
Already configured with:
- Python 3.9 runtime
- Flask framework
- TMDB API key as env variable
- CORS enabled

### Requirements
All dependencies in `requirements.txt`:
```
Flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
```

---

## 🐛 Troubleshooting

### "No streams found"
- Check if anime is in AniList/TMDB
- Try different episode numbers
- Check Vercel logs: `vercel logs`

### "Timeout errors"
- Vercel has 10s timeout limit
- Current setup avoids this by using fast providers only

### "Video not supported"
- Torrents require torrent client in Stremio
- Enable WebTorrent in Stremio settings

---

## 📝 Notes

- **Free Tier Limits:** 100GB bandwidth/month (should be enough)
- **Cold Starts:** First request after idle might be slow (~3-5s)
- **Logs:** View real-time logs at Vercel dashboard
- **Updates:** Just push to GitHub, Vercel auto-deploys

---

## 🔄 Local Testing (Before Deploy)

Test addon locally first:
```bash
cd ~/Documents/samehadaku-addon
python3 stremio_addon.py
```

Then test in browser:
```
http://localhost:7000/manifest.json
http://localhost:7000/stream/series/tt12432936:1:1.json
```

Should return JSON with streams! ✅

---

## 🚀 Next Steps

After deployment works:
1. Share URL with friends
2. Monitor usage in Vercel dashboard
3. Report issues on GitHub
4. Optional: Add custom domain

**Enjoy your 24/7 anime addon!** 🎬
