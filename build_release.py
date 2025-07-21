"""
SMWCentral Downloader - Professional Build System
Creates industry-standard release package with hidden updater directory structure.
Version is automatically pulled from main.py
"""

import os
import shutil
import subprocess
import time
import zipfile
import stat
from datetime import datetime
import json
from version_manager import get_version, get_version_string, get_package_name, get_zip_name
from generate_version import generate_version_txt

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
    
    # Generate version.txt with current version
    print("📝 Generating version.txt...")
    generate_version_txt()
    
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
    package_dir = os.path.join(release_dir, get_package_name())
    os.makedirs(package_dir)
    
    # Create updater subdirectory (hidden updater structure)
    updater_subdir = os.path.join(package_dir, "updater")
    os.makedirs(updater_subdir)
    
    # Copy executables
    shutil.copy2(main_exe, package_dir)
    shutil.copy2(updater_exe, updater_subdir)
    
    # Create config.json with sensible defaults (paths remain empty for user setup)
    default_config = {
        "base_rom_path": "",
        "output_dir": "",
        "api_delay": 0.8,
        "multi_type_enabled": True,
        "multi_type_download_mode": "primary_only",
        "auto_check_updates": True
    }
    with open(os.path.join(package_dir, "config.json"), "w") as f:
        json.dump(default_config, f, indent=2)
    
    # Create README.md
    readme_content = f"""# SMWCentral Downloader & Patcher {get_version()}

A desktop application for downloading and patching Super Mario World ROM hacks from SMWCentral.

## Installation

1. Extract this entire folder to your desired location
2. Run `SMWC Downloader.exe` to start the application
3. **DO NOT** move or delete the `updater` folder - it's required for automatic updates

## Features

- Download and patch Super Mario World ROM hacks from SMWCentral
- **NEW**: Download completion messages - clear feedback when fast downloads finish
- **NEW**: Obsolete Records filter in History page to show/hide superseded hack versions
- **ENHANCED**: Download page layout improvements with better button positioning
- **ENHANCED**: Select All/Deselect All functionality fixes
- Manual hack entry system - track hacks you've played elsewhere
- Full CRUD operations for managing your hack collection
- Duplicate detection with smart conflict resolution
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
    zip_path = os.path.join(release_dir, get_zip_name())
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
    print(f"🏭 SMWCentral Downloader {get_version()} - Professional Build System")
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
