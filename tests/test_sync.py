import pytest
from unittest.mock import MagicMock
from core.sync import SyncManager

@pytest.fixture
def manager():
    mock_config = MagicMock()
    # Ensure config.get returns a safe value during initialization
    mock_config.get.return_value = None
    mock_widget = MagicMock()
    
    sync_mgr = SyncManager(mock_config, mock_widget)
    # Inject mocks to isolate logic
    sync_mgr.mpris = MagicMock()
    sync_mgr.parser = MagicMock()
    return sync_mgr

def test_sync_state_track_change(manager):
    """Verify that SyncManager detects track changes and updates lyrics."""
    mpris = manager.mpris
    mpris.find_active_player.return_value = True
    mpris.get_metadata.return_value = {"url": "/path/to/song.mp3", "title": "Song"}
    mpris.get_position.return_value = 10.0
    
    parser = manager.parser
    parser.parse.return_value = [{"time": 0, "text": "Start"}]
    parser.find_index.return_value = 0
    
    manager.sync_state()
    
    # Verify parser.parse was called with correct lrc path (only 1 arg)
    parser.parse.assert_called_with("/path/to/song.lrc")
    # Verify widget.set_lyrics was called with (lyrics_data, meta)
    manager.lyrics_widget.set_lyrics.assert_called_once()
    actual_meta = manager.lyrics_widget.set_lyrics.call_args[0][1]
    assert actual_meta["url"] == "/path/to/song.mp3"
    # Verify widget index update
    manager.lyrics_widget.set_current_index.assert_called_with(0)

def test_sync_state_position_update(manager):
    """Verify that SyncManager updates current index when position changes."""
    mpris = manager.mpris
    mpris.find_active_player.return_value = True
    mpris.get_metadata.return_value = {"url": "/path/to/song.mp3"}
    mpris.get_position.return_value = 20.0
    
    parser = manager.parser
    parser.find_index.return_value = 5
    
    manager.last_idx = 4 # Previous index
    
    manager.sync_state()
    
    # Index changed from 4 to 5, widget should be updated
    manager.lyrics_widget.set_current_index.assert_called_with(5)
    assert manager.last_idx == 5
