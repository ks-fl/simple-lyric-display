"""
Centralized theme definitions and system color resolution utilities.
"""

import os
import re
import subprocess

THEME_PRESETS = {
    "Default Dark": {"bg": "#1a1a1a", "fg": "#aaaaaa"},
    "Midnight": {"bg": "#0b0e14", "fg": "#d1d5db"},
    "Solarized Dark": {"bg": "#002b36", "fg": "#839496"},
    "Gruvbox": {"bg": "#282828", "fg": "#ebdbb2"},
    "Nord": {"bg": "#2e3440", "fg": "#d8dee9"},
    "Matrix": {"bg": "#000000", "fg": "#00ff00"},
    "Manual": {"bg": None, "fg": None},
}

# Qt Fusion style default colors
QT_FUSION_COLORS = {"bg": "#323232", "fg": "#f0f0f0"}


def _run(cmd):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip().strip("'")
    except Exception:
        return ""


def _parse_gtk_css_color(css_path, var_name):
    """Reads a @define-color value from a GTK CSS file, resolving aliases."""
    if not os.path.exists(css_path):
        return None
    try:
        with open(css_path, "r", errors="ignore") as f:
            content = f.read()
    except Exception:
        return None

    defines = {}
    for m in re.finditer(r"@define-color\s+(\w+)\s+([^;]+);", content):
        defines[m.group(1)] = m.group(2).strip()

    val = defines.get(var_name)
    if val and val.startswith("@"):
        val = defines.get(val[1:])
    return val if val and val.startswith("#") else None


def get_gtk_colors():
    """
    Reads the active GTK theme's background and foreground colors from
    the theme's gtk-3.0/gtk.css file. Falls back to dark defaults on failure.
    """
    theme_name = _run(["gsettings", "get", "org.cinnamon.desktop.interface", "gtk-theme"])
    if not theme_name:
        theme_name = _run(["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"])

    search_dirs = [
        os.path.expanduser(f"~/.themes/{theme_name}/gtk-3.0/gtk.css"),
        f"/usr/share/themes/{theme_name}/gtk-3.0/gtk.css",
        os.path.expanduser(f"~/.themes/{theme_name}/gtk-3.20/gtk.css"),
        f"/usr/share/themes/{theme_name}/gtk-3.20/gtk.css",
    ]

    bg, fg = None, None
    for path in search_dirs:
        bg = _parse_gtk_css_color(path, "bg_color") or _parse_gtk_css_color(path, "theme_bg_color")
        fg = _parse_gtk_css_color(path, "fg_color") or _parse_gtk_css_color(path, "theme_fg_color")
        if bg and fg:
            break

    return bg or "#1e1f29", fg or "#f8f8f2"


def get_system_colors():
    """
    Detects system light/dark preference via gsettings and returns appropriate colors.
    Falls back to GTK colors if color-scheme detection fails.
    """
    scheme = _run(["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"])
    if "dark" in scheme.lower():
        return get_gtk_colors()
    elif "light" in scheme.lower():
        return "#f5f5f5", "#1a1a1a"
    # Fallback: try GTK colors
    return get_gtk_colors()
