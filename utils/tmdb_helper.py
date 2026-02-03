"""
TMDB Helper for metadata matching
Converts IMDb/TMDB IDs to anime titles for scraper searches
"""

import requests
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class TMDBHelper:
    def __init__(self, api_key=None):
        # TMDB API key (free for non-commercial use)
        self.api_key = api_key or "3860b57595ccaead6c727d84327e5ff0"
        self.base_url = "https://api.themoviedb.org/3"
    
    @lru_cache(maxsize=200)
    def get_anime_metadata(self, id_str, season=1, episode=1):
        """
        Get anime metadata from IMDb/TMDB ID with alternative titles
        Returns: {
            'title': 'Naruto',
            'original_title': 'ナルト',
            'romaji': 'Naruto',
            'alternative_titles': ['Naruto Shippuuden', ...]
        }
        """
        try:
            # Check if IMDb or TMDB ID
            if id_str.startswith('tt'):
                # IMDb ID - convert to TMDB first
                tmdb_id = self.imdb_to_tmdb(id_str)
                if not tmdb_id:
                    logger.warning(f"Could not convert IMDb {id_str} to TMDB")
                    return None
            else:
                tmdb_id = id_str
            
            # Get TV show details
            url = f"{self.base_url}/tv/{tmdb_id}"
            params = {'api_key': self.api_key}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                logger.warning(f"TMDB API error: {response.status_code}")
                return None
            
            data = response.json()
            
            # Extract titles
            title = data.get('name', '')
            original_title = data.get('original_name', '')
            
            # Get alternative titles (including romaji)
            alt_titles = self.get_alternative_titles(tmdb_id)
            
            # Try to get episode-specific data
            episode_title = self.get_episode_title(tmdb_id, season, episode)
            
            logger.info(f"TMDB metadata: title={title}, original={original_title}, alts={alt_titles}")
            
            return {
                'title': title,
                'original_title': original_title,
                'romaji': original_title if original_title else title,  # Prefer original
                'alternative_titles': alt_titles,
                'episode_title': episode_title,
                'all_titles': [title, original_title] + alt_titles  # For searching
            }
        
        except Exception as e:
            logger.error(f"TMDB metadata error: {e}")
            return None
    
    @lru_cache(maxsize=200)
    def get_alternative_titles(self, tmdb_id):
        """Get all alternative titles including romaji"""
        try:
            url = f"{self.base_url}/tv/{tmdb_id}/alternative_titles"
            params = {'api_key': self.api_key}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return []
            
            data = response.json()
            titles = []
            
            for result in data.get('results', []):
                alt_title = result.get('title', '')
                if alt_title and alt_title not in titles:
                    titles.append(alt_title)
            
            return titles[:5]  # Limit to 5 alternatives
        
        except Exception as e:
            logger.error(f"Alternative titles error: {e}")
            return []
    
    @lru_cache(maxsize=100)
    def imdb_to_tmdb(self, imdb_id):
        """Convert IMDb ID to TMDB ID"""
        try:
            url = f"{self.base_url}/find/{imdb_id}"
            params = {
                'api_key': self.api_key,
                'external_source': 'imdb_id'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Check TV results
            if data.get('tv_results'):
                return data['tv_results'][0]['id']
            
            return None
        
        except Exception as e:
            logger.error(f"IMDb to TMDB error: {e}")
            return None
    
    def get_episode_title(self, tmdb_id, season, episode):
        """Get specific episode title"""
        try:
            url = f"{self.base_url}/tv/{tmdb_id}/season/{season}/episode/{episode}"
            params = {'api_key': self.api_key}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return None
            
            data = response.json()
            return data.get('name', '')
        
        except Exception as e:
            logger.error(f"Episode title error: {e}")
            return None
