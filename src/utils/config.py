import json
import os

from utils.logger import debug_log


class Config:
    """
    Handles application configuration, including loading from and saving to a JSON file.
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
        "font": {"family": "Sans Serif", "size": 18, "weight": 400, "italic": False},
        "theme_mode": "GTK",
        "theme_bg_color": "#1a1a1a",
        "theme_fg_color": "#aaaaaa",
        "theme_preset": "Default Dark",
        "mpris": {"selected_player": "strawberry"},
    }

    def __init__(self, config_dir="~/.config/simple-lyric-display"):
        """
        Initializes the configuration manager and loads existing settings.
        """
        self.config_path = os.path.expanduser(os.path.join(config_dir, "config.json"))
        self.data = self.DEFAULT_CONFIG.copy()
        debug_log(f"CONFIG: Initializing with path {self.config_path}")
        self.load()

    def load(self):
        """
        Loads the configuration from the JSON file.
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    user_data = json.load(f)
                    self._update_recursive(self.data, user_data)
                debug_log(f"CONFIG: Loaded from file: {self.data}")
            except Exception as e:
                debug_log(f"CONFIG ERROR: Failed to load: {e}")

    def save(self):
        """
        Saves the current configuration to the JSON file.
        """
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(self.data, f, indent=4)
            debug_log("CONFIG: Saved to file.")
        except Exception as e:
            debug_log(f"CONFIG ERROR: Failed to save: {e}")

    def _update_recursive(self, base, update):
        """
        Recursively updates a dictionary.
        """
        for k, v in update.items():
            if isinstance(v, dict) and k in base:
                self._update_recursive(base[k], v)
            else:
                base[k] = v

    def get(self, key, default=None):
        """
        Retrieves a value from the configuration.
        """
        if isinstance(key, (list, tuple)):
            keys = key
        else:
            keys = [key]

        val = self.data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def set(self, key, value):
        """
        Sets a value in the configuration and saves it.
        """
        debug_log(f"CONFIG SET: {key} -> {value}")
        if isinstance(key, (list, tuple)):
            keys = key
        else:
            keys = [key]

        target = self.data
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value
        self.save()
