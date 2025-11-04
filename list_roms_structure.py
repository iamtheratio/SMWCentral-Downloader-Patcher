#!/usr/bin/env python3
"""
List ROMS directory structure to see what's actually there
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qusb2snes_connection import QUSB2SNESConnection
from qusb2snes_device import QUSB2SNESDevice
from qusb2snes_filesystem import QUSB2SNESFileSystem


async def list_roms_structure():
    """List the actual ROMS directory structure"""
    print("📁 ROMS Directory Structure")
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
        
        # List /ROMS directory
        print(f"\n📂 /ROMS contents:")
        try:
            roms_contents = await filesystem.list_directory("/ROMS")
            
            directories = [entry for entry in roms_contents if entry.is_directory and not entry.name.startswith('.')]
            files = [entry for entry in roms_contents if not entry.is_directory]
            
            for directory in sorted(directories, key=lambda x: x.name):
                print(f"  📂 {directory.name}/")
                
                # List subdirectories
                try:
                    subdir_path = f"/ROMS/{directory.name}"
                    subdir_contents = await filesystem.list_directory(subdir_path)
                    subdirs = [entry for entry in subdir_contents if entry.is_directory and not entry.name.startswith('.')]
                    subfiles = [entry for entry in subdir_contents if not entry.is_directory and entry.name.lower().endswith(('.smc', '.sfc'))]
                    
                    for subdir in sorted(subdirs, key=lambda x: x.name):
                        print(f"    📁 {subdir.name}/")
                        
                        # Check for ROM files in subdirectory
                        try:
                            subsubdir_path = f"/ROMS/{directory.name}/{subdir.name}"
                            subsubdir_contents = await filesystem.list_directory(subsubdir_path)
                            rom_files = [entry for entry in subsubdir_contents if not entry.is_directory and entry.name.lower().endswith(('.smc', '.sfc'))]
                            
                            if rom_files:
                                for rom_file in sorted(rom_files[:5], key=lambda x: x.name):  # Show first 5
                                    size_mb = (rom_file.size or 0) / (1024 * 1024)
                                    print(f"      🎮 {rom_file.name} ({size_mb:.1f}MB)")
                                if len(rom_files) > 5:
                                    print(f"      🎮 ... and {len(rom_files) - 5} more ROM files")
                        except Exception as e:
                            print(f"      ❌ Error listing {subsubdir_path}: {e}")
                    
                    if subfiles:
                        print(f"    🎮 {len(subfiles)} ROM files in root")
                        
                except Exception as e:
                    print(f"    ❌ Error listing {subdir_path}: {e}")
            
            if files:
                rom_files = [f for f in files if f.name.lower().endswith(('.smc', '.sfc'))]
                if rom_files:
                    print(f"  🎮 {len(rom_files)} ROM files in /ROMS root")
                    
        except Exception as e:
            print(f"❌ Error listing /ROMS: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection:
            try:
                await connection.disconnect()
                print("\n🔌 Disconnected")
            except:
                pass


if __name__ == "__main__":
    try:
        asyncio.run(list_roms_structure())
    except KeyboardInterrupt:
        print("\n🛑 Cancelled")