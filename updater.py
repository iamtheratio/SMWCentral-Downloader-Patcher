"""
Automatic Updater for SMWCentral Downloader & Patcher
Handles checking for updates, downloading, and applying updates from GitHub releases

Copyright (c) 2025 iamtheratio
Licensed under the MIT License - see LICENSE file for details
"""

import requests
import json
import zipfile
import tarfile
import tempfile
import os
import sys
import subprocess
import shutil
import platform
import stat
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
import time
from packaging import version

try:
    from colors import get_colors
except ImportError:
    # Fallback if colors module is not available
    def get_colors():
        return {
            "bg": "#2b2b2b",
            "fg": "#ffffff",
            "cancel_bg": "#d32f2f",
            "cancel_fg": "#ffffff",
            "cancel_hover": "#b71c1c",
            "cancel_pressed": "#8b0000"
        }

try:
    from utils import resource_path
except ImportError:
    # Fallback if utils module is not available
    def resource_path(relative_path):
        return relative_path

class UpdaterError(Exception):
    """Custom exception for updater errors"""
    pass

class Updater:
    """Handles application updates from GitHub releases"""
    
    def __init__(self, current_version, repo_owner="iamtheratio", repo_name="SMWCentral-Downloader---Patcher", parent=None):
        self.current_version = current_version
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        self.check_in_progress = False
        self.update_in_progress = False
        self.parent = parent  # Store parent for logging
        
    def check_for_updates(self, silent=False):
        """
        Check for updates from GitHub releases
        
        Args:
            silent (bool): If True, don't show "no updates" message
            
        Returns:
            dict: Update information if available, None if no update
        """
        if self.check_in_progress:
            return None
            
        self.check_in_progress = True
        
        try:
            response = requests.get(self.github_api_url, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data['tag_name'].lstrip('v')  # Remove 'v' prefix if present
            
            # Compare versions
            if version.parse(latest_version) > version.parse(self.current_version):
                return {
                    'version': latest_version,
                    'release_notes': release_data.get('body', 'No release notes available.'),
                    'download_url': self._get_download_url(release_data),
                    'release_name': release_data.get('name', f'Version {latest_version}'),
                    'published_at': release_data.get('published_at', ''),
                    'release_data': release_data
                }
            else:
                if not silent:
                    messagebox.showinfo("No Updates", "You're running the latest version!")
                return None
                
        except requests.RequestException as e:
            error_msg = f"Failed to check for updates: {str(e)}"
            if not silent:
                messagebox.showerror("Update Check Failed", error_msg)
            print(f"Updater error: {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Unexpected error checking for updates: {str(e)}"
            if not silent:
                messagebox.showerror("Update Check Failed", error_msg)
            print(f"Updater error: {error_msg}")
            return None
        finally:
            self.check_in_progress = False
    
    def _get_download_url(self, release_data):
        """Extract the correct download URL from release assets based on platform"""
        import platform
        
        assets = release_data.get('assets', [])
        current_platform = platform.system().lower()
        
        # Platform-specific asset matching
        platform_patterns = {
            'darwin': ['macos', 'mac', 'darwin'],  # macOS
            'windows': ['win', 'windows'],          # Windows
            'linux': ['linux']                     # Linux
        }
        
        # Check if running from AppImage
        is_appimage = os.environ.get('APPIMAGE') is not None
        
        # Look for platform-specific assets first
        if current_platform in platform_patterns:
            patterns = platform_patterns[current_platform]
            for asset in assets:
                asset_name_lower = asset['name'].lower()
                if any(pattern in asset_name_lower for pattern in patterns):
                    if asset_name_lower.endswith(('.zip', '.dmg', '.exe', '.tar.gz', '.appimage')):
                        # On Linux, prefer AppImage if running from AppImage
                        if current_platform == 'linux' and is_appimage:
                            if asset_name_lower.endswith('.appimage'):
                                return asset['browser_download_url']
                        else:
                            return asset['browser_download_url']
        
        # Fallback: Look for .zip files first (cross-platform)
        for asset in assets:
            if asset['name'].endswith('.zip'):
                return asset['browser_download_url']
        
        # Fallback: Platform-specific executables
        if current_platform == 'darwin':
            for asset in assets:
                if asset['name'].endswith('.dmg'):
                    return asset['browser_download_url']
        elif current_platform == 'windows':
            for asset in assets:
                if asset['name'].endswith('.exe'):
                    return asset['browser_download_url']
        elif current_platform == 'linux':
            # Prefer AppImage if running from AppImage
            if is_appimage:
                for asset in assets:
                    if asset['name'].endswith('.AppImage'):
                        return asset['browser_download_url']
            # Otherwise use tar.gz
            for asset in assets:
                if asset['name'].endswith('.tar.gz'):
                    return asset['browser_download_url']
        
        # If no suitable asset found, use the zipball URL
        return release_data.get('zipball_url')
    
    def download_update(self, update_info, progress_callback=None):
        """
        Download update files
        
        Args:
            update_info (dict): Update information from check_for_updates
            progress_callback (callable): Optional callback for progress updates
            
        Returns:
            str: Path to downloaded file
        """
        if self.update_in_progress:
            raise UpdaterError("Update already in progress")
        
        self.update_in_progress = True
        
        try:
            download_url = update_info['download_url']
            
            # Create temporary directory for download
            temp_dir = tempfile.mkdtemp(prefix="smwc_update_")
            
            # Determine file extension
            if download_url.endswith('.zip'):
                file_ext = '.zip'
            elif download_url.endswith('.exe'):
                file_ext = '.exe'
            elif download_url.endswith('.dmg'):
                file_ext = '.dmg'
            elif download_url.endswith('.tar.gz'):
                file_ext = '.tar.gz'
            elif download_url.endswith('.AppImage'):
                file_ext = '.AppImage'
            else:
                file_ext = '.zip'  # Default assumption
            
            file_path = os.path.join(temp_dir, f"update{file_ext}")
            
            # Download with progress
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            return file_path
            
        except Exception as e:
            self.update_in_progress = False
            raise UpdaterError(f"Failed to download update: {str(e)}")
    
    def apply_update(self, downloaded_file_path, update_info):
        """
        Apply the downloaded update
        
        Args:
            downloaded_file_path (str): Path to downloaded update file
            update_info (dict): Update information
        """
        try:
            current_exe = None
            
            # Check if running from PyInstaller bundle
            if getattr(sys, 'frozen', False):
                # Running from PyInstaller bundle - sys.executable is the actual exe
                current_exe = sys.executable
            else:
                # Running from Python - try to find the exe
                current_exe = sys.executable
                if not current_exe.endswith('.exe'):
                    # If running from Python, try to find the exe in the same directory
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    exe_candidates = [
                        os.path.join(script_dir, "SMWC Downloader.exe"),
                        os.path.join(script_dir, "SMWC_Downloader.exe"),
                        os.path.join(script_dir, "SMWCentral Downloader.exe")
                    ]
                    for candidate in exe_candidates:
                        if os.path.exists(candidate):
                            current_exe = candidate
                            break
                    else:
                        raise UpdaterError("Could not locate application executable for update")
            
            # Extract update based on file type
            if downloaded_file_path.endswith('.zip'):
                extract_dir = tempfile.mkdtemp(prefix="smwc_extract_")
                
                with zipfile.ZipFile(downloaded_file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Find the new executable in the extracted files
                new_exe = None
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        if file.endswith('.exe') and 'SMWC' in file:
                            new_exe = os.path.join(root, file)
                            break
                    if new_exe:
                        break
                
                if not new_exe:
                    raise UpdaterError("Could not find executable in update package")
                
                update_exe = new_exe
                
            elif downloaded_file_path.endswith('.tar.gz'):
                import tarfile
                extract_dir = tempfile.mkdtemp(prefix="smwc_extract_")
                
                with tarfile.open(downloaded_file_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_dir)
                
                # Find the new executable in the extracted files
                new_exe = None
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        # Linux executables typically don't have .exe extension
                        if ('SMWC' in file or 'smwc' in file) and not file.endswith(('.txt', '.md', '.json', '.spec')):
                            # Check if file is executable
                            file_path = os.path.join(root, file)
                            if os.access(file_path, os.X_OK):
                                new_exe = file_path
                                break
                    if new_exe:
                        break
                
                if not new_exe:
                    raise UpdaterError("Could not find executable in update package")
                
                update_exe = new_exe
                
            elif downloaded_file_path.endswith('.AppImage'):
                # AppImage is a single-file executable, just use it directly
                # Make it executable
                os.chmod(downloaded_file_path, 0o755)
                update_exe = downloaded_file_path
                
            elif downloaded_file_path.endswith('.dmg'):
                # For macOS DMG files, we need to mount and copy the app
                import platform
                if platform.system().lower() != 'darwin':
                    raise UpdaterError("DMG files can only be installed on macOS")
                
                try:
                    # Mount the DMG
                    mount_result = subprocess.run(['hdiutil', 'attach', downloaded_file_path, '-nobrowse', '-quiet'], 
                                                capture_output=True, text=True)
                    if mount_result.returncode != 0:
                        raise UpdaterError(f"Failed to mount DMG: {mount_result.stderr}")
                    
                    # Parse mount output to find volume path
                    mount_point = None
                    for line in mount_result.stdout.split('\n'):
                        if '/Volumes/' in line:
                            mount_point = line.split('\t')[-1].strip()
                            break
                    
                    if not mount_point:
                        raise UpdaterError("Could not find mount point for DMG")
                    
                    # Find the .app bundle
                    app_bundle = None
                    for item in os.listdir(mount_point):
                        if item.endswith('.app') and 'SMWC' in item:
                            app_bundle = os.path.join(mount_point, item)
                            break
                    
                    if not app_bundle:
                        subprocess.run(['hdiutil', 'detach', mount_point, '-quiet'])
                        raise UpdaterError("Could not find application bundle in DMG")
                    
                    # Copy to Applications folder
                    applications_dir = "/Applications"
                    app_name = os.path.basename(app_bundle)
                    target_path = os.path.join(applications_dir, app_name)
                    
                    # Remove existing installation if present
                    if os.path.exists(target_path):
                        subprocess.run(['rm', '-rf', target_path])
                    
                    # Copy new version
                    subprocess.run(['cp', '-R', app_bundle, applications_dir])
                    
                    # Unmount DMG
                    subprocess.run(['hdiutil', 'detach', mount_point, '-quiet'])
                    
                    # DMG installation complete - no need for further processing
                    self.update_in_progress = False
                    return
                    
                except Exception as e:
                    # Try to unmount if something went wrong
                    try:
                        if 'mount_point' in locals():
                            subprocess.run(['hdiutil', 'detach', mount_point, '-quiet'])
                    except:
                        pass
                    raise UpdaterError(f"Failed to install DMG: {str(e)}")
                
            else:
                # Direct executable download
                update_exe = downloaded_file_path
            
            # Create update script
            update_script = self._create_update_script(current_exe, update_exe)
            
            # Execute update script and close application
            # Note: Release notes are now shown on the main thread before this method
            subprocess.Popen([update_script], creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Close the application
            os._exit(0)
            
        except Exception as e:
            self.update_in_progress = False
            raise UpdaterError(f"Failed to apply update: {str(e)}")
    
    def apply_update_silent(self, downloaded_file_path, update_info):
        """
        Apply the downloaded update silently without showing release notes
        
        Args:
            downloaded_file_path (str): Path to downloaded update file
            update_info (dict): Update information
        """
        try:
            current_exe = None
            
            # Check if running from PyInstaller bundle
            if getattr(sys, 'frozen', False):
                # Running from PyInstaller bundle - sys.executable is the actual exe
                current_exe = sys.executable
            else:
                # Running from Python - try to find the exe
                current_exe = sys.executable
                if not current_exe.endswith('.exe'):
                    # If running from Python, try to find the exe in the same directory
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    exe_candidates = [
                        os.path.join(script_dir, "SMWC Downloader.exe"),
                        os.path.join(script_dir, "SMWC_Downloader.exe"),
                        os.path.join(script_dir, "SMWCentral Downloader.exe")
                    ]
                    for candidate in exe_candidates:
                        if os.path.exists(candidate):
                            current_exe = candidate
                            break
                    else:
                        raise UpdaterError("Could not locate application executable for update")
            
            # Extract update based on file type
            if downloaded_file_path.endswith('.zip'):
                extract_dir = tempfile.mkdtemp(prefix="smwc_extract_")
                
                with zipfile.ZipFile(downloaded_file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Find the new executable in the extracted files
                new_exe = None
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        if file.endswith('.exe') and 'SMWC' in file:
                            new_exe = os.path.join(root, file)
                            break
                    if new_exe:
                        break
                
                if not new_exe:
                    raise UpdaterError("Could not find executable in update package")
                
                update_exe = new_exe
                
            elif downloaded_file_path.endswith('.tar.gz'):
                import tarfile
                extract_dir = tempfile.mkdtemp(prefix="smwc_extract_")
                
                with tarfile.open(downloaded_file_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_dir)
                
                # Find the new executable in the extracted files
                new_exe = None
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        # Linux executables typically don't have .exe extension
                        if ('SMWC' in file or 'smwc' in file) and not file.endswith(('.txt', '.md', '.json', '.spec')):
                            # Check if file is executable
                            file_path = os.path.join(root, file)
                            if os.access(file_path, os.X_OK):
                                new_exe = file_path
                                break
                    if new_exe:
                        break
                
                if not new_exe:
                    raise UpdaterError("Could not find executable in update package")
                
                update_exe = new_exe
                
            elif downloaded_file_path.endswith('.AppImage'):
                # AppImage is a single-file executable, just use it directly
                # Make it executable
                os.chmod(downloaded_file_path, 0o755)
                update_exe = downloaded_file_path
                
            elif downloaded_file_path.endswith('.dmg'):
                # For macOS DMG files, we need to mount and copy the app
                import platform
                if platform.system().lower() != 'darwin':
                    raise UpdaterError("DMG files can only be installed on macOS")
                
                try:
                    # Mount the DMG
                    mount_result = subprocess.run(['hdiutil', 'attach', downloaded_file_path, '-nobrowse', '-quiet'], 
                                                capture_output=True, text=True)
                    if mount_result.returncode != 0:
                        raise UpdaterError(f"Failed to mount DMG: {mount_result.stderr}")
                    
                    # Parse mount output to find volume path
                    mount_point = None
                    for line in mount_result.stdout.split('\n'):
                        if '/Volumes/' in line:
                            mount_point = line.split('\t')[-1].strip()
                            break
                    
                    if not mount_point:
                        raise UpdaterError("Could not find mount point for DMG")
                    
                    # Find the .app bundle
                    app_bundle = None
                    for item in os.listdir(mount_point):
                        if item.endswith('.app') and 'SMWC' in item:
                            app_bundle = os.path.join(mount_point, item)
                            break
                    
                    if not app_bundle:
                        subprocess.run(['hdiutil', 'detach', mount_point, '-quiet'])
                        raise UpdaterError("Could not find application bundle in DMG")
                    
                    # Copy to Applications folder
                    applications_dir = "/Applications"
                    app_name = os.path.basename(app_bundle)
                    target_path = os.path.join(applications_dir, app_name)
                    
                    # Remove existing installation if present
                    if os.path.exists(target_path):
                        subprocess.run(['rm', '-rf', target_path])
                    
                    # Copy new version
                    subprocess.run(['cp', '-R', app_bundle, applications_dir])
                    
                    # Unmount DMG
                    subprocess.run(['hdiutil', 'detach', mount_point, '-quiet'])
                    
                    # DMG installation complete
                    self.update_in_progress = False
                    return
                    
                except Exception as e:
                    # Try to unmount if something went wrong
                    try:
                        if 'mount_point' in locals():
                            subprocess.run(['hdiutil', 'detach', mount_point, '-quiet'])
                    except:
                        pass
                    raise UpdaterError(f"Failed to install DMG: {str(e)}")
                
            else:
                # Direct executable download
                update_exe = downloaded_file_path
            
            # Copy update executable to a permanent location to avoid temp directory cleanup
            script_dir = os.path.dirname(current_exe)
            
            # Determine appropriate filename based on platform and file type
            import platform
            current_platform = platform.system().lower()
            
            if update_exe.endswith('.exe') or current_platform == 'windows':
                permanent_update_exe = os.path.join(script_dir, "update_new.exe")
            else:
                # Linux or other platform
                permanent_update_exe = os.path.join(script_dir, "update_new")
            
            # Copy the update executable to permanent location
            import shutil
            shutil.copy2(update_exe, permanent_update_exe)
            
            # Ensure executable permissions on Linux/macOS
            if current_platform in ['linux', 'darwin']:
                import stat
                os.chmod(permanent_update_exe, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            
            # Create update script with permanent path
            update_script = self._create_update_script(current_exe, permanent_update_exe)
            
            # Prepare for update - don't exit yet, let dialog handle it
            self.update_script_path = update_script
            
        except Exception as e:
            self.update_in_progress = False
            raise UpdaterError(f"Failed to prepare update: {str(e)}")
    
    def _create_update_script(self, current_exe, update_exe):
        """Create a standalone updater process to handle the update"""
        script_dir = os.path.dirname(current_exe)
        
        # First, check if we have the standalone updater in the hidden directory (industry standard)
        hidden_updater = os.path.join(script_dir, "updater", "SMWC Updater.exe")
        standalone_updater = os.path.join(script_dir, "SMWC Updater.exe")
        
        if os.path.exists(hidden_updater):
            # Use the hidden updater executable (industry standard approach)
            
            # Store the updater command for later execution
            self.updater_command = [
                hidden_updater,
                '--current-exe', current_exe,
                '--update-exe', update_exe,
                '--wait-seconds', '3'
            ]
            
            return "standalone_updater"
        elif os.path.exists(standalone_updater):
            # Use the standalone updater executable (fallback for old distribution)
            
            # Store the updater command for later execution
            self.updater_command = [
                standalone_updater,
                '--current-exe', current_exe,
                '--update-exe', update_exe,
                '--wait-seconds', '3'
            ]
            
            return "standalone_updater"
        else:
            # Fallback to batch script method
            
            script_path = os.path.join(script_dir, "update.bat")
            backup_exe = current_exe + ".backup"
            
            # Get the absolute path to ensure proper execution
            current_exe_abs = os.path.abspath(current_exe)
            update_exe_abs = os.path.abspath(update_exe)
            backup_exe_abs = os.path.abspath(backup_exe)
            
            # Create a robust update script following the proper workflow
            script_content = f'''@echo off
setlocal EnableDelayedExpansion
echo Starting SMWCentral Downloader update process...

REM Wait for the main application to fully exit
echo Waiting for application to exit...
timeout /t 2 /nobreak >nul

REM Kill any remaining processes (silent)
taskkill /f /im "{os.path.basename(current_exe_abs)}" >nul 2>&1

REM Additional short wait to ensure clean shutdown
timeout /t 1 /nobreak >nul

REM Step 1: Backup current executable
echo Step 1: Creating backup of current application...
if exist "{current_exe_abs}" (
    copy "{current_exe_abs}" "{backup_exe_abs}" >nul 2>&1
    if exist "{backup_exe_abs}" (
        echo Backup created successfully
    ) else (
        echo ERROR: Failed to create backup
        echo Update aborted for safety
        if exist "{update_exe_abs}" del "{update_exe_abs}" >nul 2>&1
        pause
        exit /b 1
    )
) else (
    echo ERROR: Current executable not found at "{current_exe_abs}"
    echo Update aborted
    if exist "{update_exe_abs}" del "{update_exe_abs}" >nul 2>&1
    pause
    exit /b 1
)

REM Step 2: Replace with new version (rename update_new.exe to SMWC Downloader.exe)
echo Step 2: Installing new version...
if exist "{update_exe_abs}" (
    copy "{update_exe_abs}" "{current_exe_abs}" >nul 2>&1
    if exist "{current_exe_abs}" (
        echo New version installed successfully
    ) else (
        echo ERROR: Failed to install new version
        goto :restore_backup
    )
) else (
    echo ERROR: Update file not found at "{update_exe_abs}"
    goto :restore_backup
)

REM Step 3: Verify the update was successful
echo Step 3: Verifying update...
if exist "{current_exe_abs}" (
    echo Update verification successful
    
    REM Step 4: Start the new application
    echo Step 4: Starting updated application...
    cd /d "{script_dir}"
    start "" "{current_exe_abs}"
    
    REM Short wait for application to start before cleanup
    timeout /t 2 /nobreak >nul
    
    REM Step 5: Clean up backup and temporary files
    echo Step 5: Cleaning up temporary files...
    if exist "{backup_exe_abs}" del "{backup_exe_abs}" >nul 2>&1
    if exist "{update_exe_abs}" del "{update_exe_abs}" >nul 2>&1
    
    echo Update completed successfully!
    goto :cleanup
) else (
    echo ERROR: Update verification failed
    goto :restore_backup
)

:restore_backup
echo ERROR: Update failed - restoring backup...
if exist "{backup_exe_abs}" (
    REM Delete failed update attempt
    if exist "{current_exe_abs}" del "{current_exe_abs}" >nul 2>&1
    
    REM Restore backup
    copy "{backup_exe_abs}" "{current_exe_abs}" >nul 2>&1
    if exist "{current_exe_abs}" (
        echo Backup restored successfully
        REM Clean up backup file
        del "{backup_exe_abs}" >nul 2>&1
        
        REM Start the restored application
        cd /d "{script_dir}"
        start "" "{current_exe_abs}"
        echo Original application restored and restarted
    ) else (
        echo CRITICAL ERROR: Failed to restore backup
        echo Please manually rename "{backup_exe_abs}" to "{current_exe_abs}"
        pause
    )
) else (
    echo CRITICAL ERROR: Backup not found
    echo Update process corrupted
    pause
)

REM Clean up temporary update file
if exist "{update_exe_abs}" del "{update_exe_abs}" >nul 2>&1

:cleanup
REM Clean up script itself
del "{script_path}" >nul 2>&1
'''
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            return script_path
    
    def _show_release_notes(self, update_info):
        """Show release notes dialog"""
        dialog = UpdateReleaseNotesDialog(update_info)
        dialog.show()

class UpdateDialog:
    """Enhanced dialog for update checking and confirmation"""
    
    def __init__(self, parent, update_info):
        self.parent = parent
        self.update_info = update_info
        self.result = None
        self.progress_var = None
        self.mode = "update_available"  # "update_available" or "updating"
        
        # UI elements that will be modified during update
        self.header_frame = None
        self.notes_frame = None
        self.button_frame = None
        self.update_button = None
        self.later_button = None
        self.progress_frame = None
        self.progress_bar = None
        self.progress_label = None
        self.log_text = None
        self.log_frame = None
        
    def show(self):
        """Show the update dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Update Available")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Set application icon
        try:
            icon_path = resource_path("assets/icon.ico")
            self.dialog.iconbitmap(icon_path)
        except:
            try:
                # Fallback: try to get icon from parent window
                if hasattr(self.parent, 'iconbitmap'):
                    parent_icon = self.parent.tk.call('wm', 'iconbitmap', self.parent._w)
                    if parent_icon:
                        self.dialog.iconbitmap(parent_icon)
            except:
                pass
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        # Apply theme colors
        colors = get_colors()
        self.dialog.configure(bg=colors.get("bg", "#2b2b2b"))
        
        # Create content
        self._create_content()
        
        # Wait for user response
        self.dialog.wait_window()
        return self.result
    
    def _create_content(self):
        """Create enhanced dialog content with markdown formatting"""
        colors = get_colors()
        
        # Main frame with padding
        main_frame = ttk.Frame(self.dialog, padding=25)
        main_frame.pack(fill="both", expand=True)
        
        # Header section with icon and title
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Update icon/emoji
        icon_label = ttk.Label(
            header_frame, 
            text="🚀", 
            font=("Segoe UI", 24)
        )
        icon_label.pack(side="left", padx=(0, 15))
        
        # Title and version info
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side="left", fill="x", expand=True)
        
        title_label = ttk.Label(
            title_frame, 
            text="Update Available!", 
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(anchor="w")
        
        # Version comparison
        version_text = f"Version {self.update_info.get('current_version', 'Unknown')} → {self.update_info['version']}"
        version_label = ttk.Label(
            title_frame, 
            text=version_text, 
            font=("Segoe UI", 12),
            foreground="#2196F3"  # Blue color for version
        )
        version_label.pack(anchor="w", pady=(2, 0))
        
        # Release name if available
        if self.update_info.get('release_name') and self.update_info['release_name'] != f"Version {self.update_info['version']}":
            release_name_label = ttk.Label(
                title_frame,
                text=self.update_info['release_name'],
                font=("Segoe UI", 10, "italic")
            )
            release_name_label.pack(anchor="w", pady=(2, 0))
        
        # Separator
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill="x", pady=(0, 20))
        
        # Release notes section
        notes_frame = ttk.Frame(main_frame)
        notes_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        notes_header = ttk.Label(
            notes_frame, 
            text="📝 What's New:", 
            font=("Segoe UI", 14, "bold")
        )
        notes_header.pack(anchor="w", pady=(0, 10))
        
        # Create custom text widget for formatted release notes
        text_container = ttk.Frame(notes_frame)
        text_container.pack(fill="both", expand=True)
        
        # Text widget with scrollbar
        text_widget = tk.Text(
            text_container,
            wrap="word",
            font=("Segoe UI", 10),
            height=12,
            padx=15,
            pady=10,
            state="disabled",
            cursor="arrow"
        )
        
        scrollbar = ttk.Scrollbar(text_container, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configure text widget colors based on theme
        if colors.get("bg") == "#2b2b2b":  # Dark theme
            text_widget.configure(
                bg="#363636",
                fg="#ffffff",
                insertbackground="#ffffff",
                selectbackground="#2196F3",
                selectforeground="#ffffff"
            )
            # Configure scrollbar for dark theme with better visibility
            style = ttk.Style()
            style.configure("UpdateDialog.Vertical.TScrollbar", 
                           background="#5a5a5a",
                           troughcolor="#2b2b2b",
                           borderwidth=1,
                           arrowcolor="#ffffff",
                           darkcolor="#5a5a5a",
                           lightcolor="#7a7a7a",
                           width=16)
            scrollbar.configure(style="UpdateDialog.Vertical.TScrollbar")
        else:  # Light theme
            text_widget.configure(
                bg="#ffffff",
                fg="#000000",
                insertbackground="#000000",
                selectbackground="#2196F3",
                selectforeground="#ffffff"
            )
            # Configure scrollbar for light theme with better visibility
            style = ttk.Style()
            style.configure("UpdateDialog.Vertical.TScrollbar", 
                           background="#c0c0c0",
                           troughcolor="#f0f0f0",
                           borderwidth=1,
                           arrowcolor="#000000",
                           darkcolor="#c0c0c0",
                           lightcolor="#e0e0e0",
                           width=16)
            scrollbar.configure(style="UpdateDialog.Vertical.TScrollbar")
        
        # Format and insert release notes
        self._format_release_notes(text_widget)
        
        # Progress section (initially hidden)
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=500,
            style="TProgressbar"
        )
        self.progress_label = ttk.Label(
            self.progress_frame,
            text="",
            font=("Segoe UI", 10)
        )
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Update info on left
        info_frame = ttk.Frame(button_frame)
        info_frame.pack(side="left")
        
        # File size info if available
        if self.update_info.get('release_data', {}).get('assets'):
            assets = self.update_info['release_data']['assets']
            if assets:
                size_bytes = assets[0].get('size', 0)
                if size_bytes > 0:
                    size_mb = size_bytes / (1024 * 1024)
                    size_label = ttk.Label(
                        info_frame,
                        text=f"Download size: {size_mb:.1f} MB",
                        font=("Segoe UI", 9),
                        foreground="#666666"
                    )
                    size_label.pack(anchor="w")
        
        # Published date
        if self.update_info.get('published_at'):
            try:
                from datetime import datetime
                date_str = self.update_info['published_at']
                # Parse GitHub date format
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime("%B %d, %Y")
                date_label = ttk.Label(
                    info_frame,
                    text=f"Released: {formatted_date}",
                    font=("Segoe UI", 9),
                    foreground="#666666"
                )
                date_label.pack(anchor="w")
            except:
                pass
        
        # Action buttons on right
        action_frame = ttk.Frame(button_frame)
        action_frame.pack(side="right")
        
        # Later button
        later_button = ttk.Button(
            action_frame,
            text="Later",
            command=self._cancel,
            style="TButton"
        )
        later_button.pack(side="left", padx=(0, 10))
        
        # Update button (styled as accent)
        update_button = ttk.Button(
            action_frame,
            text="Update Now",
            command=self._start_update,
            style="Accent.TButton"
        )
        update_button.pack(side="left")
        
        # Store references to key UI elements
        self.header_frame = header_frame
        self.notes_frame = notes_frame
        self.button_frame = button_frame
        self.update_button = update_button
        self.later_button = later_button
        self.text_widget = text_widget
        self.main_frame = main_frame
    
    def _switch_to_update_mode(self):
        """Switch the dialog from 'Update Available' to 'Updating' mode"""
        self.mode = "updating"
        
        # Update dialog title
        self.dialog.title("Updating...")
        
        # Update header
        for widget in self.header_frame.winfo_children():
            widget.destroy()
        
        # Update icon/emoji
        icon_label = ttk.Label(
            self.header_frame, 
            text="🔄", 
            font=("Segoe UI", 24)
        )
        icon_label.pack(side="left", padx=(0, 15))
        
        # Title and version info
        title_frame = ttk.Frame(self.header_frame)
        title_frame.pack(side="left", fill="x", expand=True)
        
        title_label = ttk.Label(
            title_frame, 
            text="Updating Now!", 
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(anchor="w")
        
        # Version comparison
        version_text = f"Updating to version {self.update_info['version']}..."
        version_label = ttk.Label(
            title_frame, 
            text=version_text, 
            font=("Segoe UI", 12),
            foreground="#2196F3"
        )
        version_label.pack(anchor="w", pady=(2, 0))
        
        # Replace release notes with log window
        for widget in self.notes_frame.winfo_children():
            widget.destroy()
        
        log_header = ttk.Label(
            self.notes_frame, 
            text="Update Progress:", 
            font=("Segoe UI", 14, "bold")
        )
        log_header.pack(anchor="w", pady=(0, 10))
        
        # Create log text widget
        log_container = ttk.Frame(self.notes_frame)
        log_container.pack(fill="both", expand=True)
        
        self.log_text = tk.Text(
            log_container,
            wrap="word",
            font=("Consolas", 9),
            height=12,
            padx=15,
            pady=10,
            state="disabled",
            cursor="arrow"
        )
        
        log_scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
        # Configure log text colors based on theme
        colors = get_colors()
        if colors.get("bg") == "#2b2b2b":  # Dark theme
            self.log_text.configure(
                bg="#363636",
                fg="#ffffff",
                insertbackground="#ffffff",
                selectbackground="#2196F3",
                selectforeground="#ffffff"
            )
            # Configure scrollbar for dark theme
            style = ttk.Style()
            style.configure("UpdateLog.Vertical.TScrollbar", 
                           background="#5a5a5a",
                           troughcolor="#2b2b2b",
                           borderwidth=1,
                           arrowcolor="#ffffff",
                           darkcolor="#5a5a5a",
                           lightcolor="#7a7a7a",
                           width=16)
            log_scrollbar.configure(style="UpdateLog.Vertical.TScrollbar")
        else:  # Light theme
            self.log_text.configure(
                bg="#ffffff",
                fg="#000000",
                insertbackground="#000000",
                selectbackground="#2196F3",
                selectforeground="#ffffff"
            )
            # Configure scrollbar for light theme
            style = ttk.Style()
            style.configure("UpdateLog.Vertical.TScrollbar", 
                           background="#c0c0c0",
                           troughcolor="#f0f0f0",
                           borderwidth=1,
                           arrowcolor="#000000",
                           darkcolor="#c0c0c0",
                           lightcolor="#e0e0e0",
                           width=16)
            log_scrollbar.configure(style="UpdateLog.Vertical.TScrollbar")
        
        # Add progress bar
        self.progress_frame = ttk.Frame(self.notes_frame)
        self.progress_frame.pack(fill="x", pady=(10, 0))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate"
        )
        self.progress_bar.pack(fill="x", pady=(0, 5))
        
        self.progress_label = ttk.Label(
            self.progress_frame,
            text="Preparing to download...",
            font=("Segoe UI", 9)
        )
        self.progress_label.pack()
        
        # Disable buttons
        self.update_button.config(state="disabled")
        self.later_button.config(state="disabled")
        
        # Add initial log message
        self._add_log_message("🚀 Starting update process...")
        
        self.dialog.update()
    
    def _switch_to_restart_mode(self):
        """Switch the dialog to show 'Restart App' button after update completes"""
        # Update header
        for widget in self.header_frame.winfo_children():
            widget.destroy()
        
        # Success icon
        icon_label = ttk.Label(
            self.header_frame, 
            text="✅", 
            font=("Segoe UI", 24)
        )
        icon_label.pack(side="left", padx=(0, 15))
        
        # Title and version info
        title_frame = ttk.Frame(self.header_frame)
        title_frame.pack(side="left", fill="x", expand=True)
        
        title_label = ttk.Label(
            title_frame, 
            text="Update Complete!", 
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(anchor="w")
        
        # Version text
        version_text = f"Successfully updated to version {self.update_info['version']}"
        version_label = ttk.Label(
            title_frame, 
            text=version_text, 
            font=("Segoe UI", 12),
            foreground="#2196F3"
        )
        version_label.pack(anchor="w", pady=(2, 0))
        
        # Replace buttons with restart button
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # Restart button
        restart_button = ttk.Button(
            self.button_frame,
            text="Restart App",
            command=self._restart_app,
            style="Accent.TButton"
        )
        restart_button.pack(side="right")
        
        # Add completion message to log
        self._add_log_message("✅ Update completed successfully!")
        self._add_log_message("💡 Click 'Restart App' to start using the new version.")
        
        self.dialog.update()
    
    def _add_log_message(self, message):
        """Add a message to the log text widget"""
        if not self.log_text or not self.dialog:
            return

        def append_to_widget():
            try:
                self.log_text.config(state="normal")
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.config(state="disabled")
                self.log_text.see(tk.END)
            except tk.TclError:
                pass

        try:
            self.dialog.after(0, append_to_widget)
        except tk.TclError:
            pass
    
    def _restart_app(self):
        """Restart the application with the update - optimized for fast exit"""
        # Store parent reference for logging to main app
        main_app_root = getattr(self, 'parent', None)
        
        # Quick logging to main app BEFORE starting restart process
        if main_app_root and hasattr(main_app_root, 'log_text'):
            try:
                main_log = main_app_root.log_text
                main_log.config(state="normal")
                main_log.insert(tk.END, "🔄 UPDATE: Starting application restart...\n")
                main_log.config(state="disabled")
                main_log.see(tk.END)
            except:
                pass
        
        # Quick dialog update and immediate close
        self._add_log_message("🔄 Restarting with update...")
        self.result = "restart"
        
        # Get the restart mechanism ready
        restart_command = None
        restart_cwd = None
        
        # Check if we have an update script (for file replacement)
        if hasattr(self, 'update_script_path') and self.update_script_path:
            # For PyInstaller executables, we need to handle this differently
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
                current_dir = os.path.dirname(current_exe)
                
                # Check if using standalone updater
                if hasattr(self, 'updater_command'):
                    # Verify updater exists
                    updater_exe = self.updater_command[0]
                    if os.path.exists(updater_exe):
                        restart_command = self.updater_command
                        restart_cwd = current_dir
                        if main_app_root and hasattr(main_app_root, 'log_text'):
                            try:
                                main_log = main_app_root.log_text
                                main_log.config(state="normal")
                                main_log.insert(tk.END, f"🔧 UPDATE: Using standalone updater\n")
                                main_log.config(state="disabled")
                            except:
                                pass
                elif self.update_script_path != "standalone_updater":
                    # Use batch script
                    if os.path.exists(self.update_script_path):
                        restart_command = [self.update_script_path]
                        restart_cwd = current_dir
                        if main_app_root and hasattr(main_app_root, 'log_text'):
                            try:
                                main_log = main_app_root.log_text
                                main_log.config(state="normal")
                                main_log.insert(tk.END, f"🔧 UPDATE: Using batch script\n")
                                main_log.config(state="disabled")
                            except:
                                pass
            else:
                # Development mode
                if os.path.exists(self.update_script_path):
                    restart_command = [self.update_script_path]
                    restart_cwd = os.path.dirname(self.update_script_path)
        else:
            # No update script - direct restart
            if getattr(sys, 'frozen', False):
                # PyInstaller executable
                current_exe = sys.executable
                current_dir = os.path.dirname(current_exe)
                
                if os.path.exists(current_exe):
                    # Create minimal restart launcher
                    launcher_script = os.path.join(current_dir, "restart_launcher.bat")
                    launcher_content = f'''@echo off
cd /d "{current_dir}"
timeout /t 1 /nobreak >nul
start "" "{current_exe}"
del "%~f0"
'''
                    try:
                        with open(launcher_script, 'w') as f:
                            f.write(launcher_content)
                        restart_command = [launcher_script]
                        restart_cwd = current_dir
                    except:
                        pass
            else:
                # Python development mode
                main_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
                if os.path.exists(main_script):
                    restart_command = [sys.executable, main_script]
                    restart_cwd = os.path.dirname(main_script)
        
        # Log final message to main app
        if main_app_root and hasattr(main_app_root, 'log_text'):
            try:
                main_log = main_app_root.log_text
                main_log.config(state="normal")
                main_log.insert(tk.END, "🔄 UPDATE: Exiting for restart...\n")
                main_log.config(state="disabled")
                main_log.see(tk.END)
                main_app_root.update_idletasks()
            except:
                pass
        
        # Close dialog immediately
        self.dialog.destroy()
        
        # Start the restart process
        if restart_command:
            try:
                subprocess.Popen(restart_command, 
                               creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
                               cwd=restart_cwd)
            except Exception as e:
                # If restart fails, try to log to main app if still alive
                if main_app_root and hasattr(main_app_root, 'log_text'):
                    try:
                        main_log = main_app_root.log_text
                        main_log.config(state="normal")
                        main_log.insert(tk.END, f"❌ UPDATE ERROR: Restart failed: {str(e)}\n")
                        main_log.config(state="disabled")
                    except:
                        pass
                return
        
        # Exit immediately - no delays
        os._exit(0)
    
    def _format_release_notes(self, text_widget):
        """Format GitHub markdown release notes for better display"""
        text_widget.config(state="normal")
        text_widget.delete("1.0", tk.END)
        
        # Configure text tags for formatting
        text_widget.tag_configure("header1", font=("Segoe UI", 16, "bold"), spacing1=10, spacing3=5)
        text_widget.tag_configure("header2", font=("Segoe UI", 14, "bold"), spacing1=8, spacing3=4)
        text_widget.tag_configure("header3", font=("Segoe UI", 12, "bold"), spacing1=6, spacing3=3)
        text_widget.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        text_widget.tag_configure("italic", font=("Segoe UI", 10, "italic"))
        text_widget.tag_configure("code", font=("Consolas", 9), background="#f5f5f5")
        text_widget.tag_configure("bullet", lmargin1=20, lmargin2=30)
        text_widget.tag_configure("emoji", font=("Segoe UI", 12))
        
        # Get release notes
        notes = self.update_info.get('release_notes', 'No release notes available.')
        
        # Split into lines for processing
        lines = notes.split('\n')
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            if not line:
                text_widget.insert(tk.END, "\n")
                continue
            
            # Headers
            if line.startswith('### '):
                text_widget.insert(tk.END, line[4:] + "\n", "header3")
            elif line.startswith('## '):
                text_widget.insert(tk.END, line[3:] + "\n", "header2")
            elif line.startswith('# '):
                text_widget.insert(tk.END, line[2:] + "\n", "header1")
            
            # Bullet points
            elif line.startswith('- ') or line.startswith('* '):
                # Handle emoji bullets
                bullet_text = line[2:]
                if bullet_text.startswith(('🚀', '✨', '🐛', '🔧', '📝', '💫', '🎯', '⚡', '🎨', '🔥', '💡', '🛠️')):
                    text_widget.insert(tk.END, f"  {bullet_text}\n", "bullet emoji")
                else:
                    text_widget.insert(tk.END, f"  • {bullet_text}\n", "bullet")
            
            # Code blocks (simple detection)
            elif line.startswith('```'):
                text_widget.insert(tk.END, line + "\n", "code")
            
            # Regular text with inline formatting
            else:
                self._insert_formatted_text(text_widget, line + "\n")
        
        text_widget.config(state="disabled")
    
    def _insert_formatted_text(self, text_widget, text):
        """Insert text with inline markdown formatting"""
        import re
        
        # Find and format bold text (**text**)
        bold_pattern = r'\*\*(.*?)\*\*'
        italic_pattern = r'\*(.*?)\*'
        code_pattern = r'`(.*?)`'
        
        last_end = 0
        
        # Process all formatting
        for match in re.finditer(f'({bold_pattern}|{italic_pattern}|{code_pattern})', text):
            # Insert text before match
            if match.start() > last_end:
                text_widget.insert(tk.END, text[last_end:match.start()])
            
            # Insert formatted text
            matched_text = match.group(1)
            if match.group(0).startswith('**'):
                # Bold text
                text_widget.insert(tk.END, matched_text, "bold")
            elif match.group(0).startswith('*'):
                # Italic text
                text_widget.insert(tk.END, matched_text, "italic")
            elif match.group(0).startswith('`'):
                # Code text
                text_widget.insert(tk.END, matched_text, "code")
            
            last_end = match.end()
        
        # Insert remaining text
        if last_end < len(text):
            text_widget.insert(tk.END, text[last_end:])
    
    def _start_update(self):
        """Start the update process"""
        # Switch to update mode
        self._switch_to_update_mode()
        
        # Start download in thread
        def download_and_apply():
            try:
                updater = Updater(self.update_info.get('current_version', '4.0'), parent=self.parent)
                
                # Download with progress callback
                def progress_callback(progress):
                    # Schedule UI update on main thread
                    def update_progress():
                        self.progress_var.set(progress)
                        self.progress_label.config(text=f"Downloading update... {progress:.1f}%")
                    
                    self.dialog.after(0, update_progress)
                
                # Update log safely
                def update_download_log():
                    self._add_log_message("⬇️ Downloading update files...")
                
                self.dialog.after(0, update_download_log)
                
                downloaded_file = updater.download_update(self.update_info, progress_callback)
                
                # Apply update
                def update_install_log():
                    self.progress_var.set(100)
                    self.progress_label.config(text="Installing update...")
                    self._add_log_message("📦 Extracting update files...")
                    self._add_log_message("🔧 Installing update...")
                
                self.dialog.after(0, update_install_log)
                
                # Apply update without showing release notes (we'll handle restart differently)
                def complete_update():
                    try:
                        # Apply the update
                        updater.apply_update_silent(downloaded_file, self.update_info)
                        
                        # Store the update script path for later use
                        self.update_script_path = getattr(updater, 'update_script_path', None)
                        
                        # Also store the updater command if it exists
                        if hasattr(updater, 'updater_command'):
                            self.updater_command = updater.updater_command
                        
                        # Switch to restart mode
                        self._switch_to_restart_mode()
                        
                    except Exception as e:
                        self._add_log_message(f"❌ Update failed: {str(e)}")
                        # Re-enable buttons on error
                        self.update_button.config(state="normal")
                        self.later_button.config(state="normal")
                        self.progress_frame.pack_forget()
                
                self.dialog.after(0, complete_update)
                
            except Exception as e:
                # Schedule error handling on main thread
                def handle_error():
                    self._add_log_message(f"❌ Update failed: {str(e)}")
                    self.update_button.config(state="normal")
                    self.later_button.config(state="normal")
                    self.progress_frame.pack_forget()
                
                self.dialog.after(0, handle_error)
        
        thread = Thread(target=download_and_apply, daemon=True)
        thread.start()
    
    def _cancel(self):
        """Cancel the update"""
        self.result = False
        self.dialog.destroy()

class UpdateReleaseNotesDialog:
    """Enhanced dialog to show release notes after update"""
    
    def __init__(self, update_info):
        self.update_info = update_info
        
    def show(self):
        """Show enhanced release notes dialog"""
        root = tk.Tk()
        root.title(f"Updated to {self.update_info['version']}")
        root.geometry("700x600")
        root.resizable(True, True)
        
        # Set application icon
        try:
            icon_path = resource_path("assets/icon.ico")
            root.iconbitmap(icon_path)
        except:
            pass
        
        # Apply theme colors
        colors = get_colors()
        root.configure(bg=colors.get("bg", "#2b2b2b"))
        
        # Main frame with padding
        main_frame = ttk.Frame(root, padding=30)
        main_frame.pack(fill="both", expand=True)
        
        # Header with celebration
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 25))
        
        # Celebration icon
        celebration_label = ttk.Label(
            header_frame,
            text="🎉",
            font=("Segoe UI", 32)
        )
        celebration_label.pack(side="left", padx=(0, 20))
        
        # Success message
        success_frame = ttk.Frame(header_frame)
        success_frame.pack(side="left", fill="x", expand=True)
        
        success_label = ttk.Label(
            success_frame,
            text="Update Successful!",
            font=("Segoe UI", 20, "bold")
        )
        success_label.pack(anchor="w")
        
        version_label = ttk.Label(
            success_frame,
            text=f"SMWCentral Downloader & Patcher is now version {self.update_info['version']}",
            font=("Segoe UI", 12),
            foreground="#2196F3"
        )
        version_label.pack(anchor="w", pady=(3, 0))
        
        # Separator
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill="x", pady=(0, 25))
        
        # Release notes section
        notes_header = ttk.Label(
            main_frame,
            text="🚀 What's New in This Version:",
            font=("Segoe UI", 16, "bold")
        )
        notes_header.pack(anchor="w", pady=(0, 15))
        
        # Scrollable text area
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill="both", expand=True, pady=(0, 25))
        
        text_widget = tk.Text(
            text_frame,
            wrap="word",
            font=("Segoe UI", 11),
            padx=20,
            pady=15,
            state="disabled",
            cursor="arrow"
        )
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configure text widget colors
        if colors.get("bg") == "#2b2b2b":  # Dark theme
            text_widget.configure(
                bg="#363636",
                fg="#ffffff",
                insertbackground="#ffffff"
            )
            # Configure scrollbar for dark theme with better visibility
            style = ttk.Style()
            style.configure("ReleaseNotes.Vertical.TScrollbar", 
                           background="#5a5a5a",
                           troughcolor="#2b2b2b",
                           borderwidth=1,
                           arrowcolor="#ffffff",
                           darkcolor="#5a5a5a",
                           lightcolor="#7a7a7a",
                           width=16)
            scrollbar.configure(style="ReleaseNotes.Vertical.TScrollbar")
        else:  # Light theme
            text_widget.configure(
                bg="#ffffff",
                fg="#000000",
                insertbackground="#000000"
            )
            # Configure scrollbar for light theme with better visibility
            style = ttk.Style()
            style.configure("ReleaseNotes.Vertical.TScrollbar", 
                           background="#c0c0c0",
                           troughcolor="#f0f0f0",
                           borderwidth=1,
                           arrowcolor="#000000",
                           darkcolor="#c0c0c0",
                           lightcolor="#e0e0e0",
                           width=16)
            scrollbar.configure(style="ReleaseNotes.Vertical.TScrollbar")
        
        # Format and insert release notes
        self._format_release_notes(text_widget)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        # Thank you message
        thank_you_label = ttk.Label(
            button_frame,
            text="Thank you for using SMWCentral Downloader & Patcher!",
            font=("Segoe UI", 10, "italic")
        )
        thank_you_label.pack(side="left")
        
        # Close button
        close_button = ttk.Button(
            button_frame,
            text="Continue",
            command=root.destroy,
            style="Accent.TButton"
        )
        close_button.pack(side="right", padx=(10, 0))
        
        # Center the window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (700 // 2)
        y = (root.winfo_screenheight() // 2) - (600 // 2)
        root.geometry(f"700x600+{x}+{y}")
        
        root.mainloop()
    
    def _format_release_notes(self, text_widget):
        """Format release notes with enhanced styling"""
        text_widget.config(state="normal")
        text_widget.delete("1.0", tk.END)
        
        # Configure enhanced text tags
        text_widget.tag_configure("header1", font=("Segoe UI", 18, "bold"), spacing1=15, spacing3=8)
        text_widget.tag_configure("header2", font=("Segoe UI", 16, "bold"), spacing1=12, spacing3=6)
        text_widget.tag_configure("header3", font=("Segoe UI", 14, "bold"), spacing1=10, spacing3=5)
        text_widget.tag_configure("bold", font=("Segoe UI", 11, "bold"))
        text_widget.tag_configure("italic", font=("Segoe UI", 11, "italic"))
        text_widget.tag_configure("code", font=("Consolas", 10), background="#f5f5f5")
        text_widget.tag_configure("bullet", lmargin1=25, lmargin2=35, spacing1=2)
        text_widget.tag_configure("emoji", font=("Segoe UI", 13))
        text_widget.tag_configure("highlight", background="#FFE082", foreground="#333333")
        
        # Get release notes
        notes = self.update_info.get('release_notes', 'No release notes available.')
        
        # Split into lines for processing
        lines = notes.split('\n')
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            if not line:
                text_widget.insert(tk.END, "\n")
                continue
            
            # Headers
            if line.startswith('### '):
                text_widget.insert(tk.END, line[4:] + "\n", "header3")
            elif line.startswith('## '):
                text_widget.insert(tk.END, line[3:] + "\n", "header2")
            elif line.startswith('# '):
                text_widget.insert(tk.END, line[2:] + "\n", "header1")
            
            # Bullet points with emoji handling
            elif line.startswith('- ') or line.startswith('* '):
                bullet_text = line[2:]
                if bullet_text.startswith(('🚀', '✨', '🐛', '🔧', '📝', '💫', '🎯', '⚡', '🎨', '🔥', '💡', '🛠️', '🎉', '💪', '🌟', '🚨')):
                    text_widget.insert(tk.END, f"  {bullet_text}\n", "bullet emoji")
                else:
                    text_widget.insert(tk.END, f"  • {bullet_text}\n", "bullet")
            
            # Code blocks
            elif line.startswith('```'):
                text_widget.insert(tk.END, line + "\n", "code")
            
            # Regular text with inline formatting
            else:
                self._insert_formatted_text(text_widget, line + "\n")
        
        text_widget.config(state="disabled")
    
    def _insert_formatted_text(self, text_widget, text):
        """Insert text with enhanced inline markdown formatting"""
        import re
        
        # Enhanced patterns
        bold_pattern = r'\*\*(.*?)\*\*'
        italic_pattern = r'\*(.*?)\*'
        code_pattern = r'`(.*?)`'
        
        last_end = 0
        
        # Process all formatting
        for match in re.finditer(f'({bold_pattern}|{italic_pattern}|{code_pattern})', text):
            # Insert text before match
            if match.start() > last_end:
                text_widget.insert(tk.END, text[last_end:match.start()])
            
            # Insert formatted text
            matched_text = match.group(1) if match.group(1) else match.group(2) if match.group(2) else match.group(3)
            if match.group(0).startswith('**'):
                text_widget.insert(tk.END, matched_text, "bold")
            elif match.group(0).startswith('*'):
                text_widget.insert(tk.END, matched_text, "italic")
            elif match.group(0).startswith('`'):
                text_widget.insert(tk.END, matched_text, "code")
            
            last_end = match.end()
        
        # Insert remaining text
        if last_end < len(text):
            text_widget.insert(tk.END, text[last_end:])

def check_for_updates_background(current_version, callback=None):
    """
    Check for updates in the background
    
    Args:
        current_version (str): Current application version
        callback (callable): Callback function to handle update info
    """
    def check():
        try:
            time.sleep(2)  # Wait a bit for the app to fully load
            updater = Updater(current_version)
            update_info = updater.check_for_updates(silent=True)
            
            if update_info and callback:
                # Add current version to update info
                update_info['current_version'] = current_version
                callback(update_info)
                
        except Exception as e:
            # Suppress errors during shutdown to prevent threading cleanup issues
            if not ("interpreter is shutting down" in str(e).lower() or 
                    "dummy thread" in str(e).lower() or
                    "cannot schedule new futures" in str(e).lower()):
                print(f"Background update check failed: {e}")
    
    thread = Thread(target=check, daemon=True)
    thread.start()

def show_update_dialog(parent, update_info):
    """Show update dialog"""
    dialog = UpdateDialog(parent, update_info)
    return dialog.show()
