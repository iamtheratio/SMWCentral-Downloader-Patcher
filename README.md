# SMWCentral Downloader & Patcher v4.0

A powerful desktop application for downloading, organizing, and patching Super Mario World ROM hacks from SMWCentral. Streamline your hack discovery and management with advanced filtering, bulk downloads, and comprehensive analytics.

![Dashboard](images/ss_app_dashboard_v4.0.png)

## 📋 Table of Contents

- [User Setup Guide](#-user-setup-guide)
- [Features](#-features)
- [File Organization](#-file-organization)
- [Technical Details](#-technical-details)
- [Changelog](#-changelog)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 User Setup Guide

### Step 1: Download & Install
1. **Download** the latest release from the [releases page](../../releases)
2. **Extract** all files to a folder of your choice (e.g., `C:\SMWCentral Downloader\`)
3. **Run** `SMWC Downloader.exe` to start the application

### Step 2: First-Time Configuration
1. **Navigate to Settings** (click the Settings tab at the top)
2. **Set Base ROM Path**: 
   - Click "Browse" next to "Base ROM Path"
   - Select your clean Super Mario World ROM file (.smc or .sfc)
   - ⚠️ **Important**: Use an unmodified, original SMW ROM
3. **Set Output Directory**:
   - Click "Browse" next to "Output Directory" 
   - Choose where you want your patched hacks to be saved
   - The app will create organized folders automatically

### Step 3: Start Using
1. **Go to Download page** to search and download individual hacks
2. **Use Dashboard** to view your collection statistics
3. **Check History** to manage your downloaded hacks
4. **Explore Settings** for additional customization options

### Quick Tips
- 💡 Use filters on the Download page to find hacks by difficulty, type, or features
- 💡 The app automatically organizes hacks into folders by type and difficulty
- 💡 Toggle between light/dark themes using the moon icon in the top navigation
- 💡 Use Ctrl+L to quickly clear the log output

## ✨ Features

### 🔍 Advanced Hack Discovery
- **Individual Download Page**: Browse and filter through thousands of hacks with advanced search options
- **Smart Filtering**: Filter by difficulty, type, authors, completion status, and more
- **Comprehensive Search**: Button-triggered search with advanced filtering capabilities
- **Detailed Previews**: View hack information, screenshots, and ratings before downloading

![Download Page](images/ss_app_download_v4.0.png)

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
- **Real-time Filtering**: Instant search results as you type in the name filter
- **Advanced Sorting**: Sort by any column with visual indicators
- **Inline Editing**: Edit hack details directly in the table
- **Bulk Operations**: Update multiple hacks at once
- **Export Options**: Export your collection data

![History Page](images/ss_app_history_v4.0.png)

### ⚙️ Professional Configuration
- **Flexible Settings**: Configure base ROM paths, output directories, and preferences
- **Theme Support**: Switch between light and dark themes
- **Multi-Type Downloads**: Choose to download hacks to multiple type folders
- **Performance Options**: Adjust download delays and concurrent operations

![Settings Page](images/ss_app_settings_v4.0.png)

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

### Requirements
- **OS**: Windows 10 or later
- **Storage**: ~20 MB for application + space for your hack collection
- **Network**: Internet connection for downloading hacks
- **ROM**: Clean Super Mario World ROM file

### File Formats
- **Input**: Supports .zip files containing .ips or .bps patches from SMWCentral
- **Output**: Generates patched .smc/.sfc ROM files ready to play
- **Database**: Uses JSON format for hack metadata and progress tracking
- **Configuration**: Automatic migration system for seamless upgrades

### Key Files
- **`config.json`**: Application configuration and settings
- **`processed.json`**: Database of downloaded hacks and metadata
- **`README.md`**: This documentation file

## 📝 Changelog

### v4.0.0 - Major Release
- **New**: Individual Download page with advanced filtering
- **New**: Comprehensive Dashboard with analytics
- **New**: Multi-type hack support system
- **Enhanced**: History page with inline editing
- **Enhanced**: Improved Settings with more options
- **Enhanced**: Modern UI with light/dark theme support
- **Fixed**: Numerous stability and performance improvements

## 🆘 Troubleshooting

### Common Issues

**Downloads not working?**
- Check your internet connection
- Verify the hack is still available on SMWCentral
- Make sure you have write permissions to the output directory

**Patches failing?**
- Ensure your base ROM is a clean, unmodified Super Mario World ROM
- Check that you have enough disk space
- Verify the ROM file isn't corrupted

**Application won't start?**
- Make sure you have the latest Windows updates
- Try running as administrator
- Check that your antivirus isn't blocking the application

### Getting Help
If you encounter issues:
1. Check the application logs for error messages
2. Try restarting the application
3. Verify your configuration settings
4. Create an issue on the GitHub repository with details

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

**Version**: 4.0.0  
**Last Updated**: July 2025  
**Platforms**: Windows 10/11