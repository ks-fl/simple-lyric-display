import os
import json
from utils.config import Config

def test_config_default_values(tmp_path):
    # Use a temporary directory for config
    config_dir = tmp_path / ".config" / "test-app"
    config = Config(config_dir=str(config_dir))
    
    assert config.get("theme_mode") == "GTK"
    assert config.get(["window", "width"]) == 600
    assert config.get(["mpris", "selected_player"]) == "strawberry"

def test_config_set_and_save(tmp_path):
    config_dir = tmp_path / ".config" / "test-app"
    config = Config(config_dir=str(config_dir))
    
    config.set("theme_mode", "Custom")
    config.save()
    
    # Check if file exists and has the new value
    config_file = config_dir / "config.json"
    assert os.path.exists(config_file)
    
    with open(config_file, "r") as f:
        data = json.load(f)
        assert data["theme_mode"] == "Custom"

def test_config_nested_get(tmp_path):
    config_dir = tmp_path / ".config" / "test-app"
    config = Config(config_dir=str(config_dir))
    
    assert config.get(["font", "size"]) == 18
    assert config.get(["nonexistent", "key"], default="fallback") == "fallback"
