#!/usr/bin/env python3
"""Test episode filtering for Maou Gakuin"""

from scraper import get_anime_episodes, get_samehadaku_video

# Test with the anime the user mentioned
anime_url = "https://v1.samehadaku.how/anime/maou-gakuin-no-futekigousha/"

print(f"Testing episode list for: {anime_url}")
episodes = get_anime_episodes(anime_url)

print(f"\nFound {len(episodes)} episodes:")
for i, ep in enumerate(episodes, 1):
    print(f"{i:2}. [{ep['episode_number']:>3}] {ep['title']}")

# Test video URL extraction for first episode
if episodes:
    print(f"\n{'='*60}")
    print("Testing video URL extraction for Episode 1...")
    first_ep = episodes[0]
    print(f"Episode URL: {first_ep['url']}")
    
    video_url = get_samehadaku_video(first_ep['url'])
    if video_url:
        print(f"✓ Video URL found: {video_url}")
    else:
        print("✗ Failed to get video URL")
