from otakudesu_scraper import get_video_links
import sys

url = "https://otakudesu.best/episode/wpoiec-episode-1150-sub-indo/"
if len(sys.argv) > 1:
    url = sys.argv[1]

print(f"Testing URL: {url}")
links = get_video_links(url)
print(f"Found {len(links)} links")

for i, link in enumerate(links):
    print(f"[{i}] {link['server']} ({link['quality']}) - Stream Ready: {link.get('stream_ready')} - URL: {link['url'][:50]}...")
