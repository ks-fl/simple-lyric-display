"""
Global constants for Simple Lyric Display.
"""

# Colors
COLOR_CYAN = "#00ffff"
COLOR_ORANGE = "#f0ad4e"
COLOR_DEFAULT_BG = "#1a1a1a"
COLOR_DEFAULT_FG = "#f8f8f2"
COLOR_WHITE = "#ffffff"
COLOR_BLACK = "#111111"
COLOR_TRAY_ICON = "SP_MediaPlay"

# UI Dimensions & Logic
DEFAULT_WINDOW_WIDTH = 600
DEFAULT_WINDOW_HEIGHT = 400
DEFAULT_WINDOW_OPACITY = 0.9
RESIZE_GRIP_SIZE = 25
TIMER_INTERVAL_MS = 50

# Lyrics Rendering
LINE_HEIGHT_SPACING = 30
INTRO_HEIGHT_FACTOR = 2.5
TRANSITION_SPEED_MS = 50
SCROLL_ANIMATION_MS = 300

# File Paths
DEFAULT_CONFIG_DIR = "~/.config/simple-lyric-display"
CONFIG_FILENAME = "config.json"

# Theme Presets
THEME_PRESETS = {
    "Default Dark": {"bg": "#1a1a1a", "fg": "#aaaaaa"},
    "Midnight": {"bg": "#0b0e14", "fg": "#d1d5db"},
    "Solarized Dark": {"bg": "#002b36", "fg": "#839496"},
    "Gruvbox": {"bg": "#282828", "fg": "#ebdbb2"},
    "Nord": {"bg": "#2e3440", "fg": "#d8dee9"},
    "Matrix": {"bg": "#000000", "fg": "#00ff00"},
    "Manual": {"bg": None, "fg": None},
}
