import json
import os

CONFIG_PATH = "config.json"

class ConfigManager:
    """Handles application configuration saving and loading"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file or return defaults"""
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save(self):
        """Save current configuration to file"""
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key, default=""):
        """Get a configuration value with optional default"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value and save"""
        self.config[key] = value
        self.save()
    
    def update_paths(self, flips_path=None, base_rom_path=None, output_dir=None):
        """Update path settings and save configuration"""
        if flips_path is not None:
            self.config["flips_path"] = flips_path
        if base_rom_path is not None:
            self.config["base_rom_path"] = base_rom_path
        if output_dir is not None:
            self.config["output_dir"] = output_dir
        self.save()