#!/usr/bin/env python3
"""
Add qusb2snes_last_sync field to all entries in processed.json
This is a one-time migration script to prepare for per-hack QUSB sync tracking
"""
import json
import os
import shutil
from datetime import datetime

def add_qusb_sync_field():
    """Add qusb2snes_last_sync: 0 to all hack entries"""
    processed_path = "processed.json"
    
    # Create backup before modification
    backup_path = f"processed.json.pre-qusb-field-{datetime.now().strftime('%Y%m%d_%H%M%S')}.backup"
    shutil.copy2(processed_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    # Load the data
    with open(processed_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Count modifications
    modified_count = 0
    total_count = 0
    
    # Add qusb2snes_last_sync field to all hack entries
    for hack_id, hack_data in data.items():
        if isinstance(hack_data, dict) and "title" in hack_data:
            total_count += 1
            if "qusb2snes_last_sync" not in hack_data:
                hack_data["qusb2snes_last_sync"] = 0
                modified_count += 1
    
    # Save the updated data
    with open(processed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Added qusb2snes_last_sync field to {modified_count}/{total_count} hack entries")
    print(f"📁 Updated processed.json saved")
    
    return modified_count, total_count

if __name__ == "__main__":
    try:
        modified, total = add_qusb_sync_field()
        print(f"\n🎉 Migration complete!")
        print(f"📊 {modified} hacks updated, {total} total hacks processed")
        print(f"🚀 Ready for per-hack QUSB2SNES sync!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")