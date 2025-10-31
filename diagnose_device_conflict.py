#!/usr/bin/env python3
"""
QUSB2SNES Device Conflict Diagnostic Tool

This tool helps diagnose and resolve device conflicts when the SD2SNES
is not responding to commands.
"""

import asyncio
import psutil
import subprocess
import sys
from qusb2snes_sync import QUSB2SNESSync

# Known applications that can conflict with QUSB2SNES
CONFLICTING_APPS = [
    "RetroAchievements.exe",
    "RA2Snes.exe", 
    "QFile2Snes.exe",
    "Savestate2Snes.exe",
    "ButtonMash.exe",
    "BizHawk.exe",
    "SNI.exe",
    "usb2snes.exe"
]

async def test_qusb2snes_connection():
    """Test basic QUSB2SNES connection"""
    print("🔍 QUSB2SNES Connection Test")
    print("=" * 40)
    
    sync = QUSB2SNESSync()
    sync.on_progress = lambda msg: print(f"   {msg}")
    sync.on_error = lambda msg: print(f"   ❌ {msg}")
    
    try:
        # Test connection
        print("1. Testing WebSocket connection...")
        connected = await sync.connect()
        
        if not connected:
            print("   ❌ Cannot connect to QUSB2SNES WebSocket")
            print("   💡 Make sure QUsb2Snes.exe is running")
            return False
        
        print("   ✅ WebSocket connection successful")
        
        # Test device list
        print("\n2. Getting device list...")
        devices = await sync.get_devices()
        print(f"   📱 Found devices: {devices}")
        
        if not devices:
            print("   ⚠️ No devices found")
            print("   💡 Make sure your SD2SNES/FXPAK Pro is connected")
            return False
        
        # Test device attachment
        print(f"\n3. Testing device attachment...")
        device = devices[0]
        print(f"   Trying to attach to: {device}")
        
        attached = await sync.attach_device(device)
        
        if not attached:
            print("   ❌ Device attachment failed")
            print("   💡 Device is likely being used by another application")
            return False
        
        print("   ✅ Device attachment successful")
        
        # Test basic command
        print(f"\n4. Testing basic device communication...")
        try:
            # Try to list the root directory
            items = await sync.list_directory("/")
            print(f"   ✅ Device communication working")
            print(f"   📁 Root directory has {len(items)} items")
            return True
        except Exception as e:
            print(f"   ❌ Device communication failed: {str(e)}")
            return False
            
    except Exception as e:
        print(f"   ❌ Connection test failed: {str(e)}")
        return False
    finally:
        if sync.websocket:
            await sync.websocket.close()

def check_conflicting_processes():
    """Check for processes that might conflict with QUSB2SNES"""
    print("\n🔍 Checking for conflicting applications...")
    print("=" * 40)
    
    found_conflicts = []
    
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            process_name = proc.info['name']
            if process_name in CONFLICTING_APPS:
                found_conflicts.append({
                    'name': process_name,
                    'pid': proc.info['pid'],
                    'exe': proc.info['exe']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if found_conflicts:
        print("❌ Found conflicting applications:")
        for app in found_conflicts:
            print(f"   • {app['name']} (PID: {app['pid']})")
            if app['exe']:
                print(f"     Path: {app['exe']}")
        
        print("\n💡 SOLUTION:")
        print("   Close these applications and try again")
        
        # Offer to kill processes
        if input("\n🤔 Kill these processes automatically? (y/n): ").lower() == 'y':
            for app in found_conflicts:
                try:
                    proc = psutil.Process(app['pid'])
                    proc.terminate()
                    print(f"   ✅ Terminated {app['name']}")
                except Exception as e:
                    print(f"   ❌ Failed to terminate {app['name']}: {e}")
        
        return len(found_conflicts) == 0
    else:
        print("✅ No conflicting applications found")
        return True

def check_qusb2snes_running():
    """Check if QUSB2SNES is running"""
    print("\n🔍 Checking QUSB2SNES status...")
    print("=" * 40)
    
    qusb2snes_found = False
    
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            process_name = proc.info['name'].lower()
            if 'qusb2snes' in process_name or 'usb2snes' in process_name:
                print(f"✅ Found QUSB2SNES: {proc.info['name']} (PID: {proc.info['pid']})")
                if proc.info['exe']:
                    print(f"   Path: {proc.info['exe']}")
                qusb2snes_found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if not qusb2snes_found:
        print("❌ QUSB2SNES not found running")
        print("💡 Please start QUsb2Snes.exe")
        return False
    
    return True

async def main():
    """Main diagnostic routine"""
    print("🧪 QUSB2SNES Device Conflict Diagnostic")
    print("=" * 50)
    print("This tool helps diagnose SD2SNES device conflicts")
    print("=" * 50)
    
    # Step 1: Check if QUSB2SNES is running
    if not check_qusb2snes_running():
        return
    
    # Step 2: Check for conflicting processes
    conflicts_resolved = check_conflicting_processes()
    
    # Step 3: Test connection
    connection_works = await test_qusb2snes_connection()
    
    # Summary
    print("\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 40)
    
    if connection_works:
        print("🎉 SUCCESS: QUSB2SNES device is working properly!")
        print("   You can now use the sync functionality")
    else:
        print("❌ ISSUE: Device conflicts still present")
        print("\n💡 TROUBLESHOOTING STEPS:")
        print("   1. Restart QUSB2SNES completely")
        print("   2. Unplug and reconnect your SD2SNES/FXPAK Pro")
        print("   3. Check Windows Device Manager for USB issues")
        print("   4. Try a different USB port")
        print("   5. Restart your computer if all else fails")
    
    return connection_works

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Diagnostic failed: {str(e)}")
        sys.exit(1)