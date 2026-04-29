import os
import pytest
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="session", autouse=True)
def qapp():
    """Create a QApplication instance for the entire test session."""
    # Force offscreen platform for headless environments
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app
