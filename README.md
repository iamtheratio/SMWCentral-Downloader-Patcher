# SMWC Downloader & Patcher v2.2

**SMWCentral Downloader & Patcher** is a Python GUI tool that automates downloading, patching, and organizing Super Mario World ROM hacks from [SMWCentral.net](https://www.smwcentral.net/). It uses the official SMWC API and integrates with Flips for patching.

## 📚 Table of Contents

- [✨ Key Features](#-key-features)
- [✅ Core Features](#-core-features)
- [📸 Screenshots](#-screenshots)
- [🚀 Getting Started](#-getting-started)
- [📝 Log Levels](#-log-levels)
- [👨‍💻 Project Structure](#-project-structure)
- [📄 Release Notes](#release-notes)
  - [v2.2.0](#v220)
  - [v2.1.0](#v210)
  - [v2.0.0](#v200)

### 📸 Screenshots
![SMWC Downloader Interface](/images/screenshot_app_v2.2.png)

### ✨ Key Features
- Official SMWC API Integration
- Visual indicators for ROM hack updates
- Support for both .bps and .ips patch formats
- Error log filtering and dedicated error view
- Rate limit handling for API requests
- Automatic difficulty folder updates
- Modern UI with dark/light theme toggle

### ✅ Core Features

**Filter & Organize**
- Hack types: Standard, Kaizo, Puzzle, Tool-Assisted, Pit
- Optional difficulty filtering (from Newcomer to Grandmaster)
- Additional filters: Hall of Fame, SA-1, Collab, Demo

**Automated Workflow**
- One-click downloading and patching
- Supports both .bps and .ips patch formats
- Handles .smc and .sfc ROM formats
- Smart update detection and management
- Organized by type and difficulty

**User Experience**
- Modern UI with light/dark theme
- Detailed logging with filterable levels
- Visual indicators for updates and errors
- Progress tracking and status updates

### 🚀 Getting Started

**Requirements**
- Python 3.9+
- Required packages: `requests`, `sv-ttk`, `pywinstyles`

**Quick Setup**
1. Clone this repository
2. Install dependencies: `pip install requests sv-ttk pywinstyles`
3. Launch with: `python main.py`
4. Configure:
   - Flips patcher location
   - Clean SMW ROM path
   - Output directory

**Building an Executable**
```bash
pip install pyinstaller
pyinstaller main.spec
```

**Organization**
ROM hacks are automatically organized by type and difficulty:
```
/Output
  /Kaizo
    /01 - Newcomer
    /02 - Casual
  /Standard
    /01 - Newcomer
    ...
```

**Configuration Files**
- `config.json`: Stores path settings
- `processed.json`: Tracks downloaded hacks for update detection

### 📝 Log Levels
- **Information**: Standard operations
- **Debug**: Detailed progress including API requests
- **Verbose**: All operations and detailed processing steps
- **Error**: Issues and failures only (filtered view with error indicators)

### 👨‍💻 Project Structure
```
/SMWCentral Downloader & Patcher
  ├── main.py             # Application entry point
  ├── api_pipeline.py     # API interaction and patching
  ├── config_manager.py   # Configuration handling
  ├── logging_system.py   # Centralized logging
  ├── utils.py            # Utility functions
  ├── /ui                 # UI components
  │   ├── __init__.py     # UI initialization
  │   ├── layout.py       # Main layout management
  │   └── components.py   # Reusable UI components
  └── config.json         # Saved configurations
```

This architecture improves maintainability, separates concerns, and makes future updates easier to implement.

# Release Notes

## v2.2.0
This update focuses on modernizing the UI, improving architecture, enhancing patch format support, and adding log filtering capabilities.

### 🛠️ Patch Format Improvements
- Added support for both .bps and .ips patch formats
- Smart detection of patch file type within downloaded zips
- Improved extraction logic to handle multiple patch formats

### 📊 Log Filtering Enhancements
- Added dedicated "Error" log level filter option
- Implemented visual indicator for error-only view
- Added informational message when in error-only view
- Improved error message visibility with consistent styling

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
- Verified patch format detection and extraction
- Confirmed error log filtering functionality
- Tested error message styling and indicators
- Validated log level switching behavior
- Verified theme switching works correctly
- Tested font consistency across light/dark modes
- Validated Windows 10/11 title bar theming

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
