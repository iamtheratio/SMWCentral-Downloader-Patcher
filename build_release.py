"""
SMWCentral Downloader v4.1 - Professional Build System
Creates industry-standard release package with hidden updater directory structure.
"""

import os
import shutil
import subprocess
import time
import zipfile
import stat
from datetime import datetime
import json

def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def safe_remove_tree(path):
    """Safely remove a directory tree on Windows"""
    if os.path.exists(path):
        try:
            shutil.rmtree(path, onerror=remove_readonly)
        except PermissionError:
            print(f"⚠️ Could not remove {path} (files in use)")
            return False
    return True

def build_executables():
    """Build both main app and updater executables"""
    print("🔨 Building SMWCentral Downloader executables...")
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    safe_remove_tree("dist")
    safe_remove_tree("build")
    
    # Build main application
    print("📦 Building main application...")
    result = subprocess.run([
        "python", "-m", "PyInstaller", 
        "--clean", 
        "SMWC Downloader.spec"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] Main app build failed: {result.stderr}")
        return False
    
    # Build updater
    print("🔄 Building updater...")
    result = subprocess.run([
        "python", "-m", "PyInstaller", 
        "--clean", 
        "SMWC Updater.spec"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] Updater build failed: {result.stderr}")
        return False
    
    # Verify executables exist
    main_exe = os.path.join("dist", "SMWC Downloader.exe")
    updater_exe = os.path.join("dist", "SMWC Updater.exe")
    
    if not os.path.exists(main_exe):
        print(f"[ERROR] Main executable not found: {main_exe}")
        return False
    
    if not os.path.exists(updater_exe):
        print(f"[ERROR] Updater executable not found: {updater_exe}")
        return False
    
    # Display build info
    main_size = os.path.getsize(main_exe) / (1024*1024)
    updater_size = os.path.getsize(updater_exe) / (1024*1024)
    print(f"[OK] Main app built: {main_size:.1f}MB")
    print(f"[OK] Updater built: {updater_size:.1f}MB")
    
    return True

def create_release_packages():
    """Create a single professional release package with hidden updater structure"""
    print("📦 Creating release package...")
    
    # Create release directory
    release_dir = "release"
    safe_remove_tree(release_dir)
    os.makedirs(release_dir)
    
    # Paths to executables
    main_exe = os.path.join("dist", "SMWC Downloader.exe")
    updater_exe = os.path.join("dist", "SMWC Updater.exe")
    
    # Create main package directory
    package_dir = os.path.join(release_dir, "SMWC_Downloader_v4.1")
    os.makedirs(package_dir)
    
    # Create updater subdirectory (hidden updater structure)
    updater_subdir = os.path.join(package_dir, "updater")
    os.makedirs(updater_subdir)
    
    # Copy executables
    shutil.copy2(main_exe, package_dir)
    shutil.copy2(updater_exe, updater_subdir)
    
    # Create empty config.json
    empty_config = {}
    with open(os.path.join(package_dir, "config.json"), "w") as f:
        json.dump(empty_config, f, indent=2)
    
    # Create README.md
    readme_content = """# SMWCentral Downloader & Patcher v4.1

A desktop application for downloading and patching Super Mario World ROM hacks from SMWCentral.

## Installation

1. Extract this entire folder to your desired location
2. Run `SMWC Downloader.exe` to start the application
3. **DO NOT** move or delete the `updater` folder - it's required for automatic updates

## Features

- Download and patch Super Mario World ROM hacks from SMWCentral
- Automatic update system with industry-standard architecture
- Dark/Light theme support
- Comprehensive hack management and filtering
- Multi-type hack support (Standard, Kaizo, Puzzle, etc.)
- Search and browse hacks with advanced filtering
- Download history and progress tracking

## Important Notes

- The `updater` folder contains the update system - keep it alongside the main executable
- Updates will be handled automatically by the application
- First-time setup will require configuring your base ROM path and output directory

## Support

For support, bug reports, or feature requests, visit:
https://github.com/iamtheratio/SMWCentral-Downloader---Patcher

## License

Copyright (c) 2025 iamtheratio
Licensed under the MIT License
"""
    
    with open(os.path.join(package_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # Create zip package with proper name
    zip_path = os.path.join(release_dir, "SMWC_Downloader_v4.1.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Create archive path relative to package_dir
                arc_name = os.path.relpath(file_path, package_dir)
                zip_file.write(file_path, arc_name)
    
    print(f"[OK] Release package created: {os.path.basename(zip_path)}")
    
    # Calculate and display package size
    package_size = os.path.getsize(zip_path) / (1024*1024)
    print(f"[OK] Package size: {package_size:.1f}MB")
    
    return True

def main():
    """Main build process"""
    print("🏭 SMWCentral Downloader v4.1 - Professional Build System")
    print("=" * 60)
    
    # Step 1: Build executables
    if not build_executables():
        print("[ERROR] Build failed!")
        return False
    
    # Step 2: Create release package
    if not create_release_packages():
        print("[ERROR] Release packaging failed!")
        return False
    
    # Step 3: Success summary
    print("\n🎉 Build Complete!")
    print("=" * 60)
    print(f"📁 Release directory: {os.path.abspath('release')}")
    print("\n📦 Release Package:")
    
    release_files = [f for f in os.listdir("release") if f.endswith(".zip")]
    for file in release_files:
        file_path = os.path.join("release", file)
        size = os.path.getsize(file_path) / (1024*1024)
        print(f"   • {file} ({size:.1f}MB)")
    
    return True

if __name__ == "__main__":
    main()
