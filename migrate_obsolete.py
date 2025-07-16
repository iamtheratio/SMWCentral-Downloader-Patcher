#!/usr/bin/env python3
"""
Manual migration script to add obsolete field to processed.json
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from api_pipeline import load_processed, save_processed

def run_migration():
    print("🔄 Running obsolete field migration...")
    
    processed = load_processed()
    needs_update = False
    
    for hack_id, hack_data in processed.items():
        if isinstance(hack_data, dict) and "obsolete" not in hack_data:
            hack_data["obsolete"] = False
            needs_update = True
    
    if needs_update:
        save_processed(processed)
        print(f"✅ Migration completed - added obsolete field to {len(processed)} hacks")
    else:
        print("ℹ️ No migration needed - all hacks already have obsolete field")

if __name__ == "__main__":
    run_migration()
