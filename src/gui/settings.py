from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QFontDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from utils.constants import THEME_PRESETS
from utils.logger import debug_log


class SettingsDialog(QDialog):
    """
    Settings dialog for configuring fonts, themes, and window properties.
    """

    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Settings")
        self.setFixedWidth(380)
        self.layout = QVBoxLayout(self)

        # 1. Media Player
        mpris_group = QGroupBox("Media Player")
        mpris_layout = QVBoxLayout(mpris_group)
        player_layout = QHBoxLayout()
        player_layout.addWidget(QLabel("Player:"))
        self.player_combo = QComboBox()
        available = self.parent_window.mpris.get_available_players()
        self.player_combo.addItem("Auto")
        for p in available:
            self.player_combo.addItem(p)

        current_selection = self.config.get(["mpris", "selected_player"])
        if current_selection in available:
            self.player_combo.setCurrentText(current_selection)
        else:
            self.player_combo.setCurrentIndex(0)

        self.player_combo.currentTextChanged.connect(self.update_selected_player)
        player_layout.addWidget(self.player_combo)
        mpris_layout.addLayout(player_layout)
        self.layout.addWidget(mpris_group)

        # 2. Typography
        font_group = QGroupBox("Typography")
        font_layout = QVBoxLayout(font_group)
        current_family = self.config.get(["font", "family"], "Sans Serif")
        self.font_btn = QPushButton(f"Font: {current_family}")
        self.font_btn.clicked.connect(self.change_font_family)
        font_layout.addWidget(self.font_btn)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(self.config.get(["font", "size"], 18))
        self.size_spin.valueChanged.connect(self.update_font_size)
        size_layout.addWidget(self.size_spin)
        font_layout.addLayout(size_layout)
        self.layout.addWidget(font_group)

        # 3. Theme
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["GTK", "Qt", "Custom"])
        self.mode_combo.setCurrentText(self.config.get("theme_mode", "GTK"))
        self.mode_combo.currentTextChanged.connect(self.update_theme_mode)
        mode_layout.addWidget(self.mode_combo)
        theme_layout.addLayout(mode_layout)

        self.custom_widget = QWidget()
        custom_layout = QVBoxLayout(self.custom_widget)
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(THEME_PRESETS.keys()))
        self.preset_combo.setCurrentText(self.config.get("theme_preset", "Default Dark"))
        self.preset_combo.currentTextChanged.connect(self.apply_preset)
        preset_layout.addWidget(self.preset_combo)
        custom_layout.addLayout(preset_layout)

        self.manual_color_widget = QWidget()
        colors_layout = QHBoxLayout(self.manual_color_widget)
        self.bg_btn = QPushButton("Background")
        self.bg_btn.clicked.connect(lambda: self.change_manual_color("theme_bg_color"))
        self.fg_btn = QPushButton("Text")
        self.fg_btn.clicked.connect(lambda: self.change_manual_color("theme_fg_color"))
        colors_layout.addWidget(self.bg_btn)
        colors_layout.addWidget(self.fg_btn)
        custom_layout.addWidget(self.manual_color_widget)
        theme_layout.addWidget(self.custom_widget)
        self.layout.addWidget(theme_group)

        # 4. Window
        window_group = QGroupBox("Window")
        win_layout = QVBoxLayout(window_group)
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(int(self.config.get(["window", "opacity"], 0.9) * 100))
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        opacity_layout.addWidget(self.opacity_slider)
        win_layout.addLayout(opacity_layout)
        self.layout.addWidget(window_group)

        self.layout.addStretch()
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        self.layout.addWidget(self.close_btn)

        self.update_ui_visibility()

    def update_selected_player(self, player_name):
        val = None if player_name == "Auto" else player_name
        self.config.set(["mpris", "selected_player"], val)
        self.parent_window.mpris.selected_player = val
        self.parent_window.mpris.find_active_player()

    def update_ui_visibility(self):
        is_custom = self.mode_combo.currentText() == "Custom"
        self.custom_widget.setVisible(is_custom)
        is_manual = self.preset_combo.currentText() == "Manual"
        self.manual_color_widget.setVisible(is_manual)

    def update_theme_mode(self, mode):
        self.config.set("theme_mode", mode)
        self.update_ui_visibility()
        self.parent_window.apply_theme_style()

    def apply_preset(self, preset_name):
        self.config.set("theme_preset", preset_name)
        if self.mode_combo.currentText() != "Custom":
            self.mode_combo.setCurrentText("Custom")
        self.update_ui_visibility()
        self.parent_window.lyrics_widget.repaint()

    def change_manual_color(self, config_key):
        current_color = QColor(self.config.get(config_key, "#ffffff"))
        color = QColorDialog.getColor(current_color, self, "Select Color")
        if color.isValid():
            self.config.set(config_key, color.name())
            if self.preset_combo.currentText() != "Manual":
                self.preset_combo.setCurrentText("Manual")
            self.parent_window.lyrics_widget.repaint()

    def update_font_size(self, value):
        self.config.set(["font", "size"], value)
        self.parent_window.lyrics_widget.repaint()

    def change_font_family(self):
        current_font = QFont(
            self.config.get(["font", "family"], "Sans Serif"),
            self.config.get(["font", "size"], 18),
        )
        res = QFontDialog.getFont(current_font, self)
        
        font, ok = None, False
        for item in res:
            if isinstance(item, QFont):
                font = item
            if isinstance(item, bool):
                ok = item
            
        if ok and font:
            family = font.family()
            size = font.pointSize()
            weight = font.weight()
            italic = font.italic()
            
            debug_log(f"UI: Font changed to {family}, Size={size}, Weight={weight}, Italic={italic}")
            
            self.config.set(["font", "family"], family)
            self.config.set(["font", "size"], size)
            self.config.set(["font", "weight"], int(weight))
            self.config.set(["font", "italic"], bool(italic))
            
            self.font_btn.setText(f"Font: {family}")
            self.size_spin.setValue(size)
            self.parent_window.lyrics_widget.repaint()

    def update_opacity(self, value):
        opacity = value / 100.0
        self.config.set(["window", "opacity"], opacity)
        self.parent_window.setWindowOpacity(opacity)
