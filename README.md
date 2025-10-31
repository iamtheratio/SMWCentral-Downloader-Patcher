# SMWC Downloader & Patcher

🎮 **Download and play Super Mario World ROM hacks with one click**

A simple desktop app that automatically downloads, patches, and organizes ROM hacks from SMWCentral. Works on Windows, Mac, and Linux.

![App Screenshot](images/ss_app_dashboard_v4.3.png)

## 📋 Table of Contents

- [📥 Download & Install](#-download--install)
- [🚀 How to Use](#-how-to-use)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [📝 What You Need](#-what-you-need)
- [📝 Changelog](#-changelog)

## 📥 Download & Install

### Windows (10/11)
1. Download `SMWC-Downloader-Windows-x64.zip` from the [Releases page](../../releases)
2. Extract the ZIP file to any folder you want (like your Desktop or Program Files)
3. Double-click `SMWC Downloader.exe` to run the app
4. **If Windows shows a security warning**: Click "More info" → "Run anyway" (this is normal for new apps)

> [!IMPORTANT]
> Windows may flag this app because it's new and unsigned. This is normal!
> 
> **If you see warnings:**
> - **Browser**: Click "Keep" if download gets blocked
> - **Windows Defender**: Click "More info" → "Run anyway" 
> - **To prevent future warnings**: Add the app folder to Windows Defender exclusions in Settings → Update & Security → Windows Security → Virus & threat protection → Exclusions

### Mac (macOS 10.15+)
1. Download `SMWC-Downloader-macOS-Universal.dmg` from the [Releases page](../../releases)
2. Open the DMG file and drag the app to your Applications folder
3. **First time only**: Right-click the app → "Open" → "Open" (to bypass security warning)
4. After that, you can launch it normally from Applications or Spotlight

### Linux (Ubuntu, Debian, Fedora, etc.)
1. Download `SMWC-Downloader-Linux-x64.tar.gz` from the [Releases page](../../releases)
2. Extract: `tar -xzf SMWC-Downloader-*.tar.gz`
3. Run the installer: `./install.sh` (this adds the app to your Applications menu)
4. Launch from Applications menu or run `smwc-downloader` in terminal

## 🚀 How to Use

### First Time Setup
1. **Launch the app** - it will open to the main dashboard
2. **Go to Settings**: Click the "Settings" tab at the top of the app
3. **Set your ROM folder**: Click the folder icon to choose where you want your patched ROMs saved
4. **Add your base ROM**: Click "Browse" next to "Super Mario World ROM" and select your clean SMW ROM file
5. **You're ready!** The app will remember these settings and you can return to the main dashboard

### Downloading ROM Hacks
1. **Set your filters**: Use the filter options to narrow down what you want to search for (difficulty, type, author, etc.)
2. **Choose display mode**: Use the "Show only non-downloaded hacks" checkbox to hide hacks you already own, making it easier to find new content
3. **Search for hacks**: Click the "Search Hacks" button to pull data from the SMWCentral API based on your filters
4. **Browse results as they load**: Results appear progressively as each page loads - no need to wait for all data to finish loading
5. **Select hacks to download**: Click the checkmark in the first column for each hack you want to download
   - **Tip**: Click the column header to select ALL hacks at once
   - **Already downloaded hacks** are shown in italic with muted colors to help you identify what you already own
6. **Start downloading**: Click "Download & Patch" to begin downloading and patching your selected hacks
7. **Wait for completion**: The app will automatically download each hack and apply it to your base ROM
8. **Play**: Your patched ROMs will be saved to your chosen folder, ready to play in any emulator

### Managing Your Collection
1. **View your collection**: Click the "Collection" tab to see all your downloaded ROMs
2. **Add hacks manually**: Use the "Add Hack" button to track hacks you've played from other sources
3. **Track progress**: Mark hacks as completed, rate them (1-5 stars), and add personal notes
4. **Quick editing**: Click directly on completion dates, time to beat, or notes to edit them
5. **Advanced editing**: Double-click any hack to open the full edit dialog
6. **📁 Quick file access**: Click the folder icon next to any hack name to instantly open its file location in your system's file manager
7. **Filter and sort**: Use filters to find specific hacks, or click column headers to sort

#### Input Format Guide

When editing **Completed Date** and **Time to Beat** fields, the app supports flexible input formats:

**📅 Date Formats:**
- `MM/DD/YYYY` - Example: `12/25/2024`
- `MM-DD-YYYY` - Example: `12-25-2024`
- `MM.DD.YYYY` - Example: `12.25.2024`
- `YYYY/MM/DD` - Example: `2024/12/25`
- `YYYY-MM-DD` - Example: `2024-12-25`

**⏱️ Time to Beat Formats:**

| Format Type | Pattern | Examples | Description |
|-------------|---------|----------|-------------|
| **Colon-Separated** | `HH:MM:SS` | `1:30:45`, `12:05:30` | Hours:Minutes:Seconds |
| | `MM:SS` | `90:30`, `5:15` | Minutes:Seconds |
| **Letter Suffix** | `XhYmZs` | `2h 30m 15s`, `1h 45m`, `90m`, `45s` | Hours/minutes/seconds with letters |
| | *Flexible spacing* | `2h30m15s` = `2h 30m 15s` | Spaces optional |
| **Day Formats** | `XdYhZmWs` | `14d 10h 2m 1s`, `7d 12h`, `2d` | Days/hours/minutes/seconds |
| | *Shortened* | `14d 10` (assumes hours) | Advanced shorthand |
| **Word-Based** | `X minutes/mins` | `150 minutes`, `90 mins` | Full word formats |
| **Simple Number** | `X` | `90`, `5`, `120` | Just a number (assumes minutes) |

### 🎮 QUSB2SNES Sync (New in v4.8!)
Transfer your ROM hack collection directly to your SD2SNES/FXPAK Pro cart with one click!

#### What You Need
- **SD2SNES or FXPAK Pro** flashcart connected via USB
- **QUSB2SNES software** installed on your computer ([download here](https://github.com/Skarsnik/QUsb2snes))

#### Setup Steps
1. **Install QUSB2SNES**: Download and install the QUSB2SNES software on your computer
2. **Connect your cart**: Plug your SD2SNES/FXPAK Pro into your computer via USB
3. **Launch QUSB2SNES**: Start the QUSB2SNES application
4. **Configure in this app**:
   - Go to **Settings** tab
   - Find the **QUSB2SNES Sync** section
   - Check **"Enable"** to activate the feature
   - Set **Host** to `localhost` (usually default)
   - **Configure Port**:
     - **Port 8080**: Default for newer QUSB2SNES versions (recommended)
     - **Port 23074**: Use for legacy QUSB2SNES installations
     - **Check your QUSB2SNES**: Look for "WebSocket server on port XXXX" message when starting
   - Choose your **Device** from the dropdown
   - Set **Sync To Folder** to where you want ROMs stored (default: `/ROMS`)

#### How to Sync
1. **Click "Connect"** to establish connection with your device
2. **Click "Sync"** to start transferring your ROM collection
3. **Wait for completion** - the app shows progress and only uploads new/changed files
4. **Your ROMs are ready** to play on real hardware!

#### Features
- **Smart Incremental Sync**: Only transfers new or modified files to save time
- **Organized Folders**: Maintains your collection structure (Kaizo, Standard, etc.)
- **Real-Time Progress**: See exactly what's being uploaded
- **Automatic Retry**: Handles connection issues and device conflicts gracefully
- **Safe Operation**: Verifies all transfers completed successfully

#### Troubleshooting
- **"Connection failed"**: Make sure QUSB2SNES software is running
- **"Device in use"**: Close other apps using your SD2SNES (like RetroAchievements)
- **"Sync timeout"**: Large files take time - the app retries automatically
- **Port Issues**: 
  - **Default port 8080**: Works with newer QUSB2SNES versions (recommended)
  - **Legacy port 23074**: Use this if you have an older QUSB2SNES installation
  - **How to check**: In QUSB2SNES software, look for "WebSocket server on port XXXX"
  - **Changing ports**: Update the port in Settings → QUSB2SNES Sync section

### App Settings
- **Download location**: Change where ROMs are saved
- **Multi-type downloads**: Configure how hacks with multiple types (like "Kaizo, Tool-Assisted") are handled
  - **Primary only**: Download to the main type folder only
  - **Copy to all folders**: Create copies in each applicable type folder
- **Auto-updates**: Choose if you want automatic app updates
- **Theme**: Switch between light and dark modes with instant, smooth transitions and optimized performance
- **API Delay Slider**: Set delay from 0.0 to 3.0 seconds between API requests to avoid rate limiting issues

## 🛠️ Troubleshooting

### Windows Security Warning
Windows may show "Windows protected your PC" when running the app. This is normal for new applications. Click "More info" → "Run anyway" to continue.

### Mac Security Warning
macOS may say the app is from an "unidentified developer." Right-click the app → "Open" → "Open" to bypass this. You only need to do this once.

### Linux: App Won't Start
If the app won't launch, install these packages:
- **Ubuntu/Debian**: `sudo apt install python3-tk`
- **Fedora**: `sudo dnf install tkinter`

### Can't Find Downloaded ROMs
Check the folder path shown in Settings. By default, ROMs are saved to:
- **Windows**: `Desktop\SMWCentral Hacks\`
- **Mac**: `Desktop/SMWCentral Hacks/`
- **Linux**: `~/Desktop/SMWCentral Hacks/`

## 📝 What You Need

- **Your Operating System**: Windows 10+, macOS 10.15+, or modern Linux
- **A clean SMW ROM**: Unmodified Super Mario World ROM file (.smc or .sfc)
- **Storage space**: About 20 MB for the app, plus space for your ROM collection
- **Internet connection**: Required for downloading hacks and app updates

##  Changelog

<details>
<summary><strong>Version 4.8 - Latest Release</strong></summary>

### v4.8.0

### 🆕 New Features
- **🎮 QUSB2SNES Sync**: Complete SD2SNES/FXPAK Pro integration for one-click ROM transfers
  - Smart incremental sync (only uploads new/changed files)
  - Organized folder structure maintenance
  - Real-time progress tracking and automatic retry logic
  - Easy setup with host/port/device configuration
- **📁 Folder Icons**: Added clickable folder icons in collection to quickly open hack file locations
- **🗂️ Cross-Platform File Explorer Integration**: Open file managers on Windows (Explorer), macOS (Finder), and Linux (various)
- **🎯 Smart File Navigation**: Click folder icons to open and highlight specific hack files

### 🔧 Improvements  
- **Enhanced QUSB2SNES Communication**: Full WebSocket integration with connection resilience
- **Optimized File Transfer**: Tree-based sync algorithm for maximum efficiency
- **Better Error Recovery**: Improved handling of device conflicts and connection timeouts
- **Enhanced Settings**: New QUSB2SNES configuration section with persistent settings
- **Cross-Platform Reliability**: Comprehensive support for multiple operating systems

</details>

<details>
<summary><strong>Previous Versions</strong></summary>

### v4.7.0

### 🔧 Improvements
- **Enhanced Download Selection**: Click anywhere on a search result row to select/deselect hacks for download
- **Improved Filter Layout**: Responsive filter sections work better when window is maximized
- **Clearer Filter Controls**: Renamed "Search Criteria" to "Show/Hide Filters" for better clarity

</details>

<details>
<summary><strong>Older Versions</strong></summary>

### v4.6.0

### 🐛 Bug Fixes
- **Time Parsing Accuracy**: Fixed critical bug where time inputs like "27m 22s" were incorrectly parsed as "2h 7m 22s"
- **Input Format Reliability**: Improved regex pattern matching order to handle all time formats correctly
- **Data Integrity**: Ensures accurate time-to-beat tracking in Collection page

### 🔧 Improvements
- **Auto-Refresh on Navigation**: Dashboard and Collection pages now automatically refresh data when navigating between tabs
- **Enhanced Input Validation**: Better handling of edge cases in time parsing (supports days, overflow values, etc.)

### v4.5.0

### 🚀 New Features
- **Progressive Data Loading**: Results display as each page loads from the API for instant review
- **Already Downloaded Indicator**: Downloaded hacks shown in italic with muted colors
- **Smart Collection Filtering**: "Show only non-downloaded hacks" checkbox for faster browsing
- **Enhanced Theme System**: Improved color management and visual consistency
- **Performance Optimizations**: Faster theme updates and UI responsiveness

### 🔧 Improvements
- **Search Experience**: Browse results immediately as data loads
- **Collection Management**: Better visual distinction and filtering for owned content
- **Theme Performance**: Optimized color updates across light and dark modes
- **UI Polish**: Consistent visual elements during theme transitions

### 🐛 Bug Fixes
- Fixed dark gray selection colors appearing in light mode
- Resolved delays in theme color updates for downloaded indicators
- Fixed visual inconsistencies during theme switching

### v4.5.0

### 🚀 New Features
- **Progressive Data Loading**: Results display as each page loads from the API for instant review
- **Already Downloaded Indicator**: Downloaded hacks shown in italic with muted colors
- **Smart Collection Filtering**: "Show only non-downloaded hacks" checkbox for faster browsing
- **Enhanced Theme System**: Improved color management and visual consistency
- **Performance Optimizations**: Faster theme updates and UI responsiveness

### 🔧 Improvements
- **Search Experience**: Browse results immediately as data loads
- **Collection Management**: Better visual distinction and filtering for owned content
- **Theme Performance**: Optimized color updates across light and dark modes
- **UI Polish**: Consistent visual elements during theme transitions

### 🐛 Bug Fixes
- Fixed dark gray selection colors appearing in light mode
- Resolved delays in theme color updates for downloaded indicators
- Fixed visual inconsistencies during theme switching

</details>

<details>
<summary><strong>Previous Versions</strong></summary>

### v4.4.0
- **Cross-Platform Support**: Full compatibility with Windows, macOS, and Linux
- **Download State Management**: Collection tab is now locked during active downloads to prevent data corruption
- **Enhanced Dashboard Analytics**: Improved accuracy and data tracking for collection metrics

### v4.3.0
- Dashboard implementation with analytics and charts
- Collection page with comprehensive filtering and editing
- Theme support (light/dark modes)
- Improved bulk download workflow

### v4.2.0
- Multi-type download support
- Enhanced search and filtering capabilities
- Progress tracking improvements
- Bug fixes and stability improvements

### v4.1.0
- Initial release with core downloading functionality
- Basic patching system
- Simple collection tracking
- Windows-only support

</details>

---

**Made for the Super Mario World ROM hacking community** ❤️