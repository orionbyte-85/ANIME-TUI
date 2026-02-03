from otakudesu_scraper import get_video_links, resolve_otakudesu_url
import sys

url = "https://otakudesu.best/episode/wpoiec-episode-1150-sub-indo/"
print(f"Getting links for {url}...")
links = get_video_links(url)

ondesu_link = next((l for l in links if 'ondesu' in l['server'].lower()), None)

if ondesu_link:
    print(f"Found ondesu link: {ondesu_link['server']}")
    print(f"URL: {ondesu_link['url']}")
    print("Resolving...")
    resolved = resolve_otakudesu_url(ondesu_link['url'])
    print(f"Resolved: {resolved}")
else:
    print("No ondesu link found")
