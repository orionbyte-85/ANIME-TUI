#!/usr/bin/env python3
"""Test Otakudesu scraper with embed URLs"""

import otakudesu_scraper

# Test with One Piece episode
episode_url = "https://otakudesu.best/episode/wpoiec-episode-1150-sub-indo/"

print(f"Testing: {episode_url}\n")
print("=" * 60)

links = otakudesu_scraper.get_video_links(episode_url)

print(f"\n✓ Found {len(links)} total options\n")

# Show first 10
for i, link in enumerate(links[:10], 1):
    stream_indicator = "🎬" if link.get('stream_ready') else "💾"
    print(f"{i}. {stream_indicator} [{link['quality']:>6}] {link['server']}")
    print(f"   URL: {link['url'][:80]}...")
    print(f"   Priority: {link.get('priority', 'N/A')}")
    print()

# Check if embed player is first
if links and '🎬 Embed Player' in links[0]['server']:
    print("✅ SUCCESS: Embed player is prioritized!")
else:
    print("❌ FAIL: Embed player is not first")
