# SMWC Downloader & Patcher v2.4

A Python GUI tool that automates downloading, patching, and organizing Super Mario World ROM hacks from [SMWCentral.net](https://www.smwcentral.net/). Features built-in IPS/BPS patching and intelligent filtering options.

## 🚀 Quick Start

1. **Download** the [latest release](https://github.com/iamtheratio/SMWCentral-Downloader-Patcher/releases/latest)
2. **Extract** to your preferred folder
3. **Run** `SMWC Downloader.exe`
4. **Setup** paths:
   - Clean SMW ROM (headerless .smc recommended)
   - Output directory
   - Optional: Adjust API delay slider if needed
5. **Select** hack type, difficulty, and filters
6. **Click** Download & Patch

![SMWC Downloader Interface](/images/screenshot_app_v2.2.png)

## ✨ Key Features

### Hack Selection
- **Types**: Standard, Kaizo, Puzzle, Tool-Assisted, Pit
- **Difficulties**: Newcomer → Grandmaster + **"No Difficulty"** option
- **Filters**: Hall of Fame, SA-1, Collab, Demo
- **Mixed Selection**: Combine multiple difficulties (e.g., "Expert + No Difficulty")

### Smart Processing
- **Built-in Patching**: No external tools needed - handles IPS & BPS formats
- **Auto-Organization**: Files sorted by type/difficulty into numbered folders
- **Update Detection**: Automatically replaces older versions
- **API Rate Control**: Adjustable delay slider (0-5 seconds) to prevent throttling

### Enhanced Experience
- **Clean Logging**: Organized progress with orange warnings for important info
- **Modern UI**: Dark/light themes with Windows titlebar integration
- **Intelligent Filtering**: Special handling for hacks without difficulty ratings
- **Error Recovery**: Robust handling of network issues and malformed files

## 🗂️ File Organization

```
/Output Folder
  /Kaizo
    /01 - Newcomer/
    /02 - Casual/
    /07 - Grandmaster/
    /08 - No Difficulty/    # For unrated hacks
  /Standard
    /01 - Newcomer/
    /08 - No Difficulty/
```

## ⚙️ Configuration

The app saves settings in `config.json`:
```json
{
  "base_rom_path": "path/to/clean.smc",
  "output_dir": "path/to/output",
  "api_delay": 0.8
}
```

**API Delay Slider**: Adjust if experiencing rate limiting (higher = slower but more reliable)

## 📋 Requirements

- Windows 10/11
- Clean Super Mario World ROM file
- Internet connection for SMWC API

## 🆕 What's New in v2.4

- **"No Difficulty" Filter**: Download hacks without difficulty ratings
- **API Delay Control**: User-adjustable request timing via slider
- **Enhanced Logging**: Cleaner output with orange warning messages
- **Mixed Selections**: Combine regular difficulties with "No Difficulty"
- **Better Performance**: Reduced debug spam, optimized filtering

## 🔧 Technical Notes

**"No Difficulty" Processing**: Due to SMWC API limitations, selecting "No Difficulty" downloads ALL hacks then filters locally. This takes longer but finds hacks that weren't properly categorized.

**File Formats**: Supports .smc/.sfc ROMs and .ips/.bps patches with automatic header detection.

## 📦 Building from Source

```bash
pip install -r requirements.txt
python main.py
```

**Dependencies**: `tkinter`, `requests`, `sv-ttk`, `pywinstyles`

## 📄 Full Changelog

<details>
<summary>Click to expand version history</summary>

### v2.4.0 - "No Difficulty" & API Controls
- Added "No Difficulty" filtering option
- User-configurable API delay slider
- Mixed difficulty selection support
- Enhanced logging with orange warnings
- Improved folder organization for unrated hacks

### v2.3.0 - API Rate Limiting
- Centralized SMWC API proxy
- Dynamic delay calculation
- Improved error handling for large batches

### v2.2.0 - Modern UI & Theming
- Sun Valley dark/light theme system
- Windows titlebar theming
- Built-in IPS/BPS patch support
- Error-only log level
- Modular architecture redesign

### v2.1.0 - Flexible Filtering
- Optional difficulty selection
- Fixed Tool-Assisted hack API keys
- Improved folder naming consistency

### v2.0.0 - Built-in Patching
- Removed Flips dependency
- Unified IPS/BPS patch handler
- Automatic header detection
- Enhanced error recovery
</details>

---

**Note**: This tool respects SMWC's terms of service and implements rate limiting to avoid server overload. Please use responsibly.
