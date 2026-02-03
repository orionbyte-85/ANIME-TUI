import sys
from unittest.mock import MagicMock

# Mock curses BEFORE importing anime_tui
mock_curses = MagicMock()
sys.modules['curses'] = mock_curses

# Mock other dependencies to avoid side effects
sys.modules['scraper'] = MagicMock()
sys.modules['otakudesu_scraper'] = MagicMock()
sys.modules['sokuja_scraper'] = MagicMock()
sys.modules['embed_resolvers'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()
sys.modules['subprocess'] = MagicMock()

import anime_tui

def test_play_with_url():
    print("Testing play_with_url...")
    
    # Setup mock
    stdscr = MagicMock()
    app = anime_tui.AnimeTUI(stdscr)
    
    # Mock selected anime/episode
    app.selected_anime = {'provider_display': 'TestProvider'}
    app.selected_provider = 'test'
    
    # Mock link data
    link_data = {
        'url': 'http://test.com/video.mp4',
        'server': 'TestServer',
        'type': 'stream'
    }
    
    # Mock curses.endwin to raise error if called twice without reset
    endwin_called = False
    
    def side_effect_endwin():
        nonlocal endwin_called
        if endwin_called:
            print("❌ CRASH: curses.endwin() called twice!")
            raise Exception("_curses.error: endwin() returned ERR")
        endwin_called = True
        print("✓ curses.endwin() called once")
        
    mock_curses.endwin.side_effect = side_effect_endwin
    
    try:
        app.play_with_url(link_data, "Test Title")
        print("✅ Test Passed: No crash")
    except Exception as e:
        print(f"❌ Test Failed: {e}")

if __name__ == "__main__":
    test_play_with_url()
