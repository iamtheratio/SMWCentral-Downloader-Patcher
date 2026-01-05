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
    # Use the same path resolution as processed.json for consistency
    from utils import CONFIG_JSON_PATH
    return CONFIG_JSON_PATH


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
            "multi_type_download_mode": "primary_only",
            "auto_check_updates": True,  # Auto-check for updates on startup
            # Emulator settings
            "emulator_path": "",
            "emulator_args": "",
            "emulator_args_enabled": False,
            # QUSB2SNES settings
            "qusb2snes_enabled": False,
            "qusb2snes_host": "localhost",
            "qusb2snes_port": 23074,  # Default modern QUSB2SNES port
            "qusb2snes_device": "",
            "qusb2snes_remote_folder": "/ROMS",
            "qusb2snes_last_sync": 0,  # Unix timestamp of last successful sync
            "qusb2snes_sync_progress": {},  # Directory-level sync progress tracking
            "qusb2snes_partial_sync": False,  # Flag indicating partial sync state
            "qusb2snes_cleanup_deleted": False  # Remove files from SD card that were deleted locally
        }

    def _clean_config(self, config):
        """Clean up invalid config entries and prevent UI reference storage"""
        if not isinstance(config, dict):
            return self._get_default_config()

        # Only allow specific configuration keys
        allowed_keys = {"base_rom_path", "output_dir", "api_delay", "flips_path",
                        "multi_type_enabled", "multi_type_download_mode", "difficulty_lookup",
                        "emulator_path", "emulator_args", "emulator_args_enabled", "auto_check_updates",
                        "qusb2snes_enabled", "qusb2snes_host", "qusb2snes_port",
                        "qusb2snes_device", "qusb2snes_remote_folder", "qusb2snes_last_sync",
                        "qusb2snes_sync_progress", "qusb2snes_partial_sync", "qusb2snes_cleanup_deleted"}
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

    def get_difficulty_lookup(self):
        """Get difficulty lookup, returns dict or None if not cached"""
        return self.config.get("difficulty_lookup")
    
    def set_difficulty_lookup(self, lookup_dict):
        """Save difficulty lookup to config"""
        self.config["difficulty_lookup"] = lookup_dict
        self.save()
    
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
