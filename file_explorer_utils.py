#!/usr/bin/env python3
"""
Cross-platform file explorer utilities for SMWCentral Downloader
Handles opening file managers/explorers with file selection on Windows, Mac, and Linux
"""

import os
import sys
import platform
import subprocess


def open_file_in_explorer(file_path):
    """
    Open the file manager/explorer and highlight/select the specified file

    Args:
        file_path (str): Full path to the file to highlight in the explorer

    Returns:
        bool: True if successful, False if failed
    """
    if not file_path or not os.path.exists(file_path):
        return False

    system = platform.system().lower()

    try:
        if system == "windows":
            # Windows: Use explorer.exe with /select flag to highlight the file
            # Convert forward slashes to backslashes for Windows and normalize path
            windows_path = os.path.normpath(file_path)

            # Try the standard explorer command with /select
            try:
                subprocess.run(['explorer', '/select,', windows_path], check=False, timeout=5)
                return True
            except:
                # Fallback: Just open the folder containing the file
                folder_path = os.path.dirname(windows_path)
                os.startfile(folder_path)
                return True

        elif system == "darwin":  # macOS
            # macOS: Use open command with -R flag to reveal in Finder
            try:
                result = subprocess.run(['open', '-R', file_path],
                                      check=False, timeout=10,
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return True
                else:
                    # Fallback: Just open the containing folder
                    folder_path = os.path.dirname(file_path)
                    result = subprocess.run(['open', folder_path],
                                          check=False, timeout=10)
                    return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
                # Last resort fallback for macOS
                try:
                    folder_path = os.path.dirname(file_path)
                    subprocess.run(['open', folder_path], check=False, timeout=5)
                    return True
                except:
                    return False

        else:  # Linux and other Unix-like systems
            # Try different file managers in order of preference
            file_managers = [
                ['nautilus', '--select', file_path],  # GNOME Files (Ubuntu default)
                ['dolphin', '--select', file_path],   # KDE Dolphin
                ['thunar', '--select', file_path],    # XFCE Thunar
                ['nemo', file_path],                  # Linux Mint Nemo
                ['pcmanfm', '--select', file_path],   # LXDE PCManFM
                ['caja', file_path],                  # MATE Caja
            ]

            # Try each file manager until one works
            for fm_cmd in file_managers:
                try:
                    result = subprocess.run(fm_cmd, check=False, timeout=10,
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return True
                except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                    continue

            # Fallback: Open the containing directory (without selecting the file)
            directory = os.path.dirname(file_path)
            fallback_managers = [
                ['xdg-open', directory],              # Universal Linux opener
                ['nautilus', directory],              # GNOME Files
                ['dolphin', directory],               # KDE Dolphin
                ['thunar', directory],                # XFCE Thunar
                ['nemo', directory],                  # Linux Mint Nemo
                ['pcmanfm', directory],               # LXDE PCManFM
                ['caja', directory],                  # MATE Caja
            ]

            for fm_cmd in fallback_managers:
                try:
                    result = subprocess.run(fm_cmd, check=False, timeout=10,
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return True
                except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                    continue

            return False

    except Exception as e:
        print(f"Error opening file explorer: {e}")
        return False


def open_folder_in_explorer(folder_path):
    """
    Open the file manager/explorer and show the specified folder

    Args:
        folder_path (str): Full path to the folder to open

    Returns:
        bool: True if successful, False if failed
    """
    if not folder_path or not os.path.exists(folder_path):
        return False

    system = platform.system().lower()

    try:
        if system == "windows":
            # Windows: Use os.startfile for better compatibility
            try:
                os.startfile(folder_path)
                return True
            except OSError as e:
                # Fallback to explorer command
                try:
                    subprocess.run(['explorer', folder_path], check=False, timeout=10)
                    return True
                except:
                    return False

        elif system == "darwin":  # macOS
            # macOS: Use open command to open in Finder
            try:
                result = subprocess.run(['open', folder_path], check=False, timeout=10,
                                      capture_output=True, text=True)
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                return False

        else:  # Linux and other Unix-like systems
            # Try different file managers in order of preference
            file_managers = [
                ['xdg-open', folder_path],            # Universal Linux opener
                ['nautilus', folder_path],            # GNOME Files (Ubuntu default)
                ['dolphin', folder_path],             # KDE Dolphin
                ['thunar', folder_path],              # XFCE Thunar
                ['nemo', folder_path],                # Linux Mint Nemo
                ['pcmanfm', folder_path],             # LXDE PCManFM
                ['caja', folder_path],                # MATE Caja
            ]

            for fm_cmd in file_managers:
                try:
                    result = subprocess.run(fm_cmd, check=False, timeout=10,
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return True
                except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                    continue

            return False

    except Exception as e:
        print(f"Error opening folder explorer: {e}")
        return False


def get_file_icon_unicode():
    """
    Get a cross-platform folder icon character

    Returns:
        str: Simple folder icon character that works in Tkinter GUI
    """
    # Try to use folder emoji, but fall back to ASCII if there are issues
    try:
        # Test if the emoji can be encoded/decoded properly
        folder_emoji = "📁"
        folder_emoji.encode('utf-8').decode('utf-8')
        return folder_emoji
    except (UnicodeError, UnicodeEncodeError, UnicodeDecodeError):
        # Fallback to ASCII representation for systems with encoding issues
        return "[ ]"


if __name__ == "__main__":
    # Test the utilities
    print(f"Platform: {platform.system()}")
    print(f"Folder icon: {get_file_icon_unicode()}")

    # Test with a known file/directory
    test_path = __file__  # This script file
    print(f"Testing with file: {test_path}")

    success = open_file_in_explorer(test_path)
    print(f"Open file in explorer: {'Success' if success else 'Failed'}")

    test_dir = os.path.dirname(test_path)
    print(f"Testing with directory: {test_dir}")

    # Wait a moment before testing folder open
    import time
    time.sleep(2)

    success = open_folder_in_explorer(test_dir)
    print(f"Open folder in explorer: {'Success' if success else 'Failed'}")
