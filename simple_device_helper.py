#!/usr/bin/env python3
"""
Simple QUSB2SNES Device Conflict Helper

Based on your error log, the issue is clear:
- QUSB2SNES connects successfully ✅
- Device is found (SD2SNES COM3) ✅  
- Device attachment fails ❌ - "likely in use by another application"

This tool provides simple solutions without installing anything extra.
"""

import asyncio
import subprocess
import sys
from qusb2snes_sync import QUSB2SNESSync

async def test_device_status():
    """Test current device status"""
    print("🔍 Testing SD2SNES Device Status")
    print("=" * 40)
    
    sync = QUSB2SNESSync()
    
    try:
        print("1. Connecting to QUSB2SNES...")
        connected = await sync.connect()
        
        if not connected:
            print("   ❌ Cannot connect to QUSB2SNES")
            return False
        
        print("   ✅ Connected successfully")
        
        print("\n2. Getting device list...")
        devices = await sync.get_devices()
        print(f"   📱 Found: {devices}")
        
        if not devices:
            print("   ❌ No devices found")
            return False
        
        print(f"\n3. Testing device attachment to {devices[0]}...")
        attached = await sync.attach_device(devices[0])
        
        if attached:
            print("   ✅ Device attached successfully - NO CONFLICT!")
            return True
        else:
            print("   ❌ Device attachment failed - CONFLICT DETECTED")
            print("   💡 Another application is using the device")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False
    finally:
        if sync.websocket:
            await sync.websocket.close()

def show_conflict_solutions():
    """Show solutions for device conflicts"""
    print("\n🛠️ DEVICE CONFLICT SOLUTIONS")
    print("=" * 40)
    print("Based on your error, another app is using SD2SNES.")
    print("\n📋 COMMON CONFLICTING APPLICATIONS:")
    print("   • RetroAchievements (RA2Snes)")
    print("   • QFile2Snes") 
    print("   • Button Mash")
    print("   • Savestate2Snes")
    print("   • BizHawk emulator")
    print("   • Any other USB2SNES app")
    
    print("\n✅ SOLUTION STEPS:")
    print("   1. Close ALL emulators and ROM tools")
    print("   2. Check Windows system tray for USB2SNES apps")
    print("   3. Open Task Manager and end any USB2SNES processes")
    print("   4. Wait 5 seconds, then try sync again")
    
    print("\n🔄 ALTERNATIVE SOLUTIONS:")
    print("   • Restart QUSB2SNES completely")
    print("   • Unplug and reconnect SD2SNES device")
    print("   • Use a different USB port")

def check_task_manager_apps():
    """Show how to check Task Manager for conflicts"""
    print("\n🔍 HOW TO CHECK TASK MANAGER:")
    print("=" * 40)
    print("1. Press Ctrl+Shift+Esc to open Task Manager")
    print("2. Click 'More details' if needed")
    print("3. Look for these process names:")
    print("   • RetroAchievements.exe")
    print("   • RA2Snes.exe")
    print("   • QFile2Snes.exe")
    print("   • BizHawk.exe")
    print("   • usb2snes.exe")
    print("4. Right-click and 'End task' on any found")
    print("5. Try the sync again")

async def main():
    """Main diagnostic"""
    print("🧪 QUSB2SNES Device Conflict Helper")
    print("=" * 50)
    
    # Test current status
    device_free = await test_device_status()
    
    if device_free:
        print("\n🎉 SUCCESS: Device is working fine!")
        print("   You can use sync functionality now.")
    else:
        print("\n❌ CONFLICT: Device is being used by another app")
        show_conflict_solutions()
        check_task_manager_apps()
        
        print(f"\n🔄 Want to test again? (y/n): ", end="")
        if input().lower() == 'y':
            print("\n" + "="*50)
            device_free = await test_device_status()
            
            if device_free:
                print("\n🎉 FIXED: Device conflict resolved!")
            else:
                print("\n❌ Still conflicted. Try restarting QUSB2SNES.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")