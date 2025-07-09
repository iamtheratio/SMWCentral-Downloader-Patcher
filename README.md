# SMWC Downloader & Patcher v2.4

**SMWCentral Downloader & Patcher** is a Python GUI tool built to automate downloading, patching, and organizing Super Mario World ROM hacks from [SMWCentral.net](https://www.smwcentral.net/). It uses the official SMWC API to fetch hack information and features a unified patch handler supporting both IPS and BPS formats.

## 📚 Table of Contents

- [👤 Users: Quick Start](#-users-quick-start)
- [✨ New Features](#-new-features)
- [✅ Core Features](#-core-features)
- [🗂️ Folder Structure](#-folder-structure)
- [🔧 Configuration](#-configuration)
- [🔄 Update Detection](#-update-detection)
- [📝 Log Levels](#-log-levels)
- [👨‍💻 Project Architecture](#-project-architecture)
- [📸 Screenshots](#-screenshots)
- [📦 Requirements](#-requirements)
- [🖥️ Usage](#-usage)
- [🧪 Building Executable](#-building-executable)
- [🎨 UI Features](#-ui-features)
- [📄 Release Notes](#release-notes)
  - [v2.4.0](#v240)
  - [v2.3.0](#v230)
  - [v2.2.0](#v220)
  - [v2.1.0](#v210)
  - [v2.0.0](#v200)

### 📸 Screenshots
![SMWC Downloader Interface](/images/screenshot_app_v2.2.png)

## 👤 Users: Quick Start

1. **Download the Latest Release**
   - Get the latest `.zip` or installer from the [Releases](https://github.com/iamtheratio/SMWCentral-Downloader-Patcher/releases/download/v2.4.0/SMWC.Downloader.V2.4.zip) page.

2. **Extract the Files**
   - Unzip to a folder of your choice.

3. **First Launch Setup**
   - Double-click `SMWC Downloader.exe` to start.
   - On first launch, set:
     - Clean SMW ROM path (headerless .smc file recommended)
     - Output directory
   - **Note:** Flips is no longer required - the app now has built-in patching!

4. **Download & Patch ROM Hacks**
   - Select hack type and filters.
   - Click **Download & Patch**.
   - Patched ROMs will appear in your output folder.

### ✨ New Features
- **Built-in Patch Handler**: No more external Flips dependency - unified IPS/BPS patching system
- **Intelligent Header Detection**: Automatically detects and handles SMC/SFC ROM headers
- **Enhanced Logging**: Italic styling for patch application messages with detailed progress
- **Improved Error Handling**: Better error messages and debugging information
- **Streamlined Setup**: Removed Flips dependency - only ROM and output paths needed
- **Automatic Checksum Handling**: Proper SNES ROM checksum calculation for IPS patches
- **Modular Architecture**: Clean separation of patching logic for better maintainability

### ✅ Core Features
- Choose Hack type:
  - Standard
  - Kaizo
  - Puzzle
  - Tool-Assisted
  - Pit
- Optional Hack difficulty:
  - Newcomer
  - Casual
  - Skilled
  - Advanced
  - Expert
  - Master
  - Grandmaster
- Filter options:
  - Hall of Fame
  - SA-1
  - Collab
  - Demo
- Automated workflow:
  - Downloads from SMWC API
  - Unzips downloaded files
  - **Built-in patching** with unified IPS/BPS handler
  - Supports both .bps and .ips patch formats
  - Supports both .smc and .sfc ROM formats
  - Automatic header detection and handling
  - Renames and organizes files
  - Updates existing hacks
- Visual feedback:
  - Progress logging with italic patch application messages
  - Special indicators for updated ROMs
  - Colored log levels
  - Detailed patching progress
- Smart file management:
  - Keeps track of processed hacks
  - Detects and handles hack updates
  - Organizes by type and difficulty

### 🗂️ Folder Structure
Patched hacks are saved based on their type > difficulty attributes:
```
/Output Folder
  /Kaizo
    /01 - Newcomer
      Hack Name.smc
    /02 - Casual
      Hack Name.smc
  /Standard
    /01 - Newcomer
      Hack Name.smc
    /02 - Casual
      Hack Name.smc
```

### 🔧 Configuration
- `config.json`: Essential paths (**Base ROM and Output Directory required**)
  ```json
  {
    "base_rom_path": "path/to/clean.smc",
    "output_dir": "path/to/output"
  }
  ```
- **Note:** You must set both Base ROM and Output Directory paths before you can download and patch ROMs. Flips is no longer required.
- `processed.json`: Tracks downloaded hacks
  - Stores hack IDs and metadata
  - Used for update detection
  - Maintains organization structure

### 🔄 Update Detection
- Detects when newer versions are available and automatically overwrites existing ROM hacks, keeping your library current
- Shows red italic "Replaced with a new version!" message
- Automatically updates ROM files while maintaining organization

### 📝 Log Levels
- Information: Standard operations
- Debug: Detailed progress including API requests
- Verbose: All operations and detailed processing steps
- Error: Only shows error/failure messages for troubleshooting
- **New**: Italic styling for patch application messages

### 👨‍💻 Project Architecture
The project features a modular architecture with unified patching system:

```
/SMWCentral Downloader & Patcher
  ├── main.py             # Application entry point
  ├── api_pipeline.py     # API interaction and processing
  ├── patch_handler.py    # Unified IPS/BPS patch handling
  ├── patcher_ips.py      # IPS patch implementation
  ├── patcher_bps.py      # BPS patch implementation
  ├── config_manager.py   # Configuration handling
  ├── logging_system.py   # Centralized logging with styling
  ├── utils.py           # Utility functions
  ├── smwc_api_proxy.py  # API proxy with rate limiting
  ├── /ui                # UI components
  │   ├── __init__.py    # UI initialization
  │   ├── layout.py      # Main layout management
  │   └── components.py  # Reusable UI components
  └── config.json        # Saved configurations
```

# Release Notes

## v2.4.0
This major update introduces a unified patch handling system, eliminates external dependencies, and significantly improves the patching experience with better error handling and user feedback.

### 🔧 Major Functionality Changes
- **Removed Flips Dependency**: Built-in patch handler replaces external Flips requirement
- **Unified Patch System**: Single `PatchHandler` class automatically detects and handles both IPS and BPS formats
- **Intelligent Header Detection**: Automatically detects and removes SMC/SFC headers before patching
- **Enhanced Error Handling**: Detailed error messages with full stack traces for debugging
- **Improved Checksum Handling**: Proper SNES ROM checksum calculation for IPS patches

### 🎨 UI & Logging Improvements
- **Italic Patch Messages**: Patch application messages now display in italics for better visibility
- **Detailed Progress Logging**: Shows patch type, filename, and detailed progress information
- **Enhanced Debug Output**: File sizes, paths, and step-by-step patching information
- **Cleaner Success Messages**: Removed redundant "patch applied successfully" messages

### 🏗️ Architecture Improvements
- **Modular Patch System**: Separate `patcher_ips.py` and `patcher_bps.py` with unified interface
- **Consistent API**: Both IPS and BPS patches use identical `Patch.load()` and `patch.apply()` methods
- **Better Error Propagation**: Improved error handling throughout the patch pipeline
- **Code Simplification**: Removed complex header detection logic in favor of library-native handling

### 🔧 Technical Improvements
- **IPS Implementation**: Uses existing `ips_util` library for reliable IPS patching
- **BPS Implementation**: Enhanced BPS handler with proper temporary file management and fallback methods
- **Header Management**: Automatic SMC header detection and removal (512-byte headers)
- **Memory Efficiency**: Better handling of large ROM files during patching
- **Compatibility Fixes**: Python 3.8+ compatibility for `time.clock` deprecation

### 📦 Dependencies Changes
- **Removed**: Flips executable requirement
- **Enhanced**: `python-bps` library integration
- **Maintained**: `ips_util` library for IPS support

### 🧪 Testing & Validation
- Verified IPS patches work correctly without checksum corruption
- Tested BPS patches with proper header handling
- Validated automatic patch format detection
- Confirmed error handling and logging improvements
- Tested both headerless and headered ROM files
- Verified temporary file cleanup and memory management

### 📁 File Changes
- **Added**: `patch_handler.py` - Unified patch handling system
- **Added**: `patcher_ips.py` - IPS patch implementation using ips_util
- **Added**: `patcher_bps.py` - BPS patch implementation with enhanced error handling
- **Modified**: `api_pipeline.py` - Updated to use new patch handler
- **Modified**: `logging_system.py` - Added italic styling support for patch messages
- **Modified**: `config_manager.py` - Removed Flips path requirement
- **Modified**: `utils.py` - Added title_case function for consistent naming
- **Removed**: Direct Flips integration code

### 🎯 User Experience Improvements
- **Simplified Setup**: Only ROM and output paths needed (no more Flips setup)
- **Better Feedback**: Clear indication of which patch is being applied
- **Improved Reliability**: Built-in patching eliminates external tool failures
- **Enhanced Debugging**: Detailed error messages help troubleshoot issues
- **Consistent Behavior**: Unified handling regardless of patch format

## v2.3.0
This update focuses on robust, centralized SMWC API rate limit handling, improved reliability for large batch operations, and better error logging.

### 🔧 Functionality Improvements
- Improved handling of API rate limits: automatic retries, smart waiting, and detailed logging
- Modularized API logic for easier maintenance

### 🏗️ Technical Improvements
- All API requests now use a single proxy for consistent rate limit handling
- Dynamic delay calculation based on API headers (when available)
- Improved debug and warning logging for API responses and rate limit events

### 📁 File Changes
- `smwc_api_proxy.py`: Added centralized proxy with dynamic delay
- `api_pipeline.py`: Updated to use proxy for all SMWC API calls

## v2.2.0
This update focuses on modernizing the UI with theming support, improving architecture, enhancing user experience, and adding important functionality improvements.

### 🔧 Functionality Improvements
- Added support for both .bps and .ips patch formats
- Added Error log level to only show failed/critical logs
- Now require all setup paths (Flips, Base ROM, Output Directory) before allowing downloads
- Improved release packaging to include only necessary files (executable, config.json, README.md)

### 🎨 UI & Theme Updates
- Added Sun Valley theme integration for modern Windows 11 styling
- Implemented dark/light theme toggle with crescent moon switch
- Added Windows title bar theming support (Windows 10/11)
- Improved font consistency across theme changes
- Enhanced UI spacing and padding for better visual hierarchy
- Right-aligned Browse buttons in Setup section
- Enlarged Download & Patch button with accent styling

### 🏗️ Architecture Improvements
- Restructured codebase into modular components
- Separated UI, configuration, and logging concerns
- Implemented improved error handling and protection against crashes
- Created centralized logging system with better level filtering
- Added debug message coloring for better visibility

### 🔧 Technical Improvements
- Integrated `sv-ttk` for modern theme system
- Added `pywinstyles` for Windows title bar customization
- Improved font handling to prevent size inconsistencies
- Better theme persistence during application state changes
- Enhanced UI layout with proper padding and alignment
- Optimized log message handling to prevent recursion

### 📦 Dependencies Added
- `sv-ttk>=2.5.5` - Sun Valley theme
- `pywinstyles>=1.0.0` - Windows title bar theming

### 🧪 Testing & Validation
- Verified theme switching works correctly
- Tested font consistency across light/dark modes
- Validated Windows 10/11 title bar theming
- Confirmed UI layout improvements
- Tested button styling and spacing
- Validated debug/verbose logging functionality

### 📁 File Changes
- `main.py`: Added theme system and font management
- Created modular UI architecture with components
- Added centralized configuration and logging
- Updated README with architecture documentation
- `.gitignore`: Added build artifacts and cache exclusions

## v2.1.0
This update focuses on improving filtering flexibility and fixing type handling inconsistencies.

### 🔄 Optional Difficulty Filtering
- Made difficulty selection optional for all hack types
- Added confirmation dialog when no difficulty selected
- Downloads all difficulties when none selected
- Maintains existing filtering when difficulties are selected

### 🛠️ Type Handling Fixes
- Fixed SMWC API type key handling for Tool-Assisted hacks
  - Now correctly uses `tool_assisted` internal key
  - Resolved inflated/incorrect API results
- Improved folder naming consistency
  - Proper casing for all type folders (e.g. "Tool-Assisted")
  - Consistent naming across all hack types
  - Better type key normalization

### 🧪 Testing & Validation
- Verified downloads work without difficulty filters
- Confirmed difficulty filtering still works when selected
- Tested confirmation dialog functionality
- Validated API responses for Tool-Assisted hacks
- Verified folder structure and naming
- Tested against all hack types

### 📁 File Changes
- `ui.py`: Modified difficulty validation logic
- `utils.py`: Updated type key handling and folder naming
- No changes to core download/patch functionality

## v2.0.0
[Previous release notes remain unchanged...]
