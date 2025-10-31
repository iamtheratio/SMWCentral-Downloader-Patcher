#!/usr/bin/env python3
"""
SD2SNES Device Diagnostic Tool

This tool will test various aspects of SD2SNES communication to identify the exact issue.
"""

import asyncio
import sys
import os
import time

# Add project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qusb2snes_sync import QUSB2SNESSync

async def test_basic_connection():
    """Test basic connection to QUsb2Snes"""
    print("🔗 Testing basic WebSocket connection...")
    
    client = QUSB2SNESSync("localhost", 23074)
    
    try:
        if await client.connect():
            print("✅ WebSocket connection successful")
            
            # Test device list
            devices = await client.get_devices()
            print(f"📱 Available devices: {devices}")
            
            if devices:
                device = devices[0]
                print(f"🎯 Testing attachment to: {device}")
                
                # Test attachment
                if await client.attach_device(device):
                    print("✅ Device attachment successful")
                    
                    # Test device info with shorter timeout
                    try:
                        print("📡 Testing device info...")
                        info = await asyncio.wait_for(client.get_device_info(), timeout=5.0)
                        print(f"✅ Device info: {info}")
                        return True
                        
                    except asyncio.TimeoutError:
                        print("❌ Device info timeout (5s)")
                        
                        # Try a different approach - test if device is responsive at all
                        print("🔍 Testing if device responds to any commands...")
                        try:
                            # Try a simple file list command
                            files = await asyncio.wait_for(client.list_files("/"), timeout=10.0)
                            print(f"✅ Device IS responsive! Files: {len(files)} items")
                            return True
                        except asyncio.TimeoutError:
                            print("❌ Device completely unresponsive")
                        except Exception as e:
                            print(f"❌ Device error: {e}")
                            
                    except Exception as e:
                        print(f"❌ Device info error: {e}")
                else:
                    print("❌ Device attachment failed")
            else:
                print("❌ No devices found")
                
        else:
            print("❌ WebSocket connection failed")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        
    finally:
        try:
            await client.disconnect()
            print("🔌 Disconnected")
        except:
            pass
            
    return False

async def test_device_reset_sequence():
    """Test if power cycling the connection helps"""
    print("\n🔄 Testing device reset sequence...")
    
    # Connect and immediately disconnect to "reset" the device state
    client = QUSB2SNESSync("localhost", 23074)
    
    try:
        print("1️⃣ Quick connect...")
        if await client.connect():
            print("2️⃣ Getting devices...")
            devices = await client.get_devices()
            if devices:
                print("3️⃣ Quick disconnect...")
                await client.disconnect()
                
                print("4️⃣ Waiting 5 seconds for reset...")
                time.sleep(5)
                
                print("5️⃣ Reconnecting...")
                client2 = QUSB2SNESSync("localhost", 23074)
                if await client2.connect():
                    devices2 = await client2.get_devices()
                    if devices2:
                        device = devices2[0]
                        print(f"6️⃣ Attempting fresh attachment to {device}...")
                        if await client2.attach_device(device):
                            print("7️⃣ Testing device info after reset...")
                            try:
                                info = await asyncio.wait_for(client2.get_device_info(), timeout=15.0)
                                print(f"✅ SUCCESS after reset! Device info: {info}")
                                await client2.disconnect()
                                return True
                            except asyncio.TimeoutError:
                                print("❌ Still timing out after reset")
                            except Exception as e:
                                print(f"❌ Error after reset: {e}")
                        else:
                            print("❌ Attachment failed after reset")
                await client2.disconnect()
        
    except Exception as e:
        print(f"❌ Reset sequence error: {e}")
        
    return False

async def test_alternative_ports():
    """Test if the device responds on different ports"""
    print("\n🔍 Testing alternative QUsb2Snes configurations...")
    
    # Test different ports that QUsb2Snes might use
    ports = [23074, 8080, 65398]
    
    for port in ports:
        print(f"📡 Testing port {port}...")
        client = QUSB2SNESSync("localhost", port)
        
        try:
            if await client.connect():
                devices = await client.get_devices()
                print(f"   Port {port}: Found devices {devices}")
                await client.disconnect()
                if devices:
                    return port
            else:
                print(f"   Port {port}: Connection failed")
        except Exception as e:
            print(f"   Port {port}: Error - {e}")
    
    return None

async def main():
    """Main diagnostic sequence"""
    print("🔧 SD2SNES DEVICE DIAGNOSTIC TOOL")
    print("=" * 60)
    print("This will test various aspects of SD2SNES communication")
    print("=" * 60)
    
    # Test 1: Basic connection
    if await test_basic_connection():
        print("\n🎉 SUCCESS: Basic device communication is working!")
        print("The issue might be with the sync process specifically.")
        return
    
    # Test 2: Device reset sequence
    if await test_device_reset_sequence():
        print("\n🎉 SUCCESS: Device works after reset sequence!")
        print("Your app should incorporate a reset sequence before sync.")
        return
    
    # Test 3: Alternative ports
    working_port = await test_alternative_ports()
    if working_port and working_port != 23074:
        print(f"\n🎯 FOUND: Device responds on port {working_port} instead of 23074!")
        print(f"Try changing your app's port setting to {working_port}")
        return
    
    # If we get here, there's a deeper issue
    print("\n❌ DEVICE ISSUE DETECTED")
    print("=" * 50)
    print("The SD2SNES device is not responding to Info commands.")
    print("This could be due to:")
    print("• Firmware issue - try updating SD2SNES firmware")
    print("• Hardware issue - try a different USB cable/port")
    print("• Driver issue - reinstall USB drivers")
    print("• SD2SNES is in the wrong mode - ensure it's in normal mode")
    print("• Cart compatibility - try without a cart inserted")
    
    print(f"\n💡 TROUBLESHOOTING STEPS:")
    print("1. Power cycle the SD2SNES (unplug for 30 seconds)")
    print("2. Try a different USB cable")
    print("3. Try a different USB port")
    print("4. Update SD2SNES firmware")
    print("5. Test with QFile2Snes to see if it works")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic cancelled")
    except Exception as e:
        print(f"\n❌ Diagnostic failed: {e}")