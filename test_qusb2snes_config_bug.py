#!/usr/bin/env python3
"""
Test for QUSB2SNES Config Bug - TDD Implementation
Tests the issue where QUSB2SNES sync fails due to empty config

Issue: QUSB2SNES section creates new ConfigManager() instead of using 
the existing one with user settings, causing "Configure ROM output 
directory in Setup section first" errors.

Copyright (c) 2025 iamtheratio
Licensed under the MIT License - see LICENSE file for details
"""

import unittest
import tempfile
import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock

# Add project path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestQUSB2SNESConfigBug(unittest.TestCase):
    """Test QUSB2SNES config access bug"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "config.json")
        
        # Create a test config with output_dir set
        self.test_config_data = {
            "output_dir": os.path.join(self.temp_dir, "ROM_HACKS"),
            "base_rom_path": os.path.join(self.temp_dir, "base.smc"),
            "qusb2snes_enabled": True,
            "qusb2snes_host": "localhost",
            "qusb2snes_port": 23074
        }
        
        # Create the output directory
        os.makedirs(self.test_config_data["output_dir"], exist_ok=True)
        
        # Write config file
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config_data, f)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_manager_loads_existing_data(self):
        """Test that ConfigManager properly loads existing config data"""
        from config_manager import ConfigManager
        
        # Test that ConfigManager loads from existing file
        config = ConfigManager(self.config_file)
        
        # Should have the output_dir from our test data
        output_dir = config.get("output_dir", "")
        self.assertEqual(output_dir, self.test_config_data["output_dir"])
        self.assertTrue(os.path.exists(output_dir))
    
    def test_new_config_manager_is_empty(self):
        """Test that new ConfigManager() creates empty config (the bug)"""
        from config_manager import ConfigManager
        
        # Create new ConfigManager without config file
        config = ConfigManager()
        
        # Should NOT have the output_dir (this is the bug)
        output_dir = config.get("output_dir", "")
        self.assertEqual(output_dir, "")
    
    def test_qusb2snes_section_with_empty_config(self):
        """Test QUSB2SNES section behavior with empty config (reproduces bug)"""
        try:
            from qusb2snes_ui import QUSB2SNESSection
            from config_manager import ConfigManager
        except ImportError:
            self.skipTest("QUSB2SNES components not available")
        
        # Mock the UI components
        mock_parent = Mock()
        mock_logger = Mock()
        
        # Create empty config (simulates the bug)
        empty_config = ConfigManager()
        
        # Create QUSB2SNES section with empty config
        section = QUSB2SNESSection(mock_parent, empty_config, mock_logger)
        
        # Test that it doesn't have output_dir
        output_dir = section.config.get("output_dir", "")
        self.assertEqual(output_dir, "")
        
        # This would trigger the "Configure ROM output directory" error
        self.assertFalse(bool(output_dir))
    
    def test_qusb2snes_section_with_populated_config(self):
        """Test QUSB2SNES section behavior with populated config (desired behavior)"""
        try:
            from qusb2snes_ui import QUSB2SNESSection
            from config_manager import ConfigManager
        except ImportError:
            self.skipTest("QUSB2SNES components not available")
        
        # Mock the UI components
        mock_parent = Mock()
        mock_logger = Mock()
        
        # Create populated config (simulates the fix)
        populated_config = ConfigManager(self.config_file)
        
        # Create QUSB2SNES section with populated config
        section = QUSB2SNESSection(mock_parent, populated_config, mock_logger)
        
        # Test that it HAS output_dir
        output_dir = section.config.get("output_dir", "")
        self.assertEqual(output_dir, self.test_config_data["output_dir"])
        
        # This would NOT trigger the "Configure ROM output directory" error
        self.assertTrue(bool(output_dir))
        self.assertTrue(os.path.exists(output_dir))
    
    def test_mock_settings_page_config_access(self):
        """Test settings page config access pattern"""
        # Mock setup_section with config
        mock_setup_section = Mock()
        mock_setup_section.config = Mock()
        mock_setup_section.config.get.return_value = self.test_config_data["output_dir"]
        
        # Simulate the proposed fix: use setup_section.config
        config_from_setup = mock_setup_section.config
        output_dir = config_from_setup.get("output_dir", "")
        
        # Should get the correct output_dir
        self.assertEqual(output_dir, self.test_config_data["output_dir"])
        
        # Verify the mock was called correctly
        config_from_setup.get.assert_called_with("output_dir", "")
    
    def test_demonstrate_the_bug_scenario(self):
        """Demonstrate the exact bug scenario from user's screenshot"""
        # User has configured these in the UI (visible in screenshot):
        user_visible_config = {
            "base_rom_path": "C:/Users/newgasm/Desktop/SMW/Super Mario World (U) [!].smc",
            "output_dir": "C:/Users/newgasm/Desktop/SMW/ROM HACKS/TEST"
        }
        
        # But QUSB2SNES section gets a new ConfigManager() - empty config
        from config_manager import ConfigManager
        buggy_config = ConfigManager()  # This is what happens in the bug
        
        # The check that fails:
        local_rom_dir = buggy_config.get("output_dir", "")
        
        # This is why the error occurs
        self.assertEqual(local_rom_dir, "")  # Empty! Even though user set it
        
        # The user sees this error message repeatedly
        error_message = "Configure ROM output directory in Setup section first"
        
        # Even though they DID configure it (it's visible in the UI)
        self.assertTrue(bool(user_visible_config["output_dir"]))
        self.assertFalse(bool(local_rom_dir))  # But the code can't see it!

if __name__ == "__main__":
    print("🧪 Testing QUSB2SNES Config Bug...")
    print("=" * 60)
    print("Issue: QUSB2SNES section creates new ConfigManager() instead")
    print("of using the existing one with user settings.")
    print("=" * 60)
    
    unittest.main(verbosity=2)