#!/usr/bin/env python3
"""
Verify SD Card Contents - Check uploads from V2 integration test
Connects to QUSB2SNES and lists the ROM files on the SD card to verify uploads worked
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qusb2snes_connection import QUSB2SNESConnection
from qusb2snes_device import QUSB2SNESDevice
from qusb2snes_filesystem import QUSB2SNESFileSystem
from logging_system import LoggingSystem


class SDCardVerifier:
    """Verify the contents of the SD card after uploads"""
    
    def __init__(self):
        self.log_system = LoggingSystem()
        # No need to call setup_logging(), it's done automatically
        
    def log_info(self, message):
        self.log_system.log(message, "Information")
        
    def log_error(self, message):
        self.log_system.log(message, "Error")
        
    async def verify_sd_contents(self):
        """Connect to QUSB2SNES and list the ROM files on SD card"""
        print("🔍 SD Card Content Verification")
        print("=" * 50)
        
        connection = None
        try:
            # Step 1: Connect to QUSB2SNES
            print("\n🔗 Connecting to QUSB2SNES...")
            connection = QUSB2SNESConnection()
            await connection.connect()
            
            # Step 2: Get device
            device = QUSB2SNESDevice(connection)
            devices = await device.discover_devices()
            
            if not devices:
                print("❌ No devices found")
                return
                
            device_info = devices[0]
            device_name = device_info.name
            await device.attach_device(device_name)
            print(f"✅ Connected to device: {device_name}")
            
            # Step 3: Initialize filesystem
            filesystem = QUSB2SNESFileSystem(connection)
            
            # Step 4: Check ROMS directory structure
            print("\n📁 Checking ROMS directory structure...")
            await self.check_directory(filesystem, "/ROMS")
            
            # Step 5: Look for our uploaded files
            print("\n🎯 Verifying uploaded test files...")
            expected_files = [
                "/ROMS/Kaizo/04 - Advanced/Learn_2_Kaizo.smc",
                "/ROMS/Kaizo/05 - Expert/Item_Abuse_3.smc", 
                "/ROMS/Traditional/01 - Newcomer/Custom_ROM.smc",
                "/ROMS/Traditional/01 - Newcomer/Super_Mario_Plus.smc",
                "/ROMS/Traditional/01 - Newcomer/Vanilla_Secret_1.smc",
                "/ROMS/Traditional/02 - Casual/VIP_Wall_Mix_5.smc"
            ]
            
            found_files = []
            missing_files = []
            
            for expected_file in expected_files:
                try:
                    exists = await filesystem.file_exists(expected_file)
                    if exists:
                        # Get file size by listing parent directory
                        parent_dir = os.path.dirname(expected_file)
                        filename = os.path.basename(expected_file)
                        
                        try:
                            dir_contents = await filesystem.list_directory(parent_dir)
                            file_entry = next((entry for entry in dir_contents if entry.name == filename), None)
                            
                            if file_entry and file_entry.size:
                                size_mb = file_entry.size / (1024 * 1024)
                                found_files.append((expected_file, size_mb))
                                print(f"✅ Found: {os.path.basename(expected_file)} ({size_mb:.1f}MB)")
                            else:
                                found_files.append((expected_file, 0))
                                print(f"✅ Found: {os.path.basename(expected_file)} (size unknown)")
                        except Exception as e:
                            found_files.append((expected_file, 0))
                            print(f"✅ Found: {os.path.basename(expected_file)} (size check failed)")
                    else:
                        missing_files.append(expected_file)
                        print(f"❌ Missing: {expected_file}")
                except Exception as e:
                    missing_files.append(expected_file)
                    print(f"❌ Error checking {expected_file}: {e}")
            
            # Step 6: Summary
            print(f"\n📊 Verification Summary:")
            print(f"   ✅ Found: {len(found_files)} files")
            print(f"   ❌ Missing: {len(missing_files)} files")
            
            if len(found_files) == len(expected_files):
                print("🎉 SUCCESS: All uploaded files verified on SD card!")
            else:
                print("⚠️ Some files were not found on SD card")
                
            return len(found_files) == len(expected_files)
            
        except Exception as e:
            self.log_error(f"Error during verification: {e}")
            print(f"❌ Verification failed: {e}")
            return False
            
        finally:
            if connection:
                try:
                    await connection.disconnect()
                    print("\n🔌 Disconnected from QUSB2SNES")
                except Exception as e:
                    print(f"⚠️ Error disconnecting: {e}")
    
    async def check_directory(self, filesystem, path, max_depth=3, current_depth=0):
        """Recursively check directory contents with depth limit"""
        if current_depth >= max_depth:
            return
            
        try:
            # List directory contents
            contents = await filesystem.list_directory(path)
            if not contents:
                return
                
            indent = "  " * current_depth
            print(f"{indent}📁 {path}:")
            
            # Sort by type (directories first) then name
            directories = []
            files = []
            
            for item in contents:
                if item.is_directory:
                    directories.append(item)
                else:
                    files.append(item)
            
            # Show directories
            for directory in sorted(directories, key=lambda x: x.name):
                dir_name = directory.name
                print(f"{indent}  📂 {dir_name}/")
                
                # Recursively check subdirectory
                subdir_path = f"{path}/{dir_name}" if path != "/" else f"/{dir_name}"
                await self.check_directory(filesystem, subdir_path, max_depth, current_depth + 1)
            
            # Show files (just count for ROM directories to avoid spam)
            rom_files = [f for f in files if f.name.lower().endswith(('.smc', '.sfc'))]
            other_files = [f for f in files if not f.name.lower().endswith(('.smc', '.sfc'))]
            
            if rom_files:
                if len(rom_files) <= 5:  # Show individual files if not too many
                    for rom_file in sorted(rom_files, key=lambda x: x.name):
                        size_mb = (rom_file.size or 0) / (1024 * 1024)
                        print(f"{indent}  🎮 {rom_file.name} ({size_mb:.1f}MB)")
                else:
                    print(f"{indent}  🎮 {len(rom_files)} ROM files")
            
            if other_files:
                for other_file in sorted(other_files[:3], key=lambda x: x.name):  # Limit other files
                    print(f"{indent}  📄 {other_file.name}")
                if len(other_files) > 3:
                    print(f"{indent}  📄 ... and {len(other_files) - 3} more files")
                    
        except Exception as e:
            print(f"{indent}❌ Error listing {path}: {e}")


async def main():
    """Main verification function"""
    verifier = SDCardVerifier()
    success = await verifier.verify_sd_contents()
    
    if success:
        print("\n🎯 Verification completed successfully!")
        return 0
    else:
        print("\n⚠️ Verification found issues")
        return 1


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n🛑 Verification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Verification failed: {e}")
        sys.exit(1)