from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from utils.logger import debug_log


class TrayManager:
    """
    Manages the system tray icon and its context menu.

    Provides a fallback mechanism if the system tray is not available or
    encounters D-Bus errors during initialization.
    """

    def __init__(self, parent, icon_style):
        """
        Initializes the TrayManager.

        Args:
            parent (MainWindow): The parent window.
            icon_style (QStyle.StandardPixmap): The icon style to use for the tray.
        """
        self.parent = parent
        self.tray = None

        if not QSystemTrayIcon.isSystemTrayAvailable():
            debug_log("TRAY: System tray is not available. Skipping tray icon initialization.")
            return

        try:
            self.tray = QSystemTrayIcon(parent)
            self.tray.setIcon(parent.style().standardIcon(icon_style))
            self.init_menu()
        except Exception as e:
            debug_log(f"TRAY ERROR: Failed to initialize system tray: {e}")
            self.tray = None

    def init_menu(self):
        """
        Creates and sets the context menu for the system tray icon.
        """
        if not self.tray:
            return

        menu = QMenu()
        menu.addAction("Settings", self.parent.open_settings)
        menu.addAction("Exit", self.parent.close)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def set_icon(self, icon):
        """
        Updates the tray icon.

        Args:
            icon (QIcon): The new icon to display.
        """
        if self.tray:
            self.tray.setIcon(icon)
