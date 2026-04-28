import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from gui.window import MainWindow
from utils.config import Config
from utils.paths import get_resource_path


def main():
    """
    Application entry point.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Simple Lyric Display")

    # Set app icon for the window and taskbar
    icon_path = get_resource_path("assets/icon.png")
    app.setWindowIcon(QIcon(icon_path))

    # Use Fusion style as a reliable base for Linux
    app.setStyle("Fusion")

    config = Config()

    window = MainWindow(config)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
