"""
Difficulty Migration System
Handles SMWC difficulty name changes by:
- Auto-detecting mismatches between stored names and current DIFFICULTY_LOOKUP
- Renaming difficulty folders
- Updating processed.json entries
- Maintaining historical consistency

FULLY AUTOMATIC - NO HARDCODED RENAMES NEEDED!

HOW IT WORKS:
=============

When SMWC renames a difficulty (e.g., "Skilled" → "Intermediate"):

1. You ONLY update utils.py:
   DIFFICULTY_LOOKUP = {
       "diff_3": "Intermediate",  # Changed from "Skilled"
   }

2. Migration AUTO-DETECTS the mismatch:
   - Scans all hacks with difficulty_id = "diff_3"
   - Compares stored current_difficulty ("Skilled") vs DIFFICULTY_LOOKUP["diff_3"] ("Intermediate")
   - If mismatch found, queues "Skilled" → "Intermediate" rename

3. Users go to Settings → Difficulty Migration:
   - Shows detected renames (e.g., "Skilled → Intermediate detected in 1,234 hacks")
   - Click "Apply Migrations" to fix folders and JSON

NO MORE MANUAL CONFIGURATION!
- No hardcoded DIFFICULTY_RENAMES dict
- No need to remove old renames
- Just update DIFFICULTY_LOOKUP and migration handles the rest

Copyright (c) 2025 iamtheratio
Licensed under the MIT License - see LICENSE file for details
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set

# Import the current difficulty lookup from utils
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import DIFFICULTY_LOOKUP

# Sorted folder name patterns (number prefix)
FOLDER_NUMBER_MAP = {
    "Newcomer": "01",
    "Casual": "02",
    "Skilled": "03",
    "Intermediate": "03",  # Same number as Skilled since it's a rename
    "Advanced": "04",
    "Expert": "05",
    "Master": "06",
    "Grandmaster": "07",
    "No Difficulty": "08"
}


class DifficultyMigrator:
    """Manages difficulty name migrations across the entire app using auto-detection"""
    
    def __init__(self, output_dir: str, processed_json_path: str = "processed.json"):
        self.output_dir = output_dir
        self.processed_json_path = processed_json_path
        self.migrations_performed: List[Tuple[str, str]] = []
        self.files_moved = 0
        self.json_entries_updated = 0
        self.detected_renames: Dict[str, str] = {}  # Auto-detected renames
    
    def detect_renames_from_data(self) -> Dict[str, Tuple[str, int]]:
        """
        Auto-detect difficulty renames by comparing stored names vs current DIFFICULTY_LOOKUP.
        
        Returns:
            Dict mapping old_name -> (new_name, count_of_affected_hacks)
        """
        if not os.path.exists(self.processed_json_path):
            return {}
        
        try:
            with open(self.processed_json_path, 'r', encoding='utf-8') as f:
                processed = json.load(f)
        except Exception:
            return {}
        
        # Track mismatches: old_name -> (new_name, count)
        mismatches: Dict[str, Dict] = {}
        
        for hack_id, hack_data in processed.items():
            if not isinstance(hack_data, dict):
                continue
            
            difficulty_id = hack_data.get("difficulty_id", "")
            current_difficulty = hack_data.get("current_difficulty", "")
            
            # Skip if no difficulty_id (old format) or no stored name
            if not difficulty_id or not current_difficulty:
                continue
            
            # Look up what the current name SHOULD be
            expected_name = DIFFICULTY_LOOKUP.get(difficulty_id, "")
            
            # If mismatch found, track it
            if expected_name and expected_name != current_difficulty:
                old_name = current_difficulty
                new_name = expected_name
                
                if old_name not in mismatches:
                    mismatches[old_name] = {"new_name": new_name, "count": 0}
                mismatches[old_name]["count"] += 1
        
        # Convert to simpler format
        result = {}
        for old_name, info in mismatches.items():
            result[old_name] = (info["new_name"], info["count"])
        
        return result
    
    def perform_migrations(self, dry_run: bool = False) -> Dict:
        """
        Perform all pending difficulty migrations using auto-detection.
        
        Args:
            dry_run: If True, only report what would be changed without making changes
            
        Returns:
            Dictionary with migration results
        """
        # Auto-detect renames from data
        detected = self.detect_renames_from_data()
        
        if not detected:
            return {"success": True, "message": "No migrations needed", "detected_renames": {}}
        
        # Convert to simple dict for processing
        self.detected_renames = {old: new for old, (new, count) in detected.items()}
        
        results = {
            "success": True,
            "migrations": [],
            "errors": [],
            "dry_run": dry_run,
            "detected_renames": detected  # Include detection info
        }
        
        # Step 1: Rename folders
        for old_name, new_name in self.detected_renames.items():
            folder_result = self._migrate_folders(old_name, new_name, dry_run)
            if folder_result:
                results["migrations"].append(folder_result)
                self.migrations_performed.append((old_name, new_name))
        
        # Step 2: Update processed.json
        if self.migrations_performed:
            json_result = self._migrate_processed_json(dry_run)
            if json_result:
                results["migrations"].append(json_result)
        
        # Step 3: Create summary
        results["summary"] = {
            "folders_renamed": self.files_moved,
            "json_entries_updated": self.json_entries_updated,
            "renames_applied": len(self.migrations_performed)
        }
        
        return results
    
    def _migrate_folders(self, old_name: str, new_name: str, dry_run: bool) -> Optional[Dict]:
        """Rename folders from old difficulty name to new name"""
        if not os.path.exists(self.output_dir):
            return None
        
        old_folder_pattern = self._get_folder_name(old_name)
        new_folder_pattern = self._get_folder_name(new_name)
        
        folders_renamed = []
        
        # Check all hack type folders (Standard, Kaizo, Pit, Tool-Assisted)
        for root, dirs, files in os.walk(self.output_dir):
            # Only process top-level type folders
            if root == self.output_dir:
                for type_folder in dirs:
                    type_path = os.path.join(self.output_dir, type_folder)
                    old_path = os.path.join(type_path, old_folder_pattern)
                    new_path = os.path.join(type_path, new_folder_pattern)
                    
                    if os.path.exists(old_path):
                        if dry_run:
                            folders_renamed.append({
                                "type": type_folder,
                                "old": old_path,
                                "new": new_path
                            })
                        else:
                            try:
                                # If new path already exists, merge folders
                                if os.path.exists(new_path):
                                    self._merge_folders(old_path, new_path)
                                else:
                                    os.rename(old_path, new_path)
                                
                                folders_renamed.append({
                                    "type": type_folder,
                                    "old": old_path,
                                    "new": new_path
                                })
                                self.files_moved += 1
                            except Exception as e:
                                return {
                                    "step": "folder_rename",
                                    "error": f"Failed to rename {old_path}: {str(e)}"
                                }
        
        if folders_renamed:
            return {
                "step": "folder_rename",
                "old_name": old_name,
                "new_name": new_name,
                "folders": folders_renamed
            }
        
        return None
    
    def _merge_folders(self, source: str, destination: str):
        """Merge source folder into destination, moving all files"""
        for item in os.listdir(source):
            source_item = os.path.join(source, item)
            dest_item = os.path.join(destination, item)
            
            if os.path.isfile(source_item):
                # Move file, overwrite if exists
                if os.path.exists(dest_item):
                    os.remove(dest_item)
                shutil.move(source_item, dest_item)
        
        # Remove empty source folder
        try:
            os.rmdir(source)
        except OSError:
            pass  # Folder not empty, that's fine
    
    def _migrate_processed_json(self, dry_run: bool) -> Optional[Dict]:
        """Update all difficulty references in processed.json"""
        if not os.path.exists(self.processed_json_path):
            return None
        
        try:
            with open(self.processed_json_path, 'r', encoding='utf-8') as f:
                processed = json.load(f)
        except Exception as e:
            return {"step": "json_update", "error": f"Failed to load JSON: {str(e)}"}
        
        # Create backup before modifying
        if not dry_run:
            backup_path = f"{self.processed_json_path}.difficulty-migration-{datetime.now().strftime('%Y%m%d_%H%M%S')}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(processed, f, indent=2)
        
        entries_updated = []
        
        # Update all hack entries
        for hack_id, hack_data in processed.items():
            if not isinstance(hack_data, dict):
                continue
            
            updated_fields = {}
            
            # Update current_difficulty field
            if "current_difficulty" in hack_data:
                old_diff = hack_data["current_difficulty"]
                if old_diff in self.detected_renames:
                    new_diff = self.detected_renames[old_diff]
                    updated_fields["current_difficulty"] = (old_diff, new_diff)
                    if not dry_run:
                        hack_data["current_difficulty"] = new_diff
            
            # Update folder_name field
            if "folder_name" in hack_data:
                old_folder = hack_data["folder_name"]
                # Check if folder contains old difficulty name
                for old_name, new_name in self.detected_renames.items():
                    old_pattern = self._get_folder_name(old_name)
                    if old_folder == old_pattern:
                        new_pattern = self._get_folder_name(new_name)
                        updated_fields["folder_name"] = (old_folder, new_pattern)
                        if not dry_run:
                            hack_data["folder_name"] = new_pattern
            
            # Update file_path field
            if "file_path" in hack_data:
                old_path = hack_data["file_path"]
                new_path = old_path
                for old_name, new_name in self.detected_renames.items():
                    old_pattern = self._get_folder_name(old_name)
                    new_pattern = self._get_folder_name(new_name)
                    if old_pattern in old_path:
                        new_path = old_path.replace(old_pattern, new_pattern)
                        break
                
                if new_path != old_path:
                    updated_fields["file_path"] = (old_path, new_path)
                    if not dry_run:
                        hack_data["file_path"] = new_path
            
            # Update additional_paths field
            if "additional_paths" in hack_data and isinstance(hack_data["additional_paths"], list):
                new_additional_paths = []
                paths_changed = False
                
                for old_path in hack_data["additional_paths"]:
                    new_path = old_path
                    for old_name, new_name in self.detected_renames.items():
                        old_pattern = self._get_folder_name(old_name)
                        new_pattern = self._get_folder_name(new_name)
                        if old_pattern in old_path:
                            new_path = old_path.replace(old_pattern, new_pattern)
                            paths_changed = True
                            break
                    new_additional_paths.append(new_path)
                
                if paths_changed:
                    updated_fields["additional_paths"] = (
                        len(hack_data["additional_paths"]),
                        "paths updated"
                    )
                    if not dry_run:
                        hack_data["additional_paths"] = new_additional_paths
            
            if updated_fields:
                entries_updated.append({
                    "hack_id": hack_id,
                    "title": hack_data.get("title", "Unknown"),
                    "fields": updated_fields
                })
                self.json_entries_updated += 1
        
        # Save updated JSON
        if not dry_run and entries_updated:
            try:
                with open(self.processed_json_path, 'w', encoding='utf-8') as f:
                    json.dump(processed, f, indent=2)
            except Exception as e:
                return {"step": "json_update", "error": f"Failed to save JSON: {str(e)}"}
        
        if entries_updated:
            return {
                "step": "json_update",
                "entries_updated": len(entries_updated),
                "sample_updates": entries_updated[:5]  # Show first 5 as samples
            }
        
        return None
    
    def _get_folder_name(self, difficulty_name: str) -> str:
        """Get the sorted folder name for a difficulty (e.g., '03 - Skilled')"""
        number = FOLDER_NUMBER_MAP.get(difficulty_name, "99")
        return f"{number} - {difficulty_name}"


def run_difficulty_migration(output_dir: str, dry_run: bool = False, log_func=None) -> Dict:
    """
    Convenience function to run difficulty migrations with auto-detection.
    
    Args:
        output_dir: Path to ROM output directory
        dry_run: If True, only report what would change
        log_func: Optional logging function
        
    Returns:
        Dictionary with migration results including detected_renames
    """
    migrator = DifficultyMigrator(output_dir)
    results = migrator.perform_migrations(dry_run=dry_run)
    
    # Log results if logger provided
    if log_func:
        detected = results.get("detected_renames", {})
        
        if detected:
            if dry_run:
                log_func("🔍 Difficulty Migration (DRY RUN) - Changes that would be made:", "Information")
            else:
                log_func("✅ Difficulty Migration Complete:", "Information")
            
            # Show detected renames
            for old_name, (new_name, count) in detected.items():
                log_func(f"  🔄 Detected: '{old_name}' → '{new_name}' ({count:,} hacks affected)", "Information")
            
            # Show migration results
            for migration in results.get("migrations", []):
                if migration["step"] == "folder_rename":
                    log_func(f"  📁 Renamed '{migration['old_name']}' → '{migration['new_name']}'", "Information")
                    log_func(f"     Affected {len(migration['folders'])} folder(s)", "Information")
                elif migration["step"] == "json_update":
                    log_func(f"  📝 Updated {migration['entries_updated']} hack entries in processed.json", "Information")
            
            summary = results.get("summary", {})
            log_func(f"  📊 Summary: {summary.get('folders_renamed', 0)} folders, {summary.get('json_entries_updated', 0)} JSON entries", "Information")
        else:
            log_func("✅ No difficulty migrations needed - all data matches current DIFFICULTY_LOOKUP", "Information")
    
    return results


if __name__ == "__main__":
    # Test/standalone execution
    import sys
    
    # Get output directory from command line or use default
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    dry_run = "--dry-run" in sys.argv
    
    print("=" * 60)
    print("Difficulty Migration System - Auto-Detection Mode")
    print("=" * 60)
    print(f"Output Directory: {output_dir}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will make changes)'}")
    print()
    
    migrator = DifficultyMigrator(output_dir)
    
    # First, detect renames
    print("Scanning for difficulty mismatches...")
    detected = migrator.detect_renames_from_data()
    
    if detected:
        print(f"\nFound {len(detected)} difficulty rename(s):")
        for old, (new, count) in detected.items():
            print(f"  • {old} → {new} ({count:,} hacks affected)")
        print()
    else:
        print("\n✅ No migrations needed - all data matches current DIFFICULTY_LOOKUP.")
        sys.exit(0)
    
    # Perform migration
    results = migrator.perform_migrations(dry_run=dry_run)
    
    print("\nMigration Results:")
    print(json.dumps(results, indent=2))
