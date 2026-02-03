"""
AniList API Helper for Anime Metadata
Provides accurate Romaji titles for Indonesian anime sites
FREE - No API key required!
"""

import requests
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class AniListHelper:
    def __init__(self):
        self.api_url = "https://graphql.anilist.co"
    
    @lru_cache(maxsize=200)
    def search_anime(self, title):
        """
        Search anime by title on AniList
        Returns: {
            'id': 113415,
            'title_romaji': 'Maou Gakuin no Futekigousha',
            'title_english': 'The Misfit of Demon King Academy',
            'title_native': '魔王学院の不適合者',
            'season': 1,
            'episodes': 13
        }
        """
        query = '''
        query ($search: String) {
            Media(search: $search, type: ANIME) {
                id
                idMal
                title {
                    romaji
                    english
                    native
                }
                episodes
                season
                seasonYear
                synonyms
            }
        }
        '''
        
        variables = {'search': title}
        
        try:
            response = requests.post(
                self.api_url,
                json={'query': query, 'variables': variables},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"AniList API error: {response.status_code}")
                return None
            
            data = response.json()
            
            if 'errors' in data:
                logger.warning(f"AniList GraphQL error: {data['errors']}")
                return None
            
            media = data.get('data', {}).get('Media')
            if not media:
                return None
            
            titles = media.get('title', {})
            
            result = {
                'id': media.get('id'),
                'mal_id': media.get('idMal'),
                'title_romaji': titles.get('romaji', ''),
                'title_english': titles.get('english', ''),
                'title_native': titles.get('native', ''),
                'synonyms': media.get('synonyms', []),
                'episodes': media.get('episodes'),
                'season_year': media.get('seasonYear'),
                # Collect all possible titles for searching
                'all_titles': [
                    titles.get('romaji'),
                    titles.get('english'),
                    titles.get('native')
                ] + media.get('synonyms', [])
            }
            
            # Remove None/empty values
            result['all_titles'] = [t for t in result['all_titles'] if t]
            
            logger.info(f"AniList found: {result['title_romaji']} (ID: {result['id']})")
            
            return result
        
        except Exception as e:
            logger.error(f"AniList search error: {e}")
            return None
    
    @lru_cache(maxsize=200)
    def get_by_mal_id(self, mal_id):
        """Get anime by MyAnimeList ID"""
        query = '''
        query ($malId: Int) {
            Media(idMal: $malId, type: ANIME) {
                id
                title {
                    romaji
                    english
                    native
                }
                synonyms
            }
        }
        '''
        
        variables = {'malId': int(mal_id)}
        
        try:
            response = requests.post(
                self.api_url,
                json={'query': query, 'variables': variables},
                timeout=10
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            media = data.get('data', {}).get('Media')
            
            if not media:
                return None
            
            titles = media.get('title', {})
            
            return {
                'id': media.get('id'),
                'title_romaji': titles.get('romaji', ''),
                'title_english': titles.get('english', ''),
                'title_native': titles.get('native', ''),
                'synonyms': media.get('synonyms', []),
                'all_titles': [
                    titles.get('romaji'),
                    titles.get('english'),
                    titles.get('native')
                ] + media.get('synonyms', [])
            }
        
        except Exception as e:
            logger.error(f"AniList MAL lookup error: {e}")
            return None
