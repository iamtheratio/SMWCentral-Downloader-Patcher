#!/usr/bin/env python3
"""
Check for recent directories that might have been created during upload
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qusb2snes_connection import QUSB2SNESConnection
from qusb2snes_device import QUSB2SNESDevice
from qusb2snes_filesystem import QUSB2SNESFileSystem


async def find_recent_uploads():
    """Look for directories that might contain our uploaded files"""
    print("🔍 Searching for Recent Upload Directories")
    print("=" * 50)
    
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
        
        # Search patterns for our uploaded files
        search_files = [
            "Learn_2_Kaizo.smc",
            "Item_Abuse_3.smc", 
            "Custom_ROM.smc",
            "Super_Mario_Plus.smc",
            "Vanilla_Secret_1.smc",
            "VIP_Wall_Mix_5.smc"
        ]
        
        print(f"\n🎯 Searching for files: {', '.join(search_files[:3])}...")
        
        # Check common upload locations
        search_locations = [
            "/ROMS",
            "/roms",  # lowercase
            "/",      # root
            "/test_upload_v2",  # our test directory
            "/ROMS/Traditional",
            "/ROMS/Kaizo"
        ]
        
        found_files = []
        
        for location in search_locations:
            try:
                print(f"\n📁 Checking {location}...")
                
                # Check if directory exists
                exists = await filesystem.directory_exists(location)
                if not exists:
                    print(f"   ❌ Directory doesn't exist")
                    continue
                
                # List directory contents
                contents = await filesystem.list_directory(location)
                
                # Look for our files directly
                files = [entry for entry in contents if not entry.is_directory]
                for file_entry in files:
                    if file_entry.name in search_files:
                        size_mb = (file_entry.size or 0) / (1024 * 1024)
                        found_files.append((location, file_entry.name, size_mb))
                        print(f"   ✅ Found: {file_entry.name} ({size_mb:.1f}MB)")
                
                # Look in subdirectories (one level deep)
                subdirs = [entry for entry in contents if entry.is_directory and not entry.name.startswith('.')]
                for subdir in subdirs:
                    try:
                        subdir_path = f"{location}/{subdir.name}" if location != "/" else f"/{subdir.name}"
                        subdir_contents = await filesystem.list_directory(subdir_path)
                        
                        subfiles = [entry for entry in subdir_contents if not entry.is_directory]
                        for file_entry in subfiles:
                            if file_entry.name in search_files:
                                size_mb = (file_entry.size or 0) / (1024 * 1024)
                                found_files.append((subdir_path, file_entry.name, size_mb))
                                print(f"   ✅ Found: {subdir_path}/{file_entry.name} ({size_mb:.1f}MB)")
                                
                    except Exception as e:
                        pass  # Skip subdirectories that can't be accessed
                        
            except Exception as e:
                print(f"   ❌ Error checking {location}: {e}")
        
        print(f"\n📊 Search Results:")
        if found_files:
            print(f"   ✅ Found {len(found_files)} uploaded files:")
            for location, filename, size_mb in found_files:
                print(f"      📄 {location}/{filename} ({size_mb:.1f}MB)")
        else:
            print(f"   ❌ No uploaded files found anywhere on SD card")
            print(f"   💡 This suggests the upload process may have failed silently")
            
        return len(found_files) > 0
        
    except Exception as e:
        print(f"❌ Error during search: {e}")
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
        result = asyncio.run(find_recent_uploads())
        if result:
            print("\n🎉 Files found on SD card!")
        else:
            print("\n⚠️ Upload verification failed - files not found")
    except KeyboardInterrupt:
        print("\n🛑 Search cancelled")