import os

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QPainter,
    QPainterPath,
    QPalette,
    QPen,
)
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QSizeGrip, QSystemTrayIcon, QWidget

from core.mpris import MprisManager
from core.parser import LrcParser
from gui.settings import THEME_PRESETS


class LyricsWidget(QWidget):
    """
    Restored rendering widget with custom drawing.
    """

    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.main_window = parent
        self.config = config
        self.lyrics = []
        self.current_index = -1
        self.meta = {}

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def set_lyrics(self, lyrics, meta):
        self.lyrics = lyrics
        self.meta = meta
        self.update()

    def set_current_index(self, index):
        if self.current_index != index:
            self.current_index = index
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        bg_hex, fg_hex = self.main_window.get_effective_colors()

        # 1. Background
        painter.setBrush(QBrush(QColor(bg_hex)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

        # 2. Reset brush for text
        painter.setBrush(Qt.BrushStyle.NoBrush)

        font_cfg = self.config.get("font")
        font = QFont(font_cfg["family"], font_cfg["size"])
        painter.setFont(font)

        fm = QFontMetrics(font)
        line_height = fm.height() + 30
        intro_height = line_height * 2.5
        center_y = self.height() / 2

        curr_y = (
            0 if self.current_index == -1 else intro_height + (self.current_index * line_height)
        )
        scroll_offset = center_y - (line_height / 2) - curr_y

        # Draw Metadata
        self.draw_text_with_outline(
            painter, self.meta.get("title", ""), scroll_offset, QColor("#00ffff"), True
        )
        self.draw_text_with_outline(
            painter, self.meta.get("artist", ""), scroll_offset + 50, QColor("#f0ad4e"), False
        )

        # Draw Lyrics
        for i, (_sec, text) in enumerate(self.lyrics):
            y = scroll_offset + intro_height + (i * line_height)
            if -line_height <= y <= self.height() + line_height:
                is_curr = i == self.current_index
                color = QColor("#00ffff") if is_curr else QColor(fg_hex)
                self.draw_text_with_outline(painter, text, y, color, is_curr)

    def draw_text_with_outline(self, painter, text, y, color, bold):
        if not text:
            return
        fm = painter.fontMetrics()
        x = (self.width() - fm.horizontalAdvance(text)) / 2

        orig_font = painter.font()
        if bold:
            f = QFont(orig_font)
            f.setBold(True)
            painter.setFont(f)

        path = QPainterPath()
        path.addText(x, y + fm.ascent(), painter.font(), text)

        painter.setPen(
            QPen(
                QColor(0, 0, 0, 230),
                3,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.drawPath(path)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(path, QBrush(color))

        painter.setFont(orig_font)


class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.mpris = MprisManager(self.config.get("mpris", "priority"))
        self.parser = LrcParser()
        self.curr_track = ""
        self.last_idx = -1
        self.drag_pos = QPoint()

        self.init_ui()
        self.init_tray()
        self.apply_theme_style()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_lyrics)
        self.timer.start(50)

    def init_ui(self):
        self.setWindowTitle("Simple Lyric Display")
        win_cfg = self.config.get("window")
        self.setGeometry(win_cfg["x"], win_cfg["y"], win_cfg["width"], win_cfg["height"])

        self.update_window_flags()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowOpacity(win_cfg["opacity"])

        self.lyrics_widget = LyricsWidget(self, self.config)
        self.setCentralWidget(self.lyrics_widget)

        self.sizegrip = QSizeGrip(self.lyrics_widget)
        self.sizegrip.setFixedSize(25, 25)

    def apply_theme_style(self):
        mode = self.config.get("theme_mode", "System")
        if mode == "GTK":
            QApplication.setStyle("gtk2")
        elif mode == "Qt":
            QApplication.setStyle("Fusion")
        else:
            QApplication.setStyle("Fusion")
        self.update()

    def get_effective_colors(self):
        mode = self.config.get("theme_mode", "System")
        if mode != "Custom":
            pal = QApplication.palette()
            bg = pal.color(QPalette.ColorRole.Window).name()
            fg = pal.color(QPalette.ColorRole.WindowText).name()
            bg_c = QColor(bg)
            fg_c = QColor(fg)
            if abs(bg_c.lightness() - fg_c.lightness()) < 60:
                fg = "#ffffff" if bg_c.lightness() < 128 else "#000000"
            return bg, fg

        preset = self.config.get("theme_preset", "Default Dark")
        if preset != "Manual":
            p = THEME_PRESETS.get(preset, THEME_PRESETS["Default Dark"])
            return p["bg"], p["fg"]
        return self.config.get("theme_bg_color"), self.config.get("theme_fg_color")

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
        ontop.setChecked(self.config.get("window", "always_on_top"))
        ontop.triggered.connect(self.toggle_always_on_top)
        menu.addSeparator()
        menu.addAction("Settings", self.open_settings)
        menu.addAction("Exit", self.close)
        menu.exec(self.mapToGlobal(event.pos()))

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MediaPlay))
        tray_menu = QMenu()
        tray_menu.addAction("Settings", self.open_settings)
        tray_menu.addAction("Exit", self.close)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def update_window_flags(self):
        flags = Qt.WindowType.FramelessWindowHint
        if self.config.get("window", "always_on_top"):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

    def toggle_always_on_top(self):
        self.config.set("window", "always_on_top", not self.config.get("window", "always_on_top"))
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

        dialog = SettingsDialog(self, self.config)
        dialog.exec()
        self.apply_theme_style()

    def update_lyrics(self):
        p = self.mpris.find_active_player()
        if not p:
            return
        meta = self.mpris.get_metadata()
        if not meta:
            return
        url = meta.get("url", "")
        if url != self.curr_track:
            self.curr_track = url
            lrc_path = os.path.splitext(url)[0] + ".lrc"
            self.lyrics_widget.set_lyrics(self.parser.parse(lrc_path), meta)
            self.last_idx = -2
        pos = self.mpris.get_position()
        idx = self.parser.find_index(pos)
        if idx != self.last_idx:
            self.last_idx = idx
            self.lyrics_widget.set_current_index(idx)

    def closeEvent(self, event):
        geo = self.geometry()
        self.config.set("window", "x", geo.x())
        self.config.set("window", "y", geo.y())
        self.config.set("window", "width", geo.width())
        self.config.set("window", "height", geo.height())
        self.config.save()
        super().closeEvent(event)
