# SMWC Downloader & Patcher v2.1

**SMWCentral Downloader & Patcher** is a Python GUI tool built to automate downloading, patching, and organizing Super Mario World ROM hacks from [SMWCentral.net](https://www.smwcentral.net/). It uses the official SMWC API to fetch hack information and integrates with Flips for patching.

## 📚 Table of Contents

- [✨ New Features](#-new-features)
- [✅ Core Features](#-core-features)
- [📦 Requirements](#-requirements)
- [🖥️ Usage](#-usage)
- [🗂️ Folder Structure](#-folder-structure)
- [🧪 Building Executable](#-building-executable)
- [🔧 Configuration](#-configuration)
- [🎨 UI Features](#-ui-features)
- [🔄 Update Detection](#-update-detection)
- [📝 Log Levels](#-log-levels)
- [📄 Release Notes](#release-notes)
  - [v2.1.0](#v210)
  - [v2.0.0](#v200)

### 📸 Screenshots
![Application Interface](/images/screenshot_app_v2.1.png?v=2)

### ✨ New Features
- Official SMWC API Integration (replacing web scraping)
- Visual indicators for ROM hack updates
- Improved error handling and retries
- Rate limit handling for API requests
- Red italic styling for replaced ROM notifications
- Automatic difficulty folder updates when SMWC changes hack difficulty

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
  - Patches using Flips
  - Supports both .smc and .sfc ROM formats
  - Renames and organizes files
  - Updates existing hacks
- Visual feedback:
  - Progress logging
  - Special indicators for updated ROMs
  - Colored log levels
- Smart file management:
  - Keeps track of processed hacks
  - Detects and handles hack updates
  - Organizes by type and difficulty

### 📦 Requirements
- Python 3.9+
- Recommended: VS Code or any IDE
- Required packages:
  ```bash
  pip install requests
  ```

### 🖥️ Usage
1. Launch `main.py`
2. Configure paths:
   - FLIPS executable
   - Clean SMW ROM
   - Output directory
3. Select filters:
   - Required: Hack type
   - Optional: Difficulties
   - Optional: Other filters (HoF, SA-1, etc.)
4. Click 'Download & Patch'
5. Monitor progress in the log window
6. Find patched ROMs in your output folder

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

### 🧪 Building Executable
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Run:
   ```bash
   pyinstaller main.spec
   ```
3. Find the executable in `dist` folder

### 🔧 Configuration
- `config.json`: Essential paths
  ```json
  {
    "flips_path": "path/to/flips.exe",
    "base_rom_path": "path/to/clean.smc",
    "output_dir": "path/to/output"
  }
  ```
- `processed.json`: Tracks downloaded hacks
  - Stores hack IDs and metadata
  - Used for update detection
  - Maintains organization structure

### 🎨 UI Features
- Clean, modern interface
- Difficulty toggles with Select/Deselect All
- Radio button filters
- Progress logging with color coding
- Log level selection (Information/Debug/Verbose)
- Visual update indicators
- Path management with file browsers

### 🔄 Update Detection
- Detects when newer versions are available and automatically overwrites existing ROM hacks, keeping your library current
- Shows red italic "Replaced with a new version!" message
- Automatically updates ROM files while maintaining organization

### 📝 Log Levels
- Information: Standard operations
- Debug: Detailed progress
- Verbose: All operations
- Error: Issues and failures (always shown)

# Release Notes

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
