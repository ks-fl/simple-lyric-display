import pytest
from unittest.mock import patch, MagicMock
from core.mpris import MprisManager

@pytest.fixture
def mpris():
    return MprisManager()

def test_get_available_players(mpris):
    """Test parsing of DBus ListNames output."""
    mock_out = "(['org.mpris.MediaPlayer2.vlc', 'org.mpris.MediaPlayer2.spotify', 'org.freedesktop.DBus'],)"
    with patch.object(mpris, "_call_dbus", return_value=mock_out):
        players = mpris.get_available_players()
        assert "vlc" in players
        assert "spotify" in players
        assert "org.freedesktop.DBus" not in players

def test_find_active_player_priority(mpris):
    """Test player selection priority (Selected > Playing > First available)."""
    mpris.selected_player = "spotify"
    
    with patch.object(mpris, "get_available_players", return_value=["vlc", "spotify"]):
        # 1. Selected player exists
        assert mpris.find_active_player() == "org.mpris.MediaPlayer2.spotify"
        
        # 2. Selected player missing, fallback to Playing
        mpris.selected_player = "missing"
        def mock_call(dest, method, *args, **kwargs):
            if "spotify" in dest and any("PlaybackStatus" in str(a) for a in args):
                return "'Playing'"
            return "'Paused'"
            
        with patch.object(mpris, "_call_dbus", side_effect=mock_call):
            assert mpris.find_active_player() == "org.mpris.MediaPlayer2.spotify"

def test_get_metadata_parsing(mpris):
    """Test metadata extraction from complex DBus output."""
    mpris.current_player = "org.mpris.MediaPlayer2.vlc"
    mock_meta = """
    {'xesam:url': <'file:///home/user/music/song.mp3'>, 
     'xesam:title': <'Test Song'>, 
     'xesam:artist': <['Test Artist']>}
    """
    with patch.object(mpris, "_call_dbus", return_value=mock_meta):
        meta = mpris.get_metadata()
        assert meta["url"] == "/home/user/music/song.mp3"
        assert meta["title"] == "Test Song"
        assert meta["artist"] == "Test Artist"

def test_get_position_conversion(mpris):
    """Test conversion from microseconds (MPRIS) to seconds."""
    mpris.current_player = "org.mpris.MediaPlayer2.vlc"
    # 123.45 seconds = 123450000 microseconds
    with patch.object(mpris, "_call_dbus", return_value="(int64 123450000,)"):
        pos = mpris.get_position()
        assert pos == 123.45
