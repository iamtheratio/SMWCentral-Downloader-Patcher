#!/usr/bin/env python3
"""
List contents of /roms/ directory to see what files actually exist
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qusb2snes_connection import QUSB2SNESConnection
from qusb2snes_device import QUSB2SNESDevice
from qusb2snes_filesystem import QUSB2SNESFileSystem

async def list_roms_directory():
    """List all files in /roms/ directory"""
    
    print("📁 Listing /roms/ Directory Contents")
    print("=" * 50)
    
    connection = None
    try:
        connection = QUSB2SNESConnection()
        await connection.connect()
        
        device = QUSB2SNESDevice(connection)
        devices = await device.discover_devices()
        await device.attach_device(devices[0].name)
        
        filesystem = QUSB2SNESFileSystem(connection)
        
        # List directory contents
        files = await filesystem.list_directory("/roms")
        
        if files:
            print(f"Found {len(files)} items in /roms/:")
            for file_entry in files:
                if hasattr(file_entry, 'name') and hasattr(file_entry, 'size'):
                    if file_entry.name not in ['.', '..']:
                        size_info = f" ({file_entry.size} bytes)" if file_entry.size else " (no size)"
                        file_type = "📁 DIR" if file_entry.is_directory else "📄 FILE"
                        print(f"  {file_type} {file_entry.name}{size_info}")
                else:
                    print(f"  📄 {file_entry}")
        else:
            print("❌ No files found or directory access failed")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if connection:
            await connection.disconnect()

if __name__ == "__main__":
    asyncio.run(list_roms_directory())