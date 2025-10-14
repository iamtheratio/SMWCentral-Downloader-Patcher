# Changelog

All notable changes to SMWC Downloader & Patcher will be documented in this file.

## [4.8.0] - 2025-10-14

### Added
- **📁 Folder Icon Feature**: Clickable folder icons in collection search results to open hack file locations
- **Cross-Platform File Explorer Integration**: Support for Windows Explorer, macOS Finder, and Linux file managers
- **Smart File Navigation**: Automatically highlights specific files in the system file manager
- **Unicode Folder Icons**: Beautiful folder emoji icons with ASCII fallback for compatibility
- **Comprehensive Error Handling**: Graceful fallbacks when file managers can't be opened
- **Multi-Platform File Manager Support**: Support for nautilus, dolphin, thunar, nemo, pcmanfm, caja on Linux

### Improved
- **Enhanced User Experience**: Quick access to hack file locations without manual navigation
- **Cross-Platform Reliability**: Robust error handling and fallback mechanisms for all operating systems
- **File Management**: Clear error messages when files are missing or haven't been downloaded

### Technical
- **New Module**: `file_explorer_utils.py` for cross-platform file manager integration
- **Updated Collection UI**: Modified collection page to include folder column with click handling
- **Data Layer Enhancement**: Updated hack data manager to include file path information

## [4.7.0] - 2025-10-13

### Improved
- Enhanced cross-platform compatibility
- Improved UI responsiveness and scrolling
- Better error handling and stability
- Threading cleanup improvements
- Download completion messaging
- Obsolete records filtering

### Fixed
- Fixed threading cleanup errors during shutdown
- Improved font consistency across themes
- Better navigation update handling

### Changed
- Updated version to v4.4
- Streamlined GitHub Actions workflows

## [4.3] - Previous Release

### Added
- Previous features...

### Fixed
- Previous fixes...
