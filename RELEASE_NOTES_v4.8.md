# Release Notes - Version 4.8.0

## 🎉 What's New

### 📁 Folder Icon Feature
The biggest addition in v4.8 is the new **folder icon feature** that makes managing your ROM hack collection much easier!

#### What It Does
- **Quick File Access**: Click the 📁 folder icon next to any hack name in your collection to instantly open its file location
- **Cross-Platform Support**: Works on Windows (Explorer), macOS (Finder), and Linux (various file managers)
- **Smart Navigation**: Automatically highlights the specific hack file in your file manager

#### How to Use
1. Go to the **Collection** tab
2. Look for the 📁 folder icon in the new column (left of the hack name)
3. Click any folder icon to open that hack's file location in your system's file manager
4. The file will be highlighted/selected automatically (when supported)

### 🔧 Technical Improvements
- **Enhanced Error Handling**: Better error messages when files can't be found
- **Graceful Fallbacks**: If file highlighting doesn't work, it opens the containing folder instead
- **Cross-Platform Reliability**: Comprehensive support for different operating systems and file managers

## 🐛 Bug Fixes
- Improved file path handling across different operating systems
- Better error recovery when file managers can't be opened
- Enhanced Unicode support for folder icons

## 📋 Files Changed
- **NEW**: `file_explorer_utils.py` - Cross-platform file explorer integration
- **UPDATED**: Collection page UI with folder icon column
- **UPDATED**: Hack data manager to include file paths
- **UPDATED**: Version numbers across all files

## 🎯 For Users
This update makes it **much easier to find and manage your downloaded ROM hacks**. No more manually browsing folders to find specific hack files - just click the folder icon and you're there!

## 🛠️ For Developers
The new folder icon feature demonstrates:
- Cross-platform subprocess handling
- Unicode emoji support with ASCII fallbacks  
- Graceful error handling and user feedback
- Clean separation of UI and utility logic

---

**Download Link**: [Releases Page](../../releases)
**Installation**: Same as previous versions - just extract and run
**Compatibility**: Windows 10/11, macOS 10.15+, Linux (most distributions)