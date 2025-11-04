#!/usr/bin/env python3
"""
Project Cleanup Script for QUSB2SNES Integration
Organizes test files and development artifacts
"""

import os
import shutil
from pathlib import Path

def organize_test_files():
    """Organize test files into appropriate directories"""
    
    base_dir = Path(__file__).parent
    
    # Create organization directories
    archive_dir = base_dir / "archive" / "qusb2snes_development"
    tests_dir = base_dir / "tests" / "qusb2snes"
    
    archive_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)
    
    print("🧹 Organizing QUSB2SNES test files...")
    
    # Production test files (keep in main tests)
    production_tests = [
        "test_v3_upload_manager.py",
        "test_v2_adapter_integration.py"
    ]
    
    # Development test files (move to archive)
    development_tests = [
        "test_two_phase_upload.py",
        "test_mkdir_delays.py", 
        "test_simplified_mkdir.py",
        "test_list_roms.py",
        "test_list_kaizo.py",
        "test_complete_working_uploader.py",
        "test_large_rom_upload.py",
        "test_connection_lifecycle.py",
        "test_connection_patterns.py",
        "test_sync_fixed.py",
        "test_sync_removal.py",
        "test_upload_debug.py",
        "test_qusb2snes_protocol.py",
        "test_qusb2snes_ui.py",
        "test_qusb2snes.py",
        "test_simple_qusb2snes.py",
        "test_single_upload.py",
        "test_minimal_upload.py",
        "test_smart_directory_mapping.py",
        "test_directory_mirroring.py",
        "test_hierarchical_directories.py"
    ]
    
    # Move production tests to tests directory
    moved_production = 0
    for test_file in production_tests:
        src = base_dir / test_file
        dst = tests_dir / test_file
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"📁 Moved to tests: {test_file}")
            moved_production += 1
    
    # Move development tests to archive
    moved_development = 0
    for test_file in development_tests:
        src = base_dir / test_file
        dst = archive_dir / test_file
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"📦 Archived: {test_file}")
            moved_development += 1
    
    print(f"\n✅ Organization complete!")
    print(f"   📁 Production tests moved: {moved_production}")
    print(f"   📦 Development tests archived: {moved_development}")
    
    # Create README for archive
    readme_content = """# QUSB2SNES Development Archive

This directory contains development and testing files from the QUSB2SNES integration project.

## Contents

### Protocol Research & Development
- Research files exploring QUSB2SNES protocol
- Connection pattern investigations  
- Upload strategy prototypes

### Test Files
- Individual component tests
- Performance benchmarks
- Edge case validations

### Development Notes
- These files were instrumental in developing the final V3 implementation
- Keep for reference and future debugging
- Not needed for production use

## Final Implementation

The production implementation consists of:
- `qusb2snes_upload_v3.py` - Core V3 implementation
- `qusb2snes_upload_v2_adapter.py` - Compatibility adapter
- Tests in `/tests/qusb2snes/` directory

## Integration Status

✅ **COMPLETE** - All research and development led to successful production integration.
"""
    
    with open(archive_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    print(f"📝 Created archive README")

if __name__ == "__main__":
    organize_test_files()