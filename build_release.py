#!/usr/bin/env python3
"""
Build script for creating the v4.0 release package.
Creates a clean distribution with only the essential files.
"""

import subprocess
import shutil
import os
import sys

def main():
    print("🚀 Building SMWCentral Downloader & Patcher v4.0...")
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    try:
        if os.path.exists("dist"):
            shutil.rmtree("dist", ignore_errors=True)
        if os.path.exists("build"):
            shutil.rmtree("build", ignore_errors=True)
    except Exception as e:
        print(f"⚠️ Warning during cleanup: {e}")
        # Continue anyway
    
    # Build the executable
    print("🔨 Building executable...")
    try:
        # Use the virtual environment's pyinstaller
        pyinstaller_path = ".venv/Scripts/pyinstaller.exe"
        if not os.path.exists(pyinstaller_path):
            print("❌ PyInstaller not found in virtual environment!")
            return False
        
        result = subprocess.run([pyinstaller_path, "SMWC_Downloader.spec"], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ PyInstaller failed: {result.stderr}")
            return False
        
        print("✅ Executable built successfully!")
        
    except Exception as e:
        print(f"❌ Error building executable: {e}")
        return False
    
    # Copy essential files to dist folder
    print("📄 Copying essential files...")
    try:
        # Copy config.json
        shutil.copy2("config.json", "dist/config.json")
        print("✅ Copied config.json")
        
        # Copy README.md
        shutil.copy2("README.md", "dist/README.md")
        print("✅ Copied README.md")
        
    except Exception as e:
        print(f"❌ Error copying files: {e}")
        return False
    
    # List final distribution contents
    print("\n📦 Final distribution contents:")
    dist_files = os.listdir("dist")
    for file in sorted(dist_files):
        file_path = os.path.join("dist", file)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            size_mb = size / (1024 * 1024)
            print(f"   📄 {file} ({size_mb:.1f} MB)")
        else:
            print(f"   📁 {file}/")
    
    print(f"\n🎉 v4.0 release package ready in dist/ folder!")
    print("   Ready for distribution! 🚀")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
