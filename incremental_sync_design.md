# Incremental QUSB2SNES Sync Design

## Problem
- Large ROM collections (1k-2k files) take a long time to sync
- If sync fails halfway through, it restarts completely from scratch
- No way to resume from where it left off

## Solution: Directory-Level Progress Tracking

### 1. Enhanced Config Schema
Add new fields to track sync progress:
```json
{
  "qusb2snes_last_sync": 1699012345,           // Global last successful sync
  "qusb2snes_sync_progress": {                 // NEW: Directory-level progress
    "/ROMS": 1699012300,                       // Root level synced
    "/ROMS/Kaizo": 1699012320,                 // Kaizo subfolder synced  
    "/ROMS/Traditional": 1699012340,           // Traditional subfolder synced
    "/ROMS/Puzzle": 1699012280                 // Puzzle subfolder synced (older)
  },
  "qusb2snes_partial_sync": true               // NEW: Flag indicating partial sync state
}
```

### 2. Incremental Sync Logic
- **Directory Completion**: Mark directories as synced when all files uploaded
- **Granular Resume**: Skip already-synced directories on retry
- **Smart Comparison**: Use per-directory timestamps vs file modification times
- **Partial Recovery**: Resume from first incomplete directory

### 3. Implementation Strategy
1. Track directory sync completion timestamps
2. On sync retry, check each directory's progress
3. Skip directories where progress timestamp > all file modification times
4. Only sync incomplete/modified directories
5. Update global timestamp only on full completion

### 4. User Benefits
- **Fast Recovery**: Resume from 90% completion instead of 0%
- **Efficient Retries**: Only sync what's actually needed
- **Progress Visibility**: Show which directories are complete
- **Bandwidth Savings**: Avoid re-uploading thousands of files

### 5. Implementation Files
- `qusb2snes_sync.py`: Core incremental sync logic
- `config_manager.py`: Enhanced config schema
- `qusb2snes_ui.py`: Progress display and partial state handling