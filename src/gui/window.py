import sys

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QSizeGrip

from core.sync import SyncManager
from gui.tray import TrayManager
from gui.widgets.lyrics import LyricsWidget
from utils.constants import (
    RESIZE_GRIP_SIZE,
    THEME_PRESETS,
)
from utils.logger import debug_log
from utils.themes import get_gtk_colors, get_system_colors


class MainWindow(QMainWindow):
    """
    View controller for the main lyric display window.

    Handles window life cycle, user input events (dragging, context menu, resizing),
    and coordinates theme application.
    """

    def __init__(self, config):
        """
        Initializes the main window and its components.

        Args:
            config (Config): Application configuration manager.
        """
        super().__init__()
        self.config = config
        self.drag_pos = QPoint()

        self.init_ui()
        self.tray = TrayManager(self, self.style().StandardPixmap.SP_MediaPlay)
        self.apply_theme_style()

        # Initialize and start the synchronization manager
        self.sync_manager = SyncManager(self.config, self.lyrics_widget)
        self.sync_manager.start()

    def init_ui(self):
        """
        Setup basic window properties, flags, and layout.
        """
        self.setWindowTitle("Simple Lyric Display")
        self.setGeometry(
            self.config.get(["window", "x"], 100),
            self.config.get(["window", "y"], 100),
            self.config.get(["window", "width"], 600),
            self.config.get(["window", "height"], 400),
        )

        self.update_window_flags()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowOpacity(self.config.get(["window", "opacity"], 0.9))

        self.lyrics_widget = LyricsWidget(self, self.config)
        self.setCentralWidget(self.lyrics_widget)

        self.sizegrip = QSizeGrip(self.lyrics_widget)
        self.sizegrip.setFixedSize(RESIZE_GRIP_SIZE, RESIZE_GRIP_SIZE)

    def apply_theme_style(self):
        """
        Update the application look and feel (style and palette) based on current settings.
        """
        mode = self.config.get("theme_mode", "GTK")
        debug_log(f"UI: Applying theme style. Mode={mode}")

        style_name = "gtk2" if mode == "GTK" else "Fusion"
        QApplication.setStyle(style_name)

        self.lyrics_widget.setPalette(QApplication.palette())
        self.lyrics_widget.repaint()
        self.update()

    def get_effective_colors(self):
        """
        Resolve the current background, foreground, and highlight colors based on theme settings.

        Returns:
            tuple: A triplet of hex strings (bg_hex, fg_hex, hl_hex).
        """
        mode = self.config.get("theme_mode", "GTK")

        if mode == "GTK":
            return get_gtk_colors()
        if mode == "Qt":
            return get_system_colors()

        preset = self.config.get("theme_preset", "Light")
        if preset != "Manual":
            p = THEME_PRESETS.get(preset, THEME_PRESETS["Light"])
            return p["bg"], p["fg"], p.get("hl", "#0078d7")

        return (
            self.config.get("theme_bg_color", "#1a1a1a"),
            self.config.get("theme_fg_color", "#aaaaaa"),
            self.config.get("theme_hl_color", "#00ffff"),
        )

    def mousePressEvent(self, event):
        """
        Handles mouse press for window dragging.
        Uses startSystemMove() for better compatibility with Wayland/GNOME.

        Args:
            event (QMouseEvent): The mouse event object.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.windowHandle().startSystemMove()
            event.accept()

    def contextMenuEvent(self, event):
        """
        Handles the context menu event (right-click).

        Args:
            event (QContextMenuEvent): The context menu event object.
        """
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #222; color: #eee; border: 1px solid #444; }")

        ontop = menu.addAction("Always on Top")
        ontop.setCheckable(True)
        ontop.setChecked(self.config.get(["window", "always_on_top"], True))
        ontop.triggered.connect(self.toggle_always_on_top)

        menu.addSeparator()
        menu.addAction("Settings", self.open_settings)
        menu.addAction("Exit", self.close)
        menu.exec(self.mapToGlobal(event.pos()))

    def update_window_flags(self):
        """
        Update window flags (Frameless, Always on Top) based on configuration.
        """
        # Adding Qt.Window ensures it's treated as a top-level window
        flags = Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.CustomizeWindowHint
        
        if self.config.get(["window", "always_on_top"], True):
            flags |= Qt.WindowType.WindowStaysOnTopHint
            if sys.platform == "linux":
                # Qt.Tool often works better across various Linux WMs (KDE, XFCE, Gnome)
                # for keeping frameless windows on top without losing integration.
                flags |= Qt.WindowType.Tool
        self.setWindowFlags(flags)

    def toggle_always_on_top(self):
        """
        Toggle the 'Always on Top' property and refresh window flags.
        """
        current = self.config.get(["window", "always_on_top"], True)
        self.config.set(["window", "always_on_top"], not current)
        
        # On Linux/Gnome, re-applying flags often requires hiding the window first
        self.hide()
        self.update_window_flags()
        # Translucent background attribute must be re-set after setWindowFlags
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.show()

    def resizeEvent(self, event):
        """
        Reposition the resize grip when the window is resized.

        Args:
            event (QResizeEvent): The resize event object.
        """
        self.sizegrip.move(
            self.width() - self.sizegrip.width(), self.height() - self.sizegrip.height()
        )
        super().resizeEvent(event)

    def open_settings(self):
        """
        Open the settings dialog and apply theme updates upon closing.
        """
        from gui.settings import SettingsDialog

        dialog = SettingsDialog(self, self.config)
        dialog.exec()
        self.apply_theme_style()

    def closeEvent(self, event):
        """
        Save window geometry and clean up upon closing.

        Args:
            event (QCloseEvent): The close event object.
        """
        geo = self.geometry()
        self.config.set(["window", "x"], geo.x())
        self.config.set(["window", "y"], geo.y())
        self.config.set(["window", "width"], geo.width())
        self.config.set(["window", "height"], geo.height())
        self.config.save()
        super().closeEvent(event)
