import json
import os

from utils.logger import debug_log


class Config:
    """
    Handles application configuration with basic validation and persistence.

    Uses a nested dictionary structure to store settings and provides recursive
    updating and keyed access.
    """

    DEFAULT_CONFIG = {
        "window": {
            "width": 600,
            "height": 600,
            "x": 100,
            "y": 100,
            "always_on_top": True,
            "opacity": 0.9,
        },
        "font": {"family": "Sans Serif", "size": 12, "weight": 400, "italic": False},
        "theme_mode": "GTK",
        "theme_bg_color": "#f5f5f5",
        "theme_fg_color": "#1a1a1a",
        "theme_hl_color": "#0078d7",
        "theme_preset": "Light",
        "mpris": {"selected_player": "strawberry"},
    }

    def __init__(self, config_dir="~/.config/simple-lyric-display"):
        """
        Initializes the configuration manager and loads existing settings.

        Args:
            config_dir (str): Base directory for the configuration file.
        """
        self.config_path = os.path.expanduser(os.path.join(config_dir, "config.json"))
        self.data = self.DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        """
        Loads the configuration from the JSON file, merging with defaults.
        """
        if not os.path.exists(self.config_path):
            return

        try:
            with open(self.config_path, "r") as f:
                user_data = json.load(f)
                self._update_recursive(self.data, user_data)
            debug_log(f"CONFIG: Loaded from {self.config_path}")
        except (json.JSONDecodeError, IOError) as e:
            debug_log(f"CONFIG ERROR: Failed to load: {e}")

    def save(self):
        """
        Persists the current configuration to disk as a JSON file.
        """
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(self.data, f, indent=4)
        except IOError as e:
            debug_log(f"CONFIG ERROR: Failed to save: {e}")

    def _update_recursive(self, base, update):
        """
        Recursively updates a base dictionary with values from another dictionary.

        Args:
            base (dict): The dictionary to be updated.
            update (dict): The dictionary containing new values.
        """
        for k, v in update.items():
            if isinstance(v, dict) and k in base and isinstance(base[k], dict):
                self._update_recursive(base[k], v)
            else:
                base[k] = v

    def get(self, key, default=None):
        """
        Retrieves a value from the configuration.

        Args:
            key (str | list): The key or list of nested keys to retrieve.
            default (any): Value to return if the key is not found.

        Returns:
            any: The configuration value or default.
        """
        keys = key if isinstance(key, (list, tuple)) else [key]

        val = self.data
        try:
            for k in keys:
                val = val[k]
            return val
        except KeyError, TypeError:
            return default

    def set(self, key, value):
        """
        Sets a configuration value and persists it to disk.

        Args:
            key (str | list): The key or list of nested keys to set.
            value (any): The value to store.
        """
        keys = key if isinstance(key, (list, tuple)) else [key]

        target = self.data
        for k in keys[:-1]:
            target = target.setdefault(k, {})

        if target.get(keys[-1]) == value:
            return  # No change, avoid unnecessary save

        target[keys[-1]] = value
        debug_log(f"CONFIG SET: {key} -> {value}")
        self.save()
