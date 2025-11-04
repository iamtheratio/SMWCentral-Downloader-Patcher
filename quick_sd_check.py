#!/usr/bin/env python3
"""
Simple SD Card File Checker - Just check if our uploaded files exist
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qusb2snes_connection import QUSB2SNESConnection
from qusb2snes_device import QUSB2SNESDevice
from qusb2snes_filesystem import QUSB2SNESFileSystem


async def quick_file_check():
    """Quick check if our uploaded files exist"""
    print("🔍 Quick SD Card File Check")
    print("=" * 40)
    
    connection = None
    try:
        # Connect
        print("🔗 Connecting...")
        connection = QUSB2SNESConnection()
        await connection.connect()
        
        device = QUSB2SNESDevice(connection)
        devices = await device.discover_devices()
        device_info = devices[0]
        await device.attach_device(device_info.name)
        print(f"✅ Connected to: {device_info.name}")
        
        filesystem = QUSB2SNESFileSystem(connection)
        
        # Files we uploaded in the test
        test_files = [
            "/ROMS/Kaizo/04 - Advanced/Learn_2_Kaizo.smc",
            "/ROMS/Kaizo/05 - Expert/Item_Abuse_3.smc", 
            "/ROMS/Traditional/01 - Newcomer/Custom_ROM.smc",
            "/ROMS/Traditional/01 - Newcomer/Super_Mario_Plus.smc",
            "/ROMS/Traditional/01 - Newcomer/Vanilla_Secret_1.smc",
            "/ROMS/Traditional/02 - Casual/VIP_Wall_Mix_5.smc"
        ]
        
        print(f"\n🎯 Checking {len(test_files)} uploaded files...")
        
        found = 0
        missing = 0
        
        for file_path in test_files:
            try:
                exists = await filesystem.file_exists(file_path)
                if exists:
                    print(f"✅ {os.path.basename(file_path)}")
                    found += 1
                else:
                    print(f"❌ {os.path.basename(file_path)}")
                    missing += 1
            except Exception as e:
                print(f"⚠️ {os.path.basename(file_path)} - Error: {e}")
                missing += 1
        
        print(f"\n📊 Results: {found} found, {missing} missing")
        
        if found == len(test_files):
            print("🎉 SUCCESS: All test files found on SD card!")
        elif found > 0:
            print(f"⚠️ Partial success: {found}/{len(test_files)} files found")
        else:
            print("❌ No test files found on SD card")
            
        return found > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        if connection:
            try:
                await connection.disconnect()
                print("🔌 Disconnected")
            except:
                pass


if __name__ == "__main__":
    try:
        result = asyncio.run(quick_file_check())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n🛑 Cancelled")
        sys.exit(1)