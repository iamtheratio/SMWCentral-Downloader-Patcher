# Changelog

All notable changes to SMWC Downloader & Patcher will be documented in this file.

## [4.8.0] - 2025-10-31

### Added
- **🎮 QUSB2SNES Sync Feature**: Complete SD2SNES/FXPAK Pro integration for one-click ROM transfers
  - Smart incremental sync (only uploads new/changed files)
  - **🗑️ Automatic cleanup**: Optional removal of deleted ROMs from SD card during sync
  - Organized folder structure maintenance on SD card
  - Real-time progress tracking with automatic retry logic
  - Easy setup with host/port/device configuration in Settings
  - WebSocket communication with connection resilience
  - Automatic device detection and conflict resolution
  - **Persistent checkbox settings**: "Remove deleted files" option saves between sessions
- **📁 Folder Icon Feature**: Clickable folder icons in collection to open hack file locations
- **Cross-Platform File Explorer Integration**: Support for Windows Explorer, macOS Finder, and Linux file managers
- **Smart File Navigation**: Automatically highlights specific files in the system file manager
- **QUSB2SNES Settings Panel**: Dedicated configuration section with persistent settings
- **Connection Management**: Connect/disconnect controls with device status feedback

### Improved
- **Enhanced User Experience**: One-click ROM sync eliminates manual file copying for SD2SNES users
- **Optimized File Transfer**: Tree-based sync algorithm for maximum efficiency (99%+ improvement)
- **Better Error Recovery**: Improved handling of device conflicts and connection timeouts
- **Cross-Platform Reliability**: Comprehensive support for multiple operating systems and file managers
- **Settings Persistence**: All QUSB2SNES settings automatically save and restore

### Technical
- **New Module**: `qusb2snes_sync.py` - Complete QUSB2SNES WebSocket protocol implementation
- **New Module**: `qusb2snes_ui.py` - Settings UI integration with connection management
- **Enhanced Config**: Added QUSB2SNES settings with default values (host: localhost, port: 8080)
- **File Explorer Utils**: `file_explorer_utils.py` for cross-platform file manager integration
- **Updated Settings Page**: Integrated QUSB2SNES configuration panel with optimized layout
- **Timestamp Tracking**: Smart incremental sync with last-sync timestamp persistence

### Fixed
- Connection timeouts during large file transfers
- Error recovery when QUSB2SNES device is in use by other applications
- Better handling of special characters in ROM file names
- Enhanced Unicode support for international file names

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
