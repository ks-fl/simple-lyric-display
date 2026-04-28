from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QWidget

from utils.constants import COLOR_CYAN, COLOR_ORANGE, INTRO_HEIGHT_FACTOR, LINE_HEIGHT_SPACING


class LyricsWidget(QWidget):
    """
    Core widget for rendering synced lyrics with smooth animations.
    """

    def __init__(self, main_window, config):
        super().__init__(main_window)
        self.main_window = main_window
        self.config = config
        self.lyrics = []
        self.current_index = -1
        self.meta = {}
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_lyrics(self, lyrics, meta):
        self.lyrics = lyrics
        self.meta = meta
        self.current_index = -1
        self.repaint()

    def update_index(self, index):
        if self.current_index != index:
            self.current_index = index
            self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

            bg_hex, fg_hex = self.main_window.get_effective_colors()

            # 1. Background
            painter.save()
            painter.setBrush(QBrush(QColor(bg_hex)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(self.rect(), 15, 15)
            painter.restore()

            # 2. Text Setup
            font_cfg = self.config.get("font", default={})
            f_family = font_cfg.get("family", "Sans Serif")
            f_size = font_cfg.get("size", 14)
            if not f_size or f_size <= 0:
                f_size = 14

            font = QFont(f_family, f_size)
            painter.setFont(font)
            fm = QFontMetrics(font)
            line_height = fm.height() + LINE_HEIGHT_SPACING
            intro_height = line_height * INTRO_HEIGHT_FACTOR
            center_y = self.height() / 2

            curr_y = (
                0 if self.current_index == -1 else intro_height + (self.current_index * line_height)
            )
            scroll_offset = center_y - (line_height / 2) - curr_y

            # Meta Information (Title/Artist)
            self._draw_meta_info(painter, scroll_offset)

            # Lyrics
            self._draw_lyrics_lines(painter, scroll_offset, line_height, intro_height, fg_hex)
        finally:
            painter.end()

    def _draw_meta_info(self, painter, scroll_offset):
        self.draw_lyric_line(
            painter, self.meta.get("title", ""), scroll_offset, QColor(COLOR_CYAN), True
        )
        self.draw_lyric_line(
            painter, self.meta.get("artist", ""), scroll_offset + 50, QColor(COLOR_ORANGE), False
        )

    def _draw_lyrics_lines(self, painter, scroll_offset, line_height, intro_height, fg_hex):
        for i, (_, text) in enumerate(self.lyrics):
            y = scroll_offset + intro_height + (i * line_height)
            # Only draw visible lines (plus buffer)
            if -line_height <= y <= self.height() + line_height:
                is_curr = i == self.current_index
                color = QColor(COLOR_CYAN) if is_curr else QColor(fg_hex)
                self.draw_lyric_line(painter, text, y, color, is_curr)

    def draw_lyric_line(self, painter, text, y, color, bold):
        if not text:
            return

        painter.save()
        if bold:
            orig_font = painter.font()
            f = QFont(orig_font)
            f.setBold(True)
            painter.setFont(f)

        painter.setPen(QPen(color))
        # Center alignment
        rect = self.rect()
        rect.setTop(int(y))
        rect.setHeight(100)  # Constant height for text block
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop, text)
        painter.restore()
