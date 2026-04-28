import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from gui.window import MainWindow
from utils.config import Config

def main():
    """
    Application entry point.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Simple Lyric Display")
    
    # Use Fusion style as a reliable base for Linux
    app.setStyle("Fusion")
    
    config = Config()
    
    window = MainWindow(config)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
