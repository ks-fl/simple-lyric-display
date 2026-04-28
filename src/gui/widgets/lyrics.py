from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QWidget

from utils.constants import (
    COLOR_CYAN,
    COLOR_ORANGE,
    INTRO_HEIGHT_FACTOR,
    LINE_HEIGHT_SPACING,
)
from utils.logger import debug_log


class LyricsWidget(QWidget):
    """
    Core widget for rendering synced lyrics with smooth animations and high readability.
    """

    def __init__(self, main_window, config):
        super().__init__(main_window)
        self.main_window = main_window
        self.config = config
        self.lyrics = []
        self.current_index = -1
        self.meta = {}

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def set_lyrics(self, lyrics, meta):
        """Update the lyric data and trigger a repaint."""
        self.lyrics = lyrics
        self.meta = meta
        self.update()

    def set_current_index(self, index):
        """Update the active lyric index and trigger a repaint if changed."""
        if self.current_index != index:
            self.current_index = index
            self.update()

    def paintEvent(self, event):
        """Main rendering logic."""
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

            # 1. Resolve Colors
            bg_hex, fg_hex = self.main_window.get_effective_colors()

            # 2. Setup Font
            font_cfg = self.config.get("font", {})
            f_family = font_cfg.get("family", "Sans Serif")
            f_size = font_cfg.get("size", 18)
            
            # Use cached values to avoid log flooding
            if not hasattr(self, "_last_debug_vals"):
                self._last_debug_vals = None
            
            curr_vals = (bg_hex, fg_hex, f_family, f_size)
            if curr_vals != self._last_debug_vals:
                debug_log(f"PAINT: BG={bg_hex}, FG={fg_hex}, Font={f_family}@{f_size}")
                self._last_debug_vals = curr_vals

            # 3. Draw Background
            painter.setBrush(QBrush(QColor(bg_hex)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(self.rect(), 15, 15)

            # 4. Apply Font
            font = QFont(f_family, f_size)
            weight_val = font_cfg.get("weight", QFont.Weight.Normal.value)
            font.setWeight(QFont.Weight(weight_val))
            font.setItalic(font_cfg.get("italic", False))
            
            painter.setFont(font)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            # 5. Layout Calculations
            fm = QFontMetrics(font)
            line_height = fm.height() + LINE_HEIGHT_SPACING
            intro_height = line_height * INTRO_HEIGHT_FACTOR
            center_y = self.height() / 2

            curr_y = 0 if self.current_index == -1 else intro_height + (self.current_index * line_height)
            scroll_offset = center_y - (line_height / 2) - curr_y

            # 6. Draw Track Metadata
            self._draw_outlined_text(
                painter, self.meta.get("title", ""), scroll_offset, QColor(COLOR_CYAN), True
            )
            self._draw_outlined_text(
                painter, self.meta.get("artist", ""), scroll_offset + 50, QColor(COLOR_ORANGE), False
            )

            # 7. Draw Lyric Lines
            for i, (_sec, text) in enumerate(self.lyrics):
                y = scroll_offset + intro_height + (i * line_height)
                if -line_height <= y <= self.height() + line_height:
                    is_curr = i == self.current_index
                    color = QColor(COLOR_CYAN) if is_curr else QColor(fg_hex)
                    self._draw_outlined_text(painter, text, y, color, is_curr)
        except Exception as e:
            # We don't have debug_log here if the import fails, 
            # but it shouldn't fail now that it's in a separate module.
            print(f"PAINT ERROR: {e}")
        finally:
            painter.end()

    def _draw_outlined_text(self, painter, text, y, color, bold):
        """Helper to draw text with a black outline for maximum visibility."""
        if not text:
            return

        fm = painter.fontMetrics()
        x = (self.width() - fm.horizontalAdvance(text)) / 2

        orig_font = painter.font()
        if bold:
            f = QFont(orig_font)
            f.setBold(True)
            painter.setFont(f)

        # Create text path for outlining
        path = QPainterPath()
        path.addText(x, y + fm.ascent(), painter.font(), text)

        # Draw the outline
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

        # Fill the text
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(path, QBrush(color))

        # Restore original font state
        painter.setFont(orig_font)
