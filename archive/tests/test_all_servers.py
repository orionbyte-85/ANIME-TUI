#!/usr/bin/env python3
"""Test the updated get_all_video_links function"""

from scraper import get_all_video_links

url = "https://v1.samehadaku.how/maou-gakuin-no-futekigousha-season-2-episode-1/"

print(f"Testing: {url}\n")
links = get_all_video_links(url)

print(f"Found {len(links)} total links\n")

# Group by quality
by_quality = {}
for link in links:
    q = link['quality']
    if q not in by_quality:
        by_quality[q] = []
    by_quality[q].append(link)

# Display organized by quality
quality_order = ['1080p', '720p', '480p', '360p', '240p']
for quality in quality_order:
    if quality in by_quality:
        print(f"=== {quality} ({len(by_quality[quality])} servers) ===")
        for link in by_quality[quality]:
            print(f"  [{link['server']}] {link['url'][:80]}")
        print()
