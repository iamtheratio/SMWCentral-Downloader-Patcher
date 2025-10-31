#!/usr/bin/env python3
"""
Config Save Debug Test - Find the Save Failure
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager

def test_config_save_detailed():
    """Test config save with detailed error reporting"""
    print("🔧 Config Save Debug Test")
    print("=" * 40)
    
    config = ConfigManager()
    print(f"Original config keys: {list(config.config.keys())}")
    
    # Try to add a test key
    test_key = "debug_test_key"
    test_value = "debug_test_value_12345"
    
    print(f"\nAdding test key: {test_key} = {test_value}")
    
    # Step 1: Check if value is serializable
    is_serializable = config._is_serializable(test_value)
    print(f"Value is serializable: {is_serializable}")
    
    if is_serializable:
        # Step 2: Add to config
        config.config[test_key] = test_value
        print(f"Added to config: {test_key} in config = {test_key in config.config}")
        
        # Step 3: Try save with detailed error catching
        print("\nAttempting save...")
        try:
            # Do the save steps manually for detailed debugging
            from utils import CONFIG_JSON_PATH
            
            print(f"Config path: {CONFIG_JSON_PATH}")
            print(f"Config path exists: {os.path.exists(CONFIG_JSON_PATH)}")
            
            # Step 3a: Clean config
            clean_config = config._clean_config(config.config)
            print(f"Cleaned config keys: {list(clean_config.keys())}")
            print(f"Test key in cleaned: {test_key in clean_config}")
            
            # Step 3b: Try to write file
            with open(CONFIG_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(clean_config, f, indent=2)
            print("✅ File write successful")
            
            # Step 4: Verify by reading back
            with open(CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
            
            if test_key in saved_data:
                print(f"✅ Test key found in saved file: {saved_data[test_key]}")
            else:
                print(f"❌ Test key NOT in saved file")
                print(f"Saved keys: {list(saved_data.keys())}")
                
        except Exception as e:
            print(f"❌ Save failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 40)
    
    # Test 2: Check if the test key shows in allowed keys
    print("Checking allowed keys...")
    allowed_keys = {"base_rom_path", "output_dir", "api_delay", "flips_path",
                    "multi_type_enabled", "multi_type_download_mode",
                    "qusb2snes_enabled", "qusb2snes_host", "qusb2snes_port",
                    "qusb2snes_device", "qusb2snes_remote_folder", "qusb2snes_last_sync"}
    
    print(f"Test key '{test_key}' in allowed keys: {test_key in allowed_keys}")
    print("This explains why the save 'failed' - the key gets filtered out!")

if __name__ == "__main__":
    test_config_save_detailed()