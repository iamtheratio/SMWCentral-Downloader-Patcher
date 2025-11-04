#!/usr/bin/env python3
"""
V1 Legacy Files Cleanup Script
Removes all V1 QUSB2SNES files that have been superseded by V2/V3 implementation

This script removes files listed in V2_CLEANUP_PLAN.md as V1 legacy files.
"""

import os
import sys
from pathlib import Path

def main():
    """Remove V1 legacy files"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    print("🧹 V1 Legacy Files Cleanup Script")
    print(f"📁 Project Root: {project_root}")
    print()
    
    # V1 legacy files to remove (from V2_CLEANUP_PLAN.md)
    legacy_files = [
        # Core V1 files already removed
        # "qusb2snes_sync.py",  # Already removed
        
        # V1 upload implementations
        "qusb2snes_upload.py",
        "qusb2snes_rom_uploader.py", 
        "simple_file_uploader.py",
        "simple_rom_uploader_working.py",
        
        # V1 test files  
        "test_simple_upload.py",
        "test_simple_rom_uploader.py",
        "test_qusb2snes_protocol.py",
        "test_qusb2snes_ui.py",
        "test_qusb2snes.py",
        "test_simple_qusb2snes.py",
        "test_upload_debug.py",
        "test_single_upload.py",
        "test_minimal_upload.py",
        
        # Connection test files (superseded by V2)
        "test_connection_lifecycle.py",
        "test_connection_patterns.py",
        
        # Sync test files (various old patterns)
        "test_sync_fixed.py",
        "test_sync_removal.py",
        "test_direct_sync.py",
        "test_clean_sync.py",
        "test_fixed_sync.py",
        
        # Other development/test files
        "check_directory_case.py",
        "test_v1_upload.py",
        "simple_directory_check.py",
        "inspect_websocket.py",
        "test_binary_protocol.py",
        "test_websocket_libraries.py",
        "test_client_state.py",
        "test_minimal_client.py",
        "test_list_sd_structure.py",
        
        # SD card verification files (now handled by V3)
        "verify_sd_card_contents.py",
        "verify_test_file.py", 
        "find_test_file.py",
        "search_uploaded_files.py",
        "check_test_file_sizes.py",
        "list_roms_contents.py",
        "list_roms_structure.py",
        "quick_sd_check.py",
    ]
    
    # Files to remove based on patterns
    pattern_files = []
    
    # Find test_* files that match patterns
    for file_path in project_root.glob("test_*.py"):
        filename = file_path.name
        if any(pattern in filename for pattern in [
            "test_robust_", "test_real_rom_", "test_case_", "test_edge_", 
            "test_existing_", "test_folder_", "test_time_", "test_theme_"
        ]):
            pattern_files.append(filename)
    
    all_files_to_remove = legacy_files + pattern_files
    
    # Track removal statistics
    removed_count = 0
    not_found_count = 0 
    failed_count = 0
    
    print("🗑️  Removing V1 legacy files:")
    print("=" * 50)
    
    for filename in sorted(all_files_to_remove):
        file_path = project_root / filename
        
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"✅ Removed: {filename}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {filename}: {e}")
                failed_count += 1
        else:
            print(f"⚠️  Not found: {filename}")
            not_found_count += 1
    
    print()
    print("📊 Cleanup Summary:")
    print(f"   ✅ Removed: {removed_count} files")
    print(f"   ⚠️  Not found: {not_found_count} files") 
    print(f"   ❌ Failed: {failed_count} files")
    print()
    
    if failed_count > 0:
        print("❌ Some files could not be removed. Check file permissions.")
        return 1
    elif removed_count > 0:
        print("🎉 V1 legacy cleanup completed successfully!")
        print()
        print("✅ Remaining V2/V3 Production Files:")
        production_files = [
            "qusb2snes_upload_v3.py",
            "qusb2snes_upload_v2_adapter.py", 
            "qusb2snes_connection.py",
            "qusb2snes_device.py",
            "qusb2snes_filesystem.py",
            "output_directory_rom_sync.py",
            "qusb2snes_ui.py"
        ]
        
        for prod_file in production_files:
            if (project_root / prod_file).exists():
                print(f"   ✅ {prod_file}")
            else:
                print(f"   ❌ MISSING: {prod_file}")
                
    else:
        print("✨ No files needed removal - already clean!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())