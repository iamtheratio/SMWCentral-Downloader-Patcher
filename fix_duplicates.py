#!/usr/bin/env python3
"""
Script to fix duplicate entries in processed.json
This will identify and merge duplicate hacks based on title, keeping the most complete entry.
"""

import json
import os
import shutil
from datetime import datetime

def load_processed():
    """Load processed.json"""
    try:
        with open("processed.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading processed.json: {e}")
        return {}

def save_processed(data):
    """Save processed.json with backup"""
    # Create backup
    backup_path = f"processed.json.duplicate-fix-backup-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if os.path.exists("processed.json"):
        shutil.copy2("processed.json", backup_path)
        print(f"Created backup: {backup_path}")
    
    try:
        with open("processed.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Successfully saved processed.json with {len(data)} entries")
        return True
    except Exception as e:
        print(f"Error saving processed.json: {e}")
        return False

def find_duplicates(data):
    """Find duplicate hacks based on title"""
    title_groups = {}
    
    for hack_id, hack_data in data.items():
        if isinstance(hack_data, dict) and "title" in hack_data:
            title = hack_data["title"]
            if title not in title_groups:
                title_groups[title] = []
            title_groups[title].append((hack_id, hack_data))
    
    # Return only groups with duplicates
    duplicates = {title: entries for title, entries in title_groups.items() if len(entries) > 1}
    return duplicates

def merge_duplicate_entries(entries):
    """Merge duplicate entries, keeping the most complete data"""
    if len(entries) <= 1:
        return entries[0] if entries else None
    
    print(f"  Found {len(entries)} duplicate entries")
    
    # Sort by completeness score (more complete entries first)
    def completeness_score(entry):
        hack_id, hack_data = entry
        score = 0
        
        # Prefer entries with additional_paths (multi-type support)
        if hack_data.get("additional_paths"):
            score += 100
        
        # Prefer entries with hack_types array
        if hack_data.get("hack_types") and len(hack_data["hack_types"]) > 1:
            score += 50
        
        # Prefer entries with more filled fields
        for field in ["completed_date", "personal_rating", "notes", "time_to_beat", "exits", "authors"]:
            if hack_data.get(field):
                if field == "authors" and isinstance(hack_data[field], list) and len(hack_data[field]) > 0:
                    score += 5
                elif field in ["completed_date", "notes"] and hack_data[field]:
                    score += 10
                elif field in ["personal_rating", "time_to_beat", "exits"] and hack_data[field] > 0:
                    score += 5
        
        # Prefer entries with file_path that exists
        if hack_data.get("file_path") and os.path.exists(hack_data["file_path"]):
            score += 20
        
        return score
    
    sorted_entries = sorted(entries, key=completeness_score, reverse=True)
    
    # Use the most complete entry as base
    best_hack_id, best_data = sorted_entries[0]
    print(f"  Keeping entry {best_hack_id} as primary (score: {completeness_score(sorted_entries[0])})")
    
    # Merge any missing data from other entries
    for hack_id, hack_data in sorted_entries[1:]:
        print(f"  Merging data from entry {hack_id} (score: {completeness_score((hack_id, hack_data))})")
        
        # Merge non-empty fields that are empty in the best entry
        for field, value in hack_data.items():
            if field not in best_data or not best_data[field]:
                if value:  # Only merge non-empty values
                    best_data[field] = value
                    print(f"    Merged {field}: {value}")
        
        # Special handling for lists (authors, hack_types)
        for list_field in ["authors", "hack_types"]:
            if list_field in hack_data and isinstance(hack_data[list_field], list):
                if list_field not in best_data:
                    best_data[list_field] = hack_data[list_field]
                    print(f"    Merged {list_field}: {hack_data[list_field]}")
                elif isinstance(best_data[list_field], list):
                    # Merge unique items
                    original_length = len(best_data[list_field])
                    for item in hack_data[list_field]:
                        if item not in best_data[list_field]:
                            best_data[list_field].append(item)
                    if len(best_data[list_field]) > original_length:
                        print(f"    Added to {list_field}: {best_data[list_field]}")
        
        # Special handling for additional_paths
        if "additional_paths" in hack_data and hack_data["additional_paths"]:
            if "additional_paths" not in best_data:
                best_data["additional_paths"] = hack_data["additional_paths"]
                print(f"    Merged additional_paths: {hack_data['additional_paths']}")
            else:
                # Merge unique paths
                original_length = len(best_data["additional_paths"])
                for path in hack_data["additional_paths"]:
                    if path not in best_data["additional_paths"]:
                        best_data["additional_paths"].append(path)
                if len(best_data["additional_paths"]) > original_length:
                    print(f"    Added to additional_paths: {best_data['additional_paths']}")
    
    return best_hack_id, best_data

def main():
    print("🔍 Loading processed.json...")
    data = load_processed()
    
    if not data:
        print("No data to process")
        return
    
    print(f"📊 Loaded {len(data)} total entries")
    
    print("\n🔍 Finding duplicates...")
    duplicates = find_duplicates(data)
    
    if not duplicates:
        print("✅ No duplicates found!")
        return
    
    print(f"⚠️ Found {len(duplicates)} titles with duplicate entries:")
    
    new_data = {}
    removed_count = 0
    
    # Process non-duplicates first
    for hack_id, hack_data in data.items():
        if isinstance(hack_data, dict) and "title" in hack_data:
            title = hack_data["title"]
            if title not in duplicates:
                new_data[hack_id] = hack_data
    
    # Process duplicates
    for title, entries in duplicates.items():
        print(f"\n📝 Processing duplicates for '{title}':")
        
        best_id, merged_data = merge_duplicate_entries(entries)
        new_data[best_id] = merged_data
        removed_count += len(entries) - 1
        
        print(f"  ✅ Merged into entry {best_id}")
        print(f"  🗑️ Removed {len(entries) - 1} duplicate entries")
    
    print(f"\n📊 Summary:")
    print(f"  Original entries: {len(data)}")
    print(f"  Duplicate titles found: {len(duplicates)}")
    print(f"  Duplicate entries removed: {removed_count}")
    print(f"  Final entries: {len(new_data)}")
    
    if removed_count > 0:
        print(f"\n💾 Saving cleaned data...")
        if save_processed(new_data):
            print("✅ Successfully cleaned up duplicates!")
        else:
            print("❌ Failed to save cleaned data")
    else:
        print("✅ No changes needed")

if __name__ == "__main__":
    main()
