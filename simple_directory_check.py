#!/usr/bin/env python3
"""
Simple directory existence checker to determine correct case
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qusb2snes_connection import QUSB2SNESConnection
from qusb2snes_device import QUSB2SNESDevice
from qusb2snes_filesystem import QUSB2SNESFileSystem

async def check_simple():
    """Simple check for directory existence"""
    print("🔍 Simple Directory Check")
    
    connection = None
    try:
        # Step 1: Connect to QUSB2SNES
        print("🔗 Connecting to QUSB2SNES...")
        connection = QUSB2SNESConnection()
        await connection.connect()
        
        # Step 2: Discover devices
        print("📱 Discovering devices...")
        device = QUSB2SNESDevice(connection)
        devices = await device.discover_devices()
        
        if not devices:
            print("❌ No devices found")
            return
            
        print(f"✅ Found device: {devices[0].name}")
        
        # Step 3: Attach to device
        print(f"🔌 Attaching to device...")
        success = await device.attach_device(devices[0].name)
        if not success:
            print("❌ Failed to attach to device")
            return
        print(f"✅ Attached to: {devices[0].name}")
        
        # Step 4: Create filesystem manager
        filesystem = QUSB2SNESFileSystem(connection)
        
        # Test directory cases
        test_dirs = ["/", "/ROMS", "/roms", "/Roms", "/ROMs"]
        
        for test_dir in test_dirs:
            try:
                print(f"\n📁 Checking {test_dir}:")
                files = await filesystem.list_directory(test_dir)
                if files is not None:
                    print(f"   ✅ EXISTS! Contains {len(files)} items")
                    if files:
                        # Show first few items
                        for i, item in enumerate(files[:3]):
                            print(f"      📄 {item}")
                        if len(files) > 3:
                            print(f"      ... and {len(files) - 3} more")
                else:
                    print(f"   ❌ No response (doesn't exist)")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        if connection:
            await connection.disconnect()
        print("\n🔌 Disconnected")

if __name__ == "__main__":
    asyncio.run(check_simple())