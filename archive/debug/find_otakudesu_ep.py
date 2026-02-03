from otakudesu_scraper import search_anime, get_anime_episodes

print("Searching for One Piece...")
results = search_anime("One Piece")
if results:
    anime = results[0]
    print(f"Found: {anime['title']} ({anime['url']})")
    
    print("Getting episodes...")
    episodes = get_anime_episodes(anime['url'])
    if episodes:
        print(f"Found {len(episodes)} episodes")
        print(f"First episode: {episodes[0]['title']} - {episodes[0]['url']}")
    else:
        print("No episodes found")
else:
    print("No results found")
