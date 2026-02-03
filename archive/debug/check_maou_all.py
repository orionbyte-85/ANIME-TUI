from scraper import get_anime_episodes

urls = [
    "https://v1.samehadaku.how/anime/maou-gakuin-no-futekigousha-season-2-part-2/",
    "https://v1.samehadaku.how/anime/maou-gakuin-no-futekigousha-season-2/",
    "https://v1.samehadaku.how/anime/maou-gakuin-no-futekigousha-shijou-saikyou-no-maou-no-shiso-tensei-shite-shison-tachi-no-gakkou-e/"
]

for url in urls:
    print(f"Checking: {url}")
    eps = get_anime_episodes(url)
    print(f"Found {len(eps)} episodes")
    if eps:
        print(f"First ep: {eps[0]['title']}")
    print("-" * 20)
