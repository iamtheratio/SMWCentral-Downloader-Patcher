# Multi-Type Support Implementation Plan

## Phase 1: Data Migration (v4.1)

### 1.1 Migration Manager Updates
- Add `migrate_to_multi_type_support()` method
- Convert `hack_type` (string) → `hack_types` (array) 
- Preserve existing data structure as fallback
- Version the migration as v4.1

### 1.2 Data Structure Changes
```json
// OLD FORMAT (v4.0 and earlier)
{
  "hack_id": {
    "hack_type": "kaizo",  // Single string
    ...
  }
}

// NEW FORMAT (v4.1+)
{
  "hack_id": {
    "hack_types": ["kaizo", "tool_assisted"],  // Array
    "hack_type": "kaizo",  // Kept for backward compatibility
    ...
  }
}
```

## Phase 2: Core Logic Updates

### 2.1 Download Logic Changes
- Update `run_single_download_pipeline()` and `run_pipeline()` 
- Support multiple folder creation
- Add user preference for multi-folder behavior:
  - "Primary Type Only" (current behavior)
  - "Copy to All Types" (duplicate files)
  - "Primary + Shortcuts" (symlinks/shortcuts to other folders)

### 2.2 Folder Structure
```
Output/
├── Standard/
│   ├── 01 - Newcomer/
│   └── SuperHack.smc
├── Kaizo/
│   ├── 01 - Newcomer/
│   └── SuperHack.smc (copy or shortcut)
└── Tool-Assisted/
    ├── 01 - Newcomer/
    └── SuperHack.smc (copy or shortcut)
```

## Phase 3: UI/Display Updates

### 3.1 History Page
- Update type filtering to handle arrays
- Update display logic (already done for download page)
- Update sorting/grouping by type

### 3.2 Dashboard 
- Update analytics to count multi-type hacks correctly
- Update charts and statistics

### 3.3 Settings Page
- Add user preference for multi-type download behavior
- Update bulk download configuration

## Phase 4: Utility Functions

### 4.1 Helper Functions
- `get_hack_types(hack_data)` - returns array of types
- `get_primary_type(hack_data)` - returns primary type
- `normalize_types(types_array)` - normalizes type strings
- `make_output_paths(output_dir, types_array, difficulty)` - creates multiple paths

### 4.2 Migration Utilities
- `convert_single_to_multi_type(hack_data)` - converts old format
- `ensure_backward_compatibility(hack_data)` - ensures both formats exist

## Implementation Priority

1. **High Priority** (Breaking changes):
   - Data migration (migration_manager.py)
   - Download logic (main.py, api_pipeline.py)
   - Core utilities (utils.py)

2. **Medium Priority** (Feature gaps):
   - History page updates
   - Dashboard analytics updates
   - Settings preferences

3. **Low Priority** (Polish):
   - Advanced multi-folder options
   - User interface refinements
   - Performance optimizations

## Backward Compatibility Strategy

- Keep both `hack_type` (string) and `hack_types` (array) in data
- Prioritize `hack_types` if available, fallback to `hack_type`
- Gradual migration - no forced breaking changes
- Support reading old format indefinitely

## User Experience

1. **Migration Dialog**: Inform users about multi-type support
2. **Settings Option**: Let users choose multi-folder behavior  
3. **Progress Feedback**: Show when creating multiple copies
4. **Clear Indicators**: Show in UI when hack has multiple types
