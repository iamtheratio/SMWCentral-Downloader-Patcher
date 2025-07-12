#!/usr/bin/env python3
"""
Build script for SMWCentral Downloader & Patcher v3.0
Automates the process of creating the executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"🔧 {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Building SMWCentral Downloader & Patcher v3.0")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: main.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check if PyInstaller is installed
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
        print("✅ PyInstaller is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller not found. Installing...")
        if not run_command("pip install pyinstaller", "Installing PyInstaller"):
            sys.exit(1)
    
    # Clean previous builds
    print("\n🧹 Cleaning previous builds...")
    for folder in ["build", "dist"]:
        if Path(folder).exists():
            shutil.rmtree(folder)
            print(f"  Removed {folder}/")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("⚠️  Warning: Some dependencies may not have installed correctly")
    
    # Build the executable
    if not run_command("pyinstaller SMWC_Downloader.spec", "Building executable with PyInstaller"):
        sys.exit(1)
    
    # Check if the executable was created
    exe_path = Path("dist/SMWC Downloader.exe")
    if exe_path.exists():
        file_size = exe_path.stat().st_size / (1024 * 1024)  # Size in MB
        print(f"\n🎉 Build completed successfully!")
        print(f"📁 Executable location: {exe_path.absolute()}")
        print(f"📊 File size: {file_size:.1f} MB")
        print(f"\n📋 Next steps:")
        print(f"  1. Test the executable: '{exe_path}'")
        print(f"  2. Create release package with README.md")
        print(f"  3. Upload to GitHub releases")
    else:
        print("❌ Build failed: Executable not found in dist/ folder")
        sys.exit(1)

if __name__ == "__main__":
    main()
