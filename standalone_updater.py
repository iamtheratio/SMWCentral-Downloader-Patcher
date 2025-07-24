"""
Standalone updater executable that handles file replacement
This will be compiled as a separate executable to avoid PyInstaller temp directory issues
Cross-platform support for Windows and macOS
"""
import sys
import os
import subprocess
import time
import shutil
import argparse
import platform

def kill_process_by_name(process_name):
    """Kill processes by name, cross-platform"""
    system = platform.system().lower()
    
    try:
        if system == "windows":
            subprocess.run(['taskkill', '/f', '/im', process_name], 
                          capture_output=True, check=False)
        elif system == "darwin":  # macOS
            subprocess.run(['pkill', '-f', process_name], 
                          capture_output=True, check=False)
        time.sleep(1)
    except:
        pass

def start_application(app_path):
    """Start application, cross-platform"""
    system = platform.system().lower()
    
    try:
        if system == "windows":
            subprocess.Popen([app_path], 
                            cwd=os.path.dirname(app_path),
                            creationflags=subprocess.CREATE_NEW_CONSOLE)
        elif system == "darwin":  # macOS
            if app_path.endswith('.app'):
                subprocess.Popen(['open', app_path])
            else:
                subprocess.Popen([app_path], cwd=os.path.dirname(app_path))
        time.sleep(3)
    except Exception as e:
        print(f"Warning: Could not start application: {e}")

def main():
    parser = argparse.ArgumentParser(description='Update SMWCentral Downloader')
    parser.add_argument('--current-exe', required=True, help='Path to current executable')
    parser.add_argument('--update-exe', required=True, help='Path to update executable')
    parser.add_argument('--wait-seconds', type=int, default=3, help='Seconds to wait before update')
    
    args = parser.parse_args()
    
    current_exe = args.current_exe
    update_exe = args.update_exe
    wait_seconds = args.wait_seconds
    
    print(f"SMWCentral Downloader Updater ({platform.system()})")
    print(f"Current executable: {current_exe}")
    print(f"Update executable: {update_exe}")
    print(f"Waiting {wait_seconds} seconds for main app to exit...")
    
    # Wait for main application to exit
    time.sleep(wait_seconds)
    
    # Kill any remaining processes
    app_name = os.path.basename(current_exe)
    if app_name.endswith('.app'):
        # For macOS .app bundles, kill by app name
        app_name = app_name.replace('.app', '')
    
    kill_process_by_name(app_name)
    
    # Create backup
    backup_exe = current_exe + '.backup'
    try:
        if os.path.exists(current_exe):
            if os.path.isdir(current_exe):  # macOS .app bundle
                shutil.copytree(current_exe, backup_exe)
            else:  # Windows .exe file
                shutil.copy2(current_exe, backup_exe)
            print(f"Created backup: {backup_exe}")
    except Exception as e:
        print(f"Warning: Could not create backup: {e}")
    
    # Replace executable
    try:
        if os.path.isdir(update_exe):  # macOS .app bundle
            if os.path.exists(current_exe):
                shutil.rmtree(current_exe)
            shutil.copytree(update_exe, current_exe)
        else:  # Windows .exe file
            shutil.copy2(update_exe, current_exe)
            
        print(f"Successfully updated executable")
        
        # Clean up update file
        if os.path.exists(update_exe):
            if os.path.isdir(update_exe):
                shutil.rmtree(update_exe)
            else:
                os.remove(update_exe)
            print(f"Cleaned up update file")
        
        # Start updated application
        print(f"Starting updated application...")
        start_application(current_exe)
        
        # Clean up backup after successful start
        time.sleep(3)
        if os.path.exists(backup_exe):
            if os.path.isdir(backup_exe):
                shutil.rmtree(backup_exe)
            else:
                os.remove(backup_exe)
            print(f"Cleaned up backup file")
            
        print("Update completed successfully!")
        
    except Exception as e:
        print(f"Update failed: {e}")
        
        # Restore backup if update failed
        if os.path.exists(backup_exe):
            try:
                if os.path.exists(current_exe):
                    if os.path.isdir(current_exe):
                        shutil.rmtree(current_exe)
                    else:
                        os.remove(current_exe)
                
                if os.path.isdir(backup_exe):
                    shutil.copytree(backup_exe, current_exe)
                else:
                    shutil.copy2(backup_exe, current_exe)
                    
                print(f"Restored backup")
                
                # Start original application
                start_application(current_exe)
                
                # Clean up backup
                if os.path.isdir(backup_exe):
                    shutil.rmtree(backup_exe)
                else:
                    os.remove(backup_exe)
                    
            except Exception as restore_error:
                print(f"Could not restore backup: {restore_error}")
        
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
