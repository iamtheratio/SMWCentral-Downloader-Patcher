# Changelog

All notable changes to SMWC Downloader & Patcher will be documented in this file.

## [Unreleased]

## [4.8] - 2025-12-29

### Added
- **Emulator Integration**: Launch ROMs directly from the Collection page with one click
  - Configure any emulator (RetroArch, Snes9x, bsnes, etc.) in Settings
  - Custom command-line arguments with `%1` placeholder support for ROM file path
  - Cross-platform support: Windows, macOS (.app bundles), and Linux
  - Play icon (▶) appears next to downloaded hacks when emulator is configured
  - Quick launch functionality integrated into Collection page interface
- **macOS .app Bundle Support**: Automatic conversion of `.app` bundles to executable paths
  - Select `Snes9x.app` and the app automatically finds `Snes9x.app/Contents/MacOS/Snes9x`
  - Works with all standard macOS application bundles
  - Seamless integration with macOS application structure
- **Live Difficulty Mapping from SMWC API**: Automatically fetches current difficulty categories from SMWC on app startup
  - Difficulty mappings cached in config.json for offline use
  - Ensures app always uses latest SMWC difficulty names without code updates
  - Falls back to hardcoded defaults if API unavailable
- **Difficulty Migration System**: Automatic detection and migration of SMWC difficulty category renames
  - Auto-detects when difficulty names have changed by comparing against live SMWC data
  - Migration UI in Settings page with check/apply buttons
  - Shows affected hack counts before applying changes
  - Automatically renames difficulty folders and updates file paths
  - Creates automatic backups before making any changes
  - Zero configuration needed - fully data-driven detection
- **Difficulty ID Tracking**: Store raw difficulty IDs (`diff_1`, `diff_2`, etc.) for reliable rename detection
  - Enables automatic detection of future SMWC difficulty renames
  - Backward compatible with existing data via automatic v4.8 migration
- **Automatic v4.8 Migration**: Seamless upgrade from v4.7
  - Automatically adds `current_difficulty` and `difficulty_id` fields to existing hacks
  - Silent migration on first launch - no user intervention needed
  - Creates backup at `processed.json.pre-v4.8.backup`

### Changed
- **Settings Page Layout**: Optimized layout with Emulator and Difficulty Migration sections side-by-side for better space utilization
- **Enhanced log section**: More vertical space for better readability
- **Improved cross-platform emulator path handling**: Better detection and handling of different emulator formats
- **Difficulty Data Model Consolidation**:
  - Removed redundant `difficulty` field
  - Now uses only `difficulty_id` (source) and `current_difficulty` (display)
  - Collection page and filters updated to use new field structure
- Updated difficulty category from "Skilled" to "Intermediate" to match SMWC
- All UI components now use "Intermediate" instead of "Skilled"
- Updated difficulty lists in download page, filters, charts, and data manager
- Difficulty mappings now fetched from SMWC API instead of hardcoded

### Fixed
- **macOS/Linux Difficulty Migration Fix**: Fixed difficulty migration not working on macOS and Linux
  - DifficultyMigrator now uses platform-specific processed.json path by default
  - Windows stores processed.json next to executable (portable mode)
  - macOS stores in ~/Library/Application Support/SMWC Downloader/
  - Linux stores in ~/.smwc-downloader/
  - Added difficulty_migration and difficulty_lookup_manager to PyInstaller hiddenimports
- Collection page Type filter now correctly finds multi-type hacks (e.g., searching "Puzzle" finds "Standard, Puzzle")
- Collection page difficulty filter now works correctly with new data model
- Removed obsolete difficulty field sync that was causing false migration warnings

### Technical
- New `difficulty_lookup_manager.py` module for fetching difficulty mappings from SMWC API
- Enhanced `difficulty_migration.py` with backfill and API-based detection
- New `migrate_to_v48()` function in `migration_manager.py` for automatic upgrades
- `ConfigManager` extended to store and retrieve difficulty lookup cache
- Global `DIFFICULTY_LOOKUP` in utils.py updated on app startup with live data
- `hack_data_manager.get_all_hacks()` transforms data for UI consumption
- Comprehensive migration documentation in DIFFICULTY_MIGRATION_README.md
- Migration system compares stored difficulty_id vs live SMWC API data
- Backward compatibility maintained with "skilled" search term
- Type filter uses containment check for multi-type hack support

## [4.7] - 2025-01-XX

### Added
- Enhanced download selection and filter controls
- Improved layout and responsiveness of UI components

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
