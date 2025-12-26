# Changelog

All notable changes to SMWC Downloader & Patcher will be documented in this file.

## [4.8] - 2025-12-26

### Added
- **Difficulty Migration System**: Automatic detection and migration of SMWC difficulty category renames
  - Auto-detects when difficulty names have changed (e.g., "Skilled" → "Intermediate")
  - Migration UI in Settings page with check/apply buttons
  - Shows affected hack counts before applying changes
  - Creates automatic backups before making any changes
  - Zero configuration needed - fully data-driven detection
- **Difficulty ID Tracking**: Store raw difficulty IDs for reliable rename detection
  - Enables automatic detection of future SMWC difficulty renames
  - Backward compatible with existing data

### Changed
- Updated difficulty category from "Skilled" to "Intermediate" to match SMWC
- All UI components now use "Intermediate" instead of "Skilled"
- Updated difficulty lists in download page, filters, charts, and data manager

### Technical
- New `difficulty_migration.py` module for handling migrations
- Added `difficulty_id` field to processed hack data
- Comprehensive migration documentation in DIFFICULTY_MIGRATION_README.md
- Migration system compares stored difficulty_id vs current DIFFICULTY_LOOKUP
- Backward compatibility maintained with "skilled" search term

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
