#!/usr/bin/env python3
"""
SD2SNES Device Recovery Tool

This will help us verify and restore your SD2SNES device.
"""

import subprocess
import time

def check_device_status():
    """Check if the SD2SNES device is properly detected"""
    print("🔍 CHECKING SD2SNES DEVICE STATUS")
    print("=" * 50)
    
    # Check serial ports
    try:
        result = subprocess.run(
            'powershell "Get-WmiObject -Class Win32_SerialPort | Select-Object Name, DeviceID, Status | Format-Table -AutoSize"',
            shell=True, capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            print("📊 Serial Ports:")
            print(result.stdout)
            
            if "COM3" in result.stdout and "USB Serial Device" in result.stdout:
                print("✅ SD2SNES found on COM3!")
                return True
            else:
                print("❌ SD2SNES not found on COM3")
                return False
        else:
            print(f"❌ Error checking serial ports: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_usb_devices():
    """Check USB device detection"""
    print("\n🔍 CHECKING USB DEVICE DETECTION")
    print("=" * 50)
    
    try:
        result = subprocess.run(
            'powershell "Get-WmiObject -Class Win32_USBControllerDevice | ForEach-Object { [wmi]($_.Dependent) } | Where-Object { $_.Name -like \'*USB Serial*\' -or $_.DeviceID -like \'*VID_1209*\' } | Select-Object Name, DeviceID, Status"',
            shell=True, capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            print("📊 USB Devices:")
            print(result.stdout)
            
            if "VID_1209" in result.stdout or "USB Serial" in result.stdout:
                print("✅ SD2SNES USB device detected!")
                return True
            else:
                print("⚠️ SD2SNES USB device not found in this query")
                return False
        else:
            print(f"❌ Error checking USB devices: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_qusb2snes_connection():
    """Test if QUsb2Snes can see the device"""
    print("\n🔍 TESTING QUSB2SNES CONNECTION")
    print("=" * 50)
    
    # First check if QUsb2Snes is running
    try:
        result = subprocess.run('tasklist | findstr QUsb2Snes', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ QUsb2Snes is running")
        else:
            print("❌ QUsb2Snes is not running - starting it...")
            try:
                subprocess.Popen([r"D:\SuperNT\QUsb2Snes\QUsb2Snes.exe"], shell=True)
                print("⏳ Waiting 5 seconds for QUsb2Snes to start...")
                time.sleep(5)
            except Exception as e:
                print(f"❌ Failed to start QUsb2Snes: {e}")
                return False
    except Exception as e:
        print(f"❌ Error checking QUsb2Snes: {e}")
        return False
    
    # Now test the actual connection
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        print("📡 Testing device detection...")
        from test_manager import test_basic_manager
        
        # Run our basic test
        result = subprocess.run([sys.executable, "test_manager.py"], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ QUsb2Snes connection test:")
            print(result.stdout)
            
            if "SD2SNES COM3" in result.stdout:
                print("🎉 SUCCESS: SD2SNES is working properly!")
                return True
            else:
                print("⚠️ Device detected but not responding properly")
                return False
        else:
            print("❌ QUsb2Snes connection test failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error testing QUsb2Snes: {e}")
        return False

def recovery_steps():
    """Provide recovery steps if device is not working"""
    print("\n🔧 DEVICE RECOVERY STEPS")
    print("=" * 50)
    
    print("If your device is not working, try these steps in order:")
    print()
    print("1. 🔌 PHYSICAL RECONNECTION:")
    print("   - Unplug the SD2SNES USB cable")
    print("   - Wait 10 seconds")
    print("   - Plug it back in")
    print("   - Wait for Windows chime/notification")
    print()
    print("2. 🔄 RESTART QUSB2SNES:")
    print("   - Close QUsb2Snes completely")
    print("   - Wait 5 seconds")
    print("   - Start QUsb2Snes again")
    print()
    print("3. 🖥️ DEVICE MANAGER:")
    print("   - Open Device Manager (devmgmt.msc)")
    print("   - Look for 'USB Serial Device (COM3)' under 'Ports (COM & LPT)'")
    print("   - Right-click it and select 'Uninstall device'")
    print("   - Unplug and replug the SD2SNES")
    print("   - Windows should reinstall the driver automatically")
    print()
    print("4. 🔄 REBOOT:")
    print("   - If all else fails, restart your computer")
    print("   - Start QUsb2Snes first after reboot")
    print("   - Then test your app")

def main():
    """Main recovery check"""
    print("🩺 SD2SNES DEVICE RECOVERY TOOL")
    print("=" * 60)
    print("Let's check if your SD2SNES device is working properly...")
    print("=" * 60)
    
    # Step 1: Check device status
    device_ok = check_device_status()
    
    # Step 2: Check USB detection
    usb_ok = check_usb_devices()
    
    # Step 3: Test QUsb2Snes connection
    qusb_ok = test_qusb2snes_connection()
    
    # Summary
    print("\n📋 RECOVERY SUMMARY")
    print("=" * 50)
    print(f"Device detected on COM3: {'✅' if device_ok else '❌'}")
    print(f"USB device detected: {'✅' if usb_ok else '❌'}")
    print(f"QUsb2Snes working: {'✅' if qusb_ok else '❌'}")
    
    if device_ok and qusb_ok:
        print("\n🎉 GOOD NEWS: Your SD2SNES is working properly!")
        print("The device was not uninstalled - it just needed a restart.")
        print("You can now use your app normally.")
    elif device_ok and not qusb_ok:
        print("\n⚠️ Device is detected but QUsb2Snes can't communicate with it.")
        print("This is likely a temporary communication issue.")
        recovery_steps()
    else:
        print("\n❌ Device detection issues found.")
        recovery_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Recovery check cancelled")
    except Exception as e:
        print(f"\n❌ Recovery check failed: {e}")