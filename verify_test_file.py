#!/usr/bin/env python3
"""
Quick verification of the uploaded test file
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qusb2snes_connection import QUSB2SNESConnection
from qusb2snes_device import QUSB2SNESDevice
from qusb2snes_filesystem import QUSB2SNESFileSystem


async def quick_verify():
    """Check if the test file was uploaded correctly"""
    print("🔍 Quick Verification: /ROMS/TEST/simple_test.smc")
    print("=" * 50)
    
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
        
        # Check file existence
        test_file = "/ROMS/TEST/simple_test.smc"
        exists = await filesystem.file_exists(test_file)
        
        if exists:
            print(f"✅ File exists: {test_file}")
            
            # Get file size
            try:
                dir_contents = await filesystem.list_directory("/ROMS/TEST")
                file_entry = next((entry for entry in dir_contents if entry.name == "simple_test.smc"), None)
                
                if file_entry:
                    size_bytes = file_entry.size or 0
                    size_kb = size_bytes / 1024
                    print(f"📊 File size: {size_bytes:,} bytes ({size_kb:.1f} KB)")
                    
                    expected_size = 524288  # 512 KB
                    if size_bytes == expected_size:
                        print("🎉 SUCCESS: File size matches expected size!")
                        print("   ✅ V2 upload is working correctly!")
                        return True
                    elif size_bytes == 0:
                        print("❌ FAILURE: File is empty (0 bytes)")
                        print("   💡 Content writing is failing")
                        return False
                    else:
                        print(f"⚠️ PARTIAL: File size mismatch (expected {expected_size:,} bytes)")
                        return False
                else:
                    print("❌ File entry not found in directory listing")
                    return False
                    
            except Exception as e:
                print(f"❌ Error checking file size: {e}")
                return False
        else:
            print(f"❌ File does not exist: {test_file}")
            return False
            
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
        result = asyncio.run(quick_verify())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n🛑 Cancelled")
        sys.exit(1)