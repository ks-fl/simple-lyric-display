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
    LINE_HEIGHT_SPACING,
    OUTLINE_OPACITY,
    OUTLINE_WIDTH,
    ROUNDED_RECT_RADIUS,
)
from utils.logger import debug_log


class LyricsWidget(QWidget):
    """
    Core widget for rendering synced lyrics with smooth animations and high readability.

    This widget handles the dynamic layout of lyrics, current line highlighting,
    and automatic vertical scrolling.
    """

    def __init__(self, main_window, config):
        """
        Initializes the LyricsWidget.

        Args:
            main_window (MainWindow): The parent main window (used to get colors).
            config (Config): Application configuration manager.
        """
        super().__init__(main_window)
        self.main_window = main_window
        self.config = config
        self.lyrics = []
        self.current_index = -1
        self.meta = {}
        self._last_debug_vals = None

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def set_lyrics(self, lyrics, meta):
        """
        Updates the lyric data and track metadata.

        Args:
            lyrics (list): A list of (timestamp, text) tuples.
            meta (dict): Track metadata (title, artist, etc.).
        """
        self.lyrics = lyrics
        self.meta = meta
        self.update()

    def set_current_index(self, index):
        """
        Updates the active lyric line index.

        Args:
            index (int): The index of the line to highlight.
        """
        if self.current_index != index:
            self.current_index = index
            self.update()

    def paintEvent(self, event):
        """
        Standard Qt paint event.

        Args:
            event (QPaintEvent): The paint event object.
        """
        painter = QPainter(self)
        try:
            self._render_contents(painter)
        except Exception as e:
            debug_log(f"PAINT ERROR: {e}")
        finally:
            painter.end()

    def _render_contents(self, painter):
        """
        Internal render flow that performs the actual drawing.

        Args:
            painter (QPainter): The active painter object.
        """
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # 1. Resolve Style & Colors
        bg_hex, fg_hex, hl_hex = self.main_window.get_effective_colors()
        font_cfg = self.config.get("font", {})
        f_family = font_cfg.get("family", "Sans Serif")
        f_size = font_cfg.get("size", 18)

        # Log changes only
        curr_vals = (bg_hex, fg_hex, hl_hex, f_family, f_size)
        if curr_vals != self._last_debug_vals:
            debug_log(f"PAINT: BG={bg_hex}, FG={fg_hex}, HL={hl_hex}, Font={f_family}@{f_size}")
            self._last_debug_vals = curr_vals

        # 2. Draw Background
        painter.setBrush(QBrush(QColor(bg_hex)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), ROUNDED_RECT_RADIUS, ROUNDED_RECT_RADIUS)

        # 3. Setup Typography
        font = QFont(f_family, f_size)
        weight_val = font_cfg.get("weight", QFont.Weight.Normal.value)
        font.setWeight(QFont.Weight(weight_val))
        font.setItalic(font_cfg.get("italic", False))

        painter.setFont(font)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # 4. Layout Calculations
        fm = QFontMetrics(font)
        line_height = fm.height() + LINE_HEIGHT_SPACING

        # Spacing for metadata (Title, Artist)
        meta_spacing = line_height * 1.2
        # Start of lyrics should be below metadata
        intro_height = meta_spacing * 2.5

        center_y = self.height() / 2

        # Scroll calculation: center on current line
        curr_y = (
            0 if self.current_index == -1 else intro_height + (self.current_index * line_height)
        )
        scroll_offset = center_y - (line_height / 2) - curr_y

        # Determine outline color based on background brightness
        bg_color = QColor(bg_hex)
        is_light_bg = bg_color.lightness() > 160
        outline_color = (
            QColor(255, 255, 255, OUTLINE_OPACITY)
            if is_light_bg
            else QColor(0, 0, 0, OUTLINE_OPACITY)
        )

        # 5. Draw Track Metadata
        self._draw_outlined_text(
            painter, self.meta.get("title", ""), scroll_offset, QColor(hl_hex), True, outline_color
        )
        self._draw_outlined_text(
            painter,
            self.meta.get("artist", ""),
            scroll_offset + meta_spacing,
            QColor(fg_hex),
            False,
            outline_color,
        )

        # 6. Draw Lyric Lines
        for i, (_sec, text) in enumerate(self.lyrics):
            y = scroll_offset + intro_height + (i * line_height)
            # Simple frustum culling
            if -line_height <= y <= self.height() + line_height:
                is_curr = i == self.current_index
                color = QColor(hl_hex) if is_curr else QColor(fg_hex)
                self._draw_outlined_text(painter, text, y, color, False, outline_color)

    def _draw_outlined_text(self, painter, text, y, color, bold, outline_color):
        """
        Helper to draw text with a dynamic outline for maximum visibility.

        Args:
            painter (QPainter): The active painter object.
            text (str): The text content to draw.
            y (float): Vertical position.
            color (QColor): Fill color of the text.
            bold (bool): Whether to use a bold font.
            outline_color (QColor): Color of the outline pen.
        """
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
                outline_color,
                OUTLINE_WIDTH,
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
