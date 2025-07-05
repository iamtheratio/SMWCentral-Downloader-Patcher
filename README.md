## 🛠️ SMWCentral Downloader & Patcher

**SMWCentral Downloader & Patcher** is a Python GUI tool built to automate downloading, patching, and organizing Super Mario World ROM hacks from [SMWCentral.net](https://www.smwcentral.net/). It uses the official SMWC API to fetch hack information and integrates with Flips for patching.

### ✨ New Features
- Official SMWC API Integration (replacing web scraping)
- Visual indicators for ROM hack updates
- Improved error handling and retries
- Rate limit handling for API requests
- Red italic styling for replaced ROM notifications

### ✅ Core Features
- Choose Hack type:
  - Standard
  - Kaizo
  - Puzzle
  - Tool-Assisted
  - Pit
- Choose Hack difficulty:
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
   - Hack type
   - Difficulties
   - Optional filters (HoF, SA-1, etc.)
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
