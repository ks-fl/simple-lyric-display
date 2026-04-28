import sys
from unittest.mock import MagicMock, patch
import pytest

# Create distinct mocks for each PySide6 module
mock_widgets = MagicMock()
class MockBase:
    def __init__(self, *args, **kwargs): pass
    def __getattr__(self, name): return MagicMock()
    def style(self): return MagicMock()
    def frameGeometry(self): return MagicMock()
    def geometry(self): return MagicMock()

mock_widgets.QMainWindow = MockBase
mock_widgets.QDialog = MockBase
mock_widgets.QWidget = MockBase

sys.modules["PySide6"] = MagicMock()
sys.modules["PySide6.QtCore"] = MagicMock()
sys.modules["PySide6.QtGui"] = MagicMock()
sys.modules["PySide6.QtWidgets"] = mock_widgets

from gui.window import MainWindow
from gui.settings import SettingsDialog

@pytest.fixture
def mock_config():
    config = MagicMock()
    # Provide sensible defaults for various config.get calls in SettingsDialog
    def side_effect(key, default=None):
        if "opacity" in str(key): return 0.9
        if "size" in str(key): return 18
        if "family" in str(key): return "Sans Serif"
        if "theme_mode" in str(key): return "GTK"
        if "theme_preset" in str(key): return "Light"
        return default
    config.get.side_effect = side_effect
    return config

def test_mainwindow_initialization(mock_config):
    """Ensure MainWindow initializes with correct components after refactoring."""
    with patch("gui.window.LyricsWidget"), \
         patch("gui.window.TrayManager"), \
         patch("gui.window.SyncManager") as MockSync:
        
        window = MainWindow(mock_config)
        assert hasattr(window, "sync_manager")
        MockSync.return_value.start.assert_called_once()

def test_settings_dialog_mpris_access(mock_config):
    """Ensure SettingsDialog accesses mpris via sync_manager correctly."""
    mock_window = MagicMock()
    mock_sync = MagicMock()
    mock_window.sync_manager = mock_sync
    mock_sync.mpris.get_available_players.return_value = ["Player1"]
    
    with patch("gui.settings.QVBoxLayout"), \
         patch("gui.settings.QHBoxLayout"), \
         patch("gui.settings.QGroupBox"), \
         patch("gui.settings.QLabel"), \
         patch("gui.settings.QComboBox"), \
         patch("gui.settings.QPushButton"), \
         patch("gui.settings.QSlider"), \
         patch("gui.settings.QSpinBox"):
        
        dialog = SettingsDialog(mock_window, mock_config)
        
        # Verify the access path fixed in settings.py
        mock_sync.mpris.get_available_players.assert_called()
        
        # Check update_selected_player path
        dialog.update_selected_player("Player1")
        assert mock_window.sync_manager.mpris.selected_player == "Player1"
        mock_window.sync_manager.mpris.find_active_player.assert_called()
