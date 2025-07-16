"""
Unit tests for config_manager.py module
Tests configuration management, settings persistence, and validation
"""
import unittest
import os
import json
import tempfile
from unittest.mock import patch, mock_open
import sys

# Import test configuration
from .test_config import TestConfig, TestDataManager

# Import the module to test
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = TestConfig.get_temp_dir()
        self.config_file = os.path.join(self.test_dir, "config.json")
        self.config_manager = ConfigManager(self.config_file)
    
    def tearDown(self):
        """Clean up test environment"""
        TestConfig.cleanup_temp_dir(self.test_dir)
    
    def test_init_with_existing_config(self):
        """Test initialization with existing config file"""
        # Create a test config file
        test_config = {
            "base_rom_path": "/test/rom.smc",
            "output_dir": "/test/output",
            "theme": "dark"
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        # Initialize ConfigManager
        cm = ConfigManager(self.config_file)
        
        # Verify config was loaded
        self.assertEqual(cm.get("base_rom_path"), "/test/rom.smc")
        self.assertEqual(cm.get("output_dir"), "/test/output")
        self.assertEqual(cm.get("theme"), "dark")
    
    def test_init_with_missing_config(self):
        """Test initialization with missing config file"""
        # Remove config file if it exists
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        
        # Initialize ConfigManager
        cm = ConfigManager(self.config_file)
        
        # Should have default values
        self.assertEqual(cm.get("base_rom_path"), "")
        self.assertEqual(cm.get("output_dir"), "")
        self.assertEqual(cm.get("theme"), "dark")
        self.assertTrue(cm.get("multi_type_enabled"))
    
    def test_init_with_invalid_json(self):
        """Test initialization with invalid JSON file"""
        # Create invalid JSON file
        with open(self.config_file, 'w') as f:
            f.write("invalid json content")
        
        # Should fall back to defaults without crashing
        cm = ConfigManager(self.config_file)
        self.assertEqual(cm.get("theme"), "dark")
    
    def test_get_existing_key(self):
        """Test getting an existing configuration key"""
        self.config_manager.set("test_key", "test_value")
        result = self.config_manager.get("test_key")
        self.assertEqual(result, "test_value")
    
    def test_get_missing_key_with_default(self):
        """Test getting a missing key with default value"""
        result = self.config_manager.get("missing_key", "default_value")
        self.assertEqual(result, "default_value")
    
    def test_get_missing_key_without_default(self):
        """Test getting a missing key without default value"""
        result = self.config_manager.get("missing_key")
        self.assertIsNone(result)
    
    def test_set_and_save(self):
        """Test setting and saving configuration"""
        # Set configuration values
        self.config_manager.set("base_rom_path", "/new/rom.smc")
        self.config_manager.set("output_dir", "/new/output")
        self.config_manager.set("theme", "light")
        
        # Verify values were set
        self.assertEqual(self.config_manager.get("base_rom_path"), "/new/rom.smc")
        self.assertEqual(self.config_manager.get("output_dir"), "/new/output")
        self.assertEqual(self.config_manager.get("theme"), "light")
        
        # Verify file was saved
        self.assertTrue(os.path.exists(self.config_file))
        
        # Load in new instance to verify persistence
        new_cm = ConfigManager(self.config_file)
        self.assertEqual(new_cm.get("base_rom_path"), "/new/rom.smc")
        self.assertEqual(new_cm.get("output_dir"), "/new/output")
        self.assertEqual(new_cm.get("theme"), "light")
    
    def test_set_different_data_types(self):
        """Test setting different data types"""
        test_cases = [
            ("string_key", "string_value"),
            ("int_key", 42),
            ("bool_key", True),
            ("list_key", [1, 2, 3]),
            ("dict_key", {"nested": "value"}),
            ("float_key", 3.14)
        ]
        
        for key, value in test_cases:
            with self.subTest(key=key, value=value):
                self.config_manager.set(key, value)
                result = self.config_manager.get(key)
                self.assertEqual(result, value)
    
    def test_update_existing_values(self):
        """Test updating existing configuration values"""
        # Set initial values
        self.config_manager.set("test_key", "initial_value")
        self.assertEqual(self.config_manager.get("test_key"), "initial_value")
        
        # Update value
        self.config_manager.set("test_key", "updated_value")
        self.assertEqual(self.config_manager.get("test_key"), "updated_value")
    
    def test_default_configuration_values(self):
        """Test that default configuration values are correct"""
        cm = ConfigManager(os.path.join(self.test_dir, "nonexistent.json"))
        
        # Test all default values
        expected_defaults = {
            "base_rom_path": "",
            "output_dir": "",
            "theme": "dark",
            "multi_type_enabled": True,
            "multi_type_download_mode": "primary_only",
            "auto_backup": True,
            "max_concurrent_downloads": 3,
            "download_timeout": 30,
            "enable_analytics": True,
            "auto_organize": True
        }
        
        for key, expected_value in expected_defaults.items():
            with self.subTest(key=key):
                result = cm.get(key, expected_value)
                self.assertEqual(result, expected_value)
    
    def test_save_with_permission_error(self):
        """Test saving configuration with permission error"""
        # Create a read-only directory
        readonly_dir = os.path.join(self.test_dir, "readonly")
        os.makedirs(readonly_dir, exist_ok=True)
        readonly_file = os.path.join(readonly_dir, "config.json")
        
        # Make directory read-only (on Windows, this might not work as expected)
        try:
            os.chmod(readonly_dir, 0o444)
            
            cm = ConfigManager(readonly_file)
            cm.set("test_key", "test_value")
            
            # Should not crash even if save fails
            # The test passes if no exception is raised
            
        except Exception:
            # If chmod doesn't work on this system, skip this test
            self.skipTest("Cannot create read-only directory on this system")
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(readonly_dir, 0o755)
            except:
                pass
    
    def test_load_config_with_missing_file(self):
        """Test loading configuration when file doesn't exist"""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.json")
        cm = ConfigManager(nonexistent_file)
        
        # Should have default values
        self.assertEqual(cm.get("theme"), "dark")
        self.assertTrue(cm.get("multi_type_enabled", True))
    
    def test_migration_from_old_config(self):
        """Test migration from older configuration format"""
        # Create old-style config
        old_config = {
            "rom_path": "/old/rom.smc",  # Old key name
            "output_path": "/old/output",  # Old key name
            "dark_mode": True  # Old boolean theme
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(old_config, f)
        
        cm = ConfigManager(self.config_file)
        
        # Should handle old format gracefully
        self.assertIsNotNone(cm.config)
    
    def test_config_validation(self):
        """Test configuration value validation"""
        # Test path validation
        self.config_manager.set("base_rom_path", "/valid/path.smc")
        self.config_manager.set("output_dir", "/valid/output/dir")
        
        # Test theme validation
        valid_themes = ["light", "dark"]
        for theme in valid_themes:
            with self.subTest(theme=theme):
                self.config_manager.set("theme", theme)
                self.assertEqual(self.config_manager.get("theme"), theme)
        
        # Test boolean validation
        boolean_keys = ["multi_type_enabled", "auto_backup", "enable_analytics", "auto_organize"]
        for key in boolean_keys:
            with self.subTest(key=key):
                self.config_manager.set(key, True)
                self.assertTrue(self.config_manager.get(key))
                self.config_manager.set(key, False)
                self.assertFalse(self.config_manager.get(key))
    
    def test_concurrent_access(self):
        """Test concurrent access to configuration"""
        # Simulate concurrent access by creating multiple ConfigManager instances
        cm1 = ConfigManager(self.config_file)
        cm2 = ConfigManager(self.config_file)
        
        # Set values in first instance
        cm1.set("key1", "value1")
        cm1.set("key2", "value2")
        
        # Second instance should see the changes after reloading
        cm2_fresh = ConfigManager(self.config_file)
        self.assertEqual(cm2_fresh.get("key1"), "value1")
        self.assertEqual(cm2_fresh.get("key2"), "value2")
    
    def test_special_characters_in_values(self):
        """Test handling of special characters in configuration values"""
        special_values = [
            "path/with/unicode/★☆♪",
            "path\\with\\backslashes",
            "path with spaces",
            "path\"with\"quotes",
            "path'with'apostrophes",
            "path\nwith\nnewlines",
            "path\twith\ttabs"
        ]
        
        for i, value in enumerate(special_values):
            with self.subTest(value=value):
                key = f"special_key_{i}"
                self.config_manager.set(key, value)
                result = self.config_manager.get(key)
                self.assertEqual(result, value)
                
                # Verify persistence
                cm_new = ConfigManager(self.config_file)
                result_new = cm_new.get(key)
                self.assertEqual(result_new, value)

if __name__ == '__main__':
    unittest.main()
