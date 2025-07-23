"""
Configuration Manager
Handles application settings and user preferences

Copyright (c) 2025 iamtheratio
Licensed under the MIT License - see LICENSE file for details
"""

import json
import os
import platform
import sys


def get_config_path():
    """Get the appropriate config path for the current platform"""
    if platform.system() == "Windows":
        # For Windows: Store config next to the executable for portability
        if hasattr(sys, 'frozen') and sys.frozen:
            # Running as PyInstaller executable
            config_dir = os.path.dirname(sys.executable)
        else:
            # Running as script in development
            config_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(config_dir, "config.json")
    elif platform.system() == "Darwin":
        # macOS - Use proper location (cannot write to app bundle)
        config_dir = os.path.expanduser("~/Library/Application Support/SMWCDownloader")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "config.json")
    else:
        # Linux - use ~/.config/smwc-downloader/
        config_dir = os.path.expanduser("~/.config/smwc-downloader")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "config.json")


CONFIG_PATH = get_config_path()


class ConfigManager:
    """Handles application configuration saving and loading"""

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from file or return defaults"""
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()

                # Check if file is empty
                if not content:
                    return self._get_default_config()

                # Try to parse JSON
                config = json.loads(content)

                # Clean up any invalid entries (like UI references)
                config = self._clean_config(config)

                return config

        except FileNotFoundError:
            return self._get_default_config()
        except json.JSONDecodeError:
            print("Warning: Invalid JSON in config file. Creating fresh config.")
            # Backup the corrupted file
            try:
                import shutil
                shutil.copy(CONFIG_PATH, f"{CONFIG_PATH}.backup")
            except Exception:
                pass

            # Return defaults and save them
            default_config = self._get_default_config()
            self._save_config(default_config)
            return default_config

    def _get_default_config(self):
        """Return default configuration"""
        return {
            "base_rom_path": "",
            "output_dir": "",
            "api_delay": 0.8,
            "multi_type_enabled": True,
            "multi_type_download_mode": "primary_only"
        }

    def _clean_config(self, config):
        """Clean up invalid config entries and prevent UI reference storage"""
        if not isinstance(config, dict):
            return self._get_default_config()

        # Only allow specific configuration keys
        allowed_keys = {"base_rom_path", "output_dir", "api_delay", "flips_path",
                        "multi_type_enabled", "multi_type_download_mode"}
        cleaned = {}

        for key, value in config.items():
            if key in allowed_keys and self._is_serializable(value):
                cleaned[key] = value

        # Ensure we have all required keys with defaults
        defaults = self._get_default_config()
        for key, default_value in defaults.items():
            if key not in cleaned:
                cleaned[key] = default_value

        return cleaned

    def _is_serializable(self, value):
        """Check if a value is JSON serializable"""
        try:
            json.dumps(value)
            return True
        except (TypeError, ValueError):
            return False

    def _save_config(self, config):
        """Internal save method with validation"""
        try:
            # Clean config before saving to prevent UI references
            clean_config = self._clean_config(config)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(clean_config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")

    def save(self):
        """Save current configuration to file"""
        self._save_config(self.config)

    def get(self, key, default=""):
        """Get a configuration value with optional default"""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set a configuration value and save (only if serializable)"""
        if self._is_serializable(value):
            self.config[key] = value
            self.save()
        else:
            print(f"Warning: Cannot save non-serializable value for key '{key}'")

    def update_paths(self, flips_path=None, base_rom_path=None, output_dir=None):
        """Update path settings and save configuration"""
        if flips_path is not None:
            self.config["flips_path"] = flips_path
        if base_rom_path is not None:
            self.config["base_rom_path"] = base_rom_path
        if output_dir is not None:
            self.config["output_dir"] = output_dir
        self.save()
