# SMWCentral Downloader & Patcher v4.4

A powerful **cross-platform** desktop application for downloading, organizing, and patching Super Mario World ROM hacks from## 🔧 Technical Details

### System Requirements

| Platform | Minimum Requirements | Notes |
|----------|---------------------|--------|
| **Windows** | Windows 10 (1903+) or Windows 11 | 64-bit architecture |
| **macOS** | macOS 10.15+ (Catalina or newer) | Universal binary (Intel + Apple Silicon) |
| **Linux** | Modern distribution with GTK support | Ubuntu 18.04+, Debian 10+, Fedora 32+, etc. |

**All Platforms**:
- **Storage**: ~20 MB for application + space for your hack collection
- **Network**: Internet connection for downloading hacks and updates
- **ROM**: Clean Super Mario World ROM file

### Cross-Platform Features
- **Identical Functionality**: All features work the same across Windows, macOS, and Linux
- **Native Look & Feel**: Application adapts to each platform's UI conventions
- **Platform-Specific Optimizations**: Mouse wheel scrolling, keyboard shortcuts, and file dialogs optimized per platform
- **Unified Auto-Updates**: Single update system that works seamlessly across all platforms

### File Formats & Compatibility
- **Input**: Supports .zip files containing .ips or .bps patches from SMWCentral
- **Output**: Generates patched .smc/.sfc ROM files ready to play on any platform
- **Database**: Uses JSON format for hack metadata and progress tracking (cross-platform compatible)
- **Configuration**: Automatic migration system for seamless upgrades across platform switches

### Architecture
- **Windows**: PyInstaller executable with embedded Python runtime
- **macOS**: Native .app bundle with Universal binary support (Intel + Apple Silicon)
- **Linux**: Portable executable with GTK+ integration
- **Auto-Updater**: Platform-aware update system with format detection (.zip/.dmg/.tar.gz)

### Key Files
- **`config.json`**: Application configuration and settings (cross-platform)
- **`processed.json`**: Database of downloaded hacks and metadata (cross-platform)
- **`README.md`**: This documentation filemline your hack discovery and management with advanced filtering, bulk downloads, comprehensive analytics, and automatic updates.

**Now available on Windows, macOS, and Linux!**

![Dashboard](images/ss_app_dashboard_v4.3.png)

## 🖥️ Platform Support

| Platform | Status | Download Format | Notes |
|----------|--------|-----------------|-------|
| **Windows** | ✅ Fully Supported | `.zip` archive | Windows 10 (1903+) or Windows 11 |
| **macOS** | ✅ Fully Supported | `.dmg` installer | macOS 10.15+ (Catalina or newer) |
| **Linux** | ✅ Fully Supported | `.tar.gz` archive | Modern distributions with GTK support |

All platforms feature **identical functionality** including the auto-updater, which automatically detects your operating system and downloads the correct version.

## 📋 Table of Contents

- [Platform-Specific Setup](#-platform-specific-setup)
  - [Windows Setup](#windows-setup)
  - [macOS Setup](#macos-setup) 
  - [Linux Setup](#linux-setup)
- [First-Time Configuration](#-first-time-configuration)
- [Features](#-features)
- [File Organization](#-file-organization)
- [Technical Details](#-technical-details)
- [Changelog](#-changelog)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Platform-Specific Setup

### Windows Setup
1. **Download** `SMWC-Downloader-v4.4-Windows-x64.zip` from [releases](../../releases)
2. **Extract** all files to a folder of your choice (e.g., `C:\SMWCentral Downloader\`)
3. **Run** `SMWC Downloader.exe` to start the application
4. **Optional**: Run `defender_exclusion.bat` as Administrator to prevent Windows Defender false positives

> **Windows Defender Note**: PyInstaller executables may trigger antivirus warnings. This is a common false positive. Use the included exclusion script or manually add the folder to Windows Defender exclusions.

### macOS Setup
1. **Download** `SMWC-Downloader-v4.4-macOS-Universal.dmg` from [releases](../../releases)
2. **Open** the DMG file and drag `SMWC Downloader.app` to your Applications folder
3. **Launch** from Applications or Spotlight search
4. **First Launch**: Right-click → "Open" to bypass Gatekeeper (required once for unsigned apps)

> **Gatekeeper Note**: macOS may warn about an unidentified developer. This is normal for open-source software. Right-click the app and select "Open" to bypass this warning.

### Linux Setup
1. **Download** `SMWC-Downloader-v4.4-Linux-x64.tar.gz` from [releases](../../releases)
2. **Extract** the archive: `tar -xzf SMWC-Downloader-v4.4-Linux-x64.tar.gz`
3. **Make executable**: `chmod +x "SMWC Downloader"`
4. **Run** from terminal: `./SMWC\ Downloader` or double-click in file manager

> **Dependencies**: Most modern Linux distributions include the required GTK libraries. If you encounter missing dependencies, install `python3-tkinter` and `libgtk-3-0` through your package manager.

## ⚙️ First-Time Configuration

After launching the application on any platform:

### Step 1: Configure Paths
1. **Navigate to Settings** (click the Settings tab at the top)
2. **Set Base ROM Path**: 
   - Click "Browse" next to "Base ROM Path"
   - Select your clean Super Mario World ROM file (.smc or .sfc)
   - ⚠️ **Important**: Use an unmodified, original SMW ROM
3. **Set Output Directory**:
   - Click "Browse" next to "Output Directory" 
   - Choose where you want your patched hacks to be saved
   - The app will create organized folders automatically

### Step 2: Start Using
1. **Go to Download page** to search and download individual hacks
2. **Use Dashboard** to view your collection statistics
3. **Check History** to manage your downloaded hacks and add manual entries
4. **Explore Settings** for additional customization options

### Quick Tips
- 💡 Use filters on the Download page to find hacks by difficulty, type, or features
- 💡 **Click "▼ Search Criteria"** to collapse/expand search filters and get more results viewing space
- 💡 **Click "Add Hack"** in History to manually track hacks you've played elsewhere
- 💡 The app automatically organizes hacks into folders by type and difficulty
- 💡 Toggle between light/dark themes using the moon icon in the top navigation
- 💡 Use Ctrl+L (Windows/Linux) or Cmd+L (macOS) to quickly clear the log output
- 💡 The app automatically checks for updates and downloads the correct version for your platform
- 💡 Check Settings > "Check for Updates" to manually look for new versions

## 🎮 ROM & Emulator Compatibility

### Supported ROM Formats
- **Input ROM**: Clean Super Mario World ROM (.smc or .sfc format)
- **Output ROMs**: Patched .smc/.sfc files compatible with all major emulators
- **Region Support**: Works with NTSC (US), PAL (Europe), and Japanese ROM versions
- **File Validation**: Automatic ROM integrity checking before patching

### Recommended Emulators

#### Windows
- **SNES9X**: Excellent compatibility and performance
- **bsnes/higan**: Cycle-accurate emulation for purists  
- **RetroArch**: Multi-system emulator with advanced features
- **ZSNES**: Legacy emulator (not recommended for modern use)

#### macOS
- **SNES9X**: Native macOS version with good performance
- **OpenEmu**: Beautiful multi-system emulator frontend
- **RetroArch**: Cross-platform emulator with extensive features
- **bsnes**: Accurate emulation for demanding hacks

#### Linux
- **SNES9X-GTK**: Native Linux version with GTK interface
- **RetroArch**: Available in most distribution repositories
- **bsnes**: Compile from source or use flatpak
- **Mednafen**: Command-line emulator with high accuracy

### ROM Management Best Practices

#### Base ROM Requirements
1. **Use Original ROMs**: Must be clean, unmodified Super Mario World ROM
2. **Verify Checksums**: Ensure ROM integrity before first use
3. **Backup Originals**: Keep clean copies separate from patched versions
4. **Legal Compliance**: Only use ROMs you legally own

#### Patch Compatibility
- **IPS Patches**: Older format, widely supported, limited to 16MB ROMs
- **BPS Patches**: Modern format, supports larger ROMs, includes integrity checking
- **Mixed Collections**: App handles both formats automatically
- **Version Conflicts**: Some hacks require specific ROM versions (app will warn you)

#### File Organization Tips
```
Recommended Structure:
├── Base ROMs/
│   ├── Super Mario World (USA).smc
│   ├── Super Mario World (Europe).smc
│   └── Super Mario World (Japan).smc
├── Patched Hacks/    # (Your configured output directory)
│   ├── Standard/
│   ├── Kaizo/
│   └── ...
└── Emulator Saves/
    ├── Save States/
    ├── SRAM/
    └── Screenshots/
```

## 🎮 Comprehensive Usage Guide

### Keyboard Shortcuts
- **Ctrl+L** (Windows/Linux) or **Cmd+L** (macOS): Clear log output
- **Tab**: Navigate between UI elements
- **Enter**: Trigger default button actions (Download, Search, etc.)
- **Escape**: Cancel dialogs and close popups
- **F1**: Show help tooltip (where available)

### Advanced Download Features

#### Bulk Download Operations
1. **Select Multiple Hacks**: Use checkboxes to select multiple hacks for download
2. **Filter While Selecting**: Apply filters first, then select hacks from filtered results
3. **Download Progress**: Watch real-time progress for each hack being downloaded
4. **Cancel Anytime**: Stop downloads in progress without losing completed downloads

#### Smart Search & Filtering
- **Type Filter**: Standard, Kaizo, Puzzle, Tool-Assisted, Pit hacks
- **Difficulty Filter**: 8 levels from Newcomer to No Difficulty  
- **Feature Filter**: Music, Graphics, Boss, Power-ups, etc.
- **Author Filter**: Find hacks by specific creators
- **Name Search**: Search hack titles (supports partial matches)
- **Advanced Operators**: Use quotes for exact matches, minus sign (-) to exclude terms

#### Download Organization
```
Your Output Directory/
├── Standard/           # Traditional Mario-style hacks
│   ├── 01-Newcomer/    # Easiest difficulty
│   ├── 02-Intermediate/
│   ├── 03-Advanced/
│   └── ...up to 08-No Difficulty/
├── Kaizo/             # Precision-based challenge hacks
├── Puzzle/            # Logic and problem-solving hacks
├── Tool-Assisted/     # Hacks designed for TAS use
└── Pit/              # Multi-creator collaboration hacks
```

### Dashboard Analytics Deep Dive

#### Collection Statistics
- **Total Hacks**: Complete count of your downloaded collection
- **Type Distribution**: Visual breakdown by hack categories
- **Difficulty Analysis**: See your preferences across difficulty levels
- **Completion Tracking**: Track which hacks you've finished
- **Rating System**: Rate hacks and view your average ratings

#### Progress Indicators
- **Download Status**: View which hacks are downloaded vs tracked manually
- **Completion Progress**: Track your playthrough status
- **Recent Activity**: See your latest downloads and updates
- **Collection Growth**: Monitor how your collection expands over time

### History Management Mastery

#### Advanced Filtering & Sorting
- **Real-time Search**: Filter by hack name as you type
- **Column Sorting**: Click any column header to sort (click again to reverse)
- **Multi-criteria Filtering**: Combine search terms with difficulty and type filters
- **Obsolete Management**: Toggle to show/hide superseded hack versions
- **Export Options**: Export your collection data for backup or analysis

#### Manual Hack Management
1. **Add Custom Entries**: Track hacks you've played elsewhere
2. **Edit Details**: Update hack information, ratings, and completion status  
3. **Delete Entries**: Remove manually added hacks (original downloads are protected)
4. **Duplicate Prevention**: System warns if you try to add existing hacks
5. **Bulk Operations**: Select multiple entries for batch operations

### Settings & Customization

#### Performance Tuning
- **Download Concurrency**: Adjust how many hacks download simultaneously
- **API Rate Limiting**: Configure delays between SMWCentral API calls
- **Cache Management**: Control local data storage and cleanup
- **Threading Options**: Optimize for your system's capabilities

#### Interface Customization  
- **Theme Selection**: Choose between light and dark modes
- **Layout Options**: Adjust window sizes and panel arrangements
- **Accessibility**: Configure for screen readers and assistive technology
- **Language Settings**: Interface localization (where available)

#### Directory Management
- **Multiple Output Folders**: Set different directories for different hack types
- **Backup Locations**: Configure automatic backup destinations
- **ROM Path Validation**: Ensure your base ROM file is correct
- **Cleanup Tools**: Manage temporary files and obsolete downloads

### Cross-Platform Update System

#### Automatic Updates
1. **Background Checking**: App quietly checks for updates on startup
2. **Smart Detection**: Automatically detects your platform (Windows/macOS/Linux)
3. **User Notification**: Shows update dialog with release notes if new version available
4. **One-Click Install**: Download and install with a single button click
5. **Safe Process**: Creates backups and validates installation before committing
6. **Quick Restart**: App closes and reopens with new version (under 6 seconds)

#### Manual Update Management
- **Check Now**: Force immediate update check from Settings
- **Update History**: View log of all previous updates
- **Rollback Options**: Restore previous version if needed
- **Platform Details**: See technical information about your installation

### Troubleshooting & Diagnostics

#### Built-in Diagnostics
- **Log Viewer**: Real-time log output with filtering capabilities
- **System Info**: View platform and system information
- **Network Test**: Test connectivity to SMWCentral and GitHub
- **File Validation**: Check ROM files and patch integrity
- **Database Repair**: Fix corrupted hack database files

#### Performance Optimization
- **Memory Usage**: Monitor and optimize RAM consumption
- **Disk Cleanup**: Remove temporary files and old backups
- **Network Optimization**: Adjust settings for slow connections
- **UI Responsiveness**: Configure for better performance on older hardware

## ✨ Features

### 🔍 Advanced Hack Discovery
- **Individual Download Page**: Browse and filter through thousands of hacks with advanced search options
- **Smart Filtering**: Filter by difficulty, type, authors, completion status, and more
- **Collapsible Search Interface**: Toggle search criteria visibility to maximize results viewing space
- **Responsive Layout**: Search results area automatically expands when search criteria is collapsed
- **Comprehensive Search**: Button-triggered search with advanced filtering capabilities
- **Detailed Previews**: View hack information, screenshots, and ratings before downloading
- **Improved UI Layout**: Reorganized filter controls for better usability and workflow

![Download Page](images/ss_app_download_v4.3.png)

### 📥 Intelligent Download System
- **Bulk Downloads**: Select and download multiple hacks simultaneously
- **Smart Organization**: Automatically organizes hacks by type and difficulty
- **Multi-Type Support**: Handles Standard, Kaizo, Puzzle, Tool-Assisted, and Pit hacks
- **Cancellable Downloads**: Stop download operations at any time
- **Duplicate Detection**: Prevents downloading the same hack twice and automatically manages obsolete versions

### 📊 Comprehensive Analytics
- **Collection Overview**: Visual dashboard showing your hack statistics
- **Progress Tracking**: Track completion status and personal ratings
- **Type Distribution**: See your preferences across different hack categories
- **Advanced Metrics**: Detailed analytics about your gaming habits

### 🗂️ Powerful History Management
- **Complete History**: View all downloaded hacks with detailed information
- **Manual Entry**: Add hacks manually to track your progress without ROM files
- **Real-time Filtering**: Instant search results as you type in the name filter
- **Advanced Sorting**: Sort by any column with visual indicators
- **Inline Editing**: Edit hack details directly in the table
- **Full CRUD Support**: Create, read, update, and delete hack entries
- **Duplicate Prevention**: Smart duplicate detection with user confirmation
- **Bulk Operations**: Update multiple hacks at once
- **Export Options**: Export your collection data
- **Obsolete Filtering**: Filter to show/hide obsolete hack versions for better collection management

![Add Hack Dialog](images/ss_app_history_addhack_v4.3.png)

### ⚙️ Professional Configuration
- **Flexible Settings**: Configure base ROM paths, output directories, and preferences
- **Theme Support**: Switch between light and dark themes
- **Multi-Type Downloads**: Choose to download hacks to multiple type folders
- **Performance Options**: Adjust download delays and concurrent operations
- **Auto-Update System**: Automatically checks for and installs application updates

### 🔄 Cross-Platform Automatic Updates
- **Smart Platform Detection**: Automatically detects Windows, macOS, or Linux and downloads the correct update format
- **Background Checks**: Quietly checks for new versions when you start the app on any platform
- **One-Click Updates**: Download and install updates with a single click regardless of your operating system
- **Safe Installation**: 
  - **Windows**: Creates backups and safely replaces executable files
  - **macOS**: Automatically installs DMG to Applications folder with proper permissions
  - **Linux**: Extracts archives and sets executable permissions correctly
- **Fast Restarts**: Lightning-quick app restart process (under 6 seconds total) across all platforms
- **Update History**: View update logs in Settings for transparency

![Settings Page](images/ss_app_settings_v4.3.png)

## � File Organization

The application automatically organizes your hacks in a clean structure:

```
Output Directory/
├── Standard/
├── Kaizo/
├── Puzzle/
├── Tool-Assisted/
└── Pit/
    └── (Each type contains 8 difficulty folders: 01-Newcomer through 08-No Difficulty)
```

**All hack types** use difficulty-based subfolders for consistent organization.

## � Technical Details

### System Requirements

#### Windows
- **OS**: Windows 10 (version 1903+) or Windows 11
- **Architecture**: x64 (64-bit)
- **Memory**: 512 MB RAM minimum, 1 GB recommended
- **Storage**: ~25 MB for application + space for your hack collection
- **Network**: Internet connection for downloading hacks and updates
- **ROM**: Clean Super Mario World ROM file (.smc or .sfc format)

#### macOS  
- **OS**: macOS 10.15 (Catalina) or later
- **Architecture**: Universal Binary (Intel x64 & Apple Silicon ARM64)
- **Memory**: 512 MB RAM minimum, 1 GB recommended
- **Storage**: ~30 MB for application + space for your hack collection
- **Network**: Internet connection for downloading hacks and updates
- **ROM**: Clean Super Mario World ROM file (.smc or .sfc format)

#### Linux
- **OS**: Modern Linux distribution with GTK+ 3.0 support
- **Architecture**: x64 (64-bit)
- **Memory**: 512 MB RAM minimum, 1 GB recommended  
- **Storage**: ~35 MB for application + space for your hack collection
- **Dependencies**: `python3-tkinter`, `libgtk-3-0` (usually pre-installed)
- **Network**: Internet connection for downloading hacks and updates
- **ROM**: Clean Super Mario World ROM file (.smc or .sfc format)

### File Formats & Processing
- **Input**: Supports .zip files containing .ips or .bps patches from SMWCentral
- **Output**: Generates patched .smc/.sfc ROM files ready to play in any emulator
- **Database**: Uses JSON format for hack metadata and progress tracking
- **Configuration**: Automatic migration system for seamless upgrades between versions
- **Patches**: Full support for both IPS (legacy) and BPS (modern) patch formats
- **Compression**: Handles nested zip files and various compression methods

### Architecture & Components

#### Core Application (`main.py`)
- **Purpose**: Main GUI application with tabbed interface
- **Framework**: Python Tkinter with custom theming
- **Features**: Multi-threaded downloads, real-time progress tracking, cross-platform UI

#### API Pipeline (`api_pipeline.py`)
- **Purpose**: Interfaces with SMWCentral API for hack data retrieval
- **Features**: Rate limiting, retry logic, data caching, error handling
- **Performance**: Optimized for bulk operations and minimal API calls

#### Patch Handlers (`patcher_ips.py`, `patcher_bps.py`)
- **Purpose**: ROM patching engines for different patch formats
- **IPS Support**: Classic IPS format with truncation and expansion support
- **BPS Support**: Modern BPS format with integrity checking and delta compression
- **Safety**: Validates patch files and ROM integrity before applying

#### Configuration System (`config_manager.py`)
- **Purpose**: Centralized configuration and settings management
- **Features**: JSON-based storage, automatic migration, default value handling
- **Migration**: Seamlessly upgrades config format between application versions

#### Data Management (`hack_data_manager.py`)
- **Purpose**: Local database management for downloaded hacks
- **Features**: CRUD operations, duplicate detection, data integrity checking
- **Performance**: Optimized JSON operations with minimal file I/O

#### Auto-Updater (`updater.py`, `standalone_updater.py`)
- **Purpose**: Cross-platform automatic update system
- **Features**: Platform detection, safe installation, rollback capability
- **Formats**: Handles .zip (Windows), .dmg (macOS), .tar.gz (Linux) packages

### Key Application Files
- **`config.json`**: Application configuration and user preferences
- **`processed.json`**: Database of downloaded hacks with metadata and progress
- **`processed.json.backup`**: Automatic backup of hack database
- **`version.txt`**: Current application version for update checking
- **`README.md`**: Comprehensive documentation (this file)
- **`LICENSE`**: MIT license terms and conditions

### Development & Build System
- **Language**: Python 3.8+ with Tkinter GUI framework
- **Packaging**: PyInstaller for standalone executables across all platforms
- **Build System**: GitHub Actions CI/CD with automated cross-platform builds
- **Architecture**: 
  - **Windows**: x64 executable with embedded Python runtime
  - **macOS**: Universal2 binary supporting both Intel and Apple Silicon
  - **Linux**: x64 executable with GTK+ integration
- **Testing**: Comprehensive test suite covering all major components
- **Distribution**: Platform-specific packages (.zip, .dmg, .tar.gz) via GitHub Releases

### Security & Privacy
- **Data Storage**: All data stored locally - no cloud dependencies
- **Network Access**: Only connects to SMWCentral API and GitHub for updates
- **Privacy**: No user data collection, tracking, or analytics
- **Code Signing**: Open source codebase available for security review
- **Updates**: Cryptographically verified updates from GitHub Releases

## 📝 Changelog

### v4.4.0 - Cross-Platform Release *(Latest)*
- **New**: Full macOS support with native .app bundle and DMG installer
- **New**: Complete Linux support with GTK+ integration and tar.gz packaging
- **New**: Universal cross-platform auto-updater that detects your operating system
- **New**: GitHub Actions CI/CD pipeline for automated multi-platform builds
- **Enhanced**: Mouse wheel scrolling now works perfectly on all platforms
- **Enhanced**: Platform-specific UI optimizations and native look & feel
- **Enhanced**: Comprehensive Windows Defender exclusion script for false positive prevention
- **Improved**: Threading cleanup and error suppression for smoother shutdown across platforms
- **Improved**: Universal keyboard shortcuts (Ctrl/Cmd+L) that work natively on each platform
- **Fixed**: Dialog timing issues that caused visual artifacts during operations
- **Architecture**: Complete rewrite of updater system to handle .zip, .dmg, and .tar.gz formats
- **Documentation**: Comprehensive README update with platform-specific setup guides

### v4.3.0 - UI Polish & Obsolete Filter Release
- **New**: Obsolete Records filter in History page to show/hide superseded hack versions
- **Enhanced**: Download page layout improvements - search buttons repositioned for better workflow
- **Enhanced**: Select All/Deselect All button moved to right side for improved accessibility  
- **Improved**: Button positioning and user interface flow on Download page
- **Improved**: History page data loading to support obsolete record filtering

### v4.2.0 - Manual Hack Management Release
- **New**: Add Hack dialog for manually adding hacks to your history
- **New**: Edit manually added hacks with full CRUD operations
- **New**: Delete functionality for user-created hack entries (usr_ prefix)
- **New**: Duplicate title validation with user confirmation dialog
- **New**: Support for personal hack tracking without ROM files
- **Enhanced**: History page now supports both downloaded and manually added hacks
- **Enhanced**: Improved button spacing and layout in edit dialogs
- **Enhanced**: Better data integrity with proper difficulty capitalization
- **Fixed**: Dialog button order and spacing for consistent UX
- **Fixed**: Data loading issues when editing hacks

### v4.1.1 - UI Enhancement Release
- **New**: Collapsible search criteria section on Download page for better space utilization
- **Enhanced**: Responsive search results area that expands when filters are collapsed
- **Enhanced**: Improved button visibility and layout on smaller displays (laptops, netbooks)
- **Enhanced**: Better space management and user interface efficiency
- **Fixed**: Download & Patch button now always visible regardless of screen size
- **Optimized**: Simplified layout calculations for more reliable UI behavior

### v4.1.0 - Auto-Update Release
- **New**: Automatic update system with background checking
- **New**: One-click updates with safe installation process
- **New**: Lightning-fast restart mechanism (95% faster app closing)
- **New**: Update progress tracking and logging
- **Enhanced**: Settings page now includes update management
- **Enhanced**: Improved application startup and shutdown performance
- **Fixed**: Various stability improvements and optimizations

### v4.0.0 - Major Release
- **New**: Individual Download page with advanced filtering
- **New**: Comprehensive Dashboard with analytics
- **New**: Multi-type hack support system
- **Enhanced**: History page with inline editing
- **Enhanced**: Improved Settings with more options
- **Enhanced**: Modern UI with light/dark theme support
- **Fixed**: Numerous stability and performance improvements

## 🆘 Troubleshooting

### Platform-Specific Issues

#### Windows
**Antivirus/Windows Defender blocking the app?**
- Run the included `defender_exclusion.bat` script as Administrator
- Manually add the application folder to Windows Defender exclusions
- This is a common false positive with PyInstaller executables

**Application won't start?**
- Make sure you have the latest Windows updates
- Try running as administrator
- Verify you have Windows 10 (1903+) or Windows 11

#### macOS
**"Cannot open because it is from an unidentified developer"?**
- Right-click the app → Select "Open" → Click "Open" in the dialog
- This only needs to be done once for unsigned applications
- The app is safe but not code-signed (requires Apple Developer account)

**App won't launch from Applications?**
- Try launching from terminal: `open "/Applications/SMWC Downloader.app"`
- Check Console.app for any error messages
- Ensure you have macOS 10.15 (Catalina) or newer

#### Linux
**Missing dependencies?**
- Install required packages: `sudo apt install python3-tkinter libgtk-3-0` (Debian/Ubuntu)
- For other distributions, use equivalent packages through your package manager
- Ensure you have a modern GTK-based desktop environment

**Permission denied when running?**
- Make sure the executable has proper permissions: `chmod +x "SMWC Downloader"`
- Run from terminal to see any error messages: `./SMWC\ Downloader`

### Common Cross-Platform Issues

**Downloads not working?**
- Check your internet connection
- Verify the hack is still available on SMWCentral
- Make sure you have write permissions to the output directory
- Check firewall settings aren't blocking the application

**Patches failing?**
- Ensure your base ROM is a clean, unmodified Super Mario World ROM
- Check that you have enough disk space
- Verify the ROM file isn't corrupted
- Make sure the ROM file format is .smc or .sfc

**Updates not working?**
- Ensure you have internet connectivity
- Check that your antivirus/firewall isn't blocking the update process
- Try manually checking for updates from Settings
- Restart the application if update checks seem stuck
- On Linux, ensure the application directory has write permissions

### Cross-Platform Auto-Updater Details

The application includes a sophisticated update system that works identically across all platforms:

1. **Platform Detection**: Automatically detects Windows, macOS, or Linux
2. **Format Selection**: Downloads the appropriate format (.zip/.dmg/.tar.gz)
3. **Background Checking**: Quietly checks GitHub for new releases on startup
4. **User Notification**: Shows update dialog with release notes if new version found
5. **Safe Download & Installation**: 
   - **Windows**: Downloads .zip, extracts, and replaces executable with backup
   - **macOS**: Downloads .dmg, mounts it, and installs to Applications folder
   - **Linux**: Downloads .tar.gz, extracts, and replaces executable with proper permissions
6. **Quick Restart**: App closes and reopens with new version (5-6 seconds total)
7. **Automatic Cleanup**: Removes temporary files and manages backups

The updater is designed to be **completely safe** across all platforms - if anything goes wrong, your original version will be automatically restored.

### Getting Help
If you encounter platform-specific issues:
1. Check the application logs for error messages
2. Try restarting the application
3. Verify your platform meets the minimum requirements
4. For Linux: Run from terminal to see detailed error output
5. For macOS: Check Console.app for system-level error messages
6. For Windows: Check Event Viewer for application errors
7. Create an issue on the GitHub repository with platform details and error logs

## ❓ Frequently Asked Questions

### General Usage

**Q: Can I use this app with ROM hacks from other sites?**
A: No, this app is specifically designed for SMWCentral hacks. It uses SMWCentral's API and expects their specific file formats and metadata.

**Q: Do I need to keep the app running while playing hacks?**
A: No, once hacks are downloaded and patched, the ROM files are completely independent. You can close the app and play hacks in any emulator.

**Q: Can I move my patched ROMs to other devices?**
A: Yes! The patched .smc/.sfc files work on any device with a compatible SNES emulator, including mobile devices, handheld consoles, and other computers.

**Q: What happens if I delete a patched ROM file?**
A: You can re-download and re-patch any hack from your History page. The app remembers what you've downloaded and can recreate the files.

### Technical Questions

**Q: Why does the app need internet access?**
A: Internet access is required to:
- Download hack data from SMWCentral's API
- Download patch files (.zip archives)
- Check for application updates
- No personal data is transmitted

**Q: How much disk space will my collection use?**
A: Each patched hack is typically 1-4 MB. A collection of 100 hacks uses about 200-400 MB. The app itself is under 50 MB on all platforms.

**Q: Can I backup my collection and settings?**
A: Yes! Your entire collection data is stored in `processed.json` and settings in `config.json`. Copy these files to backup your progress and configuration.

**Q: Does the app work offline?**
A: Partially. You can:
- Browse your downloaded collection
- Play previously patched hacks
- Manage history and settings
- But you cannot download new hacks or check for updates without internet

### Platform-Specific Questions

**Q: Why does Windows Defender flag the app as suspicious?**
A: This is a common false positive with PyInstaller executables. The app is completely safe - it's open source and builds are automated through GitHub Actions. Use the included `defender_exclusion.bat` script to resolve this.

**Q: Why can't I open the app on macOS?**
A: macOS blocks unsigned applications by default. Right-click the app and select "Open" to bypass this security feature. This only needs to be done once.

**Q: Why is the Linux version larger than Windows/macOS?**
A: The Linux version includes additional libraries for GTK+ compatibility across different distributions, making it more portable but slightly larger.

**Q: Can I run multiple instances of the app?**
A: No, the app uses file locking to prevent database corruption. Only one instance can run at a time.

### Troubleshooting

**Q: Downloads keep failing - what should I check?**
A: Common causes:
- Internet connectivity issues
- Firewall blocking the application
- Insufficient disk space
- Write permissions to output directory
- SMWCentral server temporarily unavailable

**Q: The app crashes when patching ROMs - how do I fix this?**
A: Usually caused by:
- Corrupted or wrong ROM file
- Insufficient disk space
- Antivirus software interfering
- Corrupted patch file (try re-downloading the hack)

**Q: My hack collection disappeared - how do I recover it?**
A: Check for:
- `processed.json.backup` file in the app directory
- Your configured output directory (ROM files should still be there)
- Recent backups of the application folder
- The app creates automatic backups before major operations

**Q: Can I use different base ROMs for different hacks?**
A: Currently, the app uses one configured base ROM for all patches. Most hacks work with the standard US Super Mario World ROM, but some may require specific versions.

### Advanced Usage

**Q: Can I modify the app's behavior or add features?**
A: Yes! The app is open source (MIT license). You can:
- Modify the source code for personal use
- Submit feature requests on GitHub
- Contribute improvements to the project
- Fork the project for custom versions

**Q: How does the auto-updater work across platforms?**
A: The updater:
- Detects your platform automatically
- Downloads the correct package format (.zip/.dmg/.tar.gz)
- Installs using platform-native methods
- Creates backups and handles rollbacks if needed
- Works identically on Windows, macOS, and Linux

**Q: Can I use the app for ROM hacking development?**
A: The app is designed for playing hacks, not creating them. For ROM hacking development, you'll want:
- Lunar Magic (level editor)
- AddmusicK (music insertion)
- PIXI (sprite tool)
- GPS (block tool)
- Various other specialized tools

## 🔧 For Developers

### Building from Source

#### Prerequisites
- Python 3.8 or later
- pip (Python package manager)
- Git (for cloning the repository)

#### Setup Process
```bash
# Clone the repository
git clone https://github.com/your-username/smwc-downloader.git
cd smwc-downloader

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

#### Building Executables
```bash
# Windows
pyinstaller "SMWC Downloader.spec"

# macOS  
pyinstaller "SMWC Downloader macOS.spec"

# Linux
pyinstaller "SMWC Downloader.spec"
```

#### Testing
```bash
# Run test suite
python -m pytest tests/

# Run specific test
python tests/test_specific_feature.py
```

### Project Structure
```
smwc-downloader/
├── main.py              # Main application entry point
├── ui/                  # User interface components
│   ├── components.py    # Reusable UI elements
│   ├── pages/          # Individual page implementations
│   └── components/     # Specialized components
├── api_pipeline.py      # SMWCentral API interface
├── patch_handler.py     # ROM patching logic
├── config_manager.py    # Configuration management
├── hack_data_manager.py # Local database operations
├── updater.py          # Auto-update system
└── tests/              # Test suite
```

### Contributing Guidelines
1. **Fork the repository** on GitHub
2. **Create a feature branch** for your changes
3. **Write tests** for new functionality
4. **Follow the existing code style** and conventions
5. **Test on multiple platforms** if possible
6. **Submit a pull request** with detailed description

### API Reference
The app uses SMWCentral's public API. Key endpoints:
- `/api/v1/hacks` - Hack listing and search
- `/api/v1/hack/{id}` - Individual hack details
- Rate limits apply - the app handles these automatically

## 🤝 Contributing

This project welcomes contributions! Whether it's bug reports, feature requests, or code contributions, your help makes this tool better for everyone.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**What this means:**
- ✅ **Free to use** - Download and use the software for any purpose
- ✅ **Free to modify** - Change the code to suit your needs  
- ✅ **Free to distribute** - Share copies with others
- ✅ **Commercial use allowed** - Use in commercial projects
- ✅ **Open source** - Source code is available for inspection and contribution

The only requirement is to include the original copyright notice in any copies or substantial portions of the software.

---

**Version**: 4.4.0  
**Last Updated**: July 2025  
**Platforms**: Windows 10/11, macOS 10.15+, Linux (GTK)  
**Cross-Platform**: Full feature parity across all supported operating systems