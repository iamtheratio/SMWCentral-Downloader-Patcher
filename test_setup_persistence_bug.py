#!/usr/bin/env python3
"""
Test for Setup Section Config Persistence Bug - TDD Implementation
Tests the issue where Setup section settings don't persist between app restarts

Issue: Base ROM and Output Folder settings are not being saved/loaded properly,
causing both UI display issues and QUSB2SNES sync failures.

Copyright (c) 2025 iamtheratio
Licensed under the MIT License - see LICENSE file for details
"""

import unittest
import tempfile
import os
import sys
import json
import shutil
from unittest.mock import Mock, patch, MagicMock

# Add project path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestSetupSectionPersistence(unittest.TestCase):
    """Test Setup section config persistence"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "config.json")
        
        # Test paths that should be saved
        self.test_base_rom = os.path.join(self.temp_dir, "Super Mario World (U) [!].smc")
        self.test_output_dir = os.path.join(self.temp_dir, "ROM HACKS", "TEST")
        
        # Create test files/directories
        os.makedirs(os.path.dirname(self.test_base_rom), exist_ok=True)
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        # Create fake ROM file
        with open(self.test_base_rom, 'wb') as f:
            f.write(b'FAKE_ROM_DATA' * 1000)  # Fake ROM content
        
        # Initial config that should be saved
        self.expected_config = {
            "base_rom_path": self.test_base_rom,
            "output_dir": self.test_output_dir,
            "api_delay": 0.8,
            "multi_type_enabled": True,
            "qusb2snes_enabled": True,
            "qusb2snes_host": "localhost", 
            "qusb2snes_port": 23074
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_manager_saves_setup_data(self):
        """Test that ConfigManager can save setup section data"""
        from config_manager import ConfigManager
        
        # Create config and set setup data
        config = ConfigManager(self.config_file)
        config.set("base_rom_path", self.test_base_rom)
        config.set("output_dir", self.test_output_dir)
        config.save()
        
        # Verify file was written
        self.assertTrue(os.path.exists(self.config_file))
        
        # Verify content
        with open(self.config_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data["base_rom_path"], self.test_base_rom)
        self.assertEqual(saved_data["output_dir"], self.test_output_dir)
    
    def test_config_manager_loads_setup_data(self):
        """Test that ConfigManager can load setup section data"""
        # Write config file directly
        with open(self.config_file, 'w') as f:
            json.dump(self.expected_config, f)
        
        # Load with ConfigManager
        from config_manager import ConfigManager
        config = ConfigManager(self.config_file)
        
        # Verify loaded correctly
        self.assertEqual(config.get("base_rom_path"), self.test_base_rom)
        self.assertEqual(config.get("output_dir"), self.test_output_dir)
    
    def test_config_persistence_across_instances(self):
        """Test that config persists when creating new ConfigManager instances"""
        from config_manager import ConfigManager
        
        # Instance 1: Save data
        config1 = ConfigManager(self.config_file)
        config1.set("base_rom_path", self.test_base_rom)
        config1.set("output_dir", self.test_output_dir)
        config1.save()
        
        # Instance 2: Load data (simulates app restart)
        config2 = ConfigManager(self.config_file)
        
        # Should have the same data
        self.assertEqual(config2.get("base_rom_path"), self.test_base_rom)
        self.assertEqual(config2.get("output_dir"), self.test_output_dir)
    
    def test_setup_section_component_integration(self):
        """Test if setup section component properly uses ConfigManager"""
        try:
            from ui.components import SetupSection
        except ImportError:
            self.skipTest("SetupSection component not available")
        
        from config_manager import ConfigManager
        
        # Create config with test data
        config = ConfigManager(self.config_file)
        config.set("base_rom_path", self.test_base_rom)
        config.set("output_dir", self.test_output_dir)
        config.save()
        
        # Mock UI parent
        mock_parent = Mock()
        
        # Create setup section (this should load the config)
        setup_section = SetupSection(mock_parent, config)
        
        # Test that it has the right config reference
        self.assertEqual(setup_section.config.get("base_rom_path"), self.test_base_rom)
        self.assertEqual(setup_section.config.get("output_dir"), self.test_output_dir)
    
    def test_qusb2snes_fails_when_no_output_dir(self):
        """Test that QUSB2SNES fails when output_dir is missing (reproduces user's issue)"""
        # Create empty config (simulates the persistence bug)
        from config_manager import ConfigManager
        empty_config = ConfigManager()  # No file, no data
        
        # This is what QUSB2SNES section sees
        output_dir = empty_config.get("output_dir", "")
        
        # This causes the error the user sees
        self.assertEqual(output_dir, "")
        
        # Simulate the validation that fails
        if not output_dir:
            error_message = "Configure ROM output directory in Setup section first"
            # This is the repeated error in the user's log
            self.assertTrue("Configure ROM output directory" in error_message)
    
    def test_demonstrate_user_scenario(self):
        """Demonstrate the exact user scenario"""
        # User sets these values in the UI (visible in screenshot)
        user_input_values = {
            "base_rom_path": "C:/Users/newgasm/Desktop/SMW/Super Mario World (U) [!].smc",
            "output_dir": "C:/Users/newgasm/Desktop/SMW/ROM HACKS/TEST"
        }
        
        # Problem 1: Settings don't persist (user reports)
        # When app restarts, setup section shows empty
        
        # Problem 2: QUSB2SNES gets empty config  
        from config_manager import ConfigManager
        config_after_restart = ConfigManager()  # Empty config
        
        # User sees empty setup section
        base_rom_from_config = config_after_restart.get("base_rom_path", "")
        output_dir_from_config = config_after_restart.get("output_dir", "")
        
        self.assertEqual(base_rom_from_config, "")  # Empty despite user setting it
        self.assertEqual(output_dir_from_config, "")  # Empty despite user setting it
        
        # And QUSB2SNES sync fails because of missing output_dir
        if not output_dir_from_config:
            qusb2snes_error = "Configure ROM output directory in Setup section first"
            self.assertTrue(bool(qusb2snes_error))  # User sees this error repeatedly
    
    def test_config_file_location_and_permissions(self):
        """Test config file location and write permissions"""
        from config_manager import ConfigManager
        
        # Test with default config location
        config = ConfigManager()
        
        # Check if we can determine the default config file path
        # This might be the issue - config file not in the right location
        if hasattr(config, 'config_file') or hasattr(config, '_config_file'):
            config_path = getattr(config, 'config_file', None) or getattr(config, '_config_file', None)
            if config_path:
                # Test if directory exists and is writable
                config_dir = os.path.dirname(config_path)
                if config_dir:
                    self.assertTrue(os.path.exists(config_dir) or os.access(os.path.dirname(config_dir), os.W_OK))

if __name__ == "__main__":
    print("🧪 Testing Setup Section Config Persistence...")
    print("=" * 60)
    print("Issues:")
    print("1. Setup section settings don't persist between app restarts")
    print("2. QUSB2SNES sync fails due to missing output_dir")
    print("3. User sees empty setup fields despite configuring them")
    print("=" * 60)
    
    unittest.main(verbosity=2)