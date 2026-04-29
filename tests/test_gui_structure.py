import sys
import pytest
from unittest.mock import MagicMock, patch

# Define the mocking logic in a controlled way
def get_pyside_mocks():
    mock_widgets = MagicMock()
    class MockBase:
        def __init__(self, *args, **kwargs): pass
        def __getattr__(self, name): return MagicMock()
        def style(self): return MagicMock()
        def frameGeometry(self): return MagicMock()
        def geometry(self): return MagicMock()
        def hide(self): pass
        def show(self): pass
        def setWindowFlags(self, flags): pass
        def setAttribute(self, attr, on): pass
        def windowHandle(self): return MagicMock()

    mock_widgets.QMainWindow = MockBase
    mock_widgets.QDialog = MockBase
    mock_widgets.QWidget = MockBase
    
    return {
        "PySide6": MagicMock(),
        "PySide6.QtCore": MagicMock(),
        "PySide6.QtGui": MagicMock(),
        "PySide6.QtWidgets": mock_widgets
    }

@pytest.fixture
def mock_pyside():
    """Locally patch sys.modules to avoid interference with other tests."""
    with patch.dict(sys.modules, get_pyside_mocks()):
        # We must re-import the modules under test inside the patch
        # or use a fresh import if possible.
        if "gui.window" in sys.modules: del sys.modules["gui.window"]
        if "gui.settings" in sys.modules: del sys.modules["gui.settings"]
        from gui.window import MainWindow
        from gui.settings import SettingsDialog
        yield MainWindow, SettingsDialog

@pytest.fixture
def mock_config():
    config = MagicMock()
    def side_effect(key, default=None):
        if "opacity" in str(key): return 0.9
        if "size" in str(key): return 18
        if "family" in str(key): return "Sans Serif"
        if "theme_mode" in str(key): return "GTK"
        if "theme_preset" in str(key): return "Light"
        return default
    config.get.side_effect = side_effect
    return config

def test_mainwindow_initialization(mock_pyside, mock_config):
    MainWindow, _ = mock_pyside
    with patch("gui.window.TrayManager"), \
         patch("gui.window.SyncManager") as MockSync, \
         patch("gui.window.LyricsWidget"), \
         patch("gui.window.QSizeGrip"):
        
        window = MainWindow(mock_config)
        assert hasattr(window, "sync_manager")
        MockSync.return_value.start.assert_called_once()

def test_settings_dialog_mpris_access(mock_pyside, mock_config):
    _, SettingsDialog = mock_pyside
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
        mock_sync.mpris.get_available_players.assert_called()
        
        dialog.update_selected_player("Player1")
        assert mock_window.sync_manager.mpris.selected_player == "Player1"

def test_mainwindow_toggle_always_on_top(mock_pyside, mock_config):
    MainWindow, _ = mock_pyside
    with patch("gui.window.TrayManager"), \
         patch("gui.window.SyncManager"), \
         patch("gui.window.LyricsWidget"), \
         patch("gui.window.QSizeGrip"):
        
        # In this mock environment, MainWindow inherits from our MockBase
        window = MainWindow(mock_config)
        
        # We need to mock methods on the instance which is already a MockBase
        with patch.object(window, "hide") as mock_hide, \
             patch.object(window, "show") as mock_show, \
             patch.object(window, "setWindowFlags") as mock_set_flags, \
             patch.object(window, "setAttribute") as mock_set_attr:
            
            window.toggle_always_on_top()
            
            mock_hide.assert_called_once()
            mock_set_flags.assert_called_once()
            from unittest.mock import ANY
            mock_set_attr.assert_called_with(ANY, True)
            mock_show.assert_called_once()
