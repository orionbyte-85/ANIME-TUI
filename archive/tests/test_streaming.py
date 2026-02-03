#!/usr/bin/env python3
"""
Test script to verify streaming functionality with multiple anime
"""

from scraper import search_anime, get_anime_episodes, get_all_video_links

def test_anime(query, max_episodes=3):
    """Test an anime search and episode extraction"""
    print(f"\n{'='*60}")
    print(f"Testing: {query}")
    print(f"{'='*60}")
    
    # Search
    print(f"\n🔍 Searching for '{query}'...")
    results = search_anime(query)
    
    if not results:
        print(f"❌ No results found for '{query}'")
        return
    
    print(f"✓ Found {len(results)} results")
    anime = results[0]
    print(f"Selected: {anime['title']}")
    print(f"URL: {anime['url']}")
    
    # Get episodes
    print(f"\n📺 Fetching episodes...")
    episodes = get_anime_episodes(anime['url'])
    
    if not episodes:
        print(f"❌ No episodes found")
        return
    
    print(f"✓ Found {len(episodes)} episodes")
    
    # Test first few episodes
    test_count = min(max_episodes, len(episodes))
    print(f"\n🎬 Testing first {test_count} episodes for streaming options...")
    
    for i in range(test_count):
        ep = episodes[i]
        print(f"\n  Episode {ep['episode_number']}: {ep['title']}")
        print(f"  URL: {ep['url']}")
        
        links = get_all_video_links(ep['url'])
        
        if not links:
            print(f"  ❌ No links found")
            continue
        
        # Count streaming vs download options
        streaming = [l for l in links if l['url'].startswith('ajax:')]
        downloads = [l for l in links if not l['url'].startswith('ajax:')]
        
        print(f"  ✓ Found {len(links)} total options:")
        print(f"    - 🎬 Streaming: {len(streaming)}")
        print(f"    - 💾 Download: {len(downloads)}")
        
        # Show first streaming option
        if streaming:
            s = streaming[0]
            print(f"    First streaming option: [{s['quality']}] {s['server']}")

if __name__ == "__main__":
    # Test multiple anime
    test_queries = [
        "Naruto",
        "One Piece", 
        "Bleach"
    ]
    
    for query in test_queries:
        try:
            test_anime(query, max_episodes=2)
        except Exception as e:
            print(f"\n❌ Error testing '{query}': {e}")
    
    print(f"\n{'='*60}")
    print("Testing complete!")
    print(f"{'='*60}")
