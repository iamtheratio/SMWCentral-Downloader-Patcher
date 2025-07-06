# SMWC Downloader & Patcher v2.2

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
- [👨‍💻 Project Architecture](#-project-architecture)
- [📄 Release Notes](#release-notes)
  - [v2.2.0](#v220)
  - [v2.1.0](#v210)
  - [v2.0.0](#v200)

### 📸 Screenshots
![SMWC Downloader Interface](/images/screenshot_app_v2.2.png)

### ✨ New Features
- Official SMWC API Integration (replacing web scraping)
- Visual indicators for ROM hack updates
- Improved error handling and retries
- Rate limit handling for API requests
- Red italic styling for replaced ROM notifications
- Automatic difficulty folder updates when SMWC changes hack difficulty
- Modular code architecture for better maintainability

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
  - Supports both .bps and .ips patch formats
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
  pip install requests sv-ttk pywinstyles
  ```

### 🖥️ Usage
1. Launch `main.py`
2. Configure paths (all are required):
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
- `config.json`: Essential paths (**All fields are required**)
  ```json
  {
    "flips_path": "path/to/flips.exe",
    "base_rom_path": "path/to/clean.smc",
    "output_dir": "path/to/output"
  }
  ```
- **Note:** You must set all three paths (Flips, Base ROM, Output Directory) before you can download and patch ROMs. The app will show an error message if any required path is missing.
- `processed.json`: Tracks downloaded hacks
  - Stores hack IDs and metadata
  - Used for update detection
  - Maintains organization structure

### 🎨 UI Features
- Modern Sun Valley theme with dark/light mode toggle
- Windows title bar theming (Windows 10/11)
- Clean, responsive interface design
- Difficulty toggles with Select/Deselect All
- Radio button filters with consistent styling
- Progress logging with color coding
- Log level selection (Information/Debug/Verbose)
- Visual update indicators
- Path management with right-aligned browse buttons
- Enlarged, accent-styled Download & Patch button

### 🔄 Update Detection
- Detects when newer versions are available and automatically overwrites existing ROM hacks, keeping your library current
- Shows red italic "Replaced with a new version!" message
- Automatically updates ROM files while maintaining organization

### 📝 Log Levels
- Information: Standard operations
- Debug: Detailed progress including API requests
- Verbose: All operations and detailed processing steps
- Error: Only shows error/failure messages for troubleshooting (new in v2.2)

### 👨‍💻 Project Architecture
The project has been restructured with a modular architecture:

```
/SMWCentral Downloader & Patcher
  ├── main.py             # Application entry point
  ├── api_pipeline.py     # API interaction and processing
  ├── config_manager.py   # Configuration handling
  ├── logging_system.py   # Centralized logging
  ├── utils.py           # Utility functions
  ├── /ui                # UI components
  │   ├── __init__.py    # UI initialization
  │   ├── layout.py      # Main layout management
  │   └── components.py  # Reusable UI components
  └── config.json        # Saved configurations
```

#### Component Responsibilities:
- **main.py**: Entry point, theme management, and application setup
- **api_pipeline.py**: API interaction, download, patching logic
- **config_manager.py**: Configuration file read/write
- **logging_system.py**: Centralized logging with level filtering
- **ui/layout.py**: Main UI structure and arrangement
- **ui/components.py**: Reusable UI elements (setup, filters, etc.)

This architecture improves maintainability, separates concerns, and makes future updates easier to implement.

# Release Notes

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
