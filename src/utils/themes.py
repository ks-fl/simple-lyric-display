"""
Centralized theme definitions and system color resolution utilities.

This module provides tools to detect GTK themes, parse CSS colors, and interact
with the system palette.
"""

import os
import re
import subprocess

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from utils.logger import debug_log

# Fallback defaults
DEFAULT_BG = "#1e1f29"
DEFAULT_FG = "#f8f8f2"
DEFAULT_HL = "#308cc6"


def _run(args):
    """
    Safely execute a shell command and return the stripped output.

    Args:
        args (list): List of command arguments.

    Returns:
        str: The command output or an empty string if it fails.
    """
    try:
        res = subprocess.check_output(args, stderr=subprocess.DEVNULL)
        return res.decode().strip().strip("'")
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return ""


def _parse_gtk_css_color(css_path, var_name):
    """
    Reads a @define-color value from a GTK CSS file, resolving aliases and ignoring comments.

    Args:
        css_path (str): Path to the GTK CSS file.
        var_name (str): The name of the color variable to find.

    Returns:
        str | None: The resolved hex color string or None if not found.
    """
    if not os.path.exists(css_path):
        return None

    try:
        with open(css_path, "r", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        debug_log(f"THEMES: Error reading {css_path}: {e}")
        return None

    # 1. Strip multi-line comments: /* ... */
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

    # 2. Capture all @define-color definitions
    defines = {
        m.group(1): m.group(2).strip()
        for m in re.finditer(r"@define-color\s+(\w+)\s+([^;]+);", content)
    }

    val = defines.get(var_name)

    # 3. Simple recursive resolution (max 3 levels)
    for _ in range(3):
        if val and val.startswith("@"):
            val = defines.get(val[1:])
        else:
            break

    if val and val.startswith("#"):
        return val

    return None


def get_gtk_colors():
    """
    Reads the active GTK theme's background, foreground, and highlight colors.

    Attempts to detect the theme name from common gsettings schemas and searches
    for standard color definitions in the theme's CSS files.

    Returns:
        tuple: (bg, fg, hl) hex color strings.
    """
    gsettings_targets = [
        ["org.cinnamon.desktop.interface", "gtk-theme"],
        ["org.gnome.desktop.interface", "gtk-theme"],
        ["org.mate.interface", "gtk-theme"],
    ]

    theme_name = ""
    for schema, key in gsettings_targets:
        theme_name = _run(["gsettings", "get", schema, key])
        if theme_name:
            break

    if not theme_name:
        return DEFAULT_BG, DEFAULT_FG, DEFAULT_HL

    css_locations = [
        f"~/.themes/{theme_name}/gtk-3.0/gtk.css",
        f"/usr/share/themes/{theme_name}/gtk-3.0/gtk.css",
        f"~/.themes/{theme_name}/gtk-3.20/gtk.css",
        f"/usr/share/themes/{theme_name}/gtk-3.20/gtk.css",
    ]

    bg, fg, hl = None, None, None
    for loc in css_locations:
        path = os.path.expanduser(loc)
        if not os.path.exists(path):
            continue

        bg = (
            bg
            or _parse_gtk_css_color(path, "theme_bg_color")
            or _parse_gtk_css_color(path, "bg_color")
            or _parse_gtk_css_color(path, "base_color")
        )

        fg = (
            fg
            or _parse_gtk_css_color(path, "theme_fg_color")
            or _parse_gtk_css_color(path, "fg_color")
            or _parse_gtk_css_color(path, "text_color")
        )

        hl = (
            hl
            or _parse_gtk_css_color(path, "theme_selected_bg_color")
            or _parse_gtk_css_color(path, "selected_bg_color")
            or _parse_gtk_css_color(path, "highlight_color")
            or _parse_gtk_css_color(path, "accent_bg_color")
        )

        if bg and fg and hl:
            break

    return bg or DEFAULT_BG, fg or DEFAULT_FG, hl or DEFAULT_HL


def get_system_colors():
    """
    Retrieves colors from the current Qt application palette.

    Returns:
        tuple: (bg, fg, hl) hex color strings.
    """
    try:
        pal = QApplication.palette()
        bg = pal.color(QPalette.ColorRole.Window).name()
        fg = pal.color(QPalette.ColorRole.WindowText).name()
        hl = pal.color(QPalette.ColorRole.Highlight).name()
        return bg, fg, hl
    except Exception as e:
        debug_log(f"THEMES ERROR: Failed to resolve Qt palette: {e}")
        return "#efefef", "#111111", "#308cc6"
