"""
SMWCentral Downloader v4.1 - Professional Build System
Creates industry-standard release packages with hidden updater directory structure.
"""

import os
import shutil
import subprocess
import time
import zipfile
from datetime import datetime

def build_executables():
    """Build both main app and updater executables"""
    print("🔨 Building SMWCentral Downloader executables...")
    
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Build main application
    print("📦 Building main application...")
    result = subprocess.run([
        "python", "-m", "PyInstaller", 
        "--clean", "--onefile", 
        "SMWC Downloader.spec"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Main app build failed: {result.stderr}")
        return False
    
    # Build updater
    print("🔄 Building updater...")
    result = subprocess.run([
        "python", "-m", "PyInstaller", 
        "--clean", "--onefile", 
        "SMWC Updater.spec"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Updater build failed: {result.stderr}")
        return False
    
    # Verify executables exist
    main_exe = os.path.join("dist", "SMWC Downloader.exe")
    updater_exe = os.path.join("dist", "SMWC Updater.exe")
    
    if not os.path.exists(main_exe):
        print(f"❌ Main executable not found: {main_exe}")
        return False
    
    if not os.path.exists(updater_exe):
        print(f"❌ Updater executable not found: {updater_exe}")
        return False
    
    # Show file sizes
    main_size = os.path.getsize(main_exe) / (1024*1024)
    updater_size = os.path.getsize(updater_exe) / (1024*1024)
    
    print(f"✅ Main app built: {main_size:.1f}MB")
    print(f"✅ Updater built: {updater_size:.1f}MB")
    
    return True

def create_release_packages():
    """Create professional release packages"""
    print("📦 Creating release packages...")
    
    # Create release directory
    release_dir = "release"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Paths to executables
    main_exe = os.path.join("dist", "SMWC Downloader.exe")
    updater_exe = os.path.join("dist", "SMWC Updater.exe")
    
    # Create Hidden Updater Package (Recommended)
    print("📁 Creating Hidden Updater Package...")
    hidden_dir = os.path.join(release_dir, "SMWCentral_Downloader_v4.1_HiddenUpdater")
    os.makedirs(hidden_dir)
    
    # Create updater subdirectory
    updater_subdir = os.path.join(hidden_dir, "updater")
    os.makedirs(updater_subdir)
    
    # Copy files
    shutil.copy2(main_exe, hidden_dir)
    shutil.copy2(updater_exe, updater_subdir)
    
    # Create README
    readme_content = """SMWCentral Downloader & Patcher v4.1
========================================

INSTALLATION INSTRUCTIONS:
1. Extract this entire folder to your desired location
2. Run "SMWC Downloader.exe" to start the application
3. DO NOT move or delete the "updater" folder - it's required for updates

IMPORTANT NOTES:
- The "updater" folder contains the update system
- Keep all files together in the same directory
- Updates will be handled automatically by the application

FEATURES:
- Download and patch Super Mario World ROM hacks from SMWCentral
- Automatic update system with industry-standard architecture
- Dark/Light theme support
- Comprehensive hack management and filtering
- Multi-type hack support (Standard, Kaizo, Puzzle, etc.)

For support, visit: https://github.com/iamtheratio/SMWCentral-Downloader---Patcher

Copyright (c) 2025 iamtheratio
Licensed under the MIT License
"""
    
    with open(os.path.join(hidden_dir, "README.txt"), "w") as f:
        f.write(readme_content)
    
    # Create zip package
    hidden_zip = os.path.join(release_dir, f"SMWCentral_Downloader_v4.1_HiddenUpdater_{timestamp}.zip")
    with zipfile.ZipFile(hidden_zip, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(hidden_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, release_dir)
                zip_file.write(file_path, arc_name)
    
    print(f"✅ Hidden Updater Package: {os.path.basename(hidden_zip)}")
    
    # Create Installer Package (Alternative)
    print("📁 Creating Installer Package...")
    installer_dir = os.path.join(release_dir, "SMWCentral_Downloader_v4.1_Installer")
    os.makedirs(installer_dir)
    
    # Copy files
    shutil.copy2(main_exe, installer_dir)
    shutil.copy2(updater_exe, installer_dir)
    
    # Create installer batch script
    installer_script = """@echo off
title SMWCentral Downloader v4.1 Installer
echo.
echo SMWCentral Downloader v4.1 Installer
echo ===================================
echo.
echo This installer will set up the application with proper directory structure.
echo.
pause

REM Create updater directory
if not exist "updater" mkdir "updater"

REM Move updater to subdirectory
if exist "SMWC Updater.exe" (
    move "SMWC Updater.exe" "updater\\"
    echo ✅ Updater moved to updater directory
) else (
    echo ❌ Updater executable not found
)

REM Create desktop shortcut (optional)
set /p create_shortcut="Create desktop shortcut? (y/n): "
if /i "%create_shortcut%"=="y" (
    echo Creating desktop shortcut...
    REM Note: This would require additional VBScript or PowerShell for proper shortcut creation
    echo Desktop shortcut creation requires manual setup.
)

echo.
echo ✅ Installation complete!
echo.
echo You can now run "SMWC Downloader.exe" to start the application.
echo The updater has been properly configured in the updater directory.
echo.
echo IMPORTANT: Keep the updater directory alongside the main executable.
echo.
pause
"""
    
    with open(os.path.join(installer_dir, "Install.bat"), "w") as f:
        f.write(installer_script)
    
    # Create installer README
    installer_readme = """SMWCentral Downloader & Patcher v4.1 - INSTALLER PACKAGE
============================================================

INSTALLATION INSTRUCTIONS:
1. Extract this entire folder to your desired location
2. Run "Install.bat" to automatically set up the directory structure
3. Run "SMWC Downloader.exe" to start the application

MANUAL INSTALLATION:
If you prefer manual setup:
1. Create a folder called "updater" in the same directory as "SMWC Downloader.exe"
2. Move "SMWC Updater.exe" into the "updater" folder
3. Run "SMWC Downloader.exe"

PACKAGE CONTENTS:
- SMWC Downloader.exe (Main application)
- SMWC Updater.exe (Update system)
- Install.bat (Automatic installer)
- README.txt (This file)

The automatic installer will create the proper directory structure
for the industry-standard hidden updater system.

For support, visit: https://github.com/iamtheratio/SMWCentral-Downloader---Patcher

Copyright (c) 2025 iamtheratio
Licensed under the MIT License
"""
    
    with open(os.path.join(installer_dir, "README.txt"), "w") as f:
        f.write(installer_readme)
    
    # Create installer zip package
    installer_zip = os.path.join(release_dir, f"SMWCentral_Downloader_v4.1_Installer_{timestamp}.zip")
    with zipfile.ZipFile(installer_zip, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(installer_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, release_dir)
                zip_file.write(file_path, arc_name)
    
    print(f"✅ Installer Package: {os.path.basename(installer_zip)}")
    
    # Calculate package sizes
    hidden_size = os.path.getsize(hidden_zip) / (1024*1024)
    installer_size = os.path.getsize(installer_zip) / (1024*1024)
    
    print(f"\n📊 Package Summary:")
    print(f"   Hidden Updater: {hidden_size:.1f}MB")
    print(f"   Installer: {installer_size:.1f}MB")
    
    return True

def main():
    """Main build process"""
    print("🏭 SMWCentral Downloader v4.1 - Professional Build System")
    print("=" * 60)
    
    # Step 1: Build executables
    if not build_executables():
        print("❌ Build failed!")
        return False
    
    # Step 2: Create release packages
    if not create_release_packages():
        print("❌ Release packaging failed!")
        return False
    
    # Step 3: Success summary
    print("\n🎉 Build Complete!")
    print("=" * 60)
    print(f"📁 Release directory: {os.path.abspath('release')}")
    print("\n📦 Release Packages:")
    
    release_files = [f for f in os.listdir("release") if f.endswith(".zip")]
    for file in release_files:
        file_path = os.path.join("release", file)
        size = os.path.getsize(file_path) / (1024*1024)
        print(f"   • {file} ({size:.1f}MB)")
    
    print("\n🌟 Industry-Standard Distribution:")
    print("   • Hidden Updater Package: Recommended for most users")
    print("   • Installer Package: Alternative with setup script")
    print("   • Both packages follow Chrome/Firefox/Steam architecture")
    print("   • Updater is properly hidden in subdirectory")
    print("   • Professional documentation included")
    
    return True

if __name__ == "__main__":
    main()
