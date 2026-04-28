import os
import sys


def get_resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource, works for dev and for PyInstaller/Nuitka.

    Args:
        relative_path: The path to the resource relative to the project root.

    Returns:
        The absolute path to the resource.
    """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        # For development or Nuitka (in standalone mode without data file bundling,
        # but we can adjust this as needed)
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    return os.path.join(base_path, relative_path)
