#!/usr/bin/env python3
"""
Search for our test file across the SD card
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qusb2snes_connection import QUSB2SNESConnection
from qusb2snes_device import QUSB2SNESDevice
from qusb2snes_filesystem import QUSB2SNESFileSystem


async def find_test_file():
    """Search for simple_test.smc across the SD card"""
    print("🔍 Searching for: simple_test.smc")
    print("=" * 40)
    
    connection = None
    try:
        # Connect
        connection = QUSB2SNESConnection()
        await connection.connect()
        
        device = QUSB2SNESDevice(connection)
        devices = await device.discover_devices()
        device_info = devices[0]
        await device.attach_device(device_info.name)
        print(f"✅ Connected to: {device_info.name}")
        
        filesystem = QUSB2SNESFileSystem(connection)
        
        # Search locations
        search_locations = [
            "/",
            "/ROMS",
            "/roms", 
            "/TEST",
            "/test",
            "/ROMS/TEST",
            "/roms/TEST",
            "/roms/test"
        ]
        
        found_files = []
        
        for location in search_locations:
            try:
                print(f"📁 Checking {location}...")
                
                exists = await filesystem.directory_exists(location)
                if not exists:
                    print(f"   ❌ Directory doesn't exist")
                    continue
                    
                contents = await filesystem.list_directory(location)
                files = [entry for entry in contents if not entry.is_directory]
                
                for file_entry in files:
                    if file_entry.name == "simple_test.smc":
                        size_bytes = file_entry.size or 0
                        size_kb = size_bytes / 1024
                        found_files.append((location, size_bytes))
                        print(f"   ✅ FOUND: {location}/simple_test.smc ({size_bytes:,} bytes, {size_kb:.1f} KB)")
                        
                if not any(f.name == "simple_test.smc" for f in files):
                    print(f"   ❌ Not found")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n📊 Search Results:")
        if found_files:
            for location, size in found_files:
                expected_size = 524288  # 512 KB
                status = "✅ CORRECT SIZE" if size == expected_size else ("❌ EMPTY" if size == 0 else "⚠️ WRONG SIZE")
                print(f"   📄 {location}/simple_test.smc - {size:,} bytes - {status}")
                
            return True
        else:
            print(f"   ❌ simple_test.smc not found anywhere on SD card")
            print(f"   💡 Upload may have failed or went to unexpected location")
            return False
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False
        
    finally:
        if connection:
            try:
                await connection.disconnect()
                print("\n🔌 Disconnected")
            except:
                pass


if __name__ == "__main__":
    try:
        result = asyncio.run(find_test_file())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n🛑 Search cancelled")
        sys.exit(1)