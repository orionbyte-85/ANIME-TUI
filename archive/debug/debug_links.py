from scraper import get_all_video_links
import sys

url = "https://v1.samehadaku.how/one-piece-gyojin-tou-hen-episode-1/"
if len(sys.argv) > 1:
    url = sys.argv[1]

print(f"Testing URL: {url}")
links = get_all_video_links(url)
print(f"Found {len(links)} links")

for i, link in enumerate(links):
    print(f"[{i}] {link['server']} ({link['quality']}) - Stream Ready: {link.get('stream_ready')} - URL: {link['url']}")
