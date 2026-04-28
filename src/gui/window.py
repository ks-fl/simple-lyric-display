import os

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QSizeGrip

from core.mpris import MprisManager
from core.parser import LrcParser
from gui.tray import TrayManager
from gui.widgets.lyrics import LyricsWidget
from utils.constants import (
    RESIZE_GRIP_SIZE,
    THEME_PRESETS,
    TIMER_INTERVAL_MS,
)
from utils.logger import debug_log
from utils.themes import get_gtk_colors, get_system_colors


class MainWindow(QMainWindow):
    """
    Main controller for the lyric display application.
    """

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.mpris = MprisManager(self.config.get(["mpris", "selected_player"]))
        self.parser = LrcParser()
        self.curr_track = ""
        self.last_idx = -1
        self.drag_pos = QPoint()

        self.init_ui()
        self.tray = TrayManager(self, self.style().StandardPixmap.SP_MediaPlay)
        self.apply_theme_style()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.sync_state)
        self.timer.start(TIMER_INTERVAL_MS)

    def init_ui(self):
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
        """Update the application look and feel based on current settings."""
        mode = self.config.get("theme_mode", "GTK")
        debug_log(f"UI: Applying theme style. Mode={mode}")
        if mode == "GTK":
            QApplication.setStyle("gtk2")
        else:
            QApplication.setStyle("Fusion")
        
        # Ensure we react to palette changes
        self.lyrics_widget.setPalette(QApplication.palette())
        self.lyrics_widget.repaint()
        self.update()

    def get_effective_colors(self):
        """Resolve the current background and foreground colors using theme utilities."""
        mode = self.config.get("theme_mode", "GTK")
        
        if mode == "GTK":
            return get_gtk_colors()
        elif mode == "Qt":
            return get_system_colors()
            
        # Custom Mode
        preset = self.config.get("theme_preset", "Default Dark")
        if preset != "Manual":
            p = THEME_PRESETS.get(preset, THEME_PRESETS["Default Dark"])
            return p["bg"], p["fg"]
        
        return self.config.get("theme_bg_color", "#1a1a1a"), self.config.get(
            "theme_fg_color", "#aaaaaa"
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def contextMenuEvent(self, event):
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
        flags = Qt.WindowType.FramelessWindowHint
        if self.config.get(["window", "always_on_top"], True):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

    def toggle_always_on_top(self):
        current = self.config.get(["window", "always_on_top"], True)
        self.config.set(["window", "always_on_top"], not current)
        self.update_window_flags()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.show()

    def resizeEvent(self, event):
        self.sizegrip.move(
            self.width() - self.sizegrip.width(), self.height() - self.sizegrip.height()
        )
        super().resizeEvent(event)

    def open_settings(self):
        from gui.settings import SettingsDialog
        debug_log("UI: Opening Settings")
        dialog = SettingsDialog(self, self.config)
        dialog.exec()
        self.apply_theme_style()

    def sync_state(self):
        """Timer callback to synchronize with the MPRIS player."""
        p = self.mpris.find_active_player()
        if not p:
            return
            
        meta = self.mpris.get_metadata()
        if not meta:
            return

        # Handle track change
        url = meta.get("url", "")
        if url != self.curr_track:
            self.curr_track = url
            lrc_path = os.path.splitext(url)[0] + ".lrc"
            self.lyrics_widget.set_lyrics(self.parser.parse(lrc_path), meta)
            self.last_idx = -2

        # Sync lyric position
        pos = self.mpris.get_position()
        idx = self.parser.find_index(pos)
        if idx != self.last_idx:
            self.last_idx = idx
            self.lyrics_widget.set_current_index(idx)

    def closeEvent(self, event):
        """Save window geometry on close."""
        geo = self.geometry()
        self.config.set(["window", "x"], geo.x())
        self.config.set(["window", "y"], geo.y())
        self.config.set(["window", "width"], geo.width())
        self.config.set(["window", "height"], geo.height())
        self.config.save()
        debug_log("UI: Closing Application")
        super().closeEvent(event)
