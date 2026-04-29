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

    def mousePressEvent(self, event):
        """
        Ignores mouse press events to allow them to bubble up to the parent window.

        Args:
            event (QMouseEvent): The mouse event object.
        """
        event.ignore()

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
        f_size = font_cfg.get("size", 12)

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
        line_spacing = LINE_HEIGHT_SPACING
        base_line_height = fm.height()

        # Determine outline color
        bg_color = QColor(bg_hex)
        is_light_bg = bg_color.lightness() > 160
        outline_color = (
            QColor(255, 255, 255, OUTLINE_OPACITY)
            if is_light_bg
            else QColor(0, 0, 0, OUTLINE_OPACITY)
        )

        # Calculate heights for all lines (considering wrapping)
        max_w = self.width() - 40  # Margin
        wrapped_lines = []
        for _, text in self.lyrics:
            lines = self._get_wrapped_lines(text, font, max_w)
            wrapped_lines.append(lines)

        meta_title = self._get_wrapped_lines(self.meta.get("title", ""), font, max_w)
        meta_artist = self._get_wrapped_lines(self.meta.get("artist", ""), font, max_w)

        # Calculate vertical positions
        meta_spacing = base_line_height * 1.5
        y_cursor = 0

        # Scroll calculation: center on current line
        center_y = self.height() / 2

        # Calculate Y for current line
        curr_y_target = 0
        current_block_y = 0

        # Accumulate height for meta
        current_block_y += (len(meta_title) + len(meta_artist)) * (
            base_line_height + line_spacing
        ) + meta_spacing

        # Accumulate height up to current index
        for i in range(len(wrapped_lines)):
            block_h = len(wrapped_lines[i]) * (base_line_height + line_spacing)
            if i == self.current_index:
                curr_y_target = current_block_y + (block_h / 2)
                break
            current_block_y += block_h

        scroll_offset = center_y - curr_y_target if self.current_index != -1 else 20
        y_cursor = scroll_offset

        # 5. Draw Track Metadata
        y_cursor = self._draw_wrapped_block(
            painter,
            meta_title,
            y_cursor,
            QColor(hl_hex),
            True,
            outline_color,
            base_line_height,
            line_spacing,
        )
        y_cursor = self._draw_wrapped_block(
            painter,
            meta_artist,
            y_cursor,
            QColor(fg_hex),
            False,
            outline_color,
            base_line_height,
            line_spacing,
        )
        y_cursor += meta_spacing

        # 6. Draw Lyric Lines
        for i, lines in enumerate(wrapped_lines):
            block_h = len(lines) * (base_line_height + line_spacing)
            if y_cursor + block_h > 0 and y_cursor < self.height():
                is_curr = i == self.current_index
                color = QColor(hl_hex) if is_curr else QColor(fg_hex)
                self._draw_wrapped_block(
                    painter,
                    lines,
                    y_cursor,
                    color,
                    False,
                    outline_color,
                    base_line_height,
                    line_spacing,
                )
            y_cursor += block_h

    def _get_wrapped_lines(self, text, font, max_width):
        """Helper to wrap text into multiple lines."""
        from PySide6.QtGui import QTextLayout

        if not text:
            return []

        layout = QTextLayout(text, font)
        layout.beginLayout()
        lines = []
        while True:
            line = layout.createLine()
            if not line.isValid():
                break
            line.setLineWidth(max_width)
            lines.append(text[line.textStart() : line.textStart() + line.textLength()])
        layout.endLayout()
        return lines

    def _draw_wrapped_block(self, painter, lines, y, color, bold, outline_color, line_h, spacing):
        """Draws a block of wrapped lines."""
        for line_text in lines:
            self._draw_single_line(painter, line_text, y, color, bold, outline_color)
            y += line_h + spacing
        return y

    def _draw_single_line(self, painter, text, y, color, bold, outline_color):
        """Draws a single line of outlined text (internal)."""
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
                outline_color,
                OUTLINE_WIDTH,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.drawPath(path)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(path, QBrush(color))
        painter.setFont(orig_font)
