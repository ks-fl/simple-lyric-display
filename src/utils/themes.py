"""
Centralized theme definitions and system color resolution utilities.
"""

import os
import re
import subprocess

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from utils.config import debug_log

# Qt Fusion style default colors
QT_FUSION_COLORS = {"bg": "#323232", "fg": "#f0f0f0"}


def _run(cmd):
    try:
        res = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip().strip("'")
        return res
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
    Reads the active GTK theme's background and foreground colors.
    """
    theme_name = (
        _run(["gsettings", "get", "org.cinnamon.desktop.interface", "gtk-theme"]) or
        _run(["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"]) or
        _run(["gsettings", "get", "org.mate.interface", "gtk-theme"])
    )
    
    if not theme_name:
        return "#1e1f29", "#f8f8f2"

    search_dirs = [
        os.path.expanduser(f"~/.themes/{theme_name}/gtk-3.0/gtk.css"),
        f"/usr/share/themes/{theme_name}/gtk-3.0/gtk.css",
        os.path.expanduser(f"~/.themes/{theme_name}/gtk-3.20/gtk.css"),
        f"/usr/share/themes/{theme_name}/gtk-3.20/gtk.css",
        f"/usr/share/themes/{theme_name}/gtk-3.0/gtk-main.css",
    ]

    bg, fg = None, None
    for path in search_dirs:
        if os.path.exists(path):
            bg = _parse_gtk_css_color(path, "bg_color") or \
                 _parse_gtk_css_color(path, "theme_bg_color") or \
                 _parse_gtk_css_color(path, "base_color")
            fg = _parse_gtk_css_color(path, "fg_color") or \
                 _parse_gtk_css_color(path, "theme_fg_color") or \
                 _parse_gtk_css_color(path, "text_color")
            if bg and fg:
                break

    return bg or "#1e1f29", fg or "#f8f8f2"


def get_system_colors():
    """
    Retrieves colors from the current Qt application palette.
    This ensures 'Qt' mode looks different from 'GTK' mode.
    """
    try:
        pal = QApplication.palette()
        bg = pal.color(QPalette.ColorRole.Window).name()
        fg = pal.color(QPalette.ColorRole.WindowText).name()
        debug_log(f"THEMES: Resolved Qt palette: BG={bg}, FG={fg}")
        return bg, fg
    except Exception as e:
        debug_log(f"THEMES ERROR: Failed to resolve Qt palette: {e}")
        return "#efefef", "#111111"
