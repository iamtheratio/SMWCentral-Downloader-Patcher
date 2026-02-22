#!/usr/bin/env python3
"""
Platform-specific utilities for SMWCentral Downloader
Handles cross-platform differences in executable paths and file operations
"""

import os
import platform
import sys

def get_current_executable_path():
    """
    Get the current executable path, handling platform differences
    
    Returns:
        str: Path to current executable (Windows .exe or macOS .app bundle)
    """
    system = platform.system().lower()
    
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        if system == "darwin":  # macOS
            # For .app bundles, we want the .app directory, not the internal executable
            exe_path = sys.executable
            
            # Find the .app bundle root
            app_bundle = exe_path
            while app_bundle and not app_bundle.endswith('.app'):
                app_bundle = os.path.dirname(app_bundle)
                if app_bundle == os.path.dirname(app_bundle):  # Reached root
                    break
            
            return app_bundle if app_bundle.endswith('.app') else exe_path
        else:  # Windows
            return sys.executable
    else:
        # Running as script
        return os.path.abspath(sys.argv[0])

def get_application_directory():
    """
    Get the directory containing the application
    
    Returns:
        str: Directory path containing the main application
    """
    exe_path = get_current_executable_path()
    return os.path.dirname(exe_path)

def get_updater_executable_path(app_directory):
    """
    Get the path to the updater executable
    
    Args:
        app_directory (str): Directory containing the main application
        
    Returns:
        str: Path to updater executable, or None if not found
    """
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        # Check for hidden updater first
        hidden_updater = os.path.join(app_directory, "updater", "SMWC Updater.app")
        if os.path.exists(hidden_updater):
            return hidden_updater
            
        # Check for standalone updater
        standalone_updater = os.path.join(app_directory, "SMWC Updater.app")
        if os.path.exists(standalone_updater):
            return standalone_updater
            
    else:  # Windows
        # Check for hidden updater first
        hidden_updater = os.path.join(app_directory, "updater", "SMWC Updater.exe")
        if os.path.exists(hidden_updater):
            return hidden_updater
            
        # Check for standalone updater
        standalone_updater = os.path.join(app_directory, "SMWC Updater.exe")
        if os.path.exists(standalone_updater):
            return standalone_updater
    
    return None

def get_updater_command(app_directory, current_exe, update_exe):
    """
    Get the command to run the updater
    
    Args:
        app_directory (str): Directory containing the main application
        current_exe (str): Path to current executable
        update_exe (str): Path to update executable
        
    Returns:
        list: Command list to execute updater, or None if not available
    """
    system = platform.system().lower()
    updater_path = get_updater_executable_path(app_directory)
    
    if not updater_path:
        return None
    
    if system == "darwin":  # macOS
        # For .app bundles, we need to find the actual binary inside
        updater_binary = os.path.join(updater_path, "Contents", "MacOS", "SMWC Updater")
        if not os.path.exists(updater_binary):
            return None
    else:  # Windows
        updater_binary = updater_path
    
    return [
        updater_binary,
        '--current-exe', current_exe,
        '--update-exe', update_exe,
        '--wait-seconds', '3'
    ]

def pick_file(title="Select File", filetypes=None, initial_dir=None):
    """
    Show a native file-picker dialog, with a graceful fallback chain.

    On Linux the built-in tkinter file browser is the ugly Tk widget.
    We prefer native portals:

      1. zenity  -- ships with GNOME/GTK; works on X11 and Wayland via XDG portal.
      2. kdialog -- ships with KDE Plasma; works on X11 and Wayland via XDG portal.
      3. tkinter -- silent fallback so any other desktop still works.

    On Windows and macOS the tkinter dialog is already native-quality.

    Args:
        title (str):       Dialog window title.
        filetypes (list):  List of (description, pattern) tuples, e.g.
                           [("ROM files", "*.smc *.sfc"), ("All files", "*.*")]
                           Same format as tkinter's filedialog filetypes.
        initial_dir (str): Directory to open initially (optional).

    Returns:
        str: Absolute path chosen by the user, or "" if cancelled.
    """
    import subprocess
    from tkinter import filedialog

    if filetypes is None:
        filetypes = [("All files", "*.*")]

    system = platform.system()

    if system == "Linux":
        # --- Attempt 1: zenity (GNOME / GTK / XDG portal) ---
        try:
            cmd = ["zenity", "--file-selection", f"--title={title}"]
            if initial_dir:
                cmd.append(f"--filename={initial_dir}/")
            for desc, pattern in filetypes:
                # zenity filter format: "Description | *.ext1 *.ext2"
                cmd.append(f"--file-filter={desc} | {pattern}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                path = result.stdout.strip()
                return path if path else ""
            elif result.returncode == 1:
                # User explicitly cancelled — stop here.
                return ""
            # Any other non-zero code: zenity had an error; fall through to kdialog.
        except (OSError, subprocess.SubprocessError):
            pass  # zenity not usable; try next option

        # --- Attempt 2: kdialog (KDE Plasma / XDG portal) ---
        try:
            start = initial_dir if initial_dir else os.path.expanduser("~")
            # kdialog filter format: "*.smc *.sfc|ROM files\n*.*|All files"
            filter_str = "\n".join(f"{pattern}|{desc}" for desc, pattern in filetypes)
            result = subprocess.run(
                ["kdialog", "--getopenfilename", start, filter_str, "--title", title],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                path = result.stdout.strip()
                return path if path else ""
            elif result.returncode == 1:
                # User explicitly cancelled — stop here.
                return ""
            # Any other non-zero code: kdialog had an error; fall through to tkinter.
        except (OSError, subprocess.SubprocessError):
            pass  # kdialog not usable; fall back to tkinter

    # --- Fallback / non-Linux: tkinter built-in dialog ---
    kwargs = {"title": title, "filetypes": filetypes}
    if initial_dir:
        kwargs["initialdir"] = initial_dir
    path = filedialog.askopenfilename(**kwargs)
    return path if path else ""


def pick_directory(title="Select Folder", initial_dir=None):
    """
    Show a native folder-picker dialog, with a graceful fallback chain.

    On Linux the built-in tkinter directory browser renders Tk's own widget
    (horizontal-scroll only, not user friendly).  We prefer native portals:

      1. zenity  -- ships with GNOME/GTK; works on X11 and Wayland via XDG portal.
      2. kdialog -- ships with KDE Plasma; works on X11 and Wayland via XDG portal.
      3. tkinter -- silent fallback so any other desktop still works.

    On Windows and macOS the tkinter dialog is already native-quality, so we
    call it directly without the subprocess overhead.

    Args:
        title (str):       Dialog window title.
        initial_dir (str): Directory to open initially (optional).

    Returns:
        str: Absolute path chosen by the user, or "" if cancelled.
    """
    import subprocess
    from tkinter import filedialog

    system = platform.system()

    if system == "Linux":
        # --- Attempt 1: zenity (GNOME / GTK / XDG portal) ---
        try:
            cmd = ["zenity", "--file-selection", "--directory", f"--title={title}"]
            if initial_dir:
                cmd.append(f"--filename={initial_dir}/")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5-minute safety timeout
            )
            if result.returncode == 0:
                path = result.stdout.strip()
                return path if path else ""
            elif result.returncode == 1:
                # returncode 1 means the user explicitly cancelled — stop here.
                return ""
            # Any other non-zero code means zenity encountered an error
            # (e.g. no display available); fall through to kdialog.
        except (OSError, subprocess.SubprocessError):
            # OSError covers FileNotFoundError (not installed) and PermissionError.
            # SubprocessError covers TimeoutExpired and other subprocess failures.
            pass  # zenity not usable; try next option

        # --- Attempt 2: kdialog (KDE Plasma / XDG portal) ---
        try:
            start = initial_dir if initial_dir else os.path.expanduser("~")
            result = subprocess.run(
                ["kdialog", "--getexistingdirectory", start, "--title", title],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                path = result.stdout.strip()
                return path if path else ""
            elif result.returncode == 1:
                # returncode 1 means the user explicitly cancelled — stop here.
                return ""
            # Any other non-zero code: kdialog had an error; fall through to tkinter.
        except (OSError, subprocess.SubprocessError):
            pass  # kdialog not usable; fall back to tkinter

    # --- Fallback / non-Linux: tkinter built-in dialog ---
    kwargs = {"title": title}
    if initial_dir:
        kwargs["initialdir"] = initial_dir
    path = filedialog.askdirectory(**kwargs)
    return path if path else ""


def make_executable(file_path):
    """
    Make a file executable (mainly for shell scripts on macOS/Linux)
    
    Args:
        file_path (str): Path to file to make executable
    """
    system = platform.system().lower()
    
    if system != "windows":
        try:
            os.chmod(file_path, 0o755)
        except:
            pass  # Ignore errors

if __name__ == "__main__":
    # Test the utilities
    print(f"Platform: {platform.system()}")
    print(f"Current executable: {get_current_executable_path()}")
    print(f"Application directory: {get_application_directory()}")
    
    app_dir = get_application_directory()
    updater_path = get_updater_executable_path(app_dir)
    print(f"Updater path: {updater_path}")
    
    if updater_path:
        cmd = get_updater_command(app_dir, "current.exe", "update.exe")
        print(f"Updater command: {cmd}")
