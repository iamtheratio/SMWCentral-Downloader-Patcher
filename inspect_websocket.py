#!/usr/bin/env python3
"""
Inspect the websocket object to see what methods are available
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qusb2snes_connection import QUSB2SNESConnection

async def inspect_websocket():
    """Check what methods are available on the websocket object"""
    
    print("🔍 Inspecting WebSocket Object")
    print("=" * 40)
    
    connection = QUSB2SNESConnection()
    
    try:
        await connection.connect()
        
        print("✅ Connected!")
        print(f"WebSocket object type: {type(connection.websocket)}")
        print(f"WebSocket object: {connection.websocket}")
        
        print("\n📋 Available methods:")
        methods = [method for method in dir(connection.websocket) if not method.startswith('_')]
        for method in sorted(methods):
            print(f"  - {method}")
        
        print("\n🔍 Checking for binary send methods:")
        binary_methods = [
            'send_bytes', 'send_binary', 'sendBinaryMessage', 
            'send_binary_message', 'binary_send', 'sendBinary'
        ]
        
        for method in binary_methods:
            if hasattr(connection.websocket, method):
                print(f"  ✅ {method} - AVAILABLE")
            else:
                print(f"  ❌ {method} - not available")
        
        print(f"\n📝 WebSocket library: {connection.websocket.__module__}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        if connection:
            await connection.disconnect()

if __name__ == "__main__":
    asyncio.run(inspect_websocket())