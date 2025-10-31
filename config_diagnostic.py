#!/usr/bin/env python3
"""
Config Path Diagnostic Test
Tests config file location and permissions in different environments

Copyright (c) 2025 iamtheratio
Licensed under the MIT License - see LICENSE file for details
"""

import os
import sys
import json
import tempfile
from pathlib import Path

def test_config_path_resolution():
    """Test how config path is resolved in different modes"""
    print("🔍 Config Path Resolution Test")
    print("=" * 50)
    
    # Import after adding path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from utils import get_user_data_path, CONFIG_JSON_PATH
    
    print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
    print(f"sys.executable: {sys.executable}")
    print(f"__file__: {__file__}")
    print(f"Platform: {os.name}")
    
    print(f"\nConfig path: {CONFIG_JSON_PATH}")
    print(f"Config dir: {os.path.dirname(CONFIG_JSON_PATH)}")
    print(f"Config exists: {os.path.exists(CONFIG_JSON_PATH)}")
    
    if os.path.exists(CONFIG_JSON_PATH):
        print(f"Config size: {os.path.getsize(CONFIG_JSON_PATH)} bytes")
        try:
            with open(CONFIG_JSON_PATH, 'r') as f:
                content = f.read()
            print(f"Config readable: Yes ({len(content)} chars)")
            
            try:
                config_data = json.loads(content)
                print(f"Config parseable: Yes ({len(config_data)} keys)")
                print("Config keys:", list(config_data.keys()))
                
                # Check key values
                for key in ['base_rom_path', 'output_dir']:
                    value = config_data.get(key, 'NOT_FOUND')
                    print(f"  {key}: {value}")
                    
            except json.JSONDecodeError as e:
                print(f"Config parseable: No - {e}")
                print(f"Content preview: {content[:200]}...")
                
        except Exception as e:
            print(f"Config readable: No - {e}")
    
    # Test directory permissions
    config_dir = os.path.dirname(CONFIG_JSON_PATH)
    print(f"\nDirectory permissions:")
    print(f"  Dir exists: {os.path.exists(config_dir)}")
    print(f"  Dir readable: {os.access(config_dir, os.R_OK)}")
    print(f"  Dir writable: {os.access(config_dir, os.W_OK)}")
    
    # Test file permissions
    if os.path.exists(CONFIG_JSON_PATH):
        print(f"File permissions:")
        print(f"  File readable: {os.access(CONFIG_JSON_PATH, os.R_OK)}")
        print(f"  File writable: {os.access(CONFIG_JSON_PATH, os.W_OK)}")

def test_config_manager_behavior():
    """Test ConfigManager behavior"""
    print("\n🧪 ConfigManager Behavior Test")
    print("=" * 50)
    
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config_manager import ConfigManager
    
    try:
        config = ConfigManager()
        print("ConfigManager created successfully")
        
        # Test getting values
        base_rom = config.get("base_rom_path", "DEFAULT")
        output_dir = config.get("output_dir", "DEFAULT") 
        
        print(f"base_rom_path: '{base_rom}'")
        print(f"output_dir: '{output_dir}'")
        
        # Test if values are empty (the user's issue)
        if not base_rom or base_rom == "DEFAULT":
            print("❌ base_rom_path is empty/default")
        else:
            print("✅ base_rom_path has value")
            
        if not output_dir or output_dir == "DEFAULT":
            print("❌ output_dir is empty/default")
        else:
            print("✅ output_dir has value")
            
        # Test setting and saving
        print("\nTesting save functionality...")
        original_base = config.get("base_rom_path", "")
        test_value = "TEST_PATH_12345"
        
        config.set("test_key", test_value)
        config.save()
        
        # Create new instance to test persistence
        config2 = ConfigManager()
        saved_value = config2.get("test_key", "NOT_FOUND")
        
        if saved_value == test_value:
            print("✅ Save/load works correctly")
        else:
            print(f"❌ Save/load failed: got '{saved_value}', expected '{test_value}'")
            
        # Clean up test key
        config.set("test_key", None)
        config.save()
        
    except Exception as e:
        print(f"❌ ConfigManager error: {e}")
        import traceback
        traceback.print_exc()

def simulate_user_issue():
    """Simulate the user's reported issue"""
    print("\n🎯 User Issue Simulation")
    print("=" * 50)
    
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config_manager import ConfigManager
    
    print("Simulating user's problem:")
    print("1. User sets Base ROM and Output Dir in UI")
    print("2. App restart - settings disappear")
    print("3. QUSB2SNES sync fails")
    
    config = ConfigManager()
    
    # This is what QUSB2SNES section checks
    output_dir = config.get("output_dir", "")
    base_rom = config.get("base_rom_path", "")
    
    print(f"\nWhat QUSB2SNES section sees:")
    print(f"  output_dir: '{output_dir}'")
    print(f"  base_rom_path: '{base_rom}'")
    
    # The validation that fails
    if not output_dir:
        print("\n❌ QUSB2SNES validation FAILS:")
        print("   'Configure ROM output directory in Setup section first'")
    else:
        print("\n✅ QUSB2SNES validation would PASS")
        
    # Check if paths exist (user says they set them)
    if output_dir and os.path.exists(output_dir):
        print(f"   Output directory exists: {output_dir}")
    elif output_dir:
        print(f"   Output directory missing: {output_dir}")
        
    if base_rom and os.path.exists(base_rom):
        print(f"   Base ROM exists: {base_rom}")
    elif base_rom:
        print(f"   Base ROM missing: {base_rom}")

if __name__ == "__main__":
    print("🩺 SMWC Downloader Config Diagnostic")
    print("=" * 60)
    print("Diagnosing config persistence issues...")
    print("=" * 60)
    
    test_config_path_resolution()
    test_config_manager_behavior() 
    simulate_user_issue()
    
    print("\n" + "=" * 60)
    print("📋 Diagnostic complete!")
    print("Send this output to help diagnose the issue.")