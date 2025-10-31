#!/usr/bin/env python3
"""
COM Port Lock Resolver

This tool will help identify and resolve COM port locks.
"""

import subprocess
import time

def run_powershell_command(command, description):
    """Run a PowerShell command and return the result"""
    print(f"\n🔧 {description}")
    print("-" * 50)
    
    try:
        full_command = f'powershell "{command}"'
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                print(output)
                return True, output
            else:
                print("(No output)")
                return True, ""
        else:
            print(f"❌ Command failed: {result.stderr.strip()}")
            return False, result.stderr.strip()
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False, str(e)

def restart_qusb2snes():
    """Restart QUsb2Snes to release COM port locks"""
    print("\n🔄 RESTARTING QUSB2SNES")
    print("=" * 50)
    
    # Kill QUsb2Snes
    print("1. Stopping QUsb2Snes...")
    result = subprocess.run('taskkill /F /IM QUsb2Snes.exe', shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ QUsb2Snes stopped")
    else:
        print("   ⚠️ QUsb2Snes might not be running")
    
    # Wait a moment
    print("2. Waiting 3 seconds...")
    time.sleep(3)
    
    # Try to start it again
    print("3. Starting QUsb2Snes...")
    qusb2snes_path = r"D:\SuperNT\QUsb2Snes\QUsb2Snes.exe"
    
    try:
        subprocess.Popen([qusb2snes_path], shell=True)
        print("   ✅ QUsb2Snes restart initiated")
        print("   ⏳ Waiting 5 seconds for startup...")
        time.sleep(5)
        return True
    except Exception as e:
        print(f"   ❌ Failed to restart: {e}")
        print(f"   💡 Please manually start QUsb2Snes from: {qusb2snes_path}")
        return False

def reset_com_port():
    """Try to reset the COM port using Device Manager"""
    print("\n🔌 RESETTING COM PORT")
    print("=" * 50)
    
    # Disable the device
    success, output = run_powershell_command(
        "Disable-PnpDevice -InstanceId 'USB\\VID_1209&PID_5A22\\DEMO00000000' -Confirm:$false",
        "Disabling SD2SNES device"
    )
    
    if success:
        print("⏳ Waiting 2 seconds...")
        time.sleep(2)
        
        # Re-enable the device
        success, output = run_powershell_command(
            "Enable-PnpDevice -InstanceId 'USB\\VID_1209&PID_5A22\\DEMO00000000' -Confirm:$false",
            "Re-enabling SD2SNES device"
        )
        
        if success:
            print("✅ Device reset completed")
            print("⏳ Waiting 3 seconds for device to reinitialize...")
            time.sleep(3)
            return True
    
    print("❌ Device reset failed (may need admin privileges)")
    return False

def test_com_port_access():
    """Test if COM3 is now accessible"""
    print("\n🧪 TESTING COM PORT ACCESS")
    print("=" * 50)
    
    success, output = run_powershell_command(
        "try { $port = new-Object System.IO.Ports.SerialPort COM3; $port.Open(); $port.Close(); Write-Host 'SUCCESS: COM3 is now accessible' } catch { Write-Host 'STILL LOCKED:' $_.Exception.Message }",
        "Testing COM3 accessibility"
    )
    
    return success and "SUCCESS" in output

def main():
    """Main resolution workflow"""
    print("🔧 COM PORT LOCK RESOLVER")
    print("=" * 60)
    print("This tool will attempt to resolve the COM3 lock issue")
    print("=" * 60)
    
    # Step 1: Restart QUsb2Snes
    qusb_restarted = restart_qusb2snes()
    
    # Test if that fixed it
    if test_com_port_access():
        print("\n🎉 SUCCESS: QUsb2Snes restart resolved the issue!")
        return True
    
    # Step 2: Reset the COM port device
    print("\n💡 QUsb2Snes restart didn't work, trying device reset...")
    device_reset = reset_com_port()
    
    # Test again
    if test_com_port_access():
        print("\n🎉 SUCCESS: Device reset resolved the issue!")
        return True
    
    # Step 3: Manual instructions
    print("\n⚠️ AUTOMATIC RESOLUTION FAILED")
    print("=" * 50)
    print("Please try these manual steps:")
    print("1. Unplug the SD2SNES USB cable")
    print("2. Wait 10 seconds")
    print("3. Plug it back in")
    print("4. Wait for Windows to recognize it")
    print("5. Try your app again")
    
    print("\nAlternatively:")
    print("1. Restart your computer")
    print("2. Start QUsb2Snes first")
    print("3. Then start your app")
    
    return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ You can now try running your app again!")
        else:
            print("\n⚠️ Manual intervention required")
    except KeyboardInterrupt:
        print("\n⚠️ Resolution cancelled by user")
    except Exception as e:
        print(f"\n❌ Resolution failed: {str(e)}")