#!/usr/bin/env python3
"""
Windows USB and Network Diagnostic Tool for QUSB2SNES

This tool uses Windows commands to diagnose USB device and network port issues.
"""

import subprocess
import re
import json

def run_command(cmd, description):
    """Run a Windows command and return the output"""
    print(f"\n🔍 {description}")
    print("=" * 50)
    
    try:
        # Run the command
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                print(output)
                return output
            else:
                print("(No output)")
                return ""
        else:
            print(f"❌ Command failed (exit code {result.returncode})")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return None
    except Exception as e:
        print(f"❌ Error running command: {str(e)}")
        return None

def check_network_ports():
    """Check what's using network ports, especially 23074"""
    print("\n🌐 NETWORK PORT ANALYSIS")
    print("=" * 60)
    
    # Check what's listening on port 23074 (QUSB2SNES)
    netstat_output = run_command(
        'netstat -ano | findstr :23074',
        "Checking what's using port 23074 (QUSB2SNES port)"
    )
    
    if netstat_output:
        # Parse PIDs from netstat output
        lines = netstat_output.split('\n')
        pids = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 5:
                pid = parts[-1]
                if pid.isdigit():
                    pids.append(pid)
        
        # Get process names for PIDs
        for pid in set(pids):  # Remove duplicates
            process_info = run_command(
                f'tasklist /FI "PID eq {pid}" /FO CSV',
                f"Process using port 23074 (PID {pid})"
            )
    else:
        print("No processes found using port 23074")
        print("💡 This might mean QUSB2SNES is not running")
    
    # Check all listening ports to see what USB2SNES related things are running
    print(f"\n📊 All listening ports (looking for USB2SNES related):")
    all_ports = run_command(
        'netstat -ano | findstr LISTENING',
        "All listening network ports"
    )
    
    if all_ports:
        # Look for common USB2SNES ports
        usb2snes_ports = ['23074', '8080', '65398', '28000']
        found_ports = []
        
        for line in all_ports.split('\n'):
            for port in usb2snes_ports:
                if f':{port}' in line:
                    found_ports.append((port, line.strip()))
        
        if found_ports:
            print("🎯 Found USB2SNES related ports:")
            for port, line in found_ports:
                print(f"   Port {port}: {line}")
        else:
            print("No common USB2SNES ports found listening")

def check_usb_devices():
    """Check USB device information"""
    print("\n🔌 USB DEVICE ANALYSIS")
    print("=" * 60)
    
    # Get USB device information using PowerShell
    usb_info = run_command(
        'powershell "Get-WmiObject -Class Win32_USBControllerDevice | ForEach-Object { [wmi]($_.Dependent) } | Select-Object Name, DeviceID, Status | Format-Table -AutoSize"',
        "USB Devices via WMI"
    )
    
    # Also check with a more detailed PowerShell command for serial devices
    serial_info = run_command(
        'powershell "Get-WmiObject -Class Win32_SerialPort | Select-Object Name, DeviceID, Status, Description | Format-Table -AutoSize"',
        "Serial/COM Port Devices"
    )
    
    # Check for FTDI devices specifically (SD2SNES uses FTDI chip)
    ftdi_info = run_command(
        'powershell "Get-WmiObject -Class Win32_PnPEntity | Where-Object { $_.Name -like \'*FTDI*\' -or $_.Name -like \'*USB Serial*\' -or $_.Name -like \'*COM*\' } | Select-Object Name, DeviceID, Status | Format-Table -AutoSize"',
        "FTDI and Serial Devices (SD2SNES uses FTDI)"
    )

def check_running_processes():
    """Check for USB2SNES related processes"""
    print("\n⚙️ PROCESS ANALYSIS")
    print("=" * 60)
    
    # Common USB2SNES application executables
    usb2snes_apps = [
        'QUsb2Snes.exe',
        'usb2snes.exe', 
        'RetroAchievements.exe',
        'RA2Snes.exe',
        'QFile2Snes.exe',
        'Savestate2Snes.exe',
        'ButtonMash.exe',
        'BizHawk.exe',
        'snes9x.exe',
        'bsnes.exe'
    ]
    
    # Check each application
    found_processes = []
    for app in usb2snes_apps:
        result = run_command(
            f'tasklist /FI "IMAGENAME eq {app}" /FO CSV',
            f"Checking for {app}"
        )
        
        if result and 'No tasks are running' not in result:
            found_processes.append((app, result))
    
    if found_processes:
        print("\n🎯 FOUND USB2SNES RELATED PROCESSES:")
        for app, info in found_processes:
            print(f"\n• {app}:")
            print(f"  {info}")
    else:
        print("✅ No common USB2SNES applications found running")

def check_windows_device_manager():
    """Check Device Manager information"""
    print("\n🖥️ DEVICE MANAGER ANALYSIS")
    print("=" * 60)
    
    # Use PowerShell to get device manager info
    device_info = run_command(
        'powershell "Get-PnpDevice | Where-Object { $_.FriendlyName -like \'*USB*\' -or $_.FriendlyName -like \'*Serial*\' -or $_.FriendlyName -like \'*COM*\' -or $_.FriendlyName -like \'*FTDI*\' } | Select-Object FriendlyName, Status, InstanceId | Format-Table -AutoSize"',
        "Device Manager USB/Serial devices"
    )

def main():
    """Run all diagnostics"""
    print("🧪 Windows USB & Network Diagnostic Tool")
    print("=" * 60)
    print("This tool will help diagnose QUSB2SNES device conflicts")
    print("=" * 60)
    
    # Run all diagnostic checks
    check_network_ports()
    check_usb_devices() 
    check_running_processes()
    check_windows_device_manager()
    
    print(f"\n📋 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print("Review the output above to identify:")
    print("• What's using port 23074 (should be QUsb2Snes.exe)")
    print("• If your SD2SNES device is detected properly")
    print("• What USB2SNES applications are running")
    print("• Any device conflicts or errors")
    
    print(f"\n💡 NEXT STEPS:")
    print("1. If multiple apps are using USB2SNES ports → Close conflicting apps")
    print("2. If device not detected → Check USB connection/drivers")
    print("3. If QUsb2Snes.exe not running → Start it")
    print("4. If device shows errors → Try different USB port")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic cancelled by user")
    except Exception as e:
        print(f"\n❌ Diagnostic failed: {str(e)}")