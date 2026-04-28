import json
import os

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
            "opacity": 0.9
        },
        "font": {
            "family": "Sans Serif",
            "size": 18
        },
        "theme_mode": "System",
        "theme_bg_color": "#1a1a1a",
        "theme_fg_color": "#aaaaaa",
        "theme_preset": "Default Dark",
        "mpris": {
            "priority": ["audacious", "strawberry", "clementine", "amarok", "rhythmbox"]
        }
    }

    def __init__(self, config_dir="~/.config/simple-lyric-display"):
        """
        Initializes the configuration manager and loads existing settings.
        """
        self.config_path = os.path.expanduser(os.path.join(config_dir, "config.json"))
        self.data = self.DEFAULT_CONFIG.copy()
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
            except Exception:
                pass

    def save(self):
        """
        Saves the current configuration to the JSON file.
        """
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception:
            pass

    def _update_recursive(self, base, update):
        """
        Recursively updates a dictionary.
        """
        for k, v in update.items():
            if isinstance(v, dict) and k in base:
                self._update_recursive(base[k], v)
            else:
                base[k] = v

    def get(self, *keys, default=None):
        """
        Retrieves a value from the configuration.
        """
        val = self.data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def set(self, *keys_and_val):
        """
        Sets a value in the configuration and saves it.
        """
        if len(keys_and_val) < 2: return
        keys = keys_and_val[:-1]
        val = keys_and_val[-1]
        
        target = self.data
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = val
        self.save()
