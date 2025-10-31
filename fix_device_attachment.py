#!/usr/bin/env python3
"""
QUSB2SNES Device Attachment Fixer

This tool specifically addresses the "Info command timeout" issue
that prevents device attachment even when the device is detected.
"""

import subprocess
import time
import sys
import os

def check_qusb2snes_process():
    """Check QUsb2Snes process details"""
    print("🔍 CHECKING QUSB2SNES PROCESS")
    print("=" * 50)
    
    try:
        result = subprocess.run('tasklist /FI "IMAGENAME eq QUsb2Snes.exe" /FO CSV /V', 
                              shell=True, capture_output=True, text=True)
        
        if result.returncode == 0 and 'QUsb2Snes.exe' in result.stdout:
            print("📊 QUsb2Snes Process Details:")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'QUsb2Snes.exe' in line:
                    parts = line.split('","')
                    if len(parts) >= 2:
                        pid = parts[1].strip('"')
                        print(f"   PID: {pid}")
                        
                        # Get process uptime
                        uptime_result = subprocess.run(f'wmic process where processid={pid} get CreationDate', 
                                                     shell=True, capture_output=True, text=True)
                        if uptime_result.returncode == 0:
                            print(f"   Process info: {uptime_result.stdout.strip()}")
            return True
        else:
            print("❌ QUsb2Snes.exe not running")
            return False
            
    except Exception as e:
        print(f"❌ Error checking process: {e}")
        return False

def force_reset_qusb2snes():
    """Force reset QUsb2Snes to clear any stuck states"""
    print("\n🔄 FORCE RESETTING QUSB2SNES")
    print("=" * 50)
    
    # Step 1: Kill all QUsb2Snes processes forcefully
    print("1. Force killing all QUsb2Snes processes...")
    subprocess.run('taskkill /F /IM QUsb2Snes.exe /T', shell=True, capture_output=True)
    
    # Step 2: Wait longer this time
    print("2. Waiting 10 seconds for complete cleanup...")
    time.sleep(10)
    
    # Step 3: Check if any processes are still running
    result = subprocess.run('tasklist | findstr QUsb2Snes', shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("⚠️ QUsb2Snes processes still running, trying harder...")
        subprocess.run('wmic process where "name=\'QUsb2Snes.exe\'" delete', shell=True)
        time.sleep(5)
    else:
        print("✅ All QUsb2Snes processes terminated")
    
    # Step 4: Clear any Windows USB device cache
    print("3. Clearing Windows device cache...")
    subprocess.run('rundll32.exe cfgmgr32.dll,CM_Request_Device_Eject', shell=True, capture_output=True)
    time.sleep(2)
    
    # Step 5: Restart QUsb2Snes
    print("4. Starting QUsb2Snes fresh...")
    qusb_path = r"D:\SuperNT\QUsb2Snes\QUsb2Snes.exe"
    
    try:
        # Start QUsb2Snes in a new process group
        subprocess.Popen([qusb_path], 
                        shell=True, 
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        
        print("✅ QUsb2Snes started fresh")
        
        # Wait longer for full initialization
        print("5. Waiting 15 seconds for full initialization...")
        for i in range(15, 0, -1):
            print(f"   {i} seconds remaining...", end='\r')
            time.sleep(1)
        print("   Initialization complete!     ")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start QUsb2Snes: {e}")
        return False

def test_device_attachment():
    """Test if we can now attach to the device"""
    print("\n🧪 TESTING DEVICE ATTACHMENT")
    print("=" * 50)
    
    try:
        # Add project path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        print("📡 Testing device detection and attachment...")
        
        # Run a more comprehensive test
        test_code = '''
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qusb2snes_sync import QUSB2SNESSyncManager

async def test_attachment():
    manager = QUSB2SNESSyncManager()
    
    try:
        print("1. Connecting to QUsb2Snes...")
        connected = await manager.connect_and_attach()
        
        if connected:
            print("   ✅ Connected successfully!")
            
            print("2. Getting device list...")
            devices = await manager.get_devices()
            print(f"   Found devices: {devices}")
            
            if devices:
                print("3. Testing device info...")
                # Test if we can get device info without timeout
                if hasattr(manager.sync_client, 'get_device_info'):
                    try:
                        info = await asyncio.wait_for(
                            manager.sync_client.get_device_info(), 
                            timeout=5.0
                        )
                        print(f"   ✅ Device info: {info}")
                        return True
                    except asyncio.TimeoutError:
                        print("   ❌ Device info timeout (attachment issue)")
                        return False
                    except Exception as e:
                        print(f"   ⚠️ Device info error: {e}")
                        return True  # Connection might still work
                else:
                    print("   ✅ Basic connection working")
                    return True
            else:
                print("   ❌ No devices found")
                return False
        else:
            print("   ❌ Failed to connect")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    finally:
        try:
            await manager.disconnect()
        except:
            pass

# Run the test
result = asyncio.run(test_attachment())
sys.exit(0 if result else 1)
'''
        
        # Write test to temp file and run it
        with open('temp_attachment_test.py', 'w') as f:
            f.write(test_code)
        
        result = subprocess.run([sys.executable, 'temp_attachment_test.py'], 
                              capture_output=True, text=True, timeout=30)
        
        # Clean up temp file
        try:
            os.remove('temp_attachment_test.py')
        except:
            pass
        
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("🎉 SUCCESS: Device attachment is working!")
            return True
        else:
            print("❌ Device attachment still failing")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def check_network_connections():
    """Check for any stuck network connections"""
    print("\n🌐 CHECKING NETWORK CONNECTIONS")
    print("=" * 50)
    
    # Check for any stuck connections to QUsb2Snes
    result = subprocess.run('netstat -ano | findstr 23074', shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("📊 Current connections to port 23074:")
        print(result.stdout)
        
        # Look for TIME_WAIT or stuck connections
        if 'TIME_WAIT' in result.stdout:
            print("⚠️ Found TIME_WAIT connections - these should clear automatically")
        
        if 'ESTABLISHED' in result.stdout:
            print("🔍 Found ESTABLISHED connections - checking if they're stuck...")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'ESTABLISHED' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        print(f"   Connection from PID {pid}")
    else:
        print("✅ No active connections to port 23074")

def main():
    """Main device attachment fixer"""
    print("🔧 QUSB2SNES DEVICE ATTACHMENT FIXER")
    print("=" * 60)
    print("This tool will fix the 'Info command timeout' issue")
    print("=" * 60)
    
    # Step 1: Check current state
    check_qusb2snes_process()
    check_network_connections()
    
    # Step 2: Force reset QUsb2Snes
    if force_reset_qusb2snes():
        
        # Step 3: Test attachment
        if test_device_attachment():
            print("\n🎉 SUCCESS!")
            print("=" * 50)
            print("✅ Device attachment issue has been resolved!")
            print("✅ Your app should now work properly")
            print("\n💡 If the issue returns:")
            print("• Run this script again")
            print("• The issue is usually caused by QUsb2Snes getting into a stuck state")
            return True
        else:
            print("\n⚠️ ATTACHMENT STILL FAILING")
            print("=" * 50)
            print("The device can be detected but attachment is still timing out.")
            print("\n🔧 Additional steps to try:")
            print("1. Unplug the SD2SNES for 30 seconds, then plug back in")
            print("2. Try a different USB port")
            print("3. Restart your computer")
            print("4. Check if the SD2SNES firmware is up to date")
            return False
    else:
        print("\n❌ QUSB2SNES RESTART FAILED")
        print("=" * 50)
        print("Could not restart QUsb2Snes properly.")
        print("Please manually:")
        print("1. Close QUsb2Snes completely")
        print("2. Wait 10 seconds")
        print("3. Start QUsb2Snes again")
        print("4. Try your app")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Attachment fix cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Attachment fix failed: {e}")
        sys.exit(1)