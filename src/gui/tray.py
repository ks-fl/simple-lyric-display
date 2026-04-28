from PySide6.QtWidgets import QMenu, QSystemTrayIcon


class TrayManager:
    """
    Manages the system tray icon and its context menu.
    """

    def __init__(self, parent, icon_style):
        self.parent = parent
        self.tray = QSystemTrayIcon(parent)
        self.tray.setIcon(parent.style().standardIcon(icon_style))
        self.init_menu()

    def init_menu(self):
        menu = QMenu()
        menu.addAction("Settings", self.parent.open_settings)
        menu.addAction("Exit", self.parent.close)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def set_icon(self, icon):
        self.tray.setIcon(icon)
