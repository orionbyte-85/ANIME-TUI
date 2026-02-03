#!/usr/bin/env python3
from otakudesu_scraper import get_video_links

url = "https://otakudesu.best/episode/maogkn-ftkg-s2-p2-episode-12-sub-indo/"
print(f"Testing URL: {url}")

links = get_video_links(url)
print(f"Found {len(links)} links")
for link in links:
    print(f"- {link['server']} ({link['quality']})")
