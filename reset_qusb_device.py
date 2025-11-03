#!/usr/bin/env python3
"""
QUSB2SNES Device Reset Utility
Fixes device conflicts and stuck attachment states
"""

import asyncio
import json
import websockets
from websockets.exceptions import ConnectionClosed


class QUSBDeviceReset:
    """Reset utility for stuck QUSB2SNES devices"""
    
    def __init__(self, host="localhost", port=23074):
        self.host = host
        self.port = port
        self.uri = f"ws://{host}:{port}"
    
    async def reset_device(self):
        """Reset device by forcing disconnection and cleanup"""
        print("🔧 QUSB2SNES Device Reset Utility")
        print("This will attempt to fix device conflicts and stuck states")
        
        try:
            # Connect to QUsb2snes
            print(f"🔌 Connecting to QUsb2snes at {self.uri}...")
            websocket = await websockets.connect(self.uri)
            
            try:
                # Get device list
                print("📱 Getting device list...")
                await websocket.send(json.dumps({"Opcode": "DeviceList", "Space": "SNES"}))
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                device_data = json.loads(response)
                
                if "Results" in device_data and device_data["Results"]:
                    devices = device_data["Results"]
                    print(f"📋 Found devices: {devices}")
                    
                    # Try to attach and immediately detach each device to reset state
                    for device_name in devices:
                        print(f"🔄 Resetting device: {device_name}")
                        
                        # Force attach
                        await websocket.send(json.dumps({
                            "Opcode": "Attach", 
                            "Space": "SNES", 
                            "Operands": [device_name]
                        }))
                        
                        # Brief pause
                        await asyncio.sleep(0.5)
                        
                        # Send Name command to establish connection
                        await websocket.send(json.dumps({
                            "Opcode": "Name",
                            "Space": "SNES", 
                            "Operands": ["DeviceResetUtility"]
                        }))
                        
                        # Brief pause
                        await asyncio.sleep(0.5)
                        
                        print(f"✅ Reset completed for: {device_name}")
                
                else:
                    print("⚠️ No devices found or device list empty")
                
            finally:
                # Clean disconnect
                await websocket.close()
                print("🔌 Disconnected from QUsb2snes")
            
            print("\n✅ Device reset completed!")
            print("📝 Next steps:")
            print("   1. Close any running SMWC Downloader applications")
            print("   2. Restart QUsb2snes application if problems persist")
            print("   3. Try your tests again")
            
            return True
            
        except ConnectionRefusedError:
            print("❌ Could not connect to QUsb2snes")
            print("   Make sure QUsb2snes application is running")
            return False
            
        except Exception as e:
            print(f"❌ Reset failed: {e}")
            print("   Try restarting QUsb2snes application manually")
            return False
    
    async def check_status(self):
        """Check current device status"""
        print("🔍 Checking QUSB2SNES device status...")
        
        try:
            websocket = await websockets.connect(self.uri)
            
            try:
                # Get device list
                await websocket.send(json.dumps({"Opcode": "DeviceList", "Space": "SNES"}))
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                device_data = json.loads(response)
                
                if "Results" in device_data:
                    devices = device_data["Results"]
                    print(f"📱 Available devices: {devices if devices else 'None'}")
                    
                    if devices:
                        # Check each device status
                        for device_name in devices:
                            try:
                                # Try to get device info
                                await websocket.send(json.dumps({
                                    "Opcode": "Info",
                                    "Space": "SNES"
                                }))
                                info_response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                                info_data = json.loads(info_response)
                                print(f"ℹ️ Device info for {device_name}: {info_data}")
                                
                            except asyncio.TimeoutError:
                                print(f"⚠️ Device {device_name} appears to be stuck or in conflict")
                            except Exception as e:
                                print(f"⚠️ Device {device_name} status check failed: {e}")
                
            finally:
                await websocket.close()
                
        except Exception as e:
            print(f"❌ Status check failed: {e}")


async def main():
    """Main reset utility function"""
    reset_util = QUSBDeviceReset()
    
    print("Choose an option:")
    print("1. Reset devices (recommended)")
    print("2. Check device status")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        await reset_util.reset_device()
    elif choice == "2":
        await reset_util.check_status()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())