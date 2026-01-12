# Release Notes - v4.9.0

## Summary
Version 4.9 brings major improvements to collection management with customizable columns, supercharged metadata fetching, and a polished UI with consistent theming.

## Highlights

### 🎨 Customizable Collection View
- Drag-and-drop column reordering with visual feedback
- Show/hide individual columns
- Reset to default layout anytime
- Preferences saved automatically

### ⚡ Fetch Metadata - 60-100x Faster
- Bulk API optimization: ~30 seconds instead of 30+ minutes
- Fallback lookups for obsolete/unlisted hacks
- Cancellable operation (safe to cancel during fetch)
- Checks both moderated and waiting sections

### 🎨 Consistent UI Theming
- Readable status colors (light cyan for in-progress messages)
- Centralized color constants
- Better contrast on dark backgrounds

### 🔒 Data Protection
- Collection page locks during background operations
- Prevents editing conflicts and data corruption
- Clear status messages show what's happening

## Full Feature List

### Added
- Column configuration with drag-and-drop reordering
- Visual drag feedback (floating label)
- Fetch Metadata with bulk API optimization
- Fallback individual API lookups for obsolete hacks
- Cancellable Fetch Metadata operation
- UI color theme constants (STATUS_COLOR_*)
- Collection page locking system
- Warnings for hacks not found in API

### Changed
- Simplified log messages (removed debug paths)
- Shortened migration status messages
- Data Migration section text wrapping (380px)
- Metadata fetch dialog updated with optimization info

### Fixed
- TclError crashes during column drag-and-drop
- Reset to Default button not working
- Duplicate "Reloaded X hacks" logging
- Obsolete hacks not getting metadata updates
- Widget destruction errors during rebuild

## Upgrade Notes

### From v4.8
- No migration required
- All existing features and data preserved
- Column configuration starts with default layout
- Fetch Metadata will detect and update missing dates

### Breaking Changes
None - fully backward compatible

## Files Updated
- `version.txt` - Version metadata
- `main.py` - VERSION constant
- `SMWC Downloader macOS.spec` - macOS build version
- `SMWC Updater macOS.spec` - Updater build version
- `CHANGELOG.md` - Full v4.9 changelog
- `README.md` - Feature documentation
- `ui_constants.py` - Color theme constants
- `ui/components/column_config_dialog.py` - New component
- `ui/pages/collection_page.py` - Column configuration integration
- `ui/pages/settings_page.py` - Fetch Metadata with cancellation
- `api_pipeline.py` - Bulk fetch + fallback lookups
- `config_manager.py` - Column preferences
- `hack_data_manager.py` - Simplified logging

## Testing Checklist
- [ ] Column drag-and-drop works without errors
- [ ] Reset to Default restores original layout
- [ ] Column visibility toggles persist across restarts
- [ ] Fetch Metadata completes in under 1 minute
- [ ] Obsolete hacks get individual API lookups
- [ ] Cancel button works during API fetch phase
- [ ] Collection locks/unlocks properly during operations
- [ ] Status colors are readable on dark backgrounds
- [ ] No duplicate logging on Refresh List
- [ ] All migrations (v4.8) still work correctly

## Known Issues
None currently

## Contributors
- @iamtheratio - All features and fixes

---

**Release Date:** January 12, 2026
**Build:** 4.9.0
