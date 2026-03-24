#!/usr/bin/env python3
"""
SMWCentral Downloader - Linux Build System
Creates both tar.gz archives and AppImage packages for Linux.
Version is automatically pulled from main.py

This script builds two distribution formats:
1. tar.gz - Traditional archive with install.sh for system integration
2. AppImage - Portable single-file executable requiring no installation
"""

import os
import shutil
import subprocess
import tarfile
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

def build_linux_executables():
    """Build Linux executables using PyInstaller"""
    print("🔨 Building SMWCentral Downloader for Linux...")
    
    # Generate version.txt with current version
    print("📝 Generating version.txt...")
    generate_version_txt()
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    safe_remove_tree("dist")
    safe_remove_tree("build")
    
    # Create Linux-specific spec for main downloader
    print("📦 Creating main application spec...")
    main_spec_content = """# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('ui', 'ui')],
    hiddenimports=['tkinter.filedialog', 'tkinter.messagebox', 'platform_utils', 
                   'difficulty_migration', 'difficulty_lookup_manager', 
                   'PIL._tkinter_finder', 'PIL.Image', 'PIL.ImageTk'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='smwc-downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    with open("SMWC Downloader Linux.spec", "w") as f:
        f.write(main_spec_content)
    
    # Build main application
    print("📦 Building main application...")
    result = subprocess.run([
        "python3", "-m", "PyInstaller",
        "--clean",
        "SMWC Downloader Linux.spec",
    ])
    
    if result.returncode != 0:
        print(f"[ERROR] Main app build failed (exit code {result.returncode})")
        return False
    
    # Create Linux-specific spec for updater
    print("🔄 Creating updater spec...")
    updater_spec_content = """# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['standalone_updater.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/icon.ico', 'assets'), ('assets/icons', 'assets/icons')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='smwc-updater',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    with open("SMWC Updater Linux.spec", "w") as f:
        f.write(updater_spec_content)
    
    # Build updater
    print("🔄 Building updater...")
    result = subprocess.run([
        "python3", "-m", "PyInstaller",
        "--clean",
        "SMWC Updater Linux.spec",
    ])
    
    if result.returncode != 0:
        print(f"[ERROR] Updater build failed (exit code {result.returncode})")
        return False
    
    # Verify executables exist
    main_exe = os.path.join("dist", "smwc-downloader")
    updater_exe = os.path.join("dist", "smwc-updater")
    
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

def create_tarball_package():
    """Create traditional tar.gz package with install.sh"""
    print("📦 Creating tar.gz package...")
    
    version = get_version()
    archive_name = f"SMWC-Downloader-{version}-Linux-x64.tar.gz"
    
    # Create package directory structure
    package_dir = "package_tar"
    safe_remove_tree(package_dir)
    os.makedirs(package_dir)
    os.makedirs(os.path.join(package_dir, "updater"))
    os.makedirs(os.path.join(package_dir, "usr", "share", "applications"))
    
    # Create icon directories
    icon_sizes = [16, 32, 48, 64, 128, 256, 512]
    for size in icon_sizes:
        os.makedirs(os.path.join(package_dir, "usr", "share", "icons", "hicolor", 
                                 f"{size}x{size}", "apps"))
    
    # Copy executables
    shutil.copy2("dist/smwc-downloader", package_dir)
    shutil.copy2("dist/smwc-updater", os.path.join(package_dir, "updater"))
    
    # Make executables executable
    os.chmod(os.path.join(package_dir, "smwc-downloader"), 0o755)
    os.chmod(os.path.join(package_dir, "updater", "smwc-updater"), 0o755)
    
    # Copy configuration template
    shutil.copy2("config.template.json", os.path.join(package_dir, "config.json"))
    shutil.copy2("README.md", package_dir)
    
    # Copy desktop file
    shutil.copy2("assets/smwc-downloader.desktop", 
                os.path.join(package_dir, "usr", "share", "applications"))
    
    # Copy PNG icons to proper Linux icon directories
    for size in icon_sizes:
        icon_src = f"assets/icons/smwc-downloader-{size}x{size}.png"
        icon_dst = os.path.join(package_dir, "usr", "share", "icons", "hicolor",
                               f"{size}x{size}", "apps", "smwc-downloader.png")
        if os.path.exists(icon_src):
            shutil.copy2(icon_src, icon_dst)
    
    # Create installation script
    install_script = """#!/bin/bash
# SMWC Downloader Linux Installation Script

echo "Installing SMWC Downloader..."

# Copy executable to user's local bin directory
mkdir -p ~/.local/bin
cp smwc-downloader ~/.local/bin/
chmod +x ~/.local/bin/smwc-downloader

# Copy updater
mkdir -p ~/.local/bin/updater
cp updater/smwc-updater ~/.local/bin/updater/
chmod +x ~/.local/bin/updater/smwc-updater

# Install desktop integration files
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons/hicolor/{16x16,32x32,48x48,64x64,128x128,256x256,512x512}/apps

# Copy desktop file
cp usr/share/applications/smwc-downloader.desktop ~/.local/share/applications/

# Copy icons
cp usr/share/icons/hicolor/16x16/apps/smwc-downloader.png ~/.local/share/icons/hicolor/16x16/apps/
cp usr/share/icons/hicolor/32x32/apps/smwc-downloader.png ~/.local/share/icons/hicolor/32x32/apps/
cp usr/share/icons/hicolor/48x48/apps/smwc-downloader.png ~/.local/share/icons/hicolor/48x48/apps/
cp usr/share/icons/hicolor/64x64/apps/smwc-downloader.png ~/.local/share/icons/hicolor/64x64/apps/
cp usr/share/icons/hicolor/128x128/apps/smwc-downloader.png ~/.local/share/icons/hicolor/128x128/apps/
cp usr/share/icons/hicolor/256x256/apps/smwc-downloader.png ~/.local/share/icons/hicolor/256x256/apps/
cp usr/share/icons/hicolor/512x512/apps/smwc-downloader.png ~/.local/share/icons/hicolor/512x512/apps/

# Update desktop database and icon cache
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database ~/.local/share/applications
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache ~/.local/share/icons/hicolor
fi

echo "✅ Installation complete!"
echo "You can now run 'smwc-downloader' from the terminal or find it in your applications menu."
echo "Make sure ~/.local/bin is in your PATH to run from terminal."
"""
    
    install_script_path = os.path.join(package_dir, "install.sh")
    with open(install_script_path, "w") as f:
        f.write(install_script)
    os.chmod(install_script_path, 0o755)
    
    # Create the archive
    release_dir = "release"
    os.makedirs(release_dir, exist_ok=True)
    archive_path = os.path.join(release_dir, archive_name)
    
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(package_dir, arcname=".")
    
    archive_size = os.path.getsize(archive_path) / (1024*1024)
    print(f"[OK] tar.gz package created: {archive_name} ({archive_size:.1f}MB)")
    
    return archive_path

def create_appimage():
    """Create AppImage package"""
    print("📦 Creating AppImage...")
    
    version = get_version()
    appimage_name = f"SMWC-Downloader-{version}-x86_64.AppImage"
    
    # Create AppDir structure
    appdir = "SMWC-Downloader.AppDir"
    safe_remove_tree(appdir)
    os.makedirs(appdir)
    os.makedirs(os.path.join(appdir, "usr", "bin"))
    os.makedirs(os.path.join(appdir, "usr", "bin", "updater"))
    os.makedirs(os.path.join(appdir, "usr", "share", "applications"))
    os.makedirs(os.path.join(appdir, "usr", "share", "icons", "hicolor", "256x256", "apps"))
    
    # Copy executables
    shutil.copy2("dist/smwc-downloader", os.path.join(appdir, "usr", "bin"))
    shutil.copy2("dist/smwc-updater", os.path.join(appdir, "usr", "bin", "updater"))
    
    # Make executables executable
    os.chmod(os.path.join(appdir, "usr", "bin", "smwc-downloader"), 0o755)
    os.chmod(os.path.join(appdir, "usr", "bin", "updater", "smwc-updater"), 0o755)
    
    # Copy desktop file to AppDir root and usr/share/applications
    shutil.copy2("assets/smwc-downloader.desktop", appdir)
    shutil.copy2("assets/smwc-downloader.desktop", 
                os.path.join(appdir, "usr", "share", "applications"))
    
    # Copy icon to AppDir root and proper location
    icon_256 = "assets/icons/smwc-downloader-256x256.png"
    if os.path.exists(icon_256):
        shutil.copy2(icon_256, os.path.join(appdir, "smwc-downloader.png"))
        shutil.copy2(icon_256, os.path.join(appdir, "usr", "share", "icons", "hicolor", 
                                           "256x256", "apps", "smwc-downloader.png"))
    
    # Create AppRun launcher script
    apprun_content = """#!/bin/bash
# AppRun launcher for SMWC Downloader

HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"

# Set up data directory in user's home
export APPIMAGE_DATA_DIR="$HOME/.smwc-downloader"
mkdir -p "$APPIMAGE_DATA_DIR"

# Launch the application
exec "${HERE}/usr/bin/smwc-downloader" "$@"
"""
    
    apprun_path = os.path.join(appdir, "AppRun")
    with open(apprun_path, "w") as f:
        f.write(apprun_content)
    os.chmod(apprun_path, 0o755)
    
    # Try to download appimagetool if not present
    appimagetool = "appimagetool-x86_64.AppImage"
    if not os.path.exists(appimagetool):
        print("📥 Downloading appimagetool...")
        try:
            import urllib.request
            url = "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
            urllib.request.urlretrieve(url, appimagetool)
            os.chmod(appimagetool, 0o755)
            print("[OK] appimagetool downloaded")
        except Exception as e:
            print(f"[ERROR] Could not download appimagetool: {e}")
            print("Please install appimagetool manually or run on a system with it installed")
            return None
    
    # Create AppImage
    release_dir = "release"
    os.makedirs(release_dir, exist_ok=True)
    appimage_path = os.path.join(release_dir, appimage_name)
    
    # Remove old AppImage if it exists
    if os.path.exists(appimage_path):
        os.remove(appimage_path)
    
    # Set ARCH environment variable for appimagetool
    env = os.environ.copy()
    env['ARCH'] = 'x86_64'
    
    print("🔨 Building AppImage with appimagetool...")
    
    # Try running appimagetool directly first
    result = subprocess.run([
        f"./{appimagetool}",
        appdir,
        appimage_path
    ], env=env, capture_output=True, text=True)
    
    # If it failed due to FUSE not being available, extract and run
    if result.returncode != 0 and ("libfuse" in result.stderr or "FUSE" in result.stderr):
        print("⚠️  FUSE not available, extracting appimagetool...")
        
        # Extract appimagetool
        extract_result = subprocess.run([
            f"./{appimagetool}",
            "--appimage-extract"
        ], capture_output=True, text=True)
        
        if extract_result.returncode != 0:
            print(f"[ERROR] Could not extract appimagetool: {extract_result.stderr}")
            return None
        
        # Run the extracted AppRun
        result = subprocess.run([
            "./squashfs-root/AppRun",
            appdir,
            appimage_path
        ], env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] AppImage creation failed (exit code {result.returncode})")
        if result.stderr:
            print(f"Error output: {result.stderr}")
        return None
    
    if not os.path.exists(appimage_path):
        print(f"[ERROR] AppImage not found: {appimage_path}")
        return None
    
    # Make AppImage executable
    os.chmod(appimage_path, 0o755)
    
    appimage_size = os.path.getsize(appimage_path) / (1024*1024)
    print(f"[OK] AppImage created: {appimage_name} ({appimage_size:.1f}MB)")
    
    return appimage_path

def main():
    """Main build process"""
    version = get_version()
    print(f"🏭 SMWCentral Downloader {version} - Linux Build System")
    print("=" * 60)
    
    # Step 1: Build executables
    if not build_linux_executables():
        print("[ERROR] Build failed!")
        return False
    
    # Step 2: Create release packages
    print("\n📦 Creating release packages...")
    
    tarball_path = create_tarball_package()
    appimage_path = create_appimage()
    
    # Step 3: Success summary
    print("\n🎉 Build Complete!")
    print("=" * 60)
    print(f"📁 Release directory: {os.path.abspath('release')}")
    print("\n📦 Release Packages:")
    
    if tarball_path and os.path.exists(tarball_path):
        size = os.path.getsize(tarball_path) / (1024*1024)
        print(f"   • {os.path.basename(tarball_path)} ({size:.1f}MB)")
    
    if appimage_path and os.path.exists(appimage_path):
        size = os.path.getsize(appimage_path) / (1024*1024)
        print(f"   • {os.path.basename(appimage_path)} ({size:.1f}MB)")
    
    if not appimage_path:
        print("\n⚠️  AppImage build skipped (appimagetool not available)")
        print("    To build AppImage, ensure appimagetool is installed")
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
