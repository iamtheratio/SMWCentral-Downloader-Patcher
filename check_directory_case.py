#!/usr/bin/env python3
"""
Quick test to check the actual case-sensitive directory structure on SD card
"""

import asyncio
from qusb2snes_sync import QUSB2SNESSync

async def check_directories():
    """Check what directories actually exist and their exact case"""
    
    print("🔍 Checking SD card directory structure...")
    
    # Initialize connection
    sync = QUSB2SNESSync()
    
    try:
        # Connect to QUSB2SNES
        print("🔗 Connecting to QUSB2SNES...")
        await sync.connect()
        
        # List root directory to see exact case
        print("\n📁 Root directory contents:")
        root_files = await sync._send_command("List", operands=["/"])
        if root_files:
            for item in root_files:
                print(f"  📂 {item}")
        
        # Check various case combinations
        test_paths = ["/ROMS/", "/roms/", "/Roms/", "/ROMs/"]
        
        for path in test_paths:
            print(f"\n🧪 Testing: {path}")
            try:
                files = await sync._send_command("List", operands=[path])
                if files:
                    print(f"  ✅ {path} exists! Contains {len(files)} items")
                    # Show first few items
                    for i, item in enumerate(files[:5]):
                        print(f"    📄 {item}")
                    if len(files) > 5:
                        print(f"    ... and {len(files) - 5} more items")
                else:
                    print(f"  ❌ {path} - No response or empty")
            except Exception as e:
                print(f"  ❌ {path} - Error: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        if sync:
            await sync.disconnect()
        print("🔌 Disconnected")

if __name__ == "__main__":
    asyncio.run(check_directories())