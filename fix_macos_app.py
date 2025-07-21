#!/usr/bin/env python3
"""
Post-build script to fix macOS app bundle issues
- Remove quarantine attributes
- Add proper executable permissions
- Apply self-signing to avoid Gatekeeper issues
"""

import os
import subprocess
import sys

def run_command(cmd, description=""):
    """Run a shell command and handle errors"""
    try:
        print(f"🔧 {description}...")
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️ Warning: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False

def fix_macos_app():
    """Fix the macOS app bundle to prevent startup issues"""
    app_path = "dist/SMWC Downloader.app"
    
    if not os.path.exists(app_path):
        print(f"❌ App bundle not found: {app_path}")
        return False
    
    print("🍎 Fixing macOS app bundle for PyInstaller issues...")
    
    # Remove quarantine attributes (Apple app translocation)
    run_command(f'xattr -dr com.apple.quarantine "{app_path}"', 
                "Removing quarantine attributes")
    
    # Remove additional macOS metadata that can cause issues
    run_command(f'xattr -cr "{app_path}"', 
                "Clearing extended attributes")
    
    # Make executable files actually executable
    run_command(f'find "{app_path}/Contents/MacOS" -type f -exec chmod +x {{}} \\;', 
                "Setting executable permissions on all binaries")
    
    # Ensure the main executable has the correct permissions
    run_command(f'chmod 755 "{app_path}/Contents/MacOS/SMWC Downloader"', 
                "Setting main executable permissions")
    
    # Fix the Info.plist permissions
    run_command(f'chmod 644 "{app_path}/Contents/Info.plist"', 
                "Setting Info.plist permissions")
    
    # Apply deep code signing with proper flags for PyInstaller apps
    run_command(f'codesign --force --deep --sign - --options=runtime "{app_path}"', 
                "Applying ad-hoc code signature with runtime flag")
    
    # Set proper permissions on the entire bundle
    run_command(f'chmod -R 755 "{app_path}"', 
                "Setting bundle permissions")
    
    # Fix any remaining permission issues
    run_command(f'find "{app_path}" -type d -exec chmod 755 {{}} \\;', 
                "Fixing directory permissions")
    run_command(f'find "{app_path}" -type f -exec chmod 644 {{}} \\;', 
                "Fixing file permissions")
    run_command(f'chmod +x "{app_path}/Contents/MacOS/SMWC Downloader"', 
                "Ensuring main executable is executable")
    
    # Verify the signing
    if run_command(f'codesign --verify --verbose=4 "{app_path}"', 
                   "Verifying code signature"):
        print("✅ PyInstaller macOS app bundle fixed successfully")
        return True
    else:
        print("⚠️ App bundle partially fixed (signing verification failed)")
        return True  # Still usable

if __name__ == "__main__":
    if fix_macos_app():
        print("\n🎉 macOS app fix completed!")
    else:
        print("\n❌ Failed to fix macOS app")
        sys.exit(1)
