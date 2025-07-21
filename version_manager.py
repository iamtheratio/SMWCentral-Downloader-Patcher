"""
Centralized Version Management for SMWCentral Downloader & Patcher
All version information is derived from the VERSION constant in main.py
"""

import os
import sys

def get_version():
    """Get the version string from main.py"""
    # Try to import VERSION from main.py
    try:
        # Add current directory to path if not already there
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from main import VERSION
        return VERSION
    except ImportError:
        # Fallback: read VERSION directly from main.py file
        main_py_path = os.path.join(os.path.dirname(__file__), 'main.py')
        try:
            with open(main_py_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('VERSION = '):
                        # Extract version string: VERSION = "v4.3" -> v4.3
                        version = line.split('=')[1].strip().strip('"\'')
                        return version
        except FileNotFoundError:
            pass
        
        # Ultimate fallback
        return "v4.3"

def get_version_number():
    """Get just the numeric version (e.g., '4.3' from 'v4.3')"""
    version = get_version()
    return version.lstrip('v')

def get_version_tuple():
    """Get version as tuple for version.txt (e.g., (4, 3, 0, 0))"""
    version_num = get_version_number()
    parts = version_num.split('.')
    
    # Ensure we have at least 4 parts for Windows version format
    while len(parts) < 4:
        parts.append('0')
    
    return tuple(int(part) for part in parts[:4])

def get_version_string():
    """Get version as dotted string (e.g., '4.3.0')"""
    version_num = get_version_number()
    parts = version_num.split('.')
    
    # Ensure we have at least 3 parts for standard version format
    while len(parts) < 3:
        parts.append('0')
    
    return '.'.join(parts[:3])

def get_package_name():
    """Get package name with version (e.g., 'SMWC_Downloader_v4.3')"""
    return f"SMWC_Downloader_{get_version()}"

def get_zip_name():
    """Get zip filename with version (e.g., 'SMWC_Downloader_v4.3.zip')"""
    return f"{get_package_name()}.zip"

if __name__ == "__main__":
    # Test the version manager
    print(f"Version: {get_version()}")
    print(f"Version Number: {get_version_number()}")
    print(f"Version Tuple: {get_version_tuple()}")
    print(f"Version String: {get_version_string()}")
    print(f"Package Name: {get_package_name()}")
    print(f"Zip Name: {get_zip_name()}")
