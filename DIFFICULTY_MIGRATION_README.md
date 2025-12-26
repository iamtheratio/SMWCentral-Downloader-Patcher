# Difficulty Migration System - Auto-Detection

## Overview

The difficulty migration system automatically detects and applies difficulty name changes from SMWCentral. When SMWC renames a difficulty category (e.g., "Skilled" → "Intermediate"), the app can automatically detect and fix all affected hacks, folders, and data.

## How It Works

### 1. **Data Storage**
When downloading hacks, the app now stores TWO difficulty fields:
- `difficulty_id`: The raw API identifier (e.g., "diff_3") - never changes
- `current_difficulty`: The display name (e.g., "Intermediate") - can change

### 2. **Auto-Detection**
The migration system compares stored data against the current `DIFFICULTY_LOOKUP`:

```python
# In utils.py
DIFFICULTY_LOOKUP = {
    "diff_1": "Newcomer",
    "diff_2": "Casual",
    "diff_3": "Intermediate",  # ← Changed from "Skilled"
    # ...
}
```

When scanning processed.json:
- Hack has `difficulty_id="diff_3"` and `current_difficulty="Skilled"`
- Lookup says `DIFFICULTY_LOOKUP["diff_3"] = "Intermediate"`
- **Mismatch detected!** → Skilled needs migrating to Intermediate

### 3. **Migration Actions**
When applied, the migration system:
1. **Renames folders**: `03 - Skilled` → `03 - Intermediate`
2. **Updates JSON**: Changes all difficulty fields in processed.json
3. **Creates backup**: Timestamped backup before any changes
4. **Updates paths**: Fixes file_path and additional_paths fields

## For Developers

### When SMWC Renames a Difficulty

**You only need to update ONE file: `utils.py`**

```python
# Before: SMWC calls it "Expert"
DIFFICULTY_LOOKUP = {
    "diff_5": "Expert",
}

# After: SMWC renames to "Very Hard"
DIFFICULTY_LOOKUP = {
    "diff_5": "Very Hard",
}
```

That's it! The migration system will:
1. Auto-detect all hacks with "Expert" stored but "Very Hard" expected
2. Show count of affected hacks in Settings UI
3. Let users apply the migration with one click

### No Hardcoded Mappings Needed

The old system required manually adding to `DIFFICULTY_RENAMES` dict:
```python
# OLD WAY (removed):
DIFFICULTY_RENAMES = {
    "Skilled": "Intermediate",  # Manual configuration
    "Expert": "Very Hard",       # Manual configuration
}
```

The new system auto-detects by comparing stored `difficulty_id` vs current `DIFFICULTY_LOOKUP`. Zero manual configuration!

## For Users

### Using the Migration Tool

1. **Open Settings** → Navigate to Settings page
2. **Check Status** → Migration section auto-checks on load
3. **Review Changes** → See detected renames with hack counts
4. **Apply Migration** → Click "Apply Migrations" button

### What Gets Changed

**Before Migration:**
```
output/
├── Standard/
│   └── 03 - Skilled/          ← Old name
│       └── HackName.smc
```

**After Migration:**
```
output/
├── Standard/
│   └── 03 - Intermediate/     ← New name
│       └── HackName.smc
```

Plus all entries in `processed.json` get updated with the new name.

### Safety Features

- **Dry Run First**: Check mode shows what WOULD change without making changes
- **Automatic Backups**: Creates timestamped backup of processed.json
- **Folder Merging**: If target folder exists, safely merges contents
- **Error Handling**: Detailed error messages if anything fails

## Technical Details

### Module: `difficulty_migration.py`

**Key Class: `DifficultyMigrator`**

```python
migrator = DifficultyMigrator(output_dir)

# Auto-detect renames
detected = migrator.detect_renames_from_data()
# Returns: {"Skilled": ("Intermediate", 1234)}
#          old_name -> (new_name, hack_count)

# Apply migrations
results = migrator.perform_migrations(dry_run=False)
```

**Convenience Function:**

```python
from difficulty_migration import run_difficulty_migration

results = run_difficulty_migration(
    output_dir="output",
    dry_run=True,  # True = just check, False = apply
    log_func=logger.log  # Optional logging
)
```

### Settings UI Integration

The Settings page automatically:
- **On Load**: Checks for pending migrations (500ms delay)
- **Shows Count**: Displays number of renames and affected hacks
- **Confirmation**: Asks user to confirm before applying
- **Feedback**: Shows progress and results

### Data Format

**processed.json entry (new format):**
```json
{
  "12345": {
    "title": "Hack Name",
    "difficulty_id": "diff_3",           ← Raw API ID (stable)
    "current_difficulty": "Intermediate", ← Display name (can change)
    "folder_name": "03 - Intermediate",
    "file_path": "output/Standard/03 - Intermediate/HackName.smc"
  }
}
```

**Legacy entries (no difficulty_id):**
- Skipped during auto-detection
- Will get updated when hack is re-downloaded

## Examples

### Example 1: Skilled → Intermediate
```
SMWC changes "Skilled" to "Intermediate"

1. Developer updates utils.py:
   DIFFICULTY_LOOKUP["diff_3"] = "Intermediate"

2. Users open Settings page:
   Status: "⚠️ 1 rename(s) detected (1,234 hacks total): Skilled → Intermediate"

3. User clicks "Apply Migrations":
   - Renames "03 - Skilled" folders to "03 - Intermediate"
   - Updates 1,234 entries in processed.json
   - Creates backup: processed.json.difficulty-migration-20240115_143022.backup
```

### Example 2: Multiple Renames
```
SMWC changes "Expert" → "Very Hard" and "Kaizo" → "Extreme"

1. Developer updates utils.py:
   DIFFICULTY_LOOKUP["diff_5"] = "Very Hard"
   DIFFICULTY_LOOKUP["diff_7"] = "Extreme"

2. Auto-detection finds:
   Expert → Very Hard (456 hacks)
   Kaizo → Extreme (789 hacks)

3. Migration applies both renames in one operation
```

## Backward Compatibility

### Old Hacks (no difficulty_id field)
- Still work normally
- Skip during migration detection
- Get updated field next time they're downloaded/updated

### DIFFICULTY_KEYMAP
Still maintains old names for search backward compatibility:
```python
DIFFICULTY_KEYMAP = {
    "skilled": "Intermediate",  # Maps old search term to new name
}
```

This allows searching for "skilled" to still find "Intermediate" hacks.

## Testing

Run standalone test:
```bash
# Dry run (no changes)
python difficulty_migration.py --dry-run

# Live mode (applies changes)
python difficulty_migration.py

# Specify output directory
python difficulty_migration.py /path/to/output
```

## Future Enhancements

Possible improvements:
- [ ] Show migration preview in UI (before/after folder tree)
- [ ] Support batch renames (multiple difficulties at once)
- [ ] Export migration report to file
- [ ] Automatic detection on app startup (with notification)
- [ ] Rollback feature (restore from backup)

## Changelog

**v2.0 - Auto-Detection System** (Current)
- ✅ Removed hardcoded DIFFICULTY_RENAMES dictionary
- ✅ Added difficulty_id field to all hack entries
- ✅ Implemented auto-detection via data comparison
- ✅ Updated Settings UI to show detected renames
- ✅ Zero manual configuration needed

**v1.0 - Manual System** (Deprecated)
- Required manual DIFFICULTY_RENAMES configuration
- No per-hack tracking of difficulty IDs
- Still supported for legacy data
