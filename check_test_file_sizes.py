#!/usr/bin/env python3
"""
Check the files created by our websocket library tests
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qusb2snes_connection import QUSB2SNESConnection
from qusb2snes_device import QUSB2SNESDevice
from qusb2snes_filesystem import QUSB2SNESFileSystem

async def check_test_files():
    """Check the sizes of files created by our websocket tests"""
    
    print("🔍 Checking Test File Results")
    print("=" * 40)
    
    connection = None
    try:
        connection = QUSB2SNESConnection()
        await connection.connect()
        
        device = QUSB2SNESDevice(connection)
        devices = await device.discover_devices()
        await device.attach_device(devices[0].name)
        
        filesystem = QUSB2SNESFileSystem(connection)
        
        test_files = [
            "/roms/websocket_test.bin",  # websocket-client library
            "/roms/current_test.bin",    # current websockets library  
            "/roms/test_rom.smc",        # our V2 upload manager
            "/roms/protocol_test.bin"    # our protocol test
        ]
        
        for file_path in test_files:
            try:
                # Use the connection's send_command directly to get file info
                response = await connection.send_command("Info", operands=[file_path])
                if response and len(response) >= 2:
                    size = int(response[1], 16)  # Size is returned in hex
                    print(f"📄 {file_path}: {size} bytes")
                else:
                    print(f"❌ {file_path}: File not found or invalid response")
            except Exception as e:
                print(f"❌ {file_path}: Error - {e}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        if connection:
            await connection.disconnect()

if __name__ == "__main__":
    asyncio.run(check_test_files())