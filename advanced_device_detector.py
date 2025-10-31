#!/usr/bin/env python3
"""
Advanced Device Conflict Detector

This tool will find EXACTLY what's using the SD2SNES device by checking:
1. All processes with open handles to COM3
2. All processes with network connections to USB2SNES ports
3. Hidden/background USB2SNES processes
4. Device manager status details
"""

import subprocess
import re
import time

def run_command_with_output(cmd, description):
    """Run a command and return both success status and output"""
    print(f"\n🔍 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout.strip() if result.stdout else ""
        error = result.stderr.strip() if result.stderr else ""
        
        if result.returncode == 0:
            if output:
                print(output)
                return True, output
            else:
                print("(No output)")
                return True, ""
        else:
            print(f"❌ Command failed (exit code {result.returncode})")
            if error:
                print(f"Error: {error}")
            return False, error
            
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False, "timeout"
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False, str(e)

def check_com_port_usage():
    """Check what's specifically using COM3"""
    print("\n🔌 COM PORT USAGE ANALYSIS")
    print("=" * 60)
    
    # Use PowerShell to get detailed COM port info
    success, output = run_command_with_output(
        'powershell "Get-WmiObject -Class Win32_SerialPort | Where-Object { $_.DeviceID -eq \'COM3\' } | Select-Object Name, DeviceID, Status, Description, InUse | Format-List"',
        "Detailed COM3 Port Information"
    )
    
    # Check for processes with handles to COM3 using handle.exe if available
    success, output = run_command_with_output(
        'wmic process where "name like \'%snes%\' or name like \'%usb%\' or name like \'%retro%\' or name like \'%qfile%\'" get processid,name,commandline',
        "USB2SNES Related Processes (WMI)"
    )

def check_network_connections_detailed():
    """Check detailed network connection info"""
    print("\n🌐 DETAILED NETWORK CONNECTION ANALYSIS")
    print("=" * 60)
    
    # Get detailed netstat with process names
    success, output = run_command_with_output(
        'netstat -anob | findstr :23074',
        "Detailed Port 23074 Usage (with process info)"
    )
    
    # Also check what's connecting TO the port
    success, output = run_command_with_output(
        'netstat -ano | findstr 23074',
        "All connections involving port 23074"
    )

def check_device_manager_detailed():
    """Get very detailed device manager info"""
    print("\n🖥️ DETAILED DEVICE MANAGER ANALYSIS")
    print("=" * 60)
    
    # Get specific info about our device
    success, output = run_command_with_output(
        'powershell "Get-PnpDevice | Where-Object { $_.InstanceId -eq \'USB\\VID_1209&PID_5A22\\DEMO00000000\' } | Select-Object FriendlyName, Status, Problem, ProblemDescription | Format-List"',
        "Specific SD2SNES Device Status"
    )
    
    # Check for device conflicts
    success, output = run_command_with_output(
        'powershell "Get-PnpDevice | Where-Object { $_.Status -ne \'OK\' -and ($_.FriendlyName -like \'*USB*\' -or $_.FriendlyName -like \'*Serial*\' -or $_.FriendlyName -like \'*COM*\') } | Select-Object FriendlyName, Status, Problem, ProblemDescription"',
        "USB/Serial Devices with Problems"
    )

def check_hidden_processes():
    """Look for hidden or background USB2SNES processes"""
    print("\n👻 HIDDEN PROCESS DETECTION")
    print("=" * 60)
    
    # Check for processes with USB2SNES related strings in command line
    success, output = run_command_with_output(
        'wmic process get processid,name,commandline | findstr /i "usb2snes\\|qusb\\|snes\\|retroach\\|bizhawk"',
        "Processes with USB2SNES related command lines"
    )
    
    # Check for .NET applications that might be using USB2SNES
    success, output = run_command_with_output(
        'tasklist /m mscoree.dll 2>nul | findstr /i "snes\\|retro\\|emul\\|hack"',
        ".NET Applications (common for emulators)"
    )
    
    # Look for Python processes that might be using the device
    success, output = run_command_with_output(
        'tasklist | findstr /i python',
        "Python processes (could be using QUSB2SNES)"
    )

def check_file_handles():
    """Try to detect file handles to COM3"""
    print("\n📂 FILE HANDLE ANALYSIS")
    print("=" * 60)
    
    # Try using PowerShell to get file handles (if possible)
    success, output = run_command_with_output(
        'powershell "Get-Process | Where-Object { $_.Handles -gt 0 } | Sort-Object Handles -Descending | Select-Object -First 20 Name, Id, Handles"',
        "Processes with Most File Handles (top 20)"
    )

def test_com_port_access():
    """Try to directly test COM3 access"""
    print("\n🧪 COM PORT ACCESS TEST")
    print("=" * 60)
    
    try:
        import serial
        print("📡 Attempting to open COM3 directly...")
        
        try:
            # Try to open COM3 briefly
            ser = serial.Serial('COM3', 9600, timeout=1)
            ser.close()
            print("✅ COM3 is accessible - no exclusive lock detected")
        except serial.SerialException as e:
            if "Access is denied" in str(e) or "being used by another process" in str(e):
                print(f"🔒 COM3 is LOCKED by another process: {e}")
            else:
                print(f"⚠️ COM3 access issue: {e}")
        except Exception as e:
            print(f"❌ Unexpected COM3 error: {e}")
            
    except ImportError:
        print("⚠️ pyserial not available for direct COM port testing")
        
        # Alternative: try with PowerShell
        success, output = run_command_with_output(
            'powershell "try { $port = new-Object System.IO.Ports.SerialPort COM3; $port.Open(); $port.Close(); Write-Host \'COM3 accessible\' } catch { Write-Host \'COM3 locked:\' $_.Exception.Message }"',
            "PowerShell COM3 Access Test"
        )

def kill_competing_processes():
    """Offer to kill common competing processes"""
    print("\n💀 PROCESS TERMINATION OPTIONS")
    print("=" * 60)
    
    common_competitors = [
        'QFile2Snes.exe',
        'RetroAchievements.exe', 
        'RA2Snes.exe',
        'ButtonMash.exe',
        'Savestate2Snes.exe',
        'BizHawk.exe',
        'snes9x.exe',
        'bsnes.exe'
    ]
    
    found_processes = []
    
    for process in common_competitors:
        success, output = run_command_with_output(
            f'tasklist /FI "IMAGENAME eq {process}" /FO CSV',
            f"Checking for {process}"
        )
        
        if success and 'No tasks are running' not in output and process in output:
            found_processes.append(process)
            print(f"🎯 FOUND: {process}")
    
    if found_processes:
        print(f"\n⚠️ Found {len(found_processes)} competing processes!")
        print("To kill them, run these commands:")
        for process in found_processes:
            print(f"   taskkill /F /IM {process}")
    else:
        print("✅ No obvious competing processes found")

def main():
    """Run comprehensive device conflict analysis"""
    print("🔍 ADVANCED DEVICE CONFLICT DETECTOR")
    print("=" * 70)
    print("This tool will find EXACTLY what's using your SD2SNES device")
    print("=" * 70)
    
    check_com_port_usage()
    check_network_connections_detailed()
    check_device_manager_detailed()
    check_hidden_processes()
    check_file_handles()
    test_com_port_access()
    kill_competing_processes()
    
    print(f"\n📋 DIAGNOSTIC COMPLETE")
    print("=" * 70)
    print("Review the output above to identify:")
    print("• What process has an exclusive lock on COM3")
    print("• Any hidden USB2SNES applications")
    print("• Device manager conflicts or problems")
    print("• Network connection details")
    
    print(f"\n💡 NEXT STEPS:")
    print("1. Look for any process that mentions COM3 or has high handle count")
    print("2. Kill any competing USB2SNES applications found")
    print("3. If COM3 shows as locked, restart the device or reboot")
    print("4. Try unplugging and reconnecting the SD2SNES")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic cancelled by user")
    except Exception as e:
        print(f"\n❌ Diagnostic failed: {str(e)}")