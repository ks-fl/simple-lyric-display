"""
Application-wide constants and configuration defaults.
"""

# Window Properties
RESIZE_GRIP_SIZE = 20
TIMER_INTERVAL_MS = 500

# Lyric Rendering Constants
LINE_HEIGHT_SPACING = 20

# Rendering Aesthetics
OUTLINE_WIDTH = 3
OUTLINE_OPACITY = 230
ROUNDED_RECT_RADIUS = 15

# Theme Presets
THEME_PRESETS = {
    "Light": {"bg": "#f5f5f5", "fg": "#1a1a1a", "hl": "#0078d7"},
    "Dark": {"bg": "#1e1f29", "fg": "#f8f8f2", "hl": "#308cc6"},
    "Nord": {"bg": "#2e3440", "fg": "#eceff4", "hl": "#88c0d0"},
    "Solarized Dark": {"bg": "#002b36", "fg": "#839496", "hl": "#268bd2"},
    "Solarized Light": {"bg": "#fdf6e3", "fg": "#657b83", "hl": "#268bd2"},
    "Nord Light": {"bg": "#eceff4", "fg": "#2e3440", "hl": "#5e81ac"},
    "GitHub Light": {"bg": "#ffffff", "fg": "#24292e", "hl": "#0366d6"},
    "Manual": {},
}
