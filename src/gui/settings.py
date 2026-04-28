from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QCheckBox, QPushButton, QFontDialog, QSpinBox, 
                             QColorDialog, QFrame, QComboBox, QGroupBox, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

THEME_PRESETS = {
    "Default Dark": {"bg": "#1a1a1a", "fg": "#aaaaaa"},
    "Midnight": {"bg": "#0b0e14", "fg": "#d1d5db"},
    "Solarized Dark": {"bg": "#002b36", "fg": "#839496"},
    "Gruvbox": {"bg": "#282828", "fg": "#ebdbb2"},
    "Nord": {"bg": "#2e3440", "fg": "#d8dee9"},
    "Matrix": {"bg": "#000000", "fg": "#00ff00"},
    "Manual": {"bg": None, "fg": None}
}

class SettingsDialog(QDialog):
    """
    Settings dialog for configuring fonts, themes, and window properties.
    """
    def __init__(self, parent, config):
        """
        Initializes the settings dialog.
        """
        super().__init__(parent)
        self.config = config
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        """
        Constructs the user interface for the settings dialog.
        """
        self.setWindowTitle("Settings")
        self.setFixedWidth(380)
        self.layout = QVBoxLayout(self)

        font_group = QGroupBox("Typography")
        font_layout = QVBoxLayout(font_group)
        
        self.font_btn = QPushButton(f"Font: {self.config.get('font', 'family')}")
        self.font_btn.clicked.connect(self.change_font_family)
        font_layout.addWidget(self.font_btn)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(self.config.get("font", "size"))
        self.size_spin.valueChanged.connect(self.update_font_size)
        size_layout.addWidget(self.size_spin)
        font_layout.addLayout(size_layout)
        self.layout.addWidget(font_group)

        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["System", "GTK", "Qt", "Custom"])
        self.mode_combo.setCurrentText(self.config.get("theme_mode"))
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

        window_group = QGroupBox("Window")
        win_layout = QVBoxLayout(window_group)
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(int(self.config.get("window", "opacity") * 100))
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        opacity_layout.addWidget(self.opacity_slider)
        win_layout.addLayout(opacity_layout)
        self.layout.addWidget(window_group)

        self.layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        self.layout.addWidget(self.close_btn)

        self.update_ui_visibility()

    def update_ui_visibility(self):
        """
        Updates the visibility of UI components based on theme mode and preset.
        """
        is_custom = self.mode_combo.currentText() == "Custom"
        self.custom_widget.setVisible(is_custom)
        
        is_manual = self.preset_combo.currentText() == "Manual"
        self.manual_color_widget.setVisible(is_manual)

    def update_theme_mode(self, mode):
        """
        Updates the theme mode and refreshes the UI.
        """
        self.config.set("theme_mode", mode)
        self.update_ui_visibility()
        self.parent_window.apply_theme_style()
        self.parent_window.update()
        self.parent_window.lyrics_widget.update()

    def apply_preset(self, preset_name):
        """
        Applies a predefined theme preset.
        """
        self.config.set("theme_preset", preset_name)
        self.update_ui_visibility()
        self.parent_window.update()
        self.parent_window.lyrics_widget.update()

    def change_manual_color(self, config_key):
        """
        Allows manual color selection and switches to manual preset.
        """
        current_color = QColor(self.config.get(config_key, "#ffffff"))
        color = QColorDialog.getColor(
            current_color, self, "Select Color",
            QColorDialog.ColorDialogOption.ShowAlphaChannel | QColorDialog.ColorDialogOption.DontUseNativeDialog
        )
        if color.isValid():
            self.config.set(config_key, color.name())
            self.parent_window.update()
            self.parent_window.lyrics_widget.update()

    def update_font_size(self, value):
        """
        Updates the font size.
        """
        self.config.set("font", "size", value)
        self.parent_window.lyrics_widget.update()

    def change_font_family(self):
        """
        Opens a font dialog.
        """
        current_font = QFont(self.config.get("font", "family"), self.config.get("font", "size"))
        font, ok = QFontDialog.getFont(current_font, self)
        if ok:
            family = font.family()
            self.config.set("font", "family", family)
            self.font_btn.setText(f"Font: {family}")
            self.parent_window.lyrics_widget.update()

    def update_opacity(self, value):
        """
        Updates window opacity.
        """
        opacity = value / 100.0
        self.config.set("window", "opacity", opacity)
        self.parent_window.setWindowOpacity(opacity)
