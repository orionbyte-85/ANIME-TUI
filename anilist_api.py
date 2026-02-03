#!/usr/bin/env python3
"""
AniList API Client - GraphQL API for anime and episode information
Documentation: https://anilist.gitbook.io/anilist-apiv2-docs/
"""

import requests
import json

ANILIST_API_URL = "https://graphql.anilist.co"

def search_anime(query, limit=10):
    """
    Search for anime on AniList
    
    Args:
        query: Search query string
        limit: Maximum number of results (default: 10)
    
    Returns:
        List of anime dictionaries with:
        - id: AniList ID
        - title: Anime title (romaji, english, native)
        - episodes: Total episode count
        - status: Airing status
        - coverImage: Cover image URL
        - description: Anime description
    """
    graphql_query = """
    query ($search: String, $perPage: Int) {
        Page(page: 1, perPage: $perPage) {
            media(search: $search, type: ANIME, sort: POPULARITY_DESC) {
                id
                title {
                    romaji
                    english
                    native
                }
                episodes
                status
                coverImage {
                    large
                    medium
                }
                description
                format
                season
                seasonYear
                averageScore
            }
        }
    }
    """
    
    variables = {
        "search": query,
        "perPage": limit
    }
    
    try:
        response = requests.post(
            ANILIST_API_URL,
            json={'query': graphql_query, 'variables': variables},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            media_list = data.get('data', {}).get('Page', {}).get('media', [])
            
            results = []
            for media in media_list:
                # Get the best available title
                title_obj = media.get('title', {})
                title = (title_obj.get('english') or 
                        title_obj.get('romaji') or 
                        title_obj.get('native') or 
                        'Unknown')
                
                results.append({
                    'id': media.get('id'),
                    'title': title,
                    'title_romaji': title_obj.get('romaji'),
                    'title_english': title_obj.get('english'),
                    'title_native': title_obj.get('native'),
                    'episodes': media.get('episodes'),
                    'status': media.get('status'),
                    'cover_image': media.get('coverImage', {}).get('large'),
                    'description': media.get('description'),
                    'format': media.get('format'),
                    'season': media.get('season'),
                    'year': media.get('seasonYear'),
                    'score': media.get('averageScore'),
                    'source': 'anilist'
                })
            
            return results
        else:
            print(f"[anilist] API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"[anilist] Search error: {e}")
        return []

def get_anime_info(anime_id):
    """
    Get detailed information about an anime
    
    Args:
        anime_id: AniList anime ID
    
    Returns:
        Dictionary with detailed anime information
    """
    graphql_query = """
    query ($id: Int) {
        Media(id: $id, type: ANIME) {
            id
            title {
                romaji
                english
                native
            }
            episodes
            status
            coverImage {
                large
            }
            description
            format
            season
            seasonYear
            averageScore
            genres
            studios {
                nodes {
                    name
                }
            }
        }
    }
    """
    
    variables = {"id": anime_id}
    
    try:
        response = requests.post(
            ANILIST_API_URL,
            json={'query': graphql_query, 'variables': variables},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            media = data.get('data', {}).get('Media', {})
            
            title_obj = media.get('title', {})
            title = (title_obj.get('english') or 
                    title_obj.get('romaji') or 
                    title_obj.get('native') or 
                    'Unknown')
            
            studios = media.get('studios', {}).get('nodes', [])
            studio_names = [s.get('name') for s in studios]
            
            return {
                'id': media.get('id'),
                'title': title,
                'title_romaji': title_obj.get('romaji'),
                'title_english': title_obj.get('english'),
                'title_native': title_obj.get('native'),
                'episodes': media.get('episodes'),
                'status': media.get('status'),
                'cover_image': media.get('coverImage', {}).get('large'),
                'description': media.get('description'),
                'format': media.get('format'),
                'season': media.get('season'),
                'year': media.get('seasonYear'),
                'score': media.get('averageScore'),
                'genres': media.get('genres', []),
                'studios': studio_names,
                'source': 'anilist'
            }
        else:
            print(f"[anilist] API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[anilist] Info error: {e}")
        return None

def get_episode_list(anime_id, episode_count):
    """
    Generate episode list for an anime
    
    AniList doesn't provide individual episode data, so we generate
    a simple list based on the episode count.
    
    Args:
        anime_id: AniList anime ID
        episode_count: Total number of episodes
    
    Returns:
        List of episode dictionaries
    """
    if not episode_count:
        return []
    
    episodes = []
    for i in range(1, episode_count + 1):
        episodes.append({
            'episode_number': str(i),
            'title': f'Episode {i}',
            'anilist_id': anime_id,
            'source': 'anilist'
        })
    
    return episodes

if __name__ == "__main__":
    # Test the API
    print("Testing AniList API...")
    print("=" * 60)
    
    # Test search
    print("\nSearching for 'One Piece'...")
    results = search_anime("One Piece", limit=3)
    print(f"Found {len(results)} results:")
    for i, anime in enumerate(results, 1):
        print(f"\n{i}. {anime['title']}")
        print(f"   ID: {anime['id']}")
        print(f"   Episodes: {anime['episodes']}")
        print(f"   Status: {anime['status']}")
        print(f"   Score: {anime['score']}")
    
    # Test anime info
    if results:
        anime_id = results[0]['id']
        print(f"\n{'=' * 60}")
        print(f"Getting info for anime ID {anime_id}...")
        info = get_anime_info(anime_id)
        if info:
            print(f"Title: {info['title']}")
            print(f"Episodes: {info['episodes']}")
            print(f"Genres: {', '.join(info['genres'])}")
            print(f"Studios: {', '.join(info['studios'])}")
            
            # Test episode list
            print(f"\n{'=' * 60}")
            print("Generating episode list...")
            episodes = get_episode_list(anime_id, info['episodes'])
            print(f"Generated {len(episodes)} episodes")
            print(f"First 5: {[ep['title'] for ep in episodes[:5]]}")
