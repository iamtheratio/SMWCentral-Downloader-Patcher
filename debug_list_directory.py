#!/usr/bin/env python3
"""
Debug the list_directory issue to understand why root listing fails.
"""

import asyncio
from qusb2snes_sync import QUSB2SNESSync


async def debug_list_directory_issue():
    """Debug why list_directory fails on root"""
    print("🔧 Debugging List Directory Issue")
    print("="*50)
    
    sync = QUSB2SNESSync("localhost", 23074)
    sync.on_progress = lambda msg: print(f"📡 {msg}")
    sync.on_error = lambda msg: print(f"❌ {msg}")
    
    try:
        # Connect and attach
        if not await sync.connect():
            print("❌ Failed to connect")
            return
        
        devices = await sync.get_devices()
        if not devices:
            print("❌ No devices")
            return
        
        if not await sync.attach_device(devices[0]):
            print("❌ Failed to attach")
            return
        
        print(f"✅ Connected to {devices[0]}")
        
        # Check connection status before listing
        print(f"Connection status: connected={sync.connected}")
        print(f"WebSocket status: {sync.websocket}")
        print(f"WebSocket closed: {sync.websocket.closed if sync.websocket else 'N/A'}")
        
        # Try direct command
        print("\n🧪 Testing direct List command...")
        try:
            response = await sync._send_command("List", operands=["/"])
            print(f"✅ Direct command response: {response}")
        except Exception as e:
            print(f"❌ Direct command failed: {e}")
            print(f"Connection after error: connected={sync.connected}")
            print(f"WebSocket after error: closed={sync.websocket.closed if sync.websocket else 'N/A'}")
        
        # If connection is still alive, try the list_directory method
        if sync.connected and sync.websocket and not sync.websocket.closed:
            print("\n🧪 Testing list_directory method...")
            try:
                items = await sync.list_directory("/")
                print(f"✅ list_directory worked: {len(items)} items")
                print(f"Items: {[item['name'] for item in items]}")
            except Exception as e:
                print(f"❌ list_directory failed: {e}")
        else:
            print("❌ Connection lost, cannot test list_directory")
    
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            await sync.disconnect()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(debug_list_directory_issue())