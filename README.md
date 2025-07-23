# SMWC Downloader & Patcher

🎮 **Download and play Super Mario World ROM hacks with one click**

A simple desktop app that automatically downloads, patches, and organizes ROM hacks from SMWCentral. Works on Windows, Mac, and Linux.

![App Screenshot](images/ss_app_dashboard_v4.3.png)

## 🎯 App Features

### Browse & Download
![Download View](images/ss_app_download_v4.3.png)

### Manage Your Collection
![History View](images/ss_app_history_v4.3.png)

### Customize Settings
![Settings View](images/ss_app_settings_v4.3.png)

## 📥 Download & Install

### Windows (10/11)
1. Download `SMWC-Downloader-Windows-x64.zip`
2. Extract the ZIP file anywhere you want
3. Double-click `SMWC Downloader.exe`
4. **If Windows blocks it**: Right-click → Properties → Unblock, or run the included `defender_exclusion.bat` as Administrator

### Mac (macOS 10.15+)
1. Download `SMWC-Downloader-macOS-Universal.dmg`
2. Open the DMG and drag the app to Applications
3. **First time**: Right-click the app → Open (to bypass security warning)

### Linux (Ubuntu, Debian, Fedora, etc.)
1. Download `SMWC-Downloader-Linux-x64.tar.gz`
2. Extract: `tar -xzf SMWC-Downloader-*.tar.gz`
3. Run the installer: `./install.sh`
4. Launch from Applications menu or run `smwc-downloader` in terminal

## 🚀 Quick Start

1. **First Launch**: The app will ask you to choose where to save your ROM hacks
2. **Add your SMW ROM**: Click "Browse" and select your clean Super Mario World ROM file
3. **Start Downloading**: Browse hacks, click "Download" on any hack you want to try
4. **Play**: The app automatically patches the ROM - just open the generated file in your emulator

## ✨ What It Does

- **Browse SMWCentral**: View all available ROM hacks with screenshots and descriptions
- **One-Click Downloads**: Automatically downloads, extracts, and patches ROM files
- **Smart Organization**: Keeps your hack collection organized by author, type, and rating
- **Auto-Updates**: Keeps the app updated with new features and bug fixes
- **Cross-Platform**: Same features on Windows, Mac, and Linux

## 🛠️ Troubleshooting

### Windows: "Windows protected your PC"
This is normal for new apps. Click "More info" → "Run anyway", or run the `defender_exclusion.bat` file as Administrator.

### Mac: "Cannot open because it is from an unidentified developer"
Right-click the app → "Open" → "Open" again. You only need to do this once.

### Linux: Missing dependencies
Install required packages:
- **Ubuntu/Debian**: `sudo apt install python3-tk`
- **Fedora**: `sudo dnf install tkinter`

### Can't find downloaded ROMs
Check the download folder you selected in Settings. By default, ROMs are saved to a "SMWCentral Hacks" folder on your desktop.

## 📝 System Requirements

- **Windows**: Windows 10 (version 1903 or newer) or Windows 11
- **Mac**: macOS 10.15 (Catalina) or newer - works on Intel and Apple Silicon
- **Linux**: Any modern distribution with desktop environment
- **Storage**: 20 MB for the app + space for your ROM collection
- **Internet**: Required for downloading hacks and app updates

## 🔄 Updates

The app automatically checks for updates and will notify you when a new version is available. Updates preserve all your settings and downloaded hacks.

## 📄 License

This project is open source under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Made for the Super Mario World ROM hacking community** ❤️