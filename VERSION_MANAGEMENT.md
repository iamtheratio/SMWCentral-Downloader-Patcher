# Centralized Version Management System

## Overview
The SMWCentral Downloader & Patcher now uses a centralized version management system. **All version information is managed from a single location** - the `VERSION` constant in `main.py`.

## Single Source of Truth
```python
# In main.py
VERSION = "v4.3"  # <-- Only place you need to update the version!
```

## How It Works

### Files Involved
- `main.py` - Contains the master `VERSION` constant
- `version_manager.py` - Central utilities for version information
- `generate_version.py` - Dynamically generates `version.txt` for Windows executables
- `update_version.py` - Simple script to update version in one command
- `build_release.py` - Updated to use centralized version system

### Automatic Version Propagation
When you change the version in `main.py`, it automatically updates:

1. **Build System** (`build_release.py`)
   - Package directory name: `SMWC_Downloader_v4.3`
   - Zip file name: `SMWC_Downloader_v4.3.zip`
   - README content in release package

2. **Windows Executable Metadata** (`version.txt`)
   - File version: `4.3.0`
   - Product version: `4.3.0`
   - Generated dynamically during build

3. **UI Components**
   - History page version display
   - Any other UI components that show version

## Usage

### Method 1: Manual Update
Edit `main.py` and change:
```python
VERSION = "v4.3"  # Change this to your new version
```

### Method 2: Using Update Script
```bash
# Update to version 4.4
python update_version.py v4.4
python update_version.py 4.4    # Both formats work
```

### Method 3: Check Current Version
```bash
python update_version.py        # Shows current version
python version_manager.py       # Shows detailed version info
```

## Building with New Version

The build process now automatically handles versioning:

```bash
python build_release.py
```

This will:
1. Generate `version.txt` with current version from `main.py`
2. Create package directory with versioned name
3. Generate README with current version
4. Create zip file with versioned name

## Version Format

The system supports these version formats:
- **Display Version**: `v4.3` (used in UI, package names)
- **Numeric Version**: `4.3` (used for calculations)
- **Extended Version**: `4.3.0` (used for Windows metadata)
- **Tuple Version**: `(4, 3, 0, 0)` (used for Windows version info)

## Migration Benefits

### Before (Manual Updates Required)
- `main.py` - VERSION constant
- `build_release.py` - Multiple hardcoded version strings
- `version.txt` - Windows version metadata
- `README.md` - Version in title and content
- Any other files with hardcoded versions

### After (Single Update Point)
- `main.py` - VERSION constant ✅ **ONLY FILE TO UPDATE**
- All other files automatically derive version from this source

## Testing

Test the version management system:

```bash
# Test version manager
python version_manager.py

# Test version.txt generation
python generate_version.py

# Test build system imports
python -c "from build_release import *; print(f'Build system version: {get_version()}')"
```

## Example Workflow

1. **Update version**: `python update_version.py v4.4`
2. **Test version**: `python version_manager.py`
3. **Build release**: `python build_release.py`

The build will automatically create `SMWC_Downloader_v4.4.zip` with all the correct version numbers throughout!

## No More Version Hell! 🎉

You'll never again have to hunt through multiple files to update version numbers. Just change it once in `main.py` and everything else is handled automatically.
