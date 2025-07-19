"""
Standalone updater executable that handles file replacement
This will be compiled as a separate executable to avoid PyInstaller temp directory issues
"""
import sys
import os
import subprocess
import time
import shutil
import argparse

def main():
    parser = argparse.ArgumentParser(description='Update SMWCentral Downloader')
    parser.add_argument('--current-exe', required=True, help='Path to current executable')
    parser.add_argument('--update-exe', required=True, help='Path to update executable')
    parser.add_argument('--wait-seconds', type=int, default=3, help='Seconds to wait before update')
    
    args = parser.parse_args()
    
    current_exe = args.current_exe
    update_exe = args.update_exe
    wait_seconds = args.wait_seconds
    
    print(f"SMWCentral Downloader Updater")
    print(f"Current executable: {current_exe}")
    print(f"Update executable: {update_exe}")
    print(f"Waiting {wait_seconds} seconds for main app to exit...")
    
    # Wait for main application to exit
    time.sleep(wait_seconds)
    
    # Kill any remaining processes
    try:
        exe_name = os.path.basename(current_exe)
        subprocess.run(['taskkill', '/f', '/im', exe_name], 
                      capture_output=True, check=False)
        time.sleep(1)
    except:
        pass
    
    # Create backup
    backup_exe = current_exe + '.backup'
    try:
        if os.path.exists(current_exe):
            shutil.copy2(current_exe, backup_exe)
            print(f"Created backup: {backup_exe}")
    except Exception as e:
        print(f"Warning: Could not create backup: {e}")
    
    # Replace executable
    try:
        shutil.copy2(update_exe, current_exe)
        print(f"Successfully updated executable")
        
        # Clean up update file
        if os.path.exists(update_exe):
            os.remove(update_exe)
            print(f"Cleaned up update file")
        
        # Start updated application
        print(f"Starting updated application...")
        subprocess.Popen([current_exe], 
                        cwd=os.path.dirname(current_exe),
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        # Clean up backup after successful start
        time.sleep(3)
        if os.path.exists(backup_exe):
            os.remove(backup_exe)
            print(f"Cleaned up backup file")
            
        print("Update completed successfully!")
        
    except Exception as e:
        print(f"Update failed: {e}")
        
        # Restore backup if update failed
        if os.path.exists(backup_exe):
            try:
                shutil.copy2(backup_exe, current_exe)
                print(f"Restored backup")
                
                # Start original application
                subprocess.Popen([current_exe], 
                                cwd=os.path.dirname(current_exe),
                                creationflags=subprocess.CREATE_NEW_CONSOLE)
                
                os.remove(backup_exe)
            except Exception as restore_error:
                print(f"Could not restore backup: {restore_error}")
        
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
