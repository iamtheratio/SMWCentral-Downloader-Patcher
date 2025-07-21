#!/usr/bin/env python3
"""
SMWCentral Downloader - macOS Build System
Creates macOS .app bundles and DMG installer packages.
Version is automatically pulled from main.py
"""

import os
import shutil
import subprocess
import zipfile
import stat
import json
from datetime import datetime
from version_manager import get_version, get_version_string, get_package_name, get_zip_name
from generate_version import generate_version_txt

def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def safe_remove_tree(path):
    """Safely remove a directory tree"""
    if os.path.exists(path):
        try:
            shutil.rmtree(path, onerror=remove_readonly)
        except PermissionError:
            print(f"⚠️ Could not remove {path} (files in use)")
            return False
    return True

def build_macos_executables():
    """Build macOS .app bundles using PyInstaller"""
    print("🔨 Building SMWCentral Downloader for macOS...")
    
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
        "SMWC Downloader macOS.spec"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] Main app build failed: {result.stderr}")
        return False
    
    # Build updater
    print("🔄 Building updater...")
    result = subprocess.run([
        "python", "-m", "PyInstaller", 
        "--clean", 
        "SMWC Updater macOS.spec"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] Updater build failed: {result.stderr}")
        return False
    
    # Verify applications exist
    main_app = os.path.join("dist", "SMWC Downloader.app")
    updater_app = os.path.join("dist", "SMWC Updater.app")
    
    if not os.path.exists(main_app):
        print(f"[ERROR] Main application not found: {main_app}")
        return False
    
    if not os.path.exists(updater_app):
        print(f"[ERROR] Updater application not found: {updater_app}")
        return False
    
    # Display build info
    def get_app_size(app_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(app_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size / (1024*1024)
    
    main_size = get_app_size(main_app)
    updater_size = get_app_size(updater_app)
    print(f"[OK] Main app built: {main_size:.1f}MB")
    print(f"[OK] Updater built: {updater_size:.1f}MB")
    
    return True

def create_macos_release_package():
    """Create macOS release package with .app bundles"""
    print("📦 Creating macOS release package...")
    
    # Create release directory
    release_dir = "release"
    safe_remove_tree(release_dir)
    os.makedirs(release_dir)
    
    # Paths to applications
    main_app = os.path.join("dist", "SMWC Downloader.app")
    updater_app = os.path.join("dist", "SMWC Updater.app")
    
    # Create main package directory
    package_name = get_package_name().replace("_", " ") + " macOS"
    package_dir = os.path.join(release_dir, package_name)
    os.makedirs(package_dir)
    
    # Create updater subdirectory
    updater_subdir = os.path.join(package_dir, "updater")
    os.makedirs(updater_subdir)
    
    # Copy applications
    shutil.copytree(main_app, os.path.join(package_dir, "SMWC Downloader.app"))
    shutil.copytree(updater_app, os.path.join(updater_subdir, "SMWC Updater.app"))
    
    # Create config.json with sensible defaults
    default_config = {
        "base_rom_path": "",
        "output_dir": "",
        "theme": "dark",
        "log_level": "INFO",
        "api_delay": 0.8,
        "multi_type_enabled": True,
        "multi_type_download_mode": "primary_only",
        "auto_check_updates": True
    }
    with open(os.path.join(package_dir, "config.json"), "w") as f:
        json.dump(default_config, f, indent=2)
    
    # Create macOS-specific README
    readme_content = f"""# SMWCentral Downloader & Patcher {get_version()} - macOS

A desktop application for downloading and patching Super Mario World ROM hacks from SMWCentral.

## Installation

1. Extract this folder to your Applications directory or desired location
2. Double-click "SMWC Downloader.app" to start the application
3. **DO NOT** move or delete the `updater` folder - it's required for automatic updates

## First Run Setup

1. When you first run the app, macOS may show a security warning
2. If blocked, go to System Preferences → Security & Privacy → General
3. Click "Open Anyway" to allow the application to run
4. Configure your base ROM path and output directory in Settings

## Features

- Download and patch Super Mario World ROM hacks from SMWCentral
- **NEW**: Cross-platform updates with automatic macOS detection
- **NEW**: Native macOS application bundle format
- Comprehensive hack management and filtering
- Multi-type hack support (Standard, Kaizo, Puzzle, etc.)
- Search and browse hacks with advanced filtering
- Download history and progress tracking
- Dark/Light theme support
- Automatic update system

## Important Notes

- The `updater` folder contains the update system - keep it alongside the main app
- Updates will be handled automatically by the application
- First-time setup will require configuring your base ROM path and output directory
- This is a native macOS build optimized for Apple Silicon and Intel Macs

## System Requirements

- macOS 10.14 (Mojave) or later
- 50MB free disk space (plus space for your ROM hack collection)
- Internet connection for downloading hacks

## Support

For support, bug reports, or feature requests, visit:
https://github.com/iamtheratio/SMWCentral-Downloader---Patcher

## License

Copyright (c) 2025 iamtheratio
Licensed under the MIT License
"""
    
    with open(os.path.join(package_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # Create zip package with macOS-specific name
    zip_name = get_zip_name().replace(".zip", "_macOS.zip")
    zip_path = os.path.join(release_dir, zip_name)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zip_file:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Create archive path relative to package_dir
                arc_name = os.path.relpath(file_path, package_dir)
                zip_file.write(file_path, arc_name)
    
    print(f"[OK] macOS release package created: {os.path.basename(zip_path)}")
    
    # Calculate and display package size
    package_size = os.path.getsize(zip_path) / (1024*1024)
    print(f"[OK] Package size: {package_size:.1f}MB")
    
    return True

def create_dmg_installer():
    """Create a DMG installer for easier distribution (optional)"""
    print("💿 Creating DMG installer...")
    
    try:
        # Check if create-dmg is available (brew install create-dmg)
        result = subprocess.run(["which", "create-dmg"], capture_output=True)
        if result.returncode != 0:
            print("[SKIP] create-dmg not found. Install with: brew install create-dmg")
            return True
        
        # Create DMG
        main_app = os.path.join("dist", "SMWC Downloader.app")
        dmg_name = get_zip_name().replace(".zip", "_macOS.dmg")
        dmg_path = os.path.join("release", dmg_name)
        
        # Create temporary directory for DMG contents
        dmg_temp = "dmg_temp"
        safe_remove_tree(dmg_temp)
        os.makedirs(dmg_temp)
        
        # Copy main app to temp directory
        shutil.copytree(main_app, os.path.join(dmg_temp, "SMWC Downloader.app"))
        
        # Create DMG
        subprocess.run([
            "create-dmg",
            "--volname", f"SMWCentral Downloader {get_version()}",
            "--window-size", "600", "400",
            "--icon-size", "100",
            "--app-drop-link", "400", "200",
            dmg_path,
            dmg_temp
        ], capture_output=True)
        
        # Clean up temp directory
        safe_remove_tree(dmg_temp)
        
        if os.path.exists(dmg_path):
            dmg_size = os.path.getsize(dmg_path) / (1024*1024)
            print(f"[OK] DMG installer created: {os.path.basename(dmg_path)} ({dmg_size:.1f}MB)")
        
        return True
        
    except Exception as e:
        print(f"[SKIP] DMG creation failed: {e}")
        return True  # Not critical

def main():
    """Main macOS build process"""
    print(f"🍎 SMWCentral Downloader {get_version()} - macOS Build System")
    print("=" * 60)
    
    # Step 1: Build applications
    if not build_macos_executables():
        print("[ERROR] Build failed!")
        return False
    
    # Step 2: Create release package
    if not create_macos_release_package():
        print("[ERROR] Release packaging failed!")
        return False
    
    # Step 3: Create DMG (optional)
    create_dmg_installer()
    
    # Step 4: Success summary
    print("\n🎉 macOS Build Complete!")
    print("=" * 60)
    print(f"📁 Release directory: {os.path.abspath('release')}")
    print("\n📦 macOS Release Packages:")
    
    release_files = [f for f in os.listdir("release") if f.endswith((".zip", ".dmg"))]
    for file in release_files:
        file_path = os.path.join("release", file)
        size = os.path.getsize(file_path) / (1024*1024)
        print(f"   • {file} ({size:.1f}MB)")
    
    print("\n💡 Next Steps:")
    print("   1. Test the .app bundle on different macOS versions")
    print("   2. Upload both Windows and macOS assets to GitHub release")
    print("   3. Update release notes to mention macOS support")
    
    return True

if __name__ == "__main__":
    main()
