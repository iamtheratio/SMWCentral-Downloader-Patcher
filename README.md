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
   - **NEW**: Select "No Difficulty" to download hacks without difficulty ratings
   - Click **Download & Patch**.
   - Patched ROMs will appear in your output folder.

### ✨ New Features
- **"No Difficulty" Filter**: Download hacks that don't have difficulty ratings assigned
- **Mixed Difficulty Selection**: Combine "No Difficulty" with regular difficulty levels
- **Enhanced Filtering Logic**: Intelligent API handling for special difficulty cases
- **Improved Logging**: Cleaner output with warning messages for special operations
- **Orange Warning Messages**: Clear visual indicators for important information
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
  - **NEW**: No Difficulty (for hacks without ratings)
- Filter options:
  - Hall of Fame
  - SA-1
  - Collab
  - Demo
- Automated workflow:
  - Downloads from SMWC API
  - **NEW**: Smart API handling for "No Difficulty" selections
  - Unzips downloaded files
  - **Built-in patching** with unified IPS/BPS handler
  - Supports both .bps and .ips patch formats
  - Supports both .smc and .sfc ROM formats
  - Automatic header detection and handling
  - Renames and organizes files
  - Updates existing hacks
- Visual feedback:
  - Progress logging with italic patch application messages
  - **NEW**: Orange warning messages for important information
  - Special indicators for updated ROMs
  - Colored log levels
  - **NEW**: Cleaner, organized log output
  - Detailed patching progress
- Smart file management:
  - Keeps track of processed hacks
  - Detects and handles hack updates
  - Organizes by type and difficulty
  - **NEW**: Handles hacks without difficulty ratings

### 🗂️ Folder Structure
Patched hacks are saved based on their type > difficulty attributes:
```
/Output Folder
  /Kaizo
    /01 - Newcomer
      Hack Name.smc
    /02 - Casual
      Hack Name.smc
    /No Difficulty        # NEW: Folder for hacks without ratings
      Hack Name.smc
  /Standard
    /01 - Newcomer
      Hack Name.smc
    /02 - Casual
      Hack Name.smc
    /No Difficulty        # NEW: Folder for hacks without ratings
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
- Information: Standard operations with clean, organized output
- Debug: Detailed progress including API requests and timing
- Verbose: All operations and detailed processing steps
- Error: Only shows error/failure messages for troubleshooting
- **Enhanced**: Orange warning messages for important information
- **Enhanced**: Cleaner log formatting with reduced debug spam

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
  ├── utils.py           # Utility functions and difficulty mappings
  ├── smwc_api_proxy.py  # API proxy with rate limiting
  ├── /ui                # UI components
  │   ├── __init__.py    # UI initialization
  │   ├── layout.py      # Main layout management
  │   └── components.py  # Reusable UI components
  └── config.json        # Saved configurations
```

# Release Notes

## v2.4.0
This major update introduces "No Difficulty" filtering support, enhanced logging, and significant improvements to the user experience with cleaner output and better API handling.

### 🆕 Major New Features
- **"No Difficulty" Filter**: New option to download hacks that don't have difficulty ratings assigned on SMWC
- **Mixed Difficulty Selection**: Can combine "No Difficulty" with regular difficulty levels (e.g., "Newcomer + No Difficulty")
- **Intelligent API Handling**: Automatically downloads all hacks then filters locally when "No Difficulty" is selected due to SMWC API limitations
- **Enhanced Warning System**: Clear orange warning messages explain when special processing is needed

### 🔧 API & Filtering Improvements
- **Smart Post-Processing**: When "No Difficulty" is selected, downloads all hacks then filters for empty difficulty fields
- **Mixed Mode Support**: Handles combinations like "Expert + No Difficulty" by including both categories
- **Improved Pagination**: Continues downloading all pages even when individual pages return fewer results
- **Better Error Handling**: Enhanced validation and error messages for filter combinations

### 🎨 Logging & UI Enhancements
- **Cleaner Log Output**: Dramatically reduced debug message spam for better readability
- **Orange Warning Messages**: Important warnings now display in bright orange (#ff9900) for visibility
- **Organized Message Flow**: Logical progression from download → filter → patch for better user understanding
- **Simplified Debug Mode**: Debug messages only show timing information without cluttering main flow
- **Enhanced Progress Feedback**: Clear indication of filtering progress when processing large datasets

### 🗂️ File Organization Updates
- **"No Difficulty" Folders**: Hacks without difficulty ratings are organized into "No Difficulty" subfolders
- **Consistent Naming**: Updated folder structure to handle edge cases and maintain organization
- **Better Path Handling**: Improved file organization for mixed difficulty selections

### 🏗️ Architecture Improvements
- **Enhanced Utils**: Added comprehensive difficulty mapping system for "No Difficulty" support
- **Improved Pipeline Logic**: Better separation of API downloading vs. local filtering
- **Rate Limit Optimization**: Reduced unnecessary API debug output while maintaining functionality
- **Memory Efficiency**: Better handling of large hack datasets during filtering operations

### 🧪 Testing & Validation
- Verified "No Difficulty" filtering works correctly across all hack types
- Tested mixed difficulty selections (e.g., "Newcomer + No Difficulty")
- Confirmed proper folder organization for hacks without difficulty ratings
- Validated API performance with large datasets (1000+ hacks)
- Tested warning message display and color formatting
- Verified clean log output in both normal and debug modes

### 📁 Technical Changes
- **Modified**: `api_pipeline.py` - Added "No Difficulty" detection and post-filtering logic
- **Modified**: `utils.py` - Added DIFFICULTY_KEYMAP and "No Difficulty" folder handling
- **Modified**: `ui/components.py` - Added "No Difficulty" to difficulty selection UI
- **Modified**: `ui/__init__.py` - Updated DIFFICULTY_LIST to include "No Difficulty"
- **Modified**: `logging_system.py` - Enhanced warning message color formatting
- **Modified**: `smwc_api_proxy.py` - Simplified debug output for cleaner logs

### 🎯 User Experience Improvements
- **Clear Expectations**: Warning messages explain why "No Difficulty" selections take longer
- **Better Visual Feedback**: Orange warnings and cleaner progress messages
- **Simplified Output**: Removed excessive debug spam while maintaining essential information
- **Logical Flow**: Download → Filter → Patch progression is now clear and easy to follow
- **Enhanced Discovery**: Users can now find and download hacks that weren't properly categorized with difficulty ratings

### 🔄 Backward Compatibility
- All existing functionality remains unchanged
- Previous difficulty selections work exactly as before
- Existing folder structures are maintained
- No configuration changes required

### 🚀 Performance Improvements
- **Optimized Logging**: Reduced message volume by 80% for better performance
- **Smart Filtering**: Efficient post-processing only when needed
- **Better Memory Usage**: Improved handling of large hack collections
- **Reduced API Spam**: Cleaner rate limit handling with less verbose output

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
