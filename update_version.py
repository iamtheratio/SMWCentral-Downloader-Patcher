"""
Version Update Script for SMWCentral Downloader & Patcher
This script makes it easy to update the version in one place
"""

import os
import re
from version_manager import get_version

def update_version(new_version):
    """Update the version in main.py"""
    if not new_version.startswith('v'):
        new_version = f'v{new_version}'
    
    main_py_path = 'main.py'
    
    # Read current content
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update VERSION line
    old_pattern = r'VERSION = "[^"]*"'
    new_content = re.sub(old_pattern, f'VERSION = "{new_version}"', content)
    
    # Write updated content
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated VERSION to {new_version} in {main_py_path}")
    
    # Test the update
    from importlib import reload
    import version_manager
    reload(version_manager)
    
    print(f"✅ Verified: {version_manager.get_version()}")

def show_current_version():
    """Show the current version"""
    print(f"Current version: {get_version()}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        new_ver = sys.argv[1]
        print(f"Updating version to {new_ver}...")
        update_version(new_ver)
    else:
        show_current_version()
        print("\nTo update version, run:")
        print("python update_version.py v4.4")
        print("python update_version.py 4.4")
